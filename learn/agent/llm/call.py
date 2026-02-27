import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

def get_weather(location):
    """Simple mock weather function"""
    weather_data = {
        "new york": "72°F, sunny",
        "london": "59°F, cloudy", 
        "tokyo": "68°F, partly cloudy",
        "paris": "64°F, rainy"
    }
    return weather_data.get(location.lower(), f"Weather data not available for {location}")

# Define the tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# First request - user asks about weather
response = client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "user", "content": "What's the weather like in London?"}
    ],
    tools=tools
)

print("=== First Response ===")
print(f"Content: {response.choices[0].message.content}")
print(f"Tool calls: {response.choices[0].message.tool_calls}")

# If model wants to call function, execute it
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    
    # Execute the function
    args = json.loads(tool_call.function.arguments)
    weather_result = get_weather(args["location"])
    
    print(f"\n=== Function Execution ===")
    print(f"Called: {tool_call.function.name}({args})")
    print(f"Result: {weather_result}")
    
    # Second request - send function result back
    final_response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content": "What's the weather like in London?"},
            response.choices[0].message,  # Assistant's tool call message
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": weather_result
            }
        ]
    )
    
    print(f"\n=== Final Response ===")
    print(f"Answer: {final_response.choices[0].message.content}")

# Save to files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

with open(f"weather_{timestamp}.txt", "w") as f:
    f.write(f"User: What's the weather like in London?\n")
    f.write(f"Tool call: {response.choices[0].message.tool_calls[0].function.name}\n")
    f.write(f"Function result: {weather_result}\n")
    f.write(f"Final answer: {final_response.choices[0].message.content}\n")

with open(f"weather_{timestamp}.json", "w") as f:
    json.dump({
        "initial_response": json.loads(response.model_dump_json()),
        "final_response": json.loads(final_response.model_dump_json())
    }, f, indent=2)

print(f"\nResults saved to weather_{timestamp}.txt and weather_{timestamp}.json")