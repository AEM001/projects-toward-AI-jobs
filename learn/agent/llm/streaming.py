import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

def stream_chat_completion():
    """Stream using Chat Completions API"""
    print("=== Chat Completions Streaming ===")
    
    stream = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": "Write a short poem about coding"}],
        stream=True
    )
    
    collected_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            collected_text += content
            print(content, end="", flush=True)
    
    print(f"\n\nCollected text: {collected_text}")
    return collected_text

def stream_responses_api():
    """Stream using Responses API"""
    print("\n=== Responses API Streaming ===")
    
    stream = client.responses.create(
        model="gpt-4.1-nano",
        input=[{"role": "user", "content": "Write a short poem about coding"}],
        stream=True
    )
    
    collected_text = ""
    for event in stream:
        if event.type == "response.output_text_delta":
            collected_text += event.delta
            print(event.delta, end="", flush=True)
    
    print(f"\n\nCollected text: {collected_text}")
    return collected_text

def stream_with_context_manager():
    """Stream using context manager (recommended)"""
    print("\n=== Context Manager Streaming ===")
    
    with client.chat.completions.stream(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": "Explain streaming in 3 sentences"}]
    ) as stream:
        collected_text = ""
        for event in stream:
            if event.type == "content.delta":
                chunk = event.delta
                collected_text += chunk
                print(chunk, end="", flush=True)
        
        # Get final usage info
        final_usage = stream.get_final_completion().usage
    
    print(f"\n\nCollected text: {collected_text}")
    print(f"Tokens used: {final_usage.total_tokens}")
    return collected_text

if __name__ == "__main__":
    # Try different streaming methods
    stream_chat_completion()
    stream_responses_api() 
    stream_with_context_manager()