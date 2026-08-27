from collections.abc import Sequence

questions = [
    {
        "question": "Oppression by corporations is more of a concern than oppression by governments.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": -5,
            "scty": 0
        }
    },
    {
        "question": "It is necessary for the government to intervene in the economy to protect consumers.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "The freer the markets, the freer the people.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "It is better to maintain a balanced budget than to ensure welfare for all citizens.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Publicly-funded research is more beneficial to the people than leaving it to the market.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Tariffs on international trade are important to encourage local production.",
        "effect": {
            "econ": 5,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "From each according to his ability, to each according to his needs.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "It would be best if social programs were abolished in favor of private charity.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Taxes should be increased on the rich to provide for the poor.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Inheritance is a legitimate form of wealth.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": -5
        }
    },
    {
        "question": "Basic utilities like roads and electricity should be publicly owned.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Government intervention is a threat to the economy.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Those with a greater ability to pay should receive better healthcare.",
        "effect": {
            "econ": -10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Quality education is a right of all people.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 5
        }
    },
    {
        "question": "The means of production should belong to the workers who use them.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "The United Nations should be abolished.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -5,
            "scty": 0
        }
    },
    {
        "question": "Military action by our nation is often necessary to protect it.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "I support regional unions, such as the European Union.",
        "effect": {
            "econ": -5,
            "dipl": 10,
            "govt": 10,
            "scty": 5
        }
    },
    {
        "question": "It is important to maintain our national sovereignty.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -5,
            "scty": 0
        }
    },
    {
        "question": "A united world government would be beneficial to mankind.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "It is more important to retain peaceful relations than to further our strength.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Wars do not need to be justified to other countries.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "Military spending is a waste of money.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "International aid is a waste of money.",
        "effect": {
            "econ": -5,
            "dipl": -10,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "My nation is great.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Research should be conducted on an international scale.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Governments should be accountable to the international community.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 5,
            "scty": 0
        }
    },
    {
        "question": "Even when protesting an authoritarian government, violence is not acceptable.",
        "effect": {
            "econ": 0,
            "dipl": 5,
            "govt": -5,
            "scty": 0
        }
    },
    {
        "question": "My religious values should be spread as much as possible.",
        "effect": {
            "econ": 0,
            "dipl": -5,
            "govt": -10,
            "scty": -10
        }
    },
    {
        "question": "Our nation's values should be spread as much as possible.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -5,
            "scty": 0
        }
    },
    {
        "question": "It is very important to maintain law and order.",
        "effect": {
            "econ": 0,
            "dipl": -5,
            "govt": -10,
            "scty": -5
        }
    },
    {
        "question": "The general populace makes poor decisions.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "Physician-assisted suicide should be legal.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "The sacrifice of some civil liberties is necessary to protect us from acts of terrorism.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "Government surveillance is necessary in the modern world.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "The very existence of the state is a threat to our liberty.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "Regardless of political opinions, it is important to side with your country.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -10,
            "scty": -5
        }
    },
    {
        "question": "All authority should be questioned.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 5
        }
    },
    {
        "question": "A hierarchical state is best.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "It is important that the government follows the majority opinion, even if it is wrong.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "The stronger the leadership, the better.",
        "effect": {
            "econ": 0,
            "dipl": -10,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "Democracy is more than a decision-making process.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "Environmental regulations are essential.",
        "effect": {
            "econ": 5,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "A better world will come from automation, science, and technology.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Children should be educated in religious or traditional values.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -5,
            "scty": -10
        }
    },
    {
        "question": "Traditions are of no value on their own.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Religion should play a role in government.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": -10
        }
    },
    {
        "question": "Churches should be taxed the same way other institutions are taxed.",
        "effect": {
            "econ": 5,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Climate change is currently one of the greatest threats to our way of life.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "It is important that we work as a united world to combat climate change.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Society was better many years ago than it is now.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": -10
        }
    },
    {
        "question": "It is important that we maintain the traditions of our past.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": -10
        }
    },
    {
        "question": "It is important that we think in the long term, beyond our lifespans.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Reason is more important than maintaining our culture.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "Drug use should be legalized or decriminalized.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 2
        }
    },
    {
        "question": "Same-sex marriage should be legal.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 10,
            "scty": 10
        }
    },
    {
        "question": "No cultures are superior to others.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 5,
            "scty": 10
        }
    },
    {
        "question": "Sex outside marriage is immoral.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -5,
            "scty": -10
        }
    },
    {
        "question": "If we accept migrants at all, it is important that they assimilate into our culture.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -5,
            "scty": -10
        }
    },
    {
        "question": "Abortion should be prohibited in most or all cases.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": -10
        }
    },
    {
        "question": "Gun ownership should be prohibited for those without a valid reason.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": 0
        }
    },
    {
        "question": "I support single-payer, universal healthcare.",
        "effect": {
            "econ": 10,
            "dipl": 0,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "Prostitution should be illegal.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": -10,
            "scty": -10
        }
    },
    {
        "question": "Maintaining family values is essential.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": -10
        }
    },
    {
        "question": "To chase progress at all costs is dangerous.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": -10
        }
    },
    {
        "question": "Genetic modification is a force for good, even on humans.",
        "effect": {
            "econ": 0,
            "dipl": 0,
            "govt": 0,
            "scty": 10
        }
    },
    {
        "question": "We should open our borders to immigration.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 10,
            "scty": 0
        }
    },
    {
        "question": "Governments should be as concerned about foreigners as they are about their own citizens.",
        "effect": {
            "econ": 0,
            "dipl": 10,
            "govt": 0,
            "scty": 0
        }
    },
    {
        "question": "All people - regardless of factors like culture or sexuality - should be treated equally.",
        "effect": {
            "econ": 10,
            "dipl": 10,
            "govt": 10,
            "scty": 10
        }
    },
    {
        "question": "It is important that we further my group's goals above all others.",
        "effect": {
            "econ": -10,
            "dipl": -10,
            "govt": -10,
            "scty": -10
        }
    }
]

from collections.abc import Sequence


ANSWER_MULTIPLIERS = {
    "strongly agree": 1.0,
    "agree": 0.5,
    "neutral": 0.0,
    "neutral/unsure": 0.0,
    "unsure": 0.0,
    "disagree": -0.5,
    "strongly disagree": -1.0,
}

AXES = ("econ", "dipl", "govt", "scty")


def _score_8values(
    answers: Sequence[str | None],
    *,
    skip_none: bool,
) -> dict:
    """
    Internal scorer.

    skip_none=False:
        Original 8Values scoring. Missing responses contribute zero,
        while their question weights remain in the denominator.

    skip_none=True:
        Adjusted scoring. Missing responses and their weights are
        excluded, so the score is based on the exact subset answered.
    """
    if len(answers) != len(questions):
        raise ValueError(
            f"Expected {len(questions)} answers, got {len(answers)}"
        )

    raw_scores = {
        axis: 0.0
        for axis in AXES
    }

    max_scores = {
        axis: 0.0
        for axis in AXES
    }

    valid_responses = 0

    for answer, question in zip(
        answers,
        questions,
        strict=True,
    ):
        effect = question["effect"]

        if answer is None:
            if not skip_none:
                # Original scoring:
                # unanswered question contributes no raw score,
                # but remains part of the possible range.
                for axis in AXES:
                    max_scores[axis] += abs(
                        effect[axis]
                    )

            continue

        normalized_answer = answer.strip().lower()

        if normalized_answer not in ANSWER_MULTIPLIERS:
            raise ValueError(
                f"Unknown answer: {answer!r}"
            )

        multiplier = ANSWER_MULTIPLIERS[
            normalized_answer
        ]

        valid_responses += 1

        for axis in AXES:
            raw_scores[axis] += (
                multiplier
                * effect[axis]
            )

            max_scores[axis] += abs(
                effect[axis]
            )

    def calc_score(
        axis: str,
    ) -> float | None:
        max_score = max_scores[axis]

        if max_score == 0:
            return None

        return round(
            100
            * (
                max_score
                + raw_scores[axis]
            )
            / (2 * max_score),
            1,
        )

    equality = calc_score("econ")
    world = calc_score("dipl")
    liberty = calc_score("govt")
    progress = calc_score("scty")

    def opposite(
        value: float | None,
    ) -> float | None:
        if value is None:
            return None

        return round(
            100 - value,
            1,
        )

    return {
        "equality": equality,
        "markets": opposite(equality),

        "world": world,
        "nation": opposite(world),

        "liberty": liberty,
        "authority": opposite(liberty),

        "progress": progress,
        "tradition": opposite(progress),

        "valid_responses": valid_responses,
        "total_questions": len(questions),
        "valid_response_rate": (
            valid_responses
            / len(questions)
        ),
    }


def _normalize(
    score: float | None,
) -> float | None:
    """
    Convert the original 8Values [0, 100] scale to [-1, 1].

    0   -> -1
    50  ->  0
    100 -> +1
    """
    if score is None:
        return None

    return round(
        (score - 50.0) / 50.0,
        4,
    )


def score_8values(
    answers: Sequence[str | None],
) -> dict:
    """
    Return original and adjusted 8Values results.

    Original:
        Uses the full 70-question denominator, so unanswered
        questions effectively contribute a neutral/zero effect.

    Adjusted:
        Calculates the possible range from the exact subset of
        questions actually answered.

    Normalized and adjusted scores are represented on [-1, 1],
    with the 8Values midpoint (50) mapped exactly to 0.
    """

    original = _score_8values(
        answers,
        skip_none=False,
    )

    adjusted_100 = _score_8values(
        answers,
        skip_none=True,
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

    result = {}

    for value in values:
        # Original test output, exactly as 8Values reports it.
        result[value] = original[value]

        # Original output mapped to [-1, 1].
        result[
            f"{value}_normalized"
        ] = _normalize(
            original[value]
        )

        # Exact-subset adjusted result on [-1, 1].
        result[
            f"{value}_adjusted"
        ] = _normalize(
            adjusted_100[value]
        )

    result["valid_responses"] = (
        original["valid_responses"]
    )

    result["total_questions"] = (
        original["total_questions"]
    )

    result["valid_response_rate"] = (
        original["valid_response_rate"]
    )

    return result