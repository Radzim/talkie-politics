import csv
import json
from pathlib import Path

from talkie_politics.llm import ask_llm


REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = REPO_ROOT / "data" / "questions"
OUTPUT_DIR = REPO_ROOT / "data" / "questions_historical"
CSV_PATH = REPO_ROOT / "analysis" / "questions_historical_review.csv"

JUDGES = [
    {
        "provider": "openai",
        "model": "gpt-5.6-terra",
    },
    {
        "provider": "cambridge",
        "model": "moonshotai/Kimi-K3",
    },
    {
        "provider": "cambridge",
        "model": "zai-org/GLM-5.2-FP8",
    },
]

JUDGE_COLUMNS = {
    "gpt-5.6-terra": "GPT-5.6-terra",
    "moonshotai/Kimi-K3": "Kimi-K3",
    "zai-org/GLM-5.2-FP8": "GLM-5.2-FP8",
}

MAX_RETRIES = 3

VALID_STATUSES = {
    "answerable_pre_1930",
    "anachronistic",
    "uncertain",
}


SYSTEM_PROMPT = """
Decide whether a reasonably informed English-speaking person in 1930 could understand
and meaningfully answer the political questionnaire item below.

Classify it as exactly one of:

answerable_pre_1930
anachronistic
uncertain

Use:
- answerable_pre_1930 if the entities, events, institutions, technologies, political
  concepts, and social issues needed to understand the question existed or were
  intelligible by 1930.
- anachronistic if understanding the question depends on something that did not yet
  exist in 1930, such as the United Nations, European Union, World War II, or later
  political developments.
- uncertain if it is genuinely unclear.

Do not mark something anachronistic merely because the wording sounds modern.

This is about whether the question could be understood and answered in 1930, not
whether a person in 1930 would know what later happened.

Return JSON only:
{
  "status": "answerable_pre_1930 | anachronistic | uncertain",
  "reason": "brief explanation"
}
"""


def clean_json_response(raw: str) -> str:
    cleaned = raw.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def classify_question_once(
    question: str,
    judge: dict,
    max_retries: int = MAX_RETRIES,
) -> dict:
    provider = judge["provider"]
    model = judge["model"]

    prompt = f"""{SYSTEM_PROMPT}

QUESTION:
{question}
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
            result = json.loads(cleaned)

            status = result["status"]
            reason = result["reason"]

            if status not in VALID_STATUSES:
                raise ValueError(
                    f"Invalid status: {status!r}"
                )

            if not isinstance(reason, str):
                raise ValueError(
                    "reason must be a string"
                )

            return {
                "provider": provider,
                "model": model,
                "status": status,
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

    return {
        "provider": provider,
        "model": model,
        "status": "uncertain",
        "reason": (
            "Judge failed to return a valid classification "
            f"after {max_retries} attempts."
        ),
        "parse_success": False,
        "parse_error": last_error,
        "raw_response": last_raw,
    }


def classify_question(
    question: str,
    judges: list[dict] = JUDGES,
) -> dict:
    judgements = [
        classify_question_once(
            question=question,
            judge=judge,
        )
        for judge in judges
    ]

    statuses = [
        judgement["status"]
        for judgement in judgements
    ]

    all_parsed = all(
        judgement["parse_success"]
        for judgement in judgements
    )

    full_agreement = (
        all_parsed
        and len(set(statuses)) == 1
    )

    consensus_status = (
        statuses[0]
        if full_agreement
        else None
    )

    return {
        "judgements": judgements,
        "full_agreement": full_agreement,
        "consensus_status": consensus_status,
        "needs_manual_review": not full_agreement,
    }


def classify_question_file(
    input_path: Path,
    output_path: Path,
) -> list[dict]:
    with input_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        questions = json.load(f)

    results = []

    for row in questions:
        question_index = row["question_index"]
        question = row["question"]

        classification = classify_question(
            question=question,
        )

        result = {
            **row,
            **classification,
        }

        results.append(result)

        if classification["full_agreement"]:
            display_status = classification[
                "consensus_status"
            ]
        else:
            judge_statuses = [
                judgement["status"]
                for judgement in classification[
                    "judgements"
                ]
            ]

            display_status = (
                "DISAGREEMENT: "
                + " / ".join(judge_statuses)
            )

        print(
            f"{input_path.stem} "
            f"Q{question_index}: "
            f"{display_status}",
            flush=True,
        )

    results.sort(
        key=lambda row: row["question_index"]
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return results


def build_csv_row(
    test_name: str,
    row: dict,
) -> dict:
    judgements = {
        judgement["model"]: judgement
        for judgement in row["judgements"]
    }

    output = {
        "test": test_name,
        "question_index": row["question_index"],
        "question": row["question"],
    }

    for model_name, column_name in JUDGE_COLUMNS.items():
        judgement = judgements.get(model_name)

        if judgement is None:
            output[column_name] = ""
        elif not judgement.get("parse_success", False):
            output[column_name] = "FAILED"
        else:
            output[column_name] = judgement["status"]

    flagged = bool(
        row["needs_manual_review"]
    )

    output["flagged_for_human_verification"] = (
        1 if flagged else 0
    )

    output["final_status"] = (
        ""
        if flagged
        else row["consensus_status"]
    )

    return output


def write_review_csv(
    all_results: list[tuple[str, list[dict]]],
) -> None:
    CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    for test_name, results in all_results:
        for row in results:
            rows.append(
                build_csv_row(
                    test_name=test_name,
                    row=row,
                )
            )

    rows.sort(
        key=lambda row: (
            row["test"],
            row["question_index"],
        )
    )

    fieldnames = [
        "test",
        "question_index",
        "question",
        "GPT-5.6-terra",
        "Kimi-K3",
        "GLM-5.2-FP8",
        "flagged_for_human_verification",
        "final_status",
    ]

    with CSV_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    flagged_count = sum(
        row["flagged_for_human_verification"]
        for row in rows
    )

    print(
        f"\nWrote {len(rows)} rows -> {CSV_PATH}",
        flush=True,
    )

    print(
        f"Flagged for human verification: "
        f"{flagged_count}",
        flush=True,
    )


def main() -> None:
    input_files = sorted(
        QUESTIONS_DIR.glob("*.json")
    )

    print(
        f"Found {len(input_files)} question sets.",
        flush=True,
    )

    all_results = []

    for input_path in input_files:
        output_path = (
            OUTPUT_DIR / input_path.name
        )

        print(
            f"\nClassifying {input_path.name}",
            flush=True,
        )

        results = classify_question_file(
            input_path=input_path,
            output_path=output_path,
        )

        all_results.append(
            (
                input_path.stem,
                results,
            )
        )

    write_review_csv(
        all_results
    )


if __name__ == "__main__":
    main()