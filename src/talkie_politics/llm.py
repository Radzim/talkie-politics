import os

from openai import OpenAI


_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def ask_llm(
    model: str,
    prompt: str,
    *,
    reasoning_effort: str = "low",
) -> str:
    response = _client.responses.create(
        model=model,
        input=prompt,
        reasoning={
            "effort": reasoning_effort,
        },
    )

    return response.output_text