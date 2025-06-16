import os

def can_handle(
        supported_formats: frozenset[str], 
        format_extensions: frozenset[str], 
        file_path: str, 
        format_name: str
    ) -> bool:
    if format_name:
        return format_name in supported_formats

    # If no format provided, check file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    for format_type, extensions in format_extensions.items():
        if ext in extensions and format_type in supported_formats:
            return True

    return False
