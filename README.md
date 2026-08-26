# talkie-politics

Political alignment evaluation of [Talkie-1930](https://talkie-lm.com/), a 13B language model trained on English-language text from around 1930.

The project tests how Talkie responds to modern political questionnaires, with a main focus on **Political Compass** and **8Values**.

## Models

Experiments use the three official Talkie checkpoints:

- `talkie-1930-13b-it`
- `talkie-1930-13b-base`
- `talkie-web-13b-base`

Each questionnaire is run **10 independent times** per model.

## Tests

The full experiment includes the 11 political questionnaires collected by Rozado (2024), totalling **401 questions**.

The main analysis uses:

- Political Compass (62 questions)
- 8Values (70 questions)

The remaining 9 tests are stored separately in `results_extended/` and are not passed through the full classification pipeline.

## Repository structure

```text
data/
    Questionnaire data and derived metadata.

results/
    Raw Talkie generations for Political Compass and 8Values.

results_classified/
    LLM-classified versions of the main results.

results_extended/
    Raw results for the other 9 political tests.

rozado_results/
    Reference results/data from Rozado used for comparison.

scripts/
    Experiment, classification, and data-processing scripts.

src/talkie_politics/
    Shared Python code, including LLM API utilities.

main.py
    Small API/model smoke test.

results_all.zip
    Archive of raw experiment outputs.
````

## Response classification

Talkie base models often produce malformed, indirect, or unrelated answers, so raw outputs are preserved first and classified separately.

Three LLM judges are used:

* `gpt-5.6-terra`
* `Qwen/Qwen3.8-27B-FP8`
* `zai-org/GLM-5.2-FP8`

Each judge maps a response to an allowed questionnaire answer or `None`.

Disagreements are flagged for human review.

## Scripts

### `scripts/run_experiments.py`

Runs Talkie on the selected political questionnaires and saves raw JSONL outputs.

Main settings:

```text
temperature = 0.7
max_tokens = 100
trials = 10
```

### `scripts/classify_responses.py`

Classifies raw Political Compass and 8Values responses using the three-judge procedure.

The script writes results incrementally and can resume at the individual-question level if interrupted.

### `scripts/classify_questions_historical.py`

Flags questions that may be anachronistic or difficult to meaningfully answer from a 1930 perspective.

### `scripts/build_classification_csv.py`

Builds a CSV for manual review of classified responses.

## Running

Install dependencies:

```bash
uv sync
```

Run experiments:

```bash
uv run python scripts/run_experiments.py
```

Classify main-test responses:

```bash
uv run python scripts/classify_responses.py
```

## References

* Levine, Duvenaud & Radford (2026), *Introducing Talkie: a 13B vintage language model from 1930*
* Rozado (2024), *The political preferences of LLMs*
* [8Values](https://github.com/8values/8values.github.io)
* [The Political Compass](https://www.politicalcompass.org/test)

## Notes

Raw Talkie generations contain offensive or objectionable text. They are preserved for reproducibility and do not represent endorsement by the authors.

This repository includes some LLM-generated code.
