"""
Simple working tests for pytest migration demonstration.

This module contains basic tests that work without external dependencies
to demonstrate pytest conversion patterns and verify the testing infrastructure.
"""
import pytest
import os
import tempfile
import json
from pathlib import Path


@pytest.mark.unit
class TestBasicPythonOperations:
    """Test basic Python operations to verify pytest setup."""

    def test_string_operations(self):
        """Test basic string operations."""
        text = "Hello, World!"
        assert text.upper() == "HELLO, WORLD!"
        assert text.lower() == "hello, world!"
        assert len(text) == 13
        assert "World" in text

    def test_list_operations(self):
        """Test basic list operations."""
        items = [1, 2, 3, 4, 5]
        assert len(items) == 5
        assert sum(items) == 15
        assert max(items) == 5
        assert min(items) == 1

    @pytest.mark.parametrize("input_val,expected", [
        (2, 4),
        (3, 9), 
        (4, 16),
        (5, 25)
    ])
    def test_square_function(self, input_val, expected):
        """Test parametrized square function."""
        assert input_val ** 2 == expected

    def test_dictionary_operations(self):
        """Test basic dictionary operations."""
        data = {"name": "test", "value": 42}
        assert data["name"] == "test"
        assert data.get("value") == 42
        assert "name" in data
        assert data.keys() == {"name", "value"}


@pytest.mark.unit
class TestFileOperations:
    """Test file operations using temporary files."""

    def test_create_and_read_file(self, temp_dir):
        """Test file creation and reading."""
        file_path = os.path.join(temp_dir, "test.txt")
        content = "Test content"
        
        # Write file
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Verify file exists
        assert os.path.exists(file_path)
        
        # Read and verify content
        with open(file_path, 'r') as f:
            read_content = f.read()
        
        assert read_content == content

    def test_json_operations(self, temp_dir):
        """Test JSON file operations."""
        json_file = os.path.join(temp_dir, "test.json")
        test_data = {"key": "value", "number": 42}
        
        # Write JSON
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Read and verify JSON
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data

    def test_path_operations(self, temp_dir):
        """Test Path operations."""
        path = Path(temp_dir)
        assert path.exists()
        assert path.is_dir()
        
        file_path = path / "test_file.txt"
        file_path.write_text("test content")
        
        assert file_path.exists()
        assert file_path.is_file()
        assert file_path.read_text() == "test content"


@pytest.mark.unit
class TestExceptionHandling:
    """Test exception handling patterns."""

    def test_division_by_zero(self):
        """Test division by zero exception."""
        with pytest.raises(ZeroDivisionError):
            result = 10 / 0

    def test_key_error(self):
        """Test KeyError exception."""
        data = {"a": 1}
        with pytest.raises(KeyError):
            value = data["nonexistent"]

    def test_type_error(self):
        """Test TypeError exception."""
        with pytest.raises(TypeError):
            result = "string" + 5

    def test_exception_message(self):
        """Test exception message matching."""
        with pytest.raises(ValueError, match="invalid literal"):
            int("not_a_number")


@pytest.mark.unit
class TestDataStructures:
    """Test various data structures."""

    def test_set_operations(self):
        """Test set operations."""
        set1 = {1, 2, 3}
        set2 = {2, 3, 4}
        
        assert set1.union(set2) == {1, 2, 3, 4}
        assert set1.intersection(set2) == {2, 3}
        assert set1.difference(set2) == {1}

    def test_tuple_operations(self):
        """Test tuple operations."""
        data = ("a", "b", "c")
        assert len(data) == 3
        assert data[0] == "a"
        assert data[-1] == "c"
        assert "b" in data

    @pytest.mark.parametrize("data_structure,expected_len", [
        ([1, 2, 3], 3),
        ({"a", "b", "c"}, 3),
        ({"x": 1, "y": 2}, 2),
        ("hello", 5)
    ])
    def test_length_operations(self, data_structure, expected_len):
        """Test length operations on different data structures."""
        assert len(data_structure) == expected_len


@pytest.mark.integration  
class TestIntegrationExample:
    """Example integration tests."""

    def test_multiple_operations_together(self, temp_dir):
        """Test multiple operations working together."""
        # Create test data
        test_data = {
            "files": ["file1.txt", "file2.txt", "file3.txt"],
            "metadata": {
                "created": "2023-01-01",
                "version": "1.0"
            }
        }
        
        # Write JSON config
        config_file = os.path.join(temp_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create referenced files
        for filename in test_data["files"]:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Content of {filename}")
        
        # Verify all files exist
        for filename in test_data["files"]:
            file_path = os.path.join(temp_dir, filename)
            assert os.path.exists(file_path)
        
        # Verify config can be loaded
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        assert loaded_config == test_data
        assert len(loaded_config["files"]) == 3
        assert loaded_config["metadata"]["version"] == "1.0"