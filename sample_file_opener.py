#!/usr/bin/env python
"""
Sample File Opener

This script demonstrates how to open a file in the main directory of the Omni Converter project.
It provides examples for both absolute and relative paths, as well as handling different file types.
"""

import os
import sys
import json
from pathlib import Path

def get_project_root() -> Path:
    """Get the absolute path to the project root directory."""
    # This gives us the directory where this script is located
    return Path(__file__).parent.absolute()

def open_file_absolute_path(filename: str) -> str:
    """
    Open a file using its absolute path.
    
    Args:
        filename: The name of the file in the project root
        
    Returns:
        The content of the file as a string
    """
    project_root = get_project_root()
    file_path = project_root / filename
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Successfully opened {filename} using absolute path")
        return content
    except FileNotFoundError:
        print(f"Error: File {filename} not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error opening {filename}: {e}")
        return ""

def open_file_relative_path(filename: str) -> str:
    """
    Open a file using its relative path from the current working directory.
    
    Args:
        filename: The name of the file relative to the current working directory
        
    Returns:
        The content of the file as a string
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Successfully opened {filename} using relative path")
        return content
    except FileNotFoundError:
        print(f"Error: File {filename} not found in the current working directory")
        return ""
    except Exception as e:
        print(f"Error opening {filename}: {e}")
        return ""

def open_config_file() -> dict:
    """
    Open and parse the configs.yaml file as an example of opening a specific file.
    
    Returns:
        The parsed content as a dictionary
    """
    import yaml
    project_root = get_project_root()
    config_path = project_root / "configs.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)
        print(f"Successfully loaded configs.yaml")
        return content
    except Exception as e:
        print(f"Error loading configs.yaml: {e}")
        return {}

def open_binary_file(filename: str) -> bytes:
    """
    Open a binary file from the project.
    
    Args:
        filename: The name of the binary file
        
    Returns:
        The binary content of the file
    """
    project_root = get_project_root()
    file_path = project_root / filename
    
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        print(f"Successfully opened binary file {filename}")
        return content
    except Exception as e:
        print(f"Error opening binary file {filename}: {e}")
        return b''

def main():
    # Example 1: Open README.md using absolute path
    readme_content = open_file_absolute_path("README.md")
    if readme_content:
        print(f"README first 100 chars: {readme_content[:100]}...\n")
    
    # Example 2: Open configs.yaml and parse it
    config = open_config_file()
    if config:
        print(f"Config keys: {list(config.keys())}\n")
    
    # Example 3: Try to open a file using relative path
    # Note: This depends on your current working directory when running the script
    try:
        relative_content = open_file_relative_path("requirements.txt")
        if relative_content:
            print(f"Requirements first 100 chars: {relative_content[:100]}...\n")
    except Exception:
        print("Could not open requirements.txt with relative path\n")
    
    # Example 4: Open a test file from the test_files directory
    try:
        test_file_path = "test_files/test.json"
        json_content = open_file_absolute_path(test_file_path)
        if json_content:
            parsed_json = json.loads(json_content)
            print(f"JSON content: {parsed_json}\n")
    except Exception as e:
        print(f"Error with JSON test file: {e}\n")

if __name__ == "__main__":
    main()
