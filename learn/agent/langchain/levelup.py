from dataclasses import dataclass
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

checkpointer = InMemorySaver()

load_dotenv()

SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""

@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a specific city."""
    return f"It's always sunny in {city}!"

@dataclass
class Context:
    user_id: str

@tool
def get_user_location(user_id: str) -> str:
    """Get user location based on user ID."""
    return "LA" if user_id == "1" else "SF"

llm = ChatOpenAI(
    model="gpt-4.1-nano",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
    max_tokens=100,
    temperature=0.7,
)

agent = create_agent(
    model=llm,
    tools=[get_weather_for_location, get_user_location],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}

# First conversation
response = agent.invoke(
    {"messages": [{"role": "user", "content": "I'm in SF. What is the weather here?"}]},
    config=config
)

# Extract final answer
final_message = response["messages"][-1]
print(f"First response: {final_message.content}")

# Continue the conversation (same thread_id maintains memory)
response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "thank you!"}]},
    config=config
)

final_message2 = response2["messages"][-1]
print(f"Second response: {final_message2.content}")

print("\n--- How Memory Works ---")
print("1. checkpointer = InMemorySaver() stores conversation history")
print("2. thread_id = '1' identifies this specific conversation")
print("3. Each invoke() with same thread_id loads previous messages")
print("4. Context maintains state across tool calls within a single invoke")
