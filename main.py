from talkie_politics.llm import ask_llm


def main():
    tests = [
        {
            "provider": "openai",
            "model": "gpt-5.6-terra",
            "expected": "OPENAI_OK",
        },
        {
            "provider": "cambridge",
            "model": "Qwen/Qwen3.8-27B-FP8",
            "expected": "QWEN_OK",
        },
        {
            "provider": "cambridge",
            "model": "zai-org/GLM-5.2-FP8",
            "expected": "GLM_OK",
        },
    ]

    for test in tests:
        provider = test["provider"]
        model = test["model"]
        expected = test["expected"]

        print(f"\nTesting {provider}/{model}...")

        try:
            response = ask_llm(
                provider=provider,
                model=model,
                prompt=f"Reply with exactly: {expected}",
                reasoning_effort="none",
            )

            print(f"Response: {response}")

        except Exception as e:
            print(f"FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()