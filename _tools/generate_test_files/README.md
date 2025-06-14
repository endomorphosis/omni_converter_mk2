# Test File Generator

An automated tool that generates comprehensive unit test scaffolds for Python codebases using AST parsing and Jinja2 templates.

## Overview

The Test File Generator analyzes Python source files and automatically creates corresponding unit test files with test scaffolds for all callable elements including functions, methods, classes, and coroutines. It follows the project's IoC (Inversion of Control) architecture pattern with dependency injection.

## Features

- **Comprehensive Coverage**: Generates tests for all callable elements:
  - Standalone functions
  - Standalone coroutines  
  - Classes and their methods
  - Class methods, static methods, and properties
  - Explicitly defined dunder methods
  - Class attributes

- **Smart Filtering**: 
  - Excludes implicit dunder methods
  - Ignores import statements
  - Supports directory exclusion patterns

- **Template-Based Generation**: Uses Jinja2 templates for customizable test structure

- **IoC Architecture**: Follows dependency injection patterns for testability and flexibility


## Usage

### Example Usage

```bash
# Always activate virtual environment
source venv/bin/activate

# Generate tests for a specific directory
source venv/bin/activate && python -m tools.generate_test_files --target_dir format_handlers --output_dir tests/format_handlers_refactored

# Generate tests with directory exclusions
source venv/bin/activate && python -m tools.generate_test_files --target_dir format_handlers --output_dir tests/format_handlers_refactored --ignore_dir_list deprecated processors

# Generate tests for root directory
source venv/bin/activate && python -m tools.generate_test_files --target_dir . --output_dir tests/generated
```

## Command Line Arguments

- **`--target_dir`** (required): Source directory containing Python files to analyze
- **`--output_dir`** (optional): Output directory for generated test files (default: "tests")
- **`--ignore_dir_list`** (optional): Space-separated list of directories to exclude from processing

## Output Structure

The tool maintains the source directory structure in the output:

```
target_dir/
├── module1.py
├── subdir/
│   └── module2.py
└── another_dir/
    └── module3.py

# Generates:
output_dir/
├── __init__.py
├── test_module1.py
├── subdir/
│   ├── __init__.py
│   └── test_module2.py
└── another_dir/
    ├── __init__.py
    └── test_module3.py
```

## Generated Test Structure

Each generated test file includes:

- Import statements from the original module
- Test class for each source class with methods for all callable elements
- Test functions for standalone functions and coroutines
- Proper test naming conventions (`test_` prefix)
- Placeholder test implementations with TODO comments

## Dependencies

- **Python 3.10+**: Required for modern Python features
- **Jinja2**: Template engine for test file generation
- **Pydantic**: Data validation and settings management
- **AST**: Built-in Python module for source code parsing
- **tqdm**: Progress bar display

## Error Handling

The tool implements robust error handling:

- **File-level errors**: Continues processing other files if one fails
- **Directory validation**: Checks target directory existence upfront
- **Graceful failures**: Logs errors and continues processing
- **Return status**: Returns count of successfully generated files

## Integration with Project

The tool integrates with the project's:

- **Configuration system**: Uses the global `configs` object
- **Logging system**: Uses the project's logger for output
- **Architecture patterns**: Follows IoC principles with dependency injection
- **Code style**: Generates tests following project conventions

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError for 'configs'**: 
   - Ensure you're running from the project root
   - Activate the virtual environment first

2. **No files generated**:
   - Check target directory path
   - Verify Python files exist in target directory
   - Check ignore directory list isn't excluding everything

3. **Template errors**:
   - Verify Jinja2 template file exists in `_templates/`
   - Check template syntax if customized

### Debug Mode

Enable verbose logging by checking the project's logger configuration in `logger.py`.

## Extending the Tool

The modular architecture allows easy extension:

- **Custom templates**: Modify Jinja2 templates in `_templates/`
- **Additional parsers**: Add new parsing functions to the resources dictionary
- **Custom filters**: Extend directory filtering logic
- **Output formats**: Add support for different test frameworks

## Future Enhancements

Potential improvements include:

- Support for different testing frameworks (pytest, nose2)
- Mock generation for external dependencies
- Test data generation based on type hints
- Integration with existing test discovery tools
- Custom template selection per file type
