import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI
from functions.call_function import call_function
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from config import MAX_ITERATIONS

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    verbose = args.verbose

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(MAX_ITERATIONS):
        response = call_llm(messages)
        usage = response.usage
        if usage == None:
            raise RuntimeError("API Error")

        if args.verbose:
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens

            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Response tokens: {completion_tokens}")

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, verbose)
                messages.append(result_message)

                if not result_message.get("content"):
                     raise RuntimeError(f"Empty result from {tool_call.function.name}")

                if verbose:
                    print(f"-> {result_message['content']}")
        else:
            content = message.content
            print(content)
            return

    print("Max iterations reached")
    exit(1)


def call_llm(messages):
    available_functions = [
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]

    return client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )



if __name__ == "__main__":
    main()
