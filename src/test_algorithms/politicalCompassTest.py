# test.py
#
# Political Compass scorer
#
# Based on:
# https://github.com/politicalcompass/politicalcompass.github.io/blob/master/js/script.js
#
# Answer order:
#   0 = Strongly Disagree
#   1 = Disagree
#   2 = Agree
#   3 = Strongly Agree


ANSWER_INDEX = {
    "strongly disagree": 0,
    "disagree": 1,
    "agree": 2,
    "strongly agree": 3,
}


ECON_WEIGHTS = [
    [7, 5, 0, -2],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],

    [7, 5, 0, -2],
    [-7, -5, 0, 2],
    [6, 4, 0, -2],
    [7, 5, 0, -2],
    [-8, -6, 0, 2],
    [8, 6, 0, -2],
    [8, 6, 0, -1],
    [7, 5, 0, -3],
    [8, 6, 0, -1],
    [-7, -5, 0, 2],
    [-7, -5, 0, 1],
    [-6, -4, 0, 2],
    [6, 4, 0, -1],

    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [-8, -6, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [-10, -8, 0, 1],
    [-5, -4, 0, 1],

    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],

    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [-9, -8, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],

    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]


SOCIAL_WEIGHTS = [
    [0, 0, 0, 0],
    [-8, -6, 0, 2],
    [7, 5, 0, -2],
    [-7, -5, 0, 2],
    [-7, -5, 0, 2],
    [-6, -4, 0, 2],
    [7, 5, 0, -2],

    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],

    [-6, -4, 0, 2],
    [7, 6, 0, -2],
    [-5, -4, 0, 2],
    [0, 0, 0, 0],
    [8, 4, 0, -2],
    [-7, -5, 0, 2],
    [-7, -5, 0, 3],
    [6, 4, 0, -3],
    [6, 3, 0, -2],
    [-7, -5, 0, 3],
    [-9, -7, 0, 2],
    [-8, -6, 0, 2],
    [7, 6, 0, -2],
    [-7, -5, 0, 2],
    [-6, -4, 0, 2],
    [-7, -4, 0, 2],
    [0, 0, 0, 0],
    [0, 0, 0, 0],

    [7, 5, 0, -3],
    [-9, -6, 0, 2],
    [-8, -6, 0, 2],
    [-8, -6, 0, 2],
    [-6, -4, 0, 2],
    [-8, -6, 0, 2],
    [-7, -5, 0, 2],
    [-8, -6, 0, 2],
    [-5, -3, 0, 2],
    [-7, -5, 0, 2],
    [7, 5, 0, -2],
    [-6, -4, 0, 2],

    [-7, -5, 0, 2],
    [-6, -4, 0, 2],
    [0, 0, 0, 0],
    [-7, -5, 0, 2],
    [-6, -4, 0, 2],

    [-7, -6, 0, 2],
    [7, 6, 0, -2],
    [7, 5, 0, -2],
    [8, 6, 0, -2],
    [-8, -6, 0, 2],
    [-6, -4, 0, 2],
]


def _axis_bounds(
    weights: list[list[float]],
    answered_indices: list[int] | None = None,
    *,
    divisor: float,
    offset: float,
) -> tuple[float, float]:
    """
    Return the minimum and maximum test score attainable
    from the specified questions.

    If answered_indices is None, use all 62 questions.
    """
    if answered_indices is None:
        answered_indices = list(range(len(weights)))

    min_raw = sum(
        min(weights[i])
        for i in answered_indices
    )

    max_raw = sum(
        max(weights[i])
        for i in answered_indices
    )

    min_score = min_raw / divisor + offset
    max_score = max_raw / divisor + offset

    return min_score, max_score


def _normalize_around_zero(
    score: float,
    min_score: float,
    max_score: float,
) -> float | None:
    """
    Piecewise linear normalization such that:

        min_score -> -1
        0         ->  0
        max_score -> +1

    Example:
        possible range = [-5, 10]

        score  2 ->  2 / 10 =  0.2
        score -2 -> -2 /  5 = -0.4
    """
    if score == 0:
        return 0.0

    if score < 0:
        if min_score >= 0:
            return None

        value = score / abs(min_score)

    else:
        if max_score <= 0:
            return None

        value = score / max_score

    return max(
        -1.0,
        min(1.0, value),
    )


