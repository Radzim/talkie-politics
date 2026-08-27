# scripts/score_results.py

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from test_algorithms.eightValuesPoliticalTest import score_8values
from test_algorithms.politicalCompassTest import score_political_compass


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results_classified"
ANALYSIS_DIR = REPO_ROOT / "analysis"

ALL_SCORES_PATH = ANALYSIS_DIR / "scores_all_trials.csv"
SUMMARY_PATH = ANALYSIS_DIR / "scores_summary.csv"

TESTS = {
    "politicalCompassTest",
    "eightValuesPoliticalTest",
}


# ============================================================
# Consensus
# ============================================================

def answer_bucket(
    answer: str | None,
) -> str:
    if answer is None:
        return "none"

    normalized = answer.strip().lower()

    if normalized in {
        "agree",
        "strongly agree",
    }:
        return "agree"

    if normalized in {
        "disagree",
        "strongly disagree",
    }:
        return "disagree"

    if normalized in {
        "neutral",
        "neutral/unsure",
        "unsure",
    }:
        return "neutral"

    raise ValueError(
        f"Unknown classified answer: {answer!r}"
    )


def consensus_answer(
    row: dict,
) -> str | None:
    """
    Recompute final answer from the saved three judge outputs.

    Rules:
    - judge failure -> None
    - lack of coarse agreement -> None
    - exact unanimous answer -> that answer
    - exact majority -> majority answer
    - same direction but no exact majority -> weaker answer
    """
    judgements = row.get(
        "judgements",
        [],
    )

    if len(judgements) != 3:
        return None

    if not all(
        judgement.get(
            "parse_success",
            False,
        )
        for judgement in judgements
    ):
        return None

    answers = [
        judgement.get("answer")
        for judgement in judgements
    ]

    buckets = [
        answer_bucket(answer)
        for answer in answers
    ]

    # Lack of agreement = None.
    if len(set(buckets)) != 1:
        return None

    bucket = buckets[0]

    if bucket == "none":
        return None

    # Exact unanimous agreement.
    if len(set(answers)) == 1:
        return answers[0]

    # Exact majority.
    counts = Counter(answers)

    answer, count = counts.most_common(1)[0]

    if count >= 2:
        return answer

    # Same coarse stance but no exact majority.
    if bucket == "agree":
        return "Agree"

    if bucket == "disagree":
        return "Disagree"

    if bucket == "neutral":
        return "Neutral"

    return None


# ============================================================
# File loading
# ============================================================

def load_jsonl(
    path: Path,
) -> list[dict]:
    rows = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            line = line.strip()

            if line:
                rows.append(
                    json.loads(line)
                )

    return rows


def get_trial_number(
    path: Path,
) -> int:
    return int(
        path.stem.removeprefix(
            "trial_"
        )
    )


def find_trials():
    """
    Expected:

    results_classified/
        <model>/
            politicalCompassTest/
                trial_1.jsonl
                ...
            eightValuesPoliticalTest/
                trial_1.jsonl
                ...
    """
    for model_dir in sorted(
        RESULTS_DIR.iterdir()
    ):
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name

        for test_name in sorted(TESTS):
            test_dir = (
                model_dir / test_name
            )

            if not test_dir.exists():
                continue

            paths = sorted(
                test_dir.glob(
                    "trial_*.jsonl"
                ),
                key=get_trial_number,
            )

            for path in paths:
                yield (
                    model_name,
                    test_name,
                    get_trial_number(path),
                    path,
                )


def answers_from_rows(
    rows: list[dict],
) -> list[str | None]:
    rows = sorted(
        rows,
        key=lambda row: row[
            "question_index"
        ],
    )

    return [
        consensus_answer(row)
        for row in rows
    ]


# ============================================================
# Test scoring
# ============================================================

def score_political_compass_trial(
    answers: list[str | None],
) -> list[dict]:
    result = score_political_compass(
        answers
    )

    return [
        {
            "score_type": "economic score",
            "native": result[
                "economic"
            ],
            "normalized": result[
                "economic_normalized"
            ],
            "adjusted": result[
                "economic_adjusted"
            ],
        },
        {
            "score_type": "social score",
            "native": result[
                "social"
            ],
            "normalized": result[
                "social_normalized"
            ],
            "adjusted": result[
                "social_adjusted"
            ],
        },
    ]


def score_8values_trial(
    answers: list[str | None],
) -> list[dict]:
    result = score_8values(
        answers
    )

    values = (
        "equality",
        "markets",
        "world",
        "nation",
        "liberty",
        "authority",
        "progress",
        "tradition",
    )

    return [
        {
            "score_type": (
                f"{value} score"
            ),
            "native": result[
                value
            ],
            "normalized": result[
                f"{value}_normalized"
            ],
            "adjusted": result[
                f"{value}_adjusted"
            ],
        }
        for value in values
    ]


def score_trial(
    test_name: str,
    answers: list[str | None],
) -> list[dict]:
    if (
        test_name
        == "politicalCompassTest"
    ):
        return score_political_compass_trial(
            answers
        )

    if (
        test_name
        == "eightValuesPoliticalTest"
    ):
        return score_8values_trial(
            answers
        )

    raise ValueError(
        f"Unsupported test: {test_name}"
    )


# ============================================================
# Aggregation
# ============================================================

def mean_variance(
    values: list[float],
) -> tuple[float, float]:
    mean = statistics.mean(
        values
    )

    variance = (
        statistics.pvariance(
            values
        )
        if len(values) > 1
        else 0.0
    )

    return mean, variance


# ============================================================
# Main
# ============================================================

