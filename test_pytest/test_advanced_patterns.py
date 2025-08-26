"""
Advanced pytest patterns and features demonstration.

This file shows additional pytest patterns that are commonly used
when converting from unittest to pytest.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock


# Fixtures can be shared across multiple test files by putting them in conftest.py
@pytest.fixture(scope="session")
def global_test_data():
    """Session-scoped fixture - runs once for entire test session."""
    return {"global_config": "test_value"}


@pytest.fixture(scope="module")
def module_test_data():
    """Module-scoped fixture - runs once per test module."""
    return {"module_data": "shared_data"}


@pytest.fixture
def temp_file_with_content():
    """Fixture that creates a temporary file with test content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test file content\nSecond line")
        temp_path = f.name
    
    yield Path(temp_path)
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_file_system(tmp_path):
    """Fixture that creates a mock file system structure."""
    # tmp_path is a built-in pytest fixture
    test_files = {
        "file1.txt": "Content of file 1",
        "file2.py": "print('Hello Python')",
        "subdir/file3.json": '{"key": "value"}',
        "subdir/nested/file4.md": "# Markdown Header"
    }
    
    created_files = {}
    for rel_path, content in test_files.items():
        file_path = tmp_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        created_files[rel_path] = file_path
    
    return created_files


class TestAdvancedPatterns:
    """Examples of advanced pytest patterns."""

    def test_with_multiple_fixtures(self, global_test_data, module_test_data, temp_file_with_content):
        """Test using multiple fixtures."""
        assert global_test_data["global_config"] == "test_value"
        assert module_test_data["module_data"] == "shared_data"
        assert temp_file_with_content.exists()
        assert temp_file_with_content.suffix == '.txt'

    @pytest.mark.parametrize("input_value,expected,operation", [
        (5, 25, "square"),
        (3, 9, "square"),
        (4, 16, "square"),
        (5, 10, "double"),
        (3, 6, "double"),
    ])
    def test_complex_parametrization(self, input_value, expected, operation):
        """Test with complex parametrization."""
        if operation == "square":
            result = input_value ** 2
        elif operation == "double":
            result = input_value * 2
        else:
            pytest.fail(f"Unknown operation: {operation}")
        
        assert result == expected

    @pytest.mark.parametrize("filename,expected_type", [
        ("document.pdf", "pdf"),
        ("image.jpg", "image"),
        ("script.py", "python"),
        ("data.json", "json"),
        ("unknown.xyz", "unknown"),
    ])
    def test_file_type_detection(self, filename, expected_type):
        """Test file type detection logic."""
        def detect_file_type(filename):
            """Simple file type detection based on extension."""
            extension = Path(filename).suffix.lower()
            type_mapping = {
                '.pdf': 'pdf',
                '.jpg': 'image',
                '.jpeg': 'image',
                '.py': 'python',
                '.json': 'json'
            }
            return type_mapping.get(extension, 'unknown')
        
        assert detect_file_type(filename) == expected_type

    def test_with_built_in_fixtures(self, tmp_path, monkeypatch):
        """Test using pytest's built-in fixtures."""
        # tmp_path provides a temporary directory
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        assert test_file.read_text() == "Hello World"
        
        # monkeypatch allows safe patching
        monkeypatch.setenv("TEST_VAR", "test_value")
        assert os.environ["TEST_VAR"] == "test_value"

    def test_with_mock_file_system(self, mock_file_system):
        """Test using the mock file system fixture."""
        assert len(mock_file_system) == 4
        
        # Test file contents
        file1 = mock_file_system["file1.txt"]
        assert file1.read_text() == "Content of file 1"
        
        # Test nested structure
        nested_file = mock_file_system["subdir/nested/file4.md"]
        assert "# Markdown Header" in nested_file.read_text()
        assert nested_file.suffix == ".md"

    @pytest.mark.slow
    def test_marked_as_slow(self):
        """Test that can be skipped with -m 'not slow'."""
        import time
        time.sleep(0.1)  # Simulate slow operation
        assert True

    @pytest.mark.skip(reason="Demonstrating skip functionality")
    def test_skipped_test(self):
        """This test is always skipped."""
        assert False  # This won't run

    @pytest.mark.skipif(os.name == "nt", reason="Unix-only test")
    def test_conditional_skip(self):
        """Test skipped conditionally based on platform."""
        # This test only runs on non-Windows systems
        assert os.name != "nt"

    @pytest.mark.xfail(reason="Known bug - expected to fail")
    def test_expected_failure(self):
        """Test that is expected to fail."""
        assert 1 == 2  # This will fail but won't cause test suite to fail

    def test_approximate_comparison(self):
        """Test using pytest.approx for floating point comparisons."""
        # Instead of unittest's assertAlmostEqual
        result = 0.1 + 0.2
        assert result == pytest.approx(0.3)
        
        # With tolerance
        assert 1.0001 == pytest.approx(1.0, abs=0.001)
        
        # Works with lists and dictionaries too
        assert [0.1 + 0.1, 0.2 + 0.2] == pytest.approx([0.2, 0.4])

    def test_exception_details(self):
        """Test examining exception details."""
        with pytest.raises(ValueError) as exc_info:
            raise ValueError("Custom error message")
        
        assert "Custom error message" in str(exc_info.value)
        assert exc_info.type == ValueError

    def test_warnings(self):
        """Test handling warnings."""
        import warnings
        
        with pytest.warns(UserWarning, match="deprecated"):
            warnings.warn("This feature is deprecated", UserWarning)

    def test_with_caplog(self, caplog):
        """Test capturing log messages."""
        import logging
        
        # Set logging level to capture info messages
        with caplog.at_level(logging.INFO):
            logger = logging.getLogger(__name__)
            
            logger.info("Test info message")
            logger.error("Test error message")
        
        assert "Test info message" in caplog.text
        assert "Test error message" in caplog.text
        # Check that we have at least 2 records
        assert len(caplog.records) >= 2

    def test_with_capsys(self, capsys):
        """Test capturing stdout/stderr."""
        print("Hello stdout")
        print("Hello stderr", file=__import__('sys').stderr)
        
        captured = capsys.readouterr()
        assert "Hello stdout" in captured.out
        assert "Hello stderr" in captured.err


# Fixtures can also be used to parametrize tests
@pytest.fixture(params=["txt", "py", "json", "md"])
def file_extension(request):
    """Parametrized fixture that provides different file extensions."""
    return request.param


def test_with_parametrized_fixture(file_extension):
    """Test using a parametrized fixture."""
    # This test will run once for each parameter in the fixture
    assert file_extension in ["txt", "py", "json", "md"]


# Class-based test organization (similar to unittest.TestCase)
class TestClassBased:
    """Class-based test organization."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Auto-use fixture for class-level setup."""
        self.test_data = "class_test_data"
    
    def test_method_one(self):
        """First test method."""
        assert hasattr(self, 'test_data')
        assert self.test_data == "class_test_data"
    
    def test_method_two(self):
        """Second test method."""
        assert self.test_data == "class_test_data"


# Custom markers can be defined in pytest.ini and used for test organization
@pytest.mark.unit
@pytest.mark.filesystem
def test_custom_markers():
    """Test demonstrating custom markers."""
    # This test has both 'unit' and 'filesystem' markers
    # Can be run with: pytest -m unit
    # Or: pytest -m filesystem
    # Or: pytest -m "unit and filesystem"
    assert True