import os

from openai import OpenAI


_openai_client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

_uis_client = OpenAI(
    api_key=os.environ["UIS_API_KEY"],
    base_url=os.environ.get(
        "UIS_BASE_URL",
        "https://llm.hpc.cam.ac.uk/v1",
    ),
)


def ask_llm(
    model: str,
    prompt: str,
    *,
    provider: str = "openai",
    reasoning_effort: str = "low",
) -> str:
    if provider == "openai":
        return ask_openai(
            model=model,
            prompt=prompt,
            reasoning_effort=reasoning_effort,
        )

    if provider == "cambridge":
        return ask_cambridge(
            model=model,
            prompt=prompt,
        )

    raise ValueError(f"Unknown provider: {provider!r}")


def ask_openai(
    model: str,
    prompt: str,
    *,
    reasoning_effort: str = "low",
) -> str:
    response = _openai_client.responses.create(
        model=model,
        input=prompt,
        reasoning={
            "effort": reasoning_effort,
        },
    )

    return response.output_text


def ask_cambridge(
    model: str,
    prompt: str,
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

    if content is None:
        raise ValueError(
            f"Cambridge model {model!r} returned no text."
        )

    return content