import os

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        
        file_records: list[dict[str, object]] = []
        file_list = os.listdir(target_dir)
        for file in file_list:
            abs_path = os.path.normpath(os.path.join(target_dir, file))
            file_records.append({
                "name": os.path.basename(abs_path),
                "size": os.path.getsize(abs_path),
                "is_dir": os.path.isdir(abs_path)
            })
        
        # Build return string
        lines = [f"Result for {directory if directory != "." else "current directory"}:"]
        for record in file_records:
            lines.append(
                f"  - {record["name"]}: file_size={record["size"]} bytes, is_dir={record["is_dir"]}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f'Error: {str(e)}'