import os
import subprocess

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Runs the python file specified",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path to the python file to run, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Optional array of string arguments to pass to the file"
                }
            },
            "required": ["file_path"],
        },
    },
}

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs =  os.path.abspath(working_directory)
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

        result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True, timeout=30)

        parts = []
        if result.returncode != 0:
            parts.append(f"Process exited with code {result.returncode}.")
        if result.stderr:
            parts.append(f"STDERR: {result.stderr}")
        if result.stdout:
            parts.append(f"STDOUT: {result.stdout}")
        if not result.stdout and not result.stderr:
            parts.append("No output produced")

        return " ".join(parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
