import json
from collections.abc import Callable
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from config import WORKING_DIRECTORY

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": (
            "Lists the contents of a directory within the permitted working directory. "
            "For each entry it returns the name, the size in bytes, and whether the entry "
            "is itself a directory (as opposed to a regular file). Use this to explore or "
            "map out the project's structure before acting on it. For example, to "
            "discover which files exist before reading, editing, or running one. The target "
            "directory must resolve to a location inside the working directory; any path that "
            "escapes it is rejected. Omitting the 'directory' argument lists the top level of "
            "the working directory itself."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": (
                        "Path of the directory to list, relative to the working directory. "
                        "Pass '.' or omit this argument to list the working directory itself. "
                        "Must resolve to a location inside the working directory."
                    ),
                },
            },
        },
    },
}
schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": (
            "Reads and returns the text contents of a single file within the permitted "
            "working directory. The output is truncated at 10,000 characters; when "
            "truncation occurs a notice is appended so you know the file continues beyond "
            "what was returned. Use this to inspect source code, configuration, or data "
            "before modifying or executing it. The target file must resolve to a location "
            "inside the working directory; any path that escapes it is rejected."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path of the file to read, relative to the working directory. "
                        "Must resolve to a location inside the working directory."
                    ),
                },
            },
            "required": ["file_path"],
        },
    },
}
schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": (
            "Writes text content to a file within the permitted working directory, creating "
            "the file if it does not already exist and overwriting it in full if it does. Any "
            "missing parent directories along the path are created automatically. This is a "
            "full-content write, not an append or patch, so provide the complete intended "
            "contents of the file. Use this to create new source files or replace the entire "
            "contents of an existing one. The target path must resolve to a location inside "
            "the working directory; any path that escapes it is rejected."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path of the file to write or overwrite, relative to the working "
                        "directory. The file and any missing parent directories are created "
                        "if they do not exist. Must resolve to a location inside the working "
                        "directory."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": (
                        "The full text content to write to the file. This replaces the "
                        "file's existing contents entirely rather than appending to them."
                    ),
                },
            },
            "required": ["file_path", "content"],
        },
    },
}
schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": (
            "Executes a Python (.py) file located within the permitted working directory "
            "using the Python interpreter, optionally forwarding command-line arguments to "
            "it. Returns the script's captured STDOUT and STDERR, along with a report of the "
            "process exit code when the script fails or raises. Execution is subject to a "
            "timeout to prevent runaway processes. Use this to run scripts or tests and "
            "observe their output. The target file must resolve to a location inside the "
            "working directory and must be a Python file; any path that escapes the working "
            "directory is rejected."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path of the Python script to execute, relative to the working "
                        "directory. Must resolve to a .py file inside the working directory."
                    ),
                },
                "args": {
                    "type": "array",
                    "description": (
                        "Optional list of command-line argument strings to pass to the "
                        "script, exposed to it via sys.argv exactly as if it were invoked "
                        "from a terminal. Omit or pass an empty list when the script takes "
                        "no arguments."
                    ),
                    "items": {
                        "type": "string",
                    },
                },
            },
            "required": ["file_path"],
        },
    },
}

def get_schemas() -> list[dict[str, dict[str, object]]]:
    """Return a list of all function schemas."""
    return [
        schema_get_file_content,
        schema_get_files_info,
        schema_run_python_file,
        schema_write_file,
    ]

def call_function(tool_call, verbose: bool = False) -> dict:
    """Call the specified function with the given arguments and return the result as a dictionary."""
    function_map: dict[str, Callable[..., str]] = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file
    }
    
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    
    if function_name not in function_map:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }
    
    function_args["working_directory"] = WORKING_DIRECTORY # Set working directory (defined in config.py)
    result = function_map[function_name](**function_args) # Call the function and store result (just a string)
    
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    }