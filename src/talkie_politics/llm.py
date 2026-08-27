import os
from openai import OpenAI
import random
import time

REQUEST_TIMEOUT_SECONDS = 180

_uis_client = OpenAI(
    api_key=os.environ["UIS_API_KEY"],
    base_url=os.environ.get(
        "UIS_BASE_URL",
        "https://llm.hpc.cam.ac.uk/v1",
    ),
    timeout=REQUEST_TIMEOUT_SECONDS,
    max_retries=0,
)

_openai_client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=REQUEST_TIMEOUT_SECONDS,
    max_retries=0,
)


def ask_llm(
    model,
    prompt,
    *,
    provider="openai",
    reasoning_effort="low",
) -> str:
    time.sleep(random.uniform(0, 5))
    if provider == "openai":
        return ask_openai(
            model,
            prompt,
            reasoning_effort=reasoning_effort,
        )

    if provider == "cambridge":
        return ask_cambridge(
            model,
            prompt,
        )

    raise ValueError(f"Unknown provider: {provider}")


def ask_openai(
    model,
    prompt,
    reasoning_effort="low",
) -> str:
    response = _openai_client.responses.create(
        model=model,
        input=prompt,
        reasoning={
            "effort": reasoning_effort,
        },
    )

    text = response.output_text

    if not text:
        raise ValueError(
            f"{model} returned no output text"
        )

    return text


def ask_cambridge(
    model,
    prompt,
) -> str:
    response = _uis_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            f"{model} returned no content"
        )

    return content