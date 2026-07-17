import os
import argparse
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from functions.call_function import get_schemas, call_function

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

parser = argparse.ArgumentParser(description="BootAI - A simple command line AI chatbot")
parser.add_argument("user_prompt", type=str, help="The prompt to send to the LLM")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

available_functions = get_schemas()

def generate_content(client, messages):
    return client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )

def valid_tool_calls(message):
    """A response is usable if it either has no tool calls (plain text answer)
    or every tool call names a function we actually expose. The free router
    sometimes lands on a model that emits malformed names like 'get_files_info>'."""
    known = {schema["function"]["name"] for schema in available_functions}
    if not message.tool_calls:
        return True
    return all(tc.function.name in known for tc in message.tool_calls)
    
def main():
    if not api_key:
        raise RuntimeError("API Key was not found in environment.")
    global args
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    max_attempts = 5
    response = None
    message = None
    for attempt in range(1, max_attempts + 1):
        response = generate_content(client, messages)
        if not response.usage:
            raise RuntimeError("Response from AI was empty!")
        message = response.choices[0].message
        if valid_tool_calls(message):
            break
        if args.verbose:
            bad = [tc.function.name for tc in message.tool_calls] # type: ignore
            print(f"Attempt {attempt}: free router returned unknown function(s) {bad}, re-rolling...")
    else:
        raise RuntimeError(
            f"Free router returned malformed tool calls on all {max_attempts} attempts. "
            "Re-run the command (the router picks a different model each time)."
        )

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    tool_calls = message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            result_message = call_function(tool_call, args.verbose)
            if len(result_message["content"]) == 0:
                raise RuntimeError("Response from tool call was empty")
            if args.verbose:
                print(f"-> {result_message['content']}")
    else:
        print(message.content)
    
if __name__ == "__main__":
    main()
