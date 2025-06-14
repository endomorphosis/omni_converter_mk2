#!/usr/bin/env python3
"""
A script to find TODO comments in a directory and append them to a TODO.md file.
"""
import argparse
from datetime import datetime
import os
import re
import sys


from logger import logger


def find_todos_in_file(filepath: str) -> list[str]:
    """Find all TODO comments in a file and return them with line numbers."""
    todos = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Match TODO in comments (common patterns)
                # Handles: # TODO, // TODO, /* TODO, <!-- TODO, etc.
                todo_match = re.search(r'(?:#|//|/\*|<!--)\s*TODO\s*:?\s*(.*)(?:\*/|-->)?', line, re.IGNORECASE)
                if todo_match:
                    todo_text = todo_match.group(1).strip()
                    # Remove trailing comment closers if any
                    todo_text = re.sub(r'\s*(\*/|-->)\s*$', '', todo_text)
                    todos.append((line_num, todo_text))
    except Exception as e:
        logger.debug(f"Error reading {filepath}: {e}")
    return todos


def walk_directory(directory: str, exclude_dirs: set[str] = None) -> list[dict]:
    """Walk through directory and find all TODO comments."""
    if exclude_dirs is None:
        exclude_dirs = set('.git', '__pycache__', 'node_modules', '.venv', 'venv')
    
    all_todos = []
    
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Skip binary files and common non-source files
            if file.endswith(('.pyc', '.pyo', '.so', '.o', '.a', '.dylib', '.dll', '.exe', '.bin')):
                continue
            
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, directory)
            
            todos = find_todos_in_file(filepath)
            for line_num, todo_text in todos:
                all_todos.append({
                    'file': relative_path,
                    'line': line_num,
                    'text': todo_text
                })
    
    return all_todos


def append_to_todo_file(todos: list[dict], todo_file: str) -> bool:
    """Append found TODOs to the TODO.md file under 'New Tasks' section."""
    # Read existing content if file exists
    existing_content = ""
    if os.path.exists(todo_file):
        try:
            with open(todo_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            logger.debug(f"Error reading {todo_file}: {e}")
            existing_content = ""
    
    # Prepare new content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_content = f"\n\n## New Tasks (Generated on {timestamp})\n\n"
    
    if not todos:
        new_content += "No TODO comments found.\n"
    else:
        for todo in todos:
            new_content += f"- [ ] **{todo['file']}** (line {todo['line']}): {todo['text']}\n"
    
    # Write back to file
    try:
        with open(todo_file, 'a', encoding='utf-8') as f:
            # If file is empty or doesn't exist, don't add extra newlines at the start
            if not existing_content.strip():
                new_content = new_content.lstrip('\n')
            f.write(new_content)
        logger.debug(f"Successfully appended {len(todos)} TODO(s) to {todo_file}")
    except Exception as e:
        logger.debug(f"Error writing to {todo_file}: {e}")
        return False
    
    return True


def main() -> str:
    """
    Find TODO comments in source files and append them to a TODO.md file

    Args:
        directory (str): Directory to search for TODO comments
        output (str): Output markdown file (default: TODO.md)
        exclude (list): Additional directories to exclude (default excludes: .git, __pycache__, node_modules, .venv, venv)

    Returns:
        A string indicating success or failure
    """
    parser = argparse.ArgumentParser(
        description='Find TODO comments in source files and append them to a TODO.md file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                    # Search current directory, output to TODO.md
  %(prog)s /path/to/project     # Search specific directory
  %(prog)s . -o my_todos.md     # Output to custom file
  %(prog)s . -e build dist      # Exclude additional directories
        """
    )
    parser.add_argument(
        'directory',
        help='Directory to search for TODO comments'
    )

    parser.add_argument(
        '-o', '--output',
        default='TODO.md',
        help='Output markdown file (default: TODO.md)'
    )

    parser.add_argument(
        '-e', '--exclude',
        nargs='+',
        help='Additional directories to exclude (default excludes: .git, __pycache__, node_modules, .venv, venv)'
    )

    args = parser.parse_args()
    directory = args.directory
    output = args.output
    exclude = args.exclude

    # Validate directory
    if not os.path.isdir(directory):
        logger.debug(f"Error: '{directory}' is not a valid directory")
        return 1

    # Prepare exclude directories
    exclude_dirs: set = set('.git', '__pycache__', 'node_modules', '.venv', 'venv')
    if exclude:
        exclude_dirs.update(exclude)

    # Find TODOs
    logger.debug(f"Searching for TODO comments in '{directory}'...")
    todos = walk_directory(directory, exclude_dirs)
    
    # Report findings
    logger.debug(f"Found {len(todos)} TODO comment(s)")

    # Append to file
    return "success" if append_to_todo_file(todos, output) else "failure"

if __name__ == '__main__':
    msg = main()
    if msg == "success":
        sys.exit(0)
    else:
        sys.exit(1)
