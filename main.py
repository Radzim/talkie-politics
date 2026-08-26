from talkie_politics.inference import ask_talkie

print("starting")

response = ask_talkie(
    "1930_it",
    "What is your opinion of democracy?",
    max_tokens=100,
)

print("\nFINAL RESPONSE:")
print(response)