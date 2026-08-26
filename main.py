from talkie_politics.llm import ask_llm


def main():
    print("Testing OpenAI...")
    print(
        ask_llm(
            provider="openai",
            model="gpt-5.6-terra",
            prompt="Reply with exactly: OPENAI_OK",
        )
    )

    print("\nTesting Cambridge Qwen...")
    print(
        ask_llm(
            provider="cambridge",
            model="Qwen/Qwen3.8-27B-FP8",
            prompt="Reply with exactly: QWEN_OK",
        )
    )

    print("\nTesting Cambridge Gemma...")
    print(
        ask_llm(
            provider="cambridge",
            model="google/gemma-4-31B-it",
            prompt="Reply with exactly: GEMMA_OK",
        )
    )


if __name__ == "__main__":
    main()