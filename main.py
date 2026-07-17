import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

def generate_content(client, messages):
    return client.chat.completions.create(model="openrouter/free", messages=messages)

def print_response(response):
    if not response.usage:
        raise RuntimeError("Response from AI was empty!")
    
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {completion_tokens}")
    print(response.choices[0].message.content)

def main():
    if not api_key:
        raise RuntimeError("API Key was not found in environment.")
    parser = argparse.ArgumentParser(description="BootAI - A simple command line AI chatbot")
    parser.add_argument("user_prompt", type=str, help="The prompt to send to the LLM.")
    args = parser.parse_args()
    
    messages = [
        {"role": "user", "content": args.user_prompt},
    ]
    
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key,)
    response = generate_content(client, messages)
    print_response(response)
    
if __name__ == "__main__":
    main()
