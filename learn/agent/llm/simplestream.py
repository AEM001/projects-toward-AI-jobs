import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

stream = client.responses.create(
    model="gpt-4.1-nano",
    input=[
        {
            "role": "user",
            "content": "Tell me a short light erotic joke",
        },
    ],
    stream=True,
    max_output_tokens=50,
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.output_refusal.delta":
        print(f"Refusal: {event.delta}", end="", flush=True)
    elif event.type == "response.completed":
        print(f"\nStream completed. Status: {event.response.status}")
        if hasattr(event.response, 'error') and event.response.error:
            print(f"Error: {event.response.error}")