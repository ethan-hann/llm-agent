import os
import subprocess

def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        
        valid_target_dir = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]
        if args:
            command.extend(args)
            
        sub_process = subprocess.run(
            args=command,
            capture_output=True,
            text=True,
            timeout=30
        )
        output_string = ""
        if sub_process.returncode != 0:
            output_string += f"Process exited with code {sub_process.returncode}\n"
        if len(sub_process.stdout) == 0 and len(sub_process.stderr) == 0:
            output_string += "No output produced\n"
        else:
            output_string += f"STDOUT: {sub_process.stdout}\n"
            output_string += f"STDERR: {sub_process.stderr}\n"
        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"