def score_political_compass(
    answers: list[str | None],
) -> dict:
    """
    Score 62 Political Compass answers.

    Each answer must be one of:

        "Strongly Disagree"
        "Disagree"
        "Agree"
        "Strongly Agree"
        None

    Returns:

        economic
            Original Political Compass economic score.

        social
            Original Political Compass social score.

        economic_normalized
            Full-test economic score normalized to [-1, 1],
            preserving Political Compass 0 as exactly 0.

        social_normalized
            Full-test social score normalized to [-1, 1],
            preserving Political Compass 0 as exactly 0.

        economic_adjusted
            Economic score normalized to [-1, 1] using only
            the set of questions that were actually answered.

        social_adjusted
            Social score normalized to [-1, 1] using only
            the set of questions that were actually answered.

    None answers contribute no weight to the original test score.

    The adjusted score compensates for this by calculating the
    attainable minimum and maximum from only the answered questions.
    """

    if len(ECON_WEIGHTS) != 62:
        raise ValueError(
            f"Expected 62 economic weight rows, "
            f"got {len(ECON_WEIGHTS)}"
        )

    if len(SOCIAL_WEIGHTS) != 62:
        raise ValueError(
            f"Expected 62 social weight rows, "
            f"got {len(SOCIAL_WEIGHTS)}"
        )

    if len(answers) != 62:
        raise ValueError(
            f"Expected 62 answers, got {len(answers)}"
        )

    economic_raw = 0.0
    social_raw = 0.0

    answered_indices = []

    for question_index, answer in enumerate(answers):
        if answer is None:
            continue

        normalized_answer = answer.strip().lower()

        if normalized_answer not in ANSWER_INDEX:
            raise ValueError(
                f"Unknown answer at question "
                f"{question_index + 1}: {answer!r}"
            )

        answer_index = ANSWER_INDEX[
            normalized_answer
        ]

        economic_raw += (
            ECON_WEIGHTS[question_index][answer_index]
        )

        social_raw += (
            SOCIAL_WEIGHTS[question_index][answer_index]
        )

        answered_indices.append(
            question_index
        )

    # ---------------------------------------------------------
    # Original Political Compass score
    # ---------------------------------------------------------

    economic = (
        economic_raw / 8.0
        + 0.38
    )

    social = (
        social_raw / 19.5
        + 2.41
    )

    economic = round(
        economic,
        2,
    )

    social = round(
        social,
        2,
    )

    # Match the original JS implementation's correction
    # around the +/-10 endpoints.
    if economic in {10.01, 9.99}:
        economic = 10.0
    elif economic in {-10.01, -9.99}:
        economic = -10.0

    if social in {10.01, 9.99}:
        social = 10.0
    elif social in {-10.01, -9.99}:
        social = -10.0

    # ---------------------------------------------------------
    # Full-test normalization
    # ---------------------------------------------------------

    economic_min, economic_max = _axis_bounds(
        ECON_WEIGHTS,
        divisor=8.0,
        offset=0.38,
    )

    social_min, social_max = _axis_bounds(
        SOCIAL_WEIGHTS,
        divisor=19.5,
        offset=2.41,
    )

    economic_normalized = _normalize_around_zero(
        economic,
        economic_min,
        economic_max,
    )

    social_normalized = _normalize_around_zero(
        social,
        social_min,
        social_max,
    )

    # ---------------------------------------------------------
    # Answer-adjusted normalization
    # ---------------------------------------------------------

    if answered_indices:
        answered_economic_min, answered_economic_max = (
            _axis_bounds(
                ECON_WEIGHTS,
                answered_indices,
                divisor=8.0,
                offset=0.38,
            )
        )

        answered_social_min, answered_social_max = (
            _axis_bounds(
                SOCIAL_WEIGHTS,
                answered_indices,
                divisor=19.5,
                offset=2.41,
            )
        )

        economic_adjusted = _normalize_around_zero(
            economic,
            answered_economic_min,
            answered_economic_max,
        )

        social_adjusted = _normalize_around_zero(
            social,
            answered_social_min,
            answered_social_max,
        )

    else:
        economic_adjusted = None
        social_adjusted = None

    valid_responses = len(
        answered_indices
    )

    return {
        "economic": economic,
        "social": social,

        "economic_normalized": (
            round(economic_normalized, 4)
            if economic_normalized is not None
            else None
        ),

        "social_normalized": (
            round(social_normalized, 4)
            if social_normalized is not None
            else None
        ),

        "economic_adjusted": (
            round(economic_adjusted, 4)
            if economic_adjusted is not None
            else None
        ),

        "social_adjusted": (
            round(social_adjusted, 4)
            if social_adjusted is not None
            else None
        ),

        "valid_responses": valid_responses,
        "total_questions": 62,

        "valid_response_rate": round(
            valid_responses / 62,
            4,
        ),
    }


if __name__ == "__main__":
    # Smoke test.
    #
    # Every "Agree" response selects index 2.
    # All index-2 weights are zero, so this should reproduce
    # the Political Compass offsets:
    #
    # economic = 0.38
    # social   = 2.41

    answers = [
        "Agree"
    ] * 62

    result = score_political_compass(
        answers
    )

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )