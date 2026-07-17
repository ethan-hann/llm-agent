import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

def main():
    if not api_key:
        raise RuntimeError("API Key was not found in environment.")
    
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key,)
    response = client.chat.completions.create(model="openrouter/free", messages=[
        {
            "role": "user",
            "content": "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum.",
        }
    ])
    
    if not response.usage:
        raise RuntimeError("Response from AI was empty!")
    
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {completion_tokens}")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
