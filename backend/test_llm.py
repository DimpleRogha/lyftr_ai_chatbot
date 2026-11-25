from llm import get_ai_response

messages = [
    {
        "role": "user",
        "content": "Introduce yourself in one sentence."
    }
]

try:
    response = get_ai_response(messages)

    print("\nAI RESPONSE:")
    print(response.choices[0].message.content)

    print("\nMODEL:")
    print(response.model)

    print("\nTOKEN USAGE:")
    print(response.usage)

except Exception as e:
    print("AI request failed:", str(e))