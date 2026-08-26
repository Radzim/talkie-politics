from typing import Literal

ModelName = Literal[
    "1930_it",
    "1930_base",
    "web_base",
]

MODEL_IDS = {
    "1930_it": "talkie-1930-13b-it",
    "1930_base": "talkie-1930-13b-base",
    "web_base": "talkie-web-13b-base",
}

_model = None
_loaded_model_name: ModelName | None = None


def load_model(model_name: ModelName):
    global _model, _loaded_model_name

    if _model is not None and _loaded_model_name == model_name:
        return _model

    print(f"Loading {model_name}...", flush=True)

    from talkie import Talkie

    print("Imported Talkie", flush=True)

    _model = Talkie(MODEL_IDS[model_name])
    _loaded_model_name = model_name

    print("Model loaded", flush=True)

    return _model


def ask_talkie(
    model_name: ModelName,
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
    top_p: float | None = None,
    top_k: int | None = None,
    stream_output: bool = True,
) -> str:
    model = load_model(model_name)

    tokens: list[str] = []

    print("Generating...", flush=True)

    for i, token in enumerate(
        model.stream(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
        ),
        start=1,
    ):
        tokens.append(token)

        if stream_output:
            print(token, end="", flush=True)
        else:
            print(
                f"\rGenerated tokens: {i}/{max_tokens}",
                end="",
                flush=True,
            )

    text = "".join(tokens)

    if stream_output:
        print()
    else:
        print()

    print(f"Generated {len(tokens)} tokens", flush=True)

    return text