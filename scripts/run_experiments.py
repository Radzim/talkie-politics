import json
import time
from pathlib import Path

from talkie_politics.inference import ask_talkie, load_model


REPO_ROOT = Path(__file__).resolve().parents[1]

QUESTIONS_DIR = REPO_ROOT / "data" / "questions"
RESULTS_DIR = REPO_ROOT / "results"

MODELS = [
    "1930_it",
    "1930_base",
    "web_base",
]

MODEL_OUTPUT_NAMES = {
    "1930_it": "talkie-1930-13b-it",
    "1930_base": "talkie-1930-13b-base",
    "web_base": "talkie-web-13b-base",
}

TESTS = [
    "politicalCompassTest",
    "eightValuesPoliticalTest",
]

N_TRIALS = 10
MAX_TOKENS = 100
TEMPERATURE = 0.7


def load_questions(test_name: str) -> list[dict]:
    path = QUESTIONS_DIR / f"{test_name}.json"

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_completed_questions(output_path: Path) -> set[int]:
    if not output_path.exists():
        return set()

    completed = set()

    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            row = json.loads(line)
            completed.add(row["question_index"])

    return completed


def append_result(output_path: Path, result: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        f.flush()


def run_test(
    model_name: str,
    test_name: str,
    trial: int,
) -> None:
    experiment_start = time.perf_counter()

    questions = load_questions(test_name)
    output_name = MODEL_OUTPUT_NAMES[model_name]

    output_path = (
        RESULTS_DIR
        / output_name
        / test_name
        / f"trial_{trial}.jsonl"
    )

    completed = get_completed_questions(output_path)

    print()
    print("=" * 80)
    print(f"Model: {output_name}")
    print(f"Test:  {test_name}")
    print(f"Trial: {trial}")
    print(f"Completed: {len(completed)}/{len(questions)}")
    print("=" * 80)

    for position, question in enumerate(questions, start=1):
        question_index = question["question_index"]

        if question_index in completed:
            print(
                f"[{position}/{len(questions)}] "
                f"Question {question_index}: already completed"
            )
            continue

        print()
        print(
            f"[{position}/{len(questions)}] "
            f"Question {question_index}"
        )
        print(question["question"])
        print()

        response = ask_talkie(
            model_name=model_name,
            prompt=question["question_expanded"],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            stream_output=True,
        )

        result = {
            "question_index": question_index,
            "question": question["question"],
            "question_expanded": question["question_expanded"],
            "allowed_answers": question["allowed_answers"],
            "model_response_raw": response,
        }

        append_result(output_path, result)

        print(f"Saved -> {output_path}")

    experiment_elapsed = time.perf_counter() - experiment_start

    print(
        f"Finished {output_name} / {test_name} / trial {trial} "
        f"in {experiment_elapsed / 60:.1f} minutes."
    )


def main() -> None:
    start_time = time.perf_counter()

    for trial in range(1, N_TRIALS + 1):
        print()
        print("#" * 80)
        print(f"TRIAL {trial}/{N_TRIALS}")
        print("#" * 80)

        for model_name in MODELS:
            print()
            print(f"Loading model: {model_name}")

            load_model(model_name)

            for test_name in TESTS:
                run_test(
                    model_name=model_name,
                    test_name=test_name,
                    trial=trial,
                )

    elapsed = time.perf_counter() - start_time

    print()
    print(f"All experiments complete in {elapsed / 60:.1f} minutes.")


if __name__ == "__main__":
    main()