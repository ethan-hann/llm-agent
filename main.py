import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

parser = argparse.ArgumentParser(description="BootAI - A simple command line AI chatbot")
parser.add_argument("user_prompt", type=str, help="The prompt to send to the LLM")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

def generate_content(client, messages):
    return client.chat.completions.create(model="openrouter/free", messages=messages)

def print_response(response, is_verbose):
    if not response.usage:
        raise RuntimeError("Response from AI was empty!")
    
    if is_verbose:
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        global args
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {completion_tokens}")
    
    print(response.choices[0].message.content)
    
def main():
    if not api_key:
        raise RuntimeError("API Key was not found in environment.")
    global args
    
    messages = [
        {"role": "user", "content": args.user_prompt},
    ]
    
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key,)
    response = generate_content(client, messages)
    print_response(response, args.verbose)
    
if __name__ == "__main__":
    main()
