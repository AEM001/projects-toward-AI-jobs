import os
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    return f"The weather in {city} is sunny."

# Create custom OpenAI client with your API
llm = ChatOpenAI(
    model="gpt-4.1-nano",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

# Create the agent using LangGraph (new LangChain v1 approach)
agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    prompt="You are a helpful assistant."
)

response = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf?"}]})

# Extract just the final answer
final_message = response["messages"][-1]
if hasattr(final_message, 'content'):
    print(final_message.content)
else:
    print(final_message)