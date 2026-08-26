import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = REPO_ROOT / "data" / "questions"
OUTPUT_DIR = REPO_ROOT / "data" / "questions_historical"

MODELS = [
    "judge_model_1",
    "judge_model_2",
    "judge_model_3",
]

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


def classify_question_once(
    question: str,
    model: str,
    max_retries: int = MAX_RETRIES,
) -> dict:
    prompt = f"""{SYSTEM_PROMPT}

QUESTION:
{question}
"""

    last_error = None
    last_raw = None

    for attempt in range(1, max_retries + 1):
        raw = ask_llm(
            model=model,
            prompt=prompt,
        )

        last_raw = raw

        try:
            result = json.loads(raw)

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
                f"{model}: invalid response "
                f"(attempt {attempt}/{max_retries}): {e}",
                flush=True,
            )

    return {
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
    models: list[str] = MODELS,
) -> dict:
    judgements = [
        classify_question_once(
            question=question,
            model=model,
        )
        for model in models
    ]

    statuses = [
        judgement["status"]
        for judgement in judgements
    ]

    counts = Counter(statuses)

    full_agreement = len(counts) == 1

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
) -> None:
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
            display_status = (
                classification["consensus_status"]
            )
        else:
            display_status = "DISAGREEMENT"

        print(
            f"{input_path.stem} "
            f"Q{question_index}: "
            f"{display_status}",
            flush=True,
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


def main() -> None:
    input_files = sorted(
        QUESTIONS_DIR.glob("*.json")
    )

    print(
        f"Found {len(input_files)} question sets.",
        flush=True,
    )

    for input_path in input_files:
        output_path = (
            OUTPUT_DIR / input_path.name
        )

        print(
            f"\nClassifying {input_path.name}",
            flush=True,
        )

        classify_question_file(
            input_path=input_path,
            output_path=output_path,
        )


if __name__ == "__main__":
    main()