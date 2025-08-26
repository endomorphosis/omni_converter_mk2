# Pytest Test Suite for Omni Converter MK2

This directory contains pytest conversions of unittest test files from the `tests/` directory.

## Directory Structure

```
tests_pytest/
├── __init__.py
├── conftest.py                    # Common fixtures and configuration
├── test_basic_setup.py           # Basic pytest setup verification
├── run_pytest_tests.py           # Test runner script (also available in root)
└── unit_tests/
    ├── interfaces_/
    │   ├── test_options.py        # Converted from unittest
    │   └── test_interface_factory.py  # Skeleton test converted
    ├── batch_processor_/
    │   └── test_batch_result.py   # Converted from unittest  
    └── utils_/
        └── filesystem/
            └── test_file_info.py  # Converted from unittest
```

## Key Conversion Patterns

### 1. Test Class Structure

**Unittest (Original):**
```python
class TestExample(unittest.TestCase):
    def setUp(self):
        self.data = "test"
    
    def test_something(self):
        self.assertEqual(self.data, "test")
```

**Pytest (Converted):**
```python
@pytest.mark.unit
class TestExample:
    def test_something(self):
        assert "test" == "test"

# Or using fixtures:
@pytest.fixture
def test_data():
    return "test"

def test_something(test_data):
    assert test_data == "test"
```

### 2. Assertions

| Unittest | Pytest |
|----------|---------|
| `self.assertEqual(a, b)` | `assert a == b` |
| `self.assertTrue(x)` | `assert x` or `assert x is True` |
| `self.assertFalse(x)` | `assert not x` or `assert x is False` |
| `self.assertIn(a, b)` | `assert a in b` |
| `self.assertIsInstance(obj, cls)` | `assert isinstance(obj, cls)` |
| `self.assertRaises(Exception)` | `pytest.raises(Exception)` |
| `self.assertLess(a, b)` | `assert a < b` |
| `self.assertGreater(a, b)` | `assert a > b` |

### 3. Setup and Teardown

**Unittest:**
```python
def setUp(self):
    self.temp_file = create_temp_file()

def tearDown(self):
    cleanup_temp_file(self.temp_file)
```

**Pytest:**
```python
@pytest.fixture
def temp_file():
    file = create_temp_file()
    yield file
    cleanup_temp_file(file)
```

### 4. Exception Testing

**Unittest:**
```python
with self.assertRaises(ValueError) as context:
    some_function()
self.assertIn("error message", str(context.exception))
```

**Pytest:**
```python
with pytest.raises(ValueError) as exc_info:
    some_function()
assert "error message" in str(exc_info.value)
```

### 5. Parametrized Tests

**Unittest (using subTest):**
```python
def test_multiple_values(self):
    values = [1, 2, 3]
    for val in values:
        with self.subTest(val=val):
            self.assertEqual(val * 2, val + val)
```

**Pytest:**
```python
@pytest.mark.parametrize("val", [1, 2, 3])
def test_multiple_values(val):
    assert val * 2 == val + val
```

### 6. Mocking

**Unittest:**
```python
from unittest.mock import patch, MagicMock

@patch('module.function')
def test_with_mock(self, mock_func):
    mock_func.return_value = "mocked"
    # test code
```

**Pytest (same pattern):**
```python
from unittest.mock import patch, MagicMock

@patch('module.function')
def test_with_mock(mock_func):
    mock_func.return_value = "mocked"
    # test code
```

### 7. Test Markers

Pytest uses markers for test categorization:

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow tests
@pytest.mark.filesystem    # Tests that interact with filesystem
@pytest.mark.skip(reason="Not implemented")  # Skip test
@pytest.mark.xfail(reason="Known bug")       # Expected failure
```

## Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest tests_pytest/

# Run with verbose output
python -m pytest tests_pytest/ -v

# Run specific test categories
python -m pytest tests_pytest/ -m unit
python -m pytest tests_pytest/ -m "not slow"
python -m pytest tests_pytest/ -m "unit and filesystem"

# Run test runner script
python run_pytest_tests.py
```

### Test Discovery

Pytest automatically discovers:
- Files matching `test_*.py` or `*_test.py`
- Classes named `Test*`
- Functions named `test_*`

## Fixtures Available

The `conftest.py` file provides common fixtures:

- `temp_dir` - Temporary directory with cleanup
- `temp_file` - Temporary file with cleanup
- `mock_logger` - Mock logger instance
- `sample_files` - Set of sample files for testing
- `nested_dir_structure` - Nested directory structure for testing

## Configuration

Test configuration is in `pytest.ini`:

- Test paths: `tests_pytest/`
- Markers are defined for categorization
- Warnings are filtered appropriately
- Short traceback format for cleaner output

## Benefits of Pytest Migration

1. **Simpler Syntax** - Plain assert statements vs unittest's assert methods
2. **Better Fixtures** - More flexible setup/teardown with dependency injection  
3. **Rich Ecosystem** - Many useful plugins available
4. **Parametrization** - Built-in support for data-driven tests
5. **Better Output** - Clearer test results and failure information
6. **Flexible Organization** - More options for test structure and discovery

## Migration Status

### Completed Conversions

- ✅ `test_options.py` - Interface options validation and configuration
- ✅ `test_batch_result.py` - Batch processing result handling
- ✅ `test_file_info.py` - File information extraction
- ✅ `test_interface_factory.py` - Interface factory skeleton tests

### Key Features Demonstrated

- Complex fixture setups (temp file management)
- Parametrized tests
- Exception testing with pytest.raises
- Test markers and categorization
- Mock integration
- Class-based test organization
- Comprehensive assertion patterns

## Next Steps

Continue converting remaining unittest files:
- Core module tests (content_extractor, file_validator, etc.)
- Processor tests (by_mime_type, etc.)
- Monitor tests (error_monitor, resource_monitor, etc.)
- Remaining skeleton tests with proper implementations

Each conversion maintains the original test logic while leveraging pytest's enhanced features for better maintainability and readability.