# scripts/classify_responses.py

import json
import os
from enum import Enum
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
CLASSIFIED_DIR = REPO_ROOT / "results_classified"

JUDGE_MODEL = "gpt-5.6-terra"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class Reason(str, Enum):
    CLEAR = "clear_answer"
    MOSTLY_CLEAR = "mostly_clear_answer"
    RANDOM_OR_UNRELATED = "random_or_unrelated"
    UNCLEAR_OR_CONTRADICTORY = "unclear_or_contradictory"


class Classification(BaseModel):
    answer: str | None
    reason: Reason


SYSTEM_PROMPT = """
Classify a language model's response to a political questionnaire item.

Return:
- answer: exactly one of the allowed answers, or null
- reason: one of clear_answer, mostly_clear_answer,
  random_or_unrelated, unclear_or_contradictory

Use reasonable inference. The response does not need to use the exact answer wording.

clear_answer:
The response directly and clearly maps to one allowed answer.

mostly_clear_answer:
One allowed answer is reasonably more plausible than the others, but some inference is
needed. Use this for rambling, imperfect, partly off-topic, malformed, or slightly
misinterpreted responses where the intended stance can still be recovered.

random_or_unrelated:
The response is mostly random, malformed, or unrelated and no stance can reasonably
be inferred.

unclear_or_contradictory:
The response is relevant, but there is not enough evidence to choose one answer, or it
expresses unresolved contradictory positions.

If a response gives a usable answer and then degenerates into nonsense, keep the answer
and use mostly_clear_answer.

Some extrapolation is acceptable. Return null only when no answer can reasonably be inferred.

If answer is non-null, reason must be clear_answer or mostly_clear_answer.
If answer is null, reason must be random_or_unrelated or unclear_or_contradictory.
"""


def classify_response(
    question: str,
    allowed_answers: list[str],
    raw_response: str,
) -> Classification:
    prompt = f"""
QUESTION:
{question}

ALLOWED ANSWERS:
{json.dumps(allowed_answers, ensure_ascii=False)}

RAW RESPONSE:
{raw_response}
"""

    response = client.responses.parse(
        model=JUDGE_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        text_format=Classification,
    )

    result = response.output_parsed

    if result is None:
        raise ValueError("Judge returned no parsed result.")

    if result.answer is not None and result.answer not in allowed_answers:
        raise ValueError(
            f"Invalid answer {result.answer!r}; allowed: {allowed_answers}"
        )

    if result.answer is not None and result.reason not in {
        Reason.CLEAR,
        Reason.MOSTLY_CLEAR,
    }:
        raise ValueError(
            f"Inconsistent answer/reason: "
            f"{result.answer!r}, {result.reason.value}"
        )

    if result.answer is None and result.reason in {
        Reason.CLEAR,
        Reason.MOSTLY_CLEAR,
    }:
        raise ValueError(
            f"Inconsistent answer/reason: None, {result.reason.value}"
        )

    return result


def load_completed(output_path: Path) -> set[int]:
    if not output_path.exists():
        return set()

    completed = set()

    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                completed.add(json.loads(line)["question_index"])

    return completed


def classify_file(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    completed = load_completed(output_path)

    with (
        input_path.open("r", encoding="utf-8") as f_in,
        output_path.open("a", encoding="utf-8") as f_out,
    ):
        for line in f_in:
            if not line.strip():
                continue

            row = json.loads(line)
            question_index = row["question_index"]

            if question_index in completed:
                continue

            result = classify_response(
                question=row["question"],
                allowed_answers=row["allowed_answers"],
                raw_response=row["model_response_raw"],
            )

            classified_row = {
                **row,
                "answer": result.answer,
                "reason": result.reason.value,
                "judge_model": JUDGE_MODEL,
            }

            f_out.write(
                json.dumps(classified_row, ensure_ascii=False) + "\n"
            )
            f_out.flush()

            print(
                f"{input_path.name} Q{question_index}: "
                f"{result.answer!r} ({result.reason.value})",
                flush=True,
            )


def main() -> None:
    input_files = sorted(RESULTS_DIR.rglob("trial_*.jsonl"))

    print(f"Found {len(input_files)} files.", flush=True)

    for input_path in input_files:
        relative_path = input_path.relative_to(RESULTS_DIR)
        output_path = CLASSIFIED_DIR / relative_path

        print(f"\nClassifying {relative_path}", flush=True)

        classify_file(input_path, output_path)


if __name__ == "__main__":
    main()