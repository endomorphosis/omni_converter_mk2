# TODO Finder

A command-line tool that scans your codebase for TODO comments and collects them into a markdown file for easy tracking.

## Features

- **Recursive directory scanning** - Searches through all subdirectories
- **Multiple comment formats** - Detects TODOs in various comment styles:
  - Python/Shell: `# TODO`
  - C-style: `// TODO` and `/* TODO */`
  - HTML/XML: `<!-- TODO -->`
- **Case-insensitive** - Finds TODO, Todo, todo, etc.
- **Smart filtering** - Automatically excludes:
  - Version control directories (`.git`)
  - Build artifacts (`__pycache__`, `node_modules`)
  - Virtual environments (`.venv`, `venv`)
  - Binary files (`.pyc`, `.so`, `.dll`, etc.)
- **Line number tracking** - Shows exact location of each TODO
- **Timestamp tracking** - Records when TODOs were collected
- **Append mode** - Preserves existing TODO entries

## Installation

1. Download the script:
```bash
curl -O https://raw.githubusercontent.com/yourusername/yourrepo/main/todo_finder.py
```

2. Make it executable (optional):
```bash
chmod +x todo_finder.py
```

3. Optionally, add to your PATH for system-wide access.

## Usage

### Basic Usage

Search the current directory and output to `TODO.md`:
```bash
python todo_finder.py .
```

### Specify Directory

Search a specific project directory:
```bash
python todo_finder.py /path/to/my/project
```

### Custom Output File

Output to a different file:
```bash
python todo_finder.py . -o my_todos.md
python todo_finder.py . --output project_tasks.md
```

### Exclude Additional Directories

Exclude specific directories from the search:
```bash
python todo_finder.py . -e build dist temp
python todo_finder.py . --exclude vendor cache logs
```

## Examples

### Example 1: Basic Search

Given a project structure:
```
myproject/
├── main.py
├── utils/
│   └── helpers.py
└── tests/
    └── test_main.py
```

With these TODO comments:
```python
# main.py
def process_data(data):
    # TODO: Add input validation
    return data

# utils/helpers.py
def format_output(text):
    // TODO: Support Unicode characters
    return text.upper()

# tests/test_main.py
def test_process():
    # todo: Write more comprehensive tests
    assert True
```

Running:
```bash
python todo_finder.py myproject/
```

Creates `TODO.md`:
```markdown
## New Tasks (Generated on 2025-05-22 15:30:45)

- [ ] **main.py** (line 3): Add input validation
- [ ] **utils/helpers.py** (line 3): Support Unicode characters
- [ ] **tests/test_main.py** (line 3): Write more comprehensive tests
```

### Example 2: Multiple Runs

The tool appends new sections on each run, preserving history:

First run:
```bash
python todo_finder.py src/
```

Second run (after adding more TODOs):
```bash
python todo_finder.py src/
```

Results in `TODO.md`:
```markdown
## New Tasks (Generated on 2025-05-22 10:00:00)

- [ ] **api.py** (line 45): Implement rate limiting
- [ ] **database.py** (line 78): Add connection pooling

## New Tasks (Generated on 2025-05-22 14:30:00)

- [ ] **api.py** (line 45): Implement rate limiting
- [ ] **api.py** (line 92): Add authentication
- [ ] **database.py** (line 78): Add connection pooling
- [ ] **cache.py** (line 23): Set up Redis backend
```

### Example 3: JavaScript Project

```bash
python todo_finder.py frontend/ -o frontend_todos.md -e node_modules dist
```

Finds TODOs in JavaScript files:
```javascript
// app.js
function handleSubmit() {
    // TODO: Add form validation
    submitForm();
}

/* config.js */
const config = {
    apiUrl: 'http://localhost:3000',
    /* TODO: Move to environment variables */
};
```

### Example 4: Mixed Language Project

The tool works across multiple languages in the same scan:

```bash
python todo_finder.py fullstack-app/
```

Finds TODOs in:
- Python files: `# TODO: Optimize database queries`
- JavaScript files: `// TODO: Add error handling`
- HTML files: `<!-- TODO: Update meta tags -->`
- CSS files: `/* TODO: Make responsive */`

## Output Format

Each TODO entry in the markdown file includes:
- **Checkbox** - For tracking completion
- **File path** - Relative to the search directory
- **Line number** - Exact location in the file
- **TODO text** - The comment content

Example entry:
```markdown
- [ ] **src/auth/login.py** (line 127): Implement 2FA support
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `directory` | - | Directory to search (required) | - |
| `--output` | `-o` | Output markdown file path | `TODO.md` |
| `--exclude` | `-e` | Additional directories to exclude | - |

## Default Excluded Directories

The following directories are excluded by default:
- `.git` - Version control
- `__pycache__` - Python cache
- `node_modules` - Node.js dependencies
- `.venv` - Python virtual environment
- `venv` - Python virtual environment

## Tips

1. **Regular Scans**: Run the tool regularly (e.g., before commits) to track new TODOs
2. **CI Integration**: Add to your CI pipeline to track TODO growth
3. **Project Root**: Run from your project root for consistent file paths
4. **Custom Excludes**: Use `-e` to exclude build or generated directories
5. **Multiple Files**: Use different output files for different parts of large projects

## Limitations

- Binary files are automatically skipped
- Very large files might take longer to process
- TODO must be preceded by a comment marker to be detected
- Multi-line TODO comments are captured as single lines

## License

This tool is provided as-is for use in your projects.