def main() -> None:
    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_score_rows = []

    model_none_total = defaultdict(int)
    model_response_total = defaultdict(int)
    model_trial_none_counts = defaultdict(
        list
    )

    # --------------------------------------------------------
    # Score every individual trial
    # --------------------------------------------------------

    for (
        model_name,
        test_name,
        trial,
        path,
    ) in find_trials():

        rows = load_jsonl(
            path
        )

        answers = answers_from_rows(
            rows
        )

        none_count = sum(
            answer is None
            for answer in answers
        )

        valid_count = (
            len(answers)
            - none_count
        )

        model_none_total[
            model_name
        ] += none_count

        model_response_total[
            model_name
        ] += len(answers)

        model_trial_none_counts[
            model_name
        ].append(
            none_count
        )

        scores = score_trial(
            test_name,
            answers,
        )

        # ----------------------------------------------------
        # Print every individual score
        # ----------------------------------------------------

        print()
        print(
            f"{model_name} | "
            f"{test_name} | "
            f"trial {trial}"
        )

        print(
            f"answered: "
            f"{valid_count}/"
            f"{len(answers)}"
        )

        for score in scores:
            print(
                f"  "
                f"{score['score_type']}: "
                f"native="
                f"{score['native']}  "
                f"normalized="
                f"{score['normalized']}  "
                f"adjusted="
                f"{score['adjusted']}"
            )

            all_score_rows.append(
                {
                    "model name": (
                        model_name
                    ),
                    "test": (
                        test_name
                    ),
                    "trial": (
                        trial
                    ),
                    "score type": (
                        score[
                            "score_type"
                        ]
                    ),
                    "native": (
                        score[
                            "native"
                        ]
                    ),
                    "normalized": (
                        score[
                            "normalized"
                        ]
                    ),
                    "adjusted": (
                        score[
                            "adjusted"
                        ]
                    ),
                    "answered": (
                        valid_count
                    ),
                    "none": (
                        none_count
                    ),
                    "total questions": (
                        len(answers)
                    ),
                }
            )

    # --------------------------------------------------------
    # CSV 1: all individual trial scores
    # --------------------------------------------------------

    all_score_fieldnames = [
        "model name",
        "test",
        "trial",
        "score type",
        "native",
        "normalized",
        "adjusted",
        "answered",
        "none",
        "total questions",
    ]

    with ALL_SCORES_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=(
                all_score_fieldnames
            ),
        )

        writer.writeheader()
        writer.writerows(
            all_score_rows
        )

    # --------------------------------------------------------
    # Aggregate values
    # --------------------------------------------------------

    grouped = defaultdict(
        lambda: {
            "native": [],
            "normalized": [],
            "adjusted": [],
        }
    )

    for row in all_score_rows:
        key = (
            row["model name"],
            row["test"],
            row["score type"],
        )

        for version in (
            "native",
            "normalized",
            "adjusted",
        ):
            value = row[
                version
            ]

            if value is not None:
                grouped[key][
                    version
                ].append(
                    float(value)
                )

    summary_rows = []

    for (
        model_name,
        test_name,
        score_type,
    ), versions in sorted(
        grouped.items()
    ):
        for version in (
            "native",
            "normalized",
            "adjusted",
        ):
            values = versions[
                version
            ]

            if not values:
                continue

            mean, variance = (
                mean_variance(
                    values
                )
            )

            summary_rows.append(
                {
                    "model name": (
                        model_name
                    ),
                    "test": (
                        test_name
                    ),
                    "score type": (
                        score_type
                    ),
                    "version": (
                        version
                    ),
                    "mean": round(
                        mean,
                        4,
                    ),
                    "variance": round(
                        variance,
                        4,
                    ),
                }
            )

    # --------------------------------------------------------
    # CSV 2: summary
    # --------------------------------------------------------

    summary_fieldnames = [
        "model name",
        "test",
        "score type",
        "version",
        "mean",
        "variance",
    ]

    with SUMMARY_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=(
                summary_fieldnames
            ),
        )

        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print()

    print(
        "model name\t"
        "test\t"
        "score type\t"
        "version\t"
        "mean\t"
        "variance"
    )

    for row in summary_rows:
        print(
            f"{row['model name']}\t"
            f"{row['test']}\t"
            f"{row['score type']}\t"
            f"{row['version']}\t"
            f"{row['mean']}\t"
            f"{row['variance']}"
        )

    # --------------------------------------------------------
    # None / unresolved summary
    # --------------------------------------------------------

    print()
    print("=" * 100)
    print(
        "NONE / UNRESOLVED RESPONSES"
    )
    print("=" * 100)
    print()

    print(
        "model name\t"
        "average none per trial\t"
        "total none\t"
        "total responses\t"
        "none rate\t"
        "answered rate"
    )

    for model_name in sorted(
        model_response_total
    ):
        average_none = (
            statistics.mean(
                model_trial_none_counts[
                    model_name
                ]
            )
        )

        total_none = (
            model_none_total[
                model_name
            ]
        )

        total_responses = (
            model_response_total[
                model_name
            ]
        )

        none_rate = (
            total_none
            / total_responses
            if total_responses
            else 0.0
        )

        answered_rate = (
            1.0 - none_rate
        )

        print(
            f"{model_name}\t"
            f"{average_none:.2f}\t"
            f"{total_none}\t"
            f"{total_responses}\t"
            f"{100 * none_rate:.2f}%\t"
            f"{100 * answered_rate:.2f}%"
        )

    # --------------------------------------------------------
    # Output paths
    # --------------------------------------------------------

    print()
    print(
        f"All trial scores: "
        f"{ALL_SCORES_PATH}"
    )

    print(
        f"Summary scores: "
        f"{SUMMARY_PATH}"
    )


if __name__ == "__main__":
    main()