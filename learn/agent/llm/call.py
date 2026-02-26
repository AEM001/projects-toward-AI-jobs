import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client=OpenAI(base_url=os.getenv("BASE_URL"),api_key=os.getenv("API_KEY"))

response=client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role":"user","content":"tell me in detail how to use python to call OpenAI api"}
    ]
)

print(response.choices[0].message.content)