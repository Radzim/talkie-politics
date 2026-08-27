# scripts/classify_responses.py

import json
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path

from talkie_politics.llm import ask_llm


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
CLASSIFIED_DIR = REPO_ROOT / "results_classified"

TESTS = {
    "politicalCompassTest",
    "eightValuesPoliticalTest",
}

JUDGES = [
    {"provider": "openai", "model": "gpt-5.6-terra"},
    {"provider": "cambridge", "model": "moonshotai/Kimi-K3"},
    {"provider": "cambridge", "model": "zai-org/GLM-5.2-FP8"},
]

MAX_RETRIES = 3
MAX_WORKERS = 10


class Reason(str, Enum):
    CLEAR = "clear_answer"
    MOSTLY_CLEAR = "mostly_clear_answer"
    RANDOM_OR_UNRELATED = "random_or_unrelated"
    UNCLEAR_OR_CONTRADICTORY = "unclear_or_contradictory"


VALID_REASONS = {reason.value for reason in Reason}


SYSTEM_PROMPT = """
Classify a language model's response to a political questionnaire item.

Return JSON only:
{
  "answer": one of the allowed answers, or null,
  "reason": "clear_answer | mostly_clear_answer | random_or_unrelated | unclear_or_contradictory"
}

Use reasonable inference. The response does not need to use the exact answer wording.

clear_answer:
The response directly and clearly maps to one allowed answer.

mostly_clear_answer:
One answer can reasonably be inferred, but the response is imperfect, rambling,
partly unrelated, malformed, or answers a slightly different interpretation.

random_or_unrelated:
The response is mostly random, malformed, or unrelated and no stance can reasonably
be inferred.

unclear_or_contradictory:
The response is relevant, but no single answer can reasonably be chosen, including
unresolved contradictions.

If a response gives a usable answer and then degenerates into nonsense, keep the
answer and use mostly_clear_answer.

Some inference and extrapolation are acceptable. Return null only when no answer can
reasonably be inferred.

If answer is non-null, reason must be clear_answer or mostly_clear_answer.
If answer is null, reason must be random_or_unrelated or unclear_or_contradictory.
"""


def clean_json_response(raw: str) -> str:
    """
    Remove common Markdown code fences around JSON.
    """
    cleaned = raw.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def classify_response_once(
    question: str,
    allowed_answers: list[str],
    raw_response: str,
    judge: dict,
    max_retries: int = MAX_RETRIES,
) -> dict:
    provider = judge["provider"]
    model = judge["model"]

    prompt = f"""
{SYSTEM_PROMPT}

QUESTION:
{question}

ALLOWED ANSWERS:
{json.dumps(allowed_answers, ensure_ascii=False)}

RAW RESPONSE:
{raw_response}
"""

    last_error = None
    last_raw = None

    for attempt in range(1, max_retries + 1):
        try:
            raw = ask_llm(
                provider=provider,
                model=model,
                prompt=prompt,
            )

            last_raw = raw
            cleaned = clean_json_response(raw)

            try:
                result = json.loads(cleaned)

            except json.JSONDecodeError as e:
                print(
                    f"\n{provider}/{model}: JSON parse error "
                    f"(attempt {attempt}/{max_retries})\n"
                    f"RAW RESPONSE: {raw!r}\n"
                    f"CLEANED RESPONSE: {cleaned!r}\n"
                    f"ERROR: {e}\n",
                    flush=True,
                )
                raise

            answer = result["answer"]
            reason = result["reason"]

            if answer is not None and answer not in allowed_answers:
                raise ValueError(
                    f"Invalid answer {answer!r}; "
                    f"allowed: {allowed_answers}"
                )

            if reason not in VALID_REASONS:
                raise ValueError(
                    f"Invalid reason: {reason!r}"
                )

            if answer is not None and reason not in {
                Reason.CLEAR.value,
                Reason.MOSTLY_CLEAR.value,
            }:
                raise ValueError(
                    f"Inconsistent answer/reason: "
                    f"{answer!r}, {reason!r}"
                )

            if answer is None and reason in {
                Reason.CLEAR.value,
                Reason.MOSTLY_CLEAR.value,
            }:
                raise ValueError(
                    f"Inconsistent answer/reason: "
                    f"None, {reason!r}"
                )

            return {
                "provider": provider,
                "model": model,
                "answer": answer,
                "reason": reason,
                "parse_success": True,
            }

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            last_error = str(e)

            print(
                f"{provider}/{model}: invalid response "
                f"(attempt {attempt}/{max_retries}): {e}",
                flush=True,
            )

        except Exception as e:
            last_error = str(e)

            print(
                f"{provider}/{model}: API error "
                f"(attempt {attempt}/{max_retries}): {e}",
                flush=True,
            )

        if attempt < max_retries:
            delay = 2 ** (attempt - 1)

            print(
                f"{provider}/{model}: "
                f"retrying in {delay}s...",
                flush=True,
            )

            time.sleep(delay)

    return {
        "provider": provider,
        "model": model,
        "answer": None,
        "reason": Reason.UNCLEAR_OR_CONTRADICTORY.value,
        "parse_success": False,
        "parse_error": last_error,
        "raw_response": last_raw,
    }


