# Extracts one canonical question set per political test from:
# Rozado, D. (2024). The Political Preferences of LLMs.
# Data: https://zenodo.org/records/10553530

import json
from pathlib import Path


ROOT = Path("rozado_results")
OUT = Path("data/questions")

TEST_NAMES = [
    "politicalCompassTest",
    "politicalSpectrumQuiz",
    "worldSmallestPoliticalQuiz",
    "politicalCoordinatesTest",
    "eysenckPoliticalTest",
    "ideologiesTest",
    "eightValuesPoliticalTest",
    "nolanTest",
    "iSideWithUS",
    "iSideWithUK",
    "politicalTypologyQuiz",
]


def extract_questions(jsonl_path: Path) -> list[dict]:
    questions = {}

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            row = json.loads(line)
            idx = row["question_index"]

            questions[idx] = {
                "question_index": idx,
                "question": row["question"],
                "question_expanded": row["question_expanded"],
                "allowed_answers": row["allowed_answers"],
            }

    return [questions[i] for i in sorted(questions)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    total_questions = 0

    for test_name in TEST_NAMES:
        test_dirs = [
            p for p in ROOT.rglob(test_name)
            if p.is_dir()
        ]

        if not test_dirs:
            print(f"Missing test: {test_name}")
            continue

        test_dir = test_dirs[0]

        # Find any single trial JSONL underneath this test.
        jsonl_files = sorted(test_dir.rglob("*.jsonl"))

        if not jsonl_files:
            print(f"No JSONL found for {test_name}")
            continue

        source = jsonl_files[0]
        questions = extract_questions(source)

        output_path = OUT / f"{test_name}.json"

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                questions,
                f,
                indent=2,
                ensure_ascii=False,
            )

        total_questions += len(questions)

        print(
            f"{test_name}: {len(questions)} questions "
            f"-> {output_path}"
        )

    print()
    print(f"Extracted {len(TEST_NAMES)} test sets")
    print(f"Extracted {total_questions} questions total")


if __name__ == "__main__":
    main()