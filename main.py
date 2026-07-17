import os
import argparse
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from functions.call_function import get_schemas

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

parser = argparse.ArgumentParser(description="BootAI - A simple command line AI chatbot")
parser.add_argument("user_prompt", type=str, help="The prompt to send to the LLM")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

available_functions = get_schemas()

def generate_content(client, messages):
    return client.chat.completions.create(model="openrouter/free", messages=messages, tools=available_functions)
    
def main():
    if not api_key:
        raise RuntimeError("API Key was not found in environment.")
    global args
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key,)
    response = generate_content(client, messages)
    if not response.usage:
        raise RuntimeError("Response from AI was empty!")
    
    if args.verbose:
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {completion_tokens}")
    
    message = response.choices[0].message
    tool_calls = message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments or "{}") # type: ignore
            print(f"Calling function: {tool_call.function.name}({function_args})") # type: ignore
    else:
        print(message.content)
    
if __name__ == "__main__":
    main()
