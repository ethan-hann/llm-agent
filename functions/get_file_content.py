import os
from config import MAX_CHARS

def get_file_content(working_directory: str, file_path: str) -> str:
    """Return the content of the specified file within the working directory, truncated to MAX_CHARS."""
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(working_dir_abs, file_path))        
        valid_target_dir = os.path.commonpath([working_dir_abs, target_file_path]) == working_dir_abs
        
        if not valid_target_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        with open(target_file_path, "r") as f:
            file_content = f.read(MAX_CHARS)
            if f.read(1):
                file_content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return file_content
        
    except Exception as e:
        return f'Error: {e}'