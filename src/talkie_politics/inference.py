from typing import Literal

ModelName = Literal["1930_it", "1930_base", "web_base"]

MODEL_IDS = {
    "1930_it": "talkie-1930-13b-it",
    "1930_base": "talkie-1930-13b-base",
    "web_base": "talkie-web-13b-base",
}

_model = None
_loaded_model_name = None


def load_model(model_name: ModelName):
    global _model, _loaded_model_name

    if _model is not None and _loaded_model_name == model_name:
        return _model

    from talkie import Talkie

    _model = Talkie(MODEL_IDS[model_name])
    _loaded_model_name = model_name
    return _model


def ask_talkie(
    model_name: ModelName,
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> str:
    model = load_model(model_name)

    result = model.generate(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return result.text