def answer_bucket(
    answer: str | None,
) -> str:
    """
    Collapse exact answers into:

    agree
    disagree
    neutral_or_none
    """
    if answer is None:
        return "neutral_or_none"

    normalized = answer.strip().lower()

    if (
        "neutral" in normalized
        or "unsure" in normalized
    ):
        return "neutral_or_none"

    # Check disagree first because "disagree"
    # contains the substring "agree".
    if "disagree" in normalized:
        return "disagree"

    if "agree" in normalized:
        return "agree"

    raise ValueError(
        f"Cannot map answer to stance bucket: "
        f"{answer!r}"
    )


def choose_exact_answer(
    judgements: list[dict],
    winning_bucket: str,
    allowed_answers: list[str],
) -> str | None:
    """
    Called only when coarse stance is agreed.

    Rules:
    - exact majority wins
    - if no exact majority within agree/disagree,
      prefer the non-strong answer
    - if no exact majority within neutral_or_none,
      return None
    """
    answers = [
        judgement["answer"]
        for judgement in judgements
    ]

    counts = Counter(answers)

    most_common_answer, most_common_count = (
        counts.most_common(1)[0]
    )

    if most_common_count >= 2:
        return most_common_answer

    if winning_bucket == "neutral_or_none":
        return None

    for allowed_answer in allowed_answers:
        if (
            answer_bucket(allowed_answer)
            == winning_bucket
            and "strong"
            not in allowed_answer.lower()
        ):
            return allowed_answer

    return answers[0]


def combine_judgements(
    judgements: list[dict],
    allowed_answers: list[str],
) -> dict:
    """
    Consensus rules:

    All 3 judges successful:
        all 3 must agree on coarse stance.

    Exactly 1 failed judge:
        manual review, EXCEPT when both
        successful judges returned exactly None.

    2+ failed judges:
        manual review.
    """
    successful = [
        judgement
        for judgement in judgements
        if judgement["parse_success"]
    ]

    failed = [
        judgement
        for judgement in judgements
        if not judgement["parse_success"]
    ]

    # Exactly one failed judge.
    if len(failed) == 1:
        if (
            len(successful) == 2
            and successful[0]["answer"] is None
            and successful[1]["answer"] is None
        ):
            return {
                "answer": None,
                "stance": "neutral_or_none",
                "needs_manual_review": False,
                "review_reason": None,
            }

        return {
            "answer": None,
            "stance": None,
            "needs_manual_review": True,
            "review_reason": "one_judge_failed",
        }

    # Two or more failed judges.
    if len(failed) >= 2:
        return {
            "answer": None,
            "stance": None,
            "needs_manual_review": True,
            "review_reason": "multiple_judges_failed",
        }

    # All three succeeded.
    buckets = [
        answer_bucket(judgement["answer"])
        for judgement in judgements
    ]

    # Require unanimous coarse stance.
    if len(set(buckets)) != 1:
        return {
            "answer": None,
            "stance": None,
            "needs_manual_review": True,
            "review_reason": "stance_disagreement",
        }

    winning_bucket = buckets[0]

    final_answer = choose_exact_answer(
        judgements=judgements,
        winning_bucket=winning_bucket,
        allowed_answers=allowed_answers,
    )

    return {
        "answer": final_answer,
        "stance": winning_bucket,
        "needs_manual_review": False,
        "review_reason": None,
    }


def classify_response(
    question: str,
    allowed_answers: list[str],
    raw_response: str,
) -> dict:
    """
    Run all three judges concurrently for one
    Talkie response.
    """
    judgements = []

    with ThreadPoolExecutor(
        max_workers=len(JUDGES)
    ) as executor:
        future_to_judge = {
            executor.submit(
                classify_response_once,
                question,
                allowed_answers,
                raw_response,
                judge,
            ): judge
            for judge in JUDGES
        }

        for future in as_completed(
            future_to_judge
        ):
            judgements.append(
                future.result()
            )

    # Restore fixed judge ordering.
    judgement_order = {
        (
            judge["provider"],
            judge["model"],
        ): i
        for i, judge in enumerate(JUDGES)
    }

    judgements.sort(
        key=lambda judgement: judgement_order[
            (
                judgement["provider"],
                judgement["model"],
            )
        ]
    )

    consensus = combine_judgements(
        judgements=judgements,
        allowed_answers=allowed_answers,
    )

    return {
        "judgements": judgements,
        **consensus,
    }


def read_existing_rows(
    output_path: Path,
) -> list[dict]:
    """
    Read all rows from an existing classified JSONL.
    """
    if not output_path.exists():
        return []

    rows = []

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            if not line.strip():
                continue

            rows.append(
                json.loads(line)
            )

    return rows


def prepare_output_file(
    output_path: Path,
) -> set[int]:
    """
    Prepare the classified file before a new pass.

    Resolved rows:
        retained and treated as completed.

    needs_manual_review=True rows:
        removed completely, making them equivalent
        to missing rows so they are judged again.

    Existing rows are sorted by question_index.

    Duplicate question indices are collapsed by
    keeping the last retained occurrence.
    """
    if not output_path.exists():
        return set()

    rows = read_existing_rows(
        output_path
    )

    kept_rows = [
        row
        for row in rows
        if not row.get(
            "needs_manual_review",
            False,
        )
    ]

    # In case duplicates exist, keep the last
    # non-flagged occurrence.
    rows_by_index = {
        row["question_index"]: row
        for row in kept_rows
    }

    kept_rows = sorted(
        rows_by_index.values(),
        key=lambda row: row["question_index"],
    )

    # Rewrite without flagged rows.
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        for row in kept_rows:
            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )

    return {
        row["question_index"]
        for row in kept_rows
    }


def sort_output_file(
    output_path: Path,
) -> None:
    """
    Sort the final JSONL by question_index.

    Since results arrive via as_completed(), they are
    naturally written in completion order rather than
    questionnaire order.
    """
    if not output_path.exists():
        return

    rows = read_existing_rows(
        output_path
    )

    # Protect against accidental duplicate indices.
    rows_by_index = {
        row["question_index"]: row
        for row in rows
    }

    sorted_rows = sorted(
        rows_by_index.values(),
        key=lambda row: row["question_index"],
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        for row in sorted_rows:
            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


def classify_row(
    row: dict,
) -> dict:
    result = classify_response(
        question=row["question"],
        allowed_answers=row["allowed_answers"],
        raw_response=row["model_response_raw"],
    )

    return {
        **row,
        "answer": result["answer"],
        "stance": result["stance"],
        "needs_manual_review": (
            result["needs_manual_review"]
        ),
        "review_reason": (
            result["review_reason"]
        ),
        "judgements": result["judgements"],
    }


def print_result(
    input_path: Path,
    row: dict,
) -> None:
    judge_summary = " / ".join(
        (
            f"{judgement['model']}: "
            f"{judgement['answer']!r} "
            f"({judgement['reason']})"
        )
        for judgement in row["judgements"]
    )

    if row["needs_manual_review"]:
        display = (
            f"MANUAL REVIEW "
            f"[{row['review_reason']}]"
        )

    else:
        display = (
            f"{row['answer']!r} "
            f"[{row['stance']}]"
        )

    print(
        f"{input_path.name} "
        f"Q{row['question_index']}: "
        f"{display} | "
        f"{judge_summary}",
        flush=True,
    )


def classify_file(
    input_path: Path,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # IMPORTANT:
    #
    # Any previously flagged rows are removed here.
    # Therefore they behave exactly like missing rows
    # and are reclassified during this run.
    completed = prepare_output_file(
        output_path
    )

    rows_to_classify = []

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            if not line.strip():
                continue

            row = json.loads(line)

            if (
                row["question_index"]
                in completed
            ):
                continue

            rows_to_classify.append(
                row
            )

    # Deterministic submission order.
    rows_to_classify.sort(
        key=lambda row: row["question_index"]
    )

    if not rows_to_classify:
        print(
            f"{input_path.name}: "
            f"already complete",
            flush=True,
        )

        # Existing file is already sorted by
        # prepare_output_file().
        return

    print(
        f"{input_path.name}: "
        f"classifying "
        f"{len(rows_to_classify)} responses "
        f"with {MAX_WORKERS} workers",
        flush=True,
    )

    write_lock = threading.Lock()

    with (
        output_path.open(
            "a",
            encoding="utf-8",
        ) as f_out,
        ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor,
    ):
        future_to_row = {
            executor.submit(
                classify_row,
                row,
            ): row
            for row in rows_to_classify
        }

        for future in as_completed(
            future_to_row
        ):
            original_row = (
                future_to_row[future]
            )

            try:
                classified_row = (
                    future.result()
                )

            except Exception as e:
                print(
                    f"{input_path.name} "
                    f"Q{original_row['question_index']}: "
                    f"FAILED: {e}",
                    flush=True,
                )
                continue

            with write_lock:
                f_out.write(
                    json.dumps(
                        classified_row,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                f_out.flush()

            print_result(
                input_path=input_path,
                row=classified_row,
            )

    # Restore questionnaire order after concurrent
    # writes.
    sort_output_file(
        output_path
    )


def main() -> None:
    input_files = sorted(
        path
        for path in RESULTS_DIR.rglob(
            "trial_*.jsonl"
        )
        if path.parent.name in TESTS
    )

    print(
        f"Found {len(input_files)} files.",
        flush=True,
    )

    print(
        f"Using {MAX_WORKERS} concurrent "
        f"responses and {len(JUDGES)} "
        f"concurrent judges per response.",
        flush=True,
    )

    print(
        f"Maximum theoretical concurrent "
        f"API calls: "
        f"{MAX_WORKERS * len(JUDGES)}",
        flush=True,
    )

    for input_path in input_files:
        relative_path = (
            input_path.relative_to(
                RESULTS_DIR
            )
        )

        output_path = (
            CLASSIFIED_DIR
            / relative_path
        )

        print(
            f"\nClassifying "
            f"{relative_path}",
            flush=True,
        )

        classify_file(
            input_path=input_path,
            output_path=output_path,
        )


if __name__ == "__main__":
    main()