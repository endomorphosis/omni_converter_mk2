# CLAUDE.md - Project Guidelines

### Documentation
- [SAD.md](SAD.md) - Architecture Implementation Details, including flowchart and class diagrams.
- [PRD.md](PRD.md) - Product Requirements Document, including Minimum Viable Product specification.
- [PHASE16_README.md](PHASE16_README.md) - Details on Phase 16 plan for the project.
- [TOOLS.md](claudes_toolbox/TOOLS.md) - CLI tools to help you when writing code.
- [TESTING.md](TESTING.md) - Guidelines and metrics for creating and running tests.
- [CHANGELOG](CHANGELOG.md) - Record of changes made to the program and to tests.
- [dummy_implementations](dummy_implementations) - Record of dummy implementations and their implementation status.

## Build & Run Commands
```bash
# Setup environment and install dependencies
./install.sh

# Run the main program
./start.sh

# Run unit tests
source venv/bin/activate && python -m unittest discover -s tests

# Run a specific test file
source venv/bin/activate && python -m unittest tests/test_filename.py

# Run a specific test case
source venv/bin/activate && python -m unittest tests.test_filename.TestClassName.test_method_name
```

## Available Tools in /claudes_toolbox
- documentation_generator: Documentation Generator automatically extracts code structure, docstrings, and type annotations from Python source code to produce comprehensive documentation in Markdown format. It supports multiple docstring styles (Google, NumPy, and reStructuredText) and preserves type hints from source code annotations.
- 

## Code Style Guidelines
- **Docstrings**: Verbose, Google-style docstrings with types, parameters, returns, and examples. This includes tests.
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

## Feature Implementation Guidelines
- **NEVER REMOVE FEATURES**: Once a feature has been implemented, NEVER remove it, even if it causes test failures. Instead, modify the code and/or tests to ensure both the feature and tests work correctly together.
- **Maintain compatibility**: When updating code, ensure backward compatibility is maintained.
- **Test adaptation**: When a feature or capability changes, adapt tests to match the new functionality rather than removing the feature to match existing tests.

## Project Structure
- Main converter in root directory
- Modular tools in claudes_toolbox/
- Tests in tests/ directory matching the module structure
- Documentation in documentation/ directory matching the module structure.

## Access Restrictions
- Do NOT access or read any files in the _Claude_ignore_this_folder_please/ directory
- This directory contains internal formulas and data that should be ignored by Claude

## Git Usage Restrictions
- NEVER run git commands (commit, push, pull, etc.)
- Do NOT make git commits or create pull requests
- Do NOT use git to view repository history
- The user will handle all git operations manually