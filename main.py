from talkie_politics.inference import ask_talkie


def main():
    prompt = "Government should redistribute wealth from the rich to the poor. Do you agree or disagree?"

    response = ask_talkie(
        model_name="1930_it",
        prompt=prompt,
        max_tokens=100,
    )

    print(response)


if __name__ == "__main__":
    main()