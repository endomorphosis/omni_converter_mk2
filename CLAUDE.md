# CLAUDE.md - Project Guidelines

### Core Documentation
- [SAD.md](SAD.md) - Architecture Implementation Details, including flowchart and class diagrams.
- [PRD.md](PRD.md) - Product Requirements Document, including Minimum Viable Product specification
- [PHASE16_README.md](PHASE16_README.md) - Details on Phase 16 plan for the project.
- [TOOLS.md](claudes_toolbox/TOOLS.md) - CLI tools to help you when writing code.
- [TESTING.md](TESTING.md) - Guidelines and metrics for creating and running tests.

## Build & Run Commands
```bash
# Setup environment and install dependencies
./install.sh

# Run the main program
./start.sh

# Run unit tests
python -m unittest discover -s tests

# Run a specific test file
python -m unittest tests/test_filename.py

# Run a specific test case
python -m unittest tests.test_filename.TestClassName.test_method_name
```

## Code Style Guidelines
- **Docstrings**: Google-style docstrings with types, parameters, returns, and examples
- **Types**: Use type hints for function parameters and return values
- **Imports**: Group standard library, third-party, and local imports; alphabetize within groups
- **Naming**:
  - Classes: PascalCase
  - Functions/methods: snake_case
  - Constants: UPPER_SNAKE_CASE
  - Variables: snake_case
- **Error handling**: Use explicit exception types with descriptive messages
- **Line length**: 100 characters maximum
- **File organization**: Module docstring first, imports second, constants third, then classes/functions

## Project Structure
- Main converter in root directory
- Modular tools in claudes_toolbox/
- Tests in tests/ directory matching the module structure

## Access Restrictions
- Do NOT access or read any files in the _Claude_ignore_this_folder_please/ directory
- This directory contains internal formulas and data that should be ignored by Claude