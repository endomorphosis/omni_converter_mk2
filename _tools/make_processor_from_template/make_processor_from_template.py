#!/usr/bin/env python3
"""
JSON Schema to Class Generator

This module converts JSON function schemas into Python classes using Jinja2 templates.
The generated classes follow the pattern established in _bs4_processor.py with proper
Google-style docstrings and type hints.
"""
import argparse
import textwrap
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment
except ImportError:
    print("Error: jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)


def load_json_schema(file_path: str) -> Dict[str, Any]:
    """
    Load and parse JSON schema from file.
    
    Args:
        file_path: Path to the JSON schema file.
        
    Returns:
        Parsed JSON schema as dictionary.
        
    Raises:
        FileNotFoundError: If schema file doesn't exist.
        json.JSONDecodeError: If JSON is malformed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        return schema
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {e.msg}", e.doc, e.pos)


def validate_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate that the JSON schema contains required fields.
    
    Args:
        schema: The parsed JSON schema dictionary.
        
    Returns:
        True if schema is valid, False otherwise.
    """
    # Check required top-level fields
    required_fields = ["module_name", "functions"]
    for field in required_fields:
        if field not in schema:
            print(f"Error: Missing required field '{field}' in schema")
            return False
    
    # Validate functions array
    if not isinstance(schema["functions"], list):
        print("Error: 'functions' must be an array")
        return False
    
    if len(schema["functions"]) == 0:
        print("Error: At least one function must be defined")
        return False
    
    # Validate each function
    for i, function in enumerate(schema["functions"]):
        if not validate_function_schema(function, i):
            return False
    
    return True


def validate_function_schema(function: Dict[str, Any], index: int) -> bool:
    """
    Validate a single function schema.
    
    Args:
        function: The function schema dictionary.
        index: The index of the function for error reporting.
        
    Returns:
        True if function schema is valid, False otherwise.
    """
    required_fields = ["name", "docstring", "parameters", "returns"]
    for field in required_fields:
        if field not in function:
            print(f"Error: Function {index} missing required field '{field}'")
            return False
    
    # Validate parameters
    if not isinstance(function["parameters"], list):
        print(f"Error: Function {index} 'parameters' must be an array")
        return False
    
    for j, param in enumerate(function["parameters"]):
        param_required = ["name", "type", "description"]
        for field in param_required:
            if field not in param:
                print(f"Error: Function {index} parameter {j} missing field '{field}'")
                return False
    
    # Validate returns
    returns = function["returns"]
    if not isinstance(returns, dict):
        print(f"Error: Function {index} 'returns' must be an object")
        return False
    
    returns_required = ["type", "description"]
    for field in returns_required:
        if field not in returns:
            print(f"Error: Function {index} returns missing field '{field}'")
            return False
    
    return True


def generate_class_code(schema: Dict[str, Any], template_path: str) -> str:
    """
    Generate Python class code from schema using Jinja2 template.
    
    Args:
        schema: The JSON schema dictionary.
        template_path: The path to a Jinja2 template.
        
    Returns:
        Generated Python code as string.
        
    Raises:
        jinja2.TemplateError: If template rendering fails.
    """
    env = Environment()
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        raise IOError(f"Error reading template file {template_path}: {e}") from e
    jinja_template = env.from_string(template_content)

    # Prepare template context
    context = {
        'module_docstring': schema.get('module_docstring', f'{schema["module_name"]} processing utilities.'),
        'imports': schema.get('imports', []),
        'dependencies_import': schema.get('dependencies_import'),
        'dependencies_class': schema.get('dependencies_class'),
        'functions': schema['functions']
    }

    # Add default body if not provided
    for function in context['functions']:
        if 'body' not in function or not function['body']:
            function['body'] = 'pass  # Implementation needed'

    # Fix indentation for function bodies
    fix_indentation(schema, context)

    rendered_code = jinja_template.render(**context)
    clean_code = clean_up_code(rendered_code)
    return clean_code


def fix_indentation(schema: dict, context: dict) -> str:  
    # Process functions and fix indentation
    for function in schema['functions']:
        processed_function = function.copy()
        
        # Handle function body indentation
        if 'body' in function and function['body']:

            # Remove any existing indentation and re-indent properly
            #body_lines = function['body'].split('\n')

            # Remove common leading whitespace
            dedented_body = textwrap.dedent(function['body'])
            processed_function['body'] = dedented_body.strip()
        
        context['functions'].append(processed_function)

def clean_up_code(rendered_code: str) -> str:
    # Clean up any extra blank lines
    lines = rendered_code.split('\n')
    cleaned_lines = []
    prev_blank = False
    
    for line in lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue  # Skip consecutive blank lines
        cleaned_lines.append(line)
        prev_blank = is_blank
    return '\n'.join(cleaned_lines)

def save_generated_code(code: str, output_path: str) -> None:
    """
    Save generated Python code to file.
    
    Args:
        code: The generated Python code string.
        output_path: Path where to save the generated file.
        
    Raises:
        IOError: If file cannot be written.
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)
        # Attempt to validate syntax
        try:
            compile(code, output_path, 'exec')
            print(f"✓ Generated valid Python code: {output_path}")
        except SyntaxError as e:
            print(f"⚠ Warning: Generated code has syntax error at line {e.lineno}: {e.msg}")
            
    except IOError as e:
        raise IOError(f"Cannot write to file {output_path}: {e}")


def main() -> None:
    """
    Main CLI entry point for the schema generator.
    """
    parser = argparse.ArgumentParser(
        description="Generate Python classes from JSON function schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python schema_generator.py -i sample_processor_schema.json -o generated_processor.py
  python schema_generator.py --input sample_processor_schema.json --output processors/my_processor.py
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input JSON schema file'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to the output Python file'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the schema without generating code'
    )

    parser.add_argument(
        '--template_path',
        default='dependency_module_template.py.jinja',
        help='Path to the Jinja2 template file (relative to current directory)'
    )

    args = parser.parse_args()
    
    try:
        # Load and validate schema
        print(f"Loading schema from: {args.input}")
        schema = load_json_schema(args.input)
        
        print("Validating schema...")
        if not validate_schema(schema):
            print("❌ Schema validation failed")
            sys.exit(1)
        
        print("✓ Schema validation passed")
        
        if args.validate_only:
            print("Validation complete. No code generated (--validate-only)")
            return

        # Generate code
        print("Generating Python code...")
        generated_code = generate_class_code(schema, args.template_path)

        # Save code
        print(f"Saving generated code to: {args.output}")
        save_generated_code(generated_code, args.output)
        
        print("🎉 Code generation completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
