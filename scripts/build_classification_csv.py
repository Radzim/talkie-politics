import csv
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED_DIR = REPO_ROOT / "results_classified"
OUTPUT_PATH = REPO_ROOT / "analysis" / "response_classifications.csv"


JUDGE_COLUMNS = {
    "gpt-5.6-terra": "GPT-5.6-terra",
    "Qwen/Qwen3.8-27B-FP8": "Qwen3.8-27B-FP8",
    "zai-org/GLM-5.2-FP8": "GLM-5.2-FP8",
}


def get_run_number(path: Path) -> int:
    match = re.search(r"trial_(\d+)", path.stem)

    if not match:
        raise ValueError(f"Could not determine run from {path}")

    return int(match.group(1))


def judgement_answer(judgement: dict) -> str:
    answer = judgement.get("answer")

    if answer is None:
        return "None"

    return answer


def make_row(input_path: Path, row: dict) -> dict:
    relative = input_path.relative_to(CLASSIFIED_DIR)

    # results_classified/<model>/<test>/trial_X.jsonl
    talkie_model = relative.parts[0]
    test = relative.parts[1]
    run = get_run_number(input_path)

    judges = {
        judgement["model"]: judgement
        for judgement in row["judgements"]
    }

    output = {
        "talkie_model": talkie_model,
        "test": test,
        "run": run,
        "question_index": row["question_index"],
        "question": row["question"],
        "raw_answer": row["model_response_raw"],
    }

    for model_name, column_name in JUDGE_COLUMNS.items():
        judgement = judges.get(model_name)

        output[column_name] = (
            judgement_answer(judgement)
            if judgement is not None
            else ""
        )

    flagged = bool(row["needs_manual_review"])

    output["flagged_for_human_verification"] = int(flagged)

    # Leave blank for the human to fill if judges do not reach
    # an acceptable majority.
    output["final_answer"] = (
        ""
        if flagged
        else (
            "None"
            if row["answer"] is None
            else row["answer"]
        )
    )

    return output


def main() -> None:
    input_files = sorted(
        CLASSIFIED_DIR.rglob("trial_*.jsonl")
    )

    rows = []

    for input_path in input_files:
        with input_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                classified = json.loads(line)

                rows.append(
                    make_row(
                        input_path=input_path,
                        row=classified,
                    )
                )

    rows.sort(
        key=lambda x: (
            x["talkie_model"],
            x["test"],
            x["run"],
            x["question_index"],
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "talkie_model",
        "test",
        "run",
        "question_index",
        "question",
        "raw_answer",
        "GPT-5.6-terra",
        "Qwen3.8-27B-FP8",
        "GLM-5.2-FP8",
        "flagged_for_human_verification",
        "final_answer",
    ]

    with OUTPUT_PATH.open(
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

    print(f"Wrote {len(rows)} rows -> {OUTPUT_PATH}")
    print(f"Flagged for human verification: {flagged_count}")


if __name__ == "__main__":
    main()