# Pytest Test Suite Documentation

This directory contains pytest conversions of the original unittest test suite located in the `tests/` directory.

## Key Conversion Patterns

### 1. Test Class Structure

**Unittest (Original):**
```python
class TestExample(unittest.TestCase):
    def setUp(self):
        self.data = "test_data"
    
    def tearDown(self):
        # cleanup
        pass
    
    def test_something(self):
        self.assertEqual(self.data, "test_data")
```

**Pytest (Converted):**
```python
class TestExample:
    def test_something(self):
        assert self.data == "test_data"

# Or using fixtures for setup/teardown:
@pytest.fixture
def test_data():
    data = "test_data"
    yield data
    # cleanup after yield

def test_something(test_data):
    assert test_data == "test_data"
```

### 2. Assertions

| Unittest | Pytest |
|----------|---------|
| `self.assertEqual(a, b)` | `assert a == b` |
| `self.assertTrue(x)` | `assert x` |
| `self.assertFalse(x)` | `assert not x` |
| `self.assertIsNone(x)` | `assert x is None` |
| `self.assertIn(a, b)` | `assert a in b` |
| `self.assertRaises(Exception)` | `pytest.raises(Exception)` |

### 3. Setup and Teardown

**Unittest setUp/tearDown → Pytest Fixtures:**

```python
# Unittest
class TestExample(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

# Pytest
@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_something(temp_dir):
    # test uses temp_dir
    pass
```

### 4. Parametrized Tests

**Unittest subTest → Pytest parametrize:**

```python
# Unittest
def test_multiple_values(self):
    values = [1, 2, 3]
    for val in values:
        with self.subTest(val=val):
            self.assertEqual(val * 2, val + val)

# Pytest
@pytest.mark.parametrize("val", [1, 2, 3])
def test_multiple_values(val):
    assert val * 2 == val + val
```

### 5. Mocking

**Unittest mock → pytest-mock:**

```python
# Unittest
from unittest.mock import MagicMock, patch

# Pytest (with pytest-mock plugin)
def test_with_mock(mocker):
    mock_obj = mocker.MagicMock()
    mocker.patch('module.function', return_value='mocked')
```

### 6. Markers and Categories

**Pytest markers replace unittest test categorization:**

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration  
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

## Running Tests

### Run All Tests
```bash
python -m pytest test_pytest/
```

### Run Specific Test Categories
```bash
# Run only unit tests
python -m pytest test_pytest/ -m unit

# Skip slow tests
python -m pytest test_pytest/ -m "not slow"

# Run integration tests
python -m pytest test_pytest/ -m integration
```

### Run with Different Output Formats
```bash
# Verbose output
python -m pytest test_pytest/ -v

# Short output
python -m pytest test_pytest/ -q

# Show local variables on failures
python -m pytest test_pytest/ -l
```

### Run Test Runner Script
```bash
python test_pytest/run_all_pytest_tests.py
```

## Directory Structure

```
test_pytest/
├── __init__.py
├── run_all_pytest_tests.py      # Main test runner
├── test_simple_example.py       # Pytest pattern examples
├── collected_results/            # Test results and reports
├── unit_tests/
│   ├── batch_processor_/
│   │   └── test_resolve_paths.py
│   └── utils_/
│       └── filesystem/
│           └── test_file_content.py
└── integration_tests/
    └── test_vertical_slice.py
```

## Advantages of Pytest

1. **Simpler syntax**: Plain `assert` statements instead of `self.assert*` methods
2. **Better fixtures**: More flexible setup/teardown with dependency injection
3. **Parametrization**: Built-in support for running same test with different inputs
4. **Rich plugin ecosystem**: Many useful plugins available
5. **Better test discovery**: More flexible test naming and organization
6. **Clearer output**: Better formatted test results and failure information

## Configuration

See `pytest.ini` for configuration options including:
- Test discovery patterns
- Output formatting
- Markers definition
- Default command-line options