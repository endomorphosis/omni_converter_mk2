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


# Test Constants
HELLO_WORLD_TEXT = "Hello, World!"
HELLO_WORLD_UPPER = "HELLO, WORLD!"
HELLO_WORLD_LOWER = "hello, world!"
HELLO_WORLD_LENGTH = 13
WORLD_SUBSTRING = "World"
TEST_LIST = [1, 2, 3, 4, 5]
TEST_LIST_LENGTH = 5
TEST_LIST_SUM = 15
TEST_LIST_MAX = 5
TEST_LIST_MIN = 1
TEST_DICT_NAME = "test"
TEST_DICT_VALUE = 42
TEST_JSON_CONTENT = '{"key": "value", "number": 123}'
EXPECTED_JSON_DICT = {"key": "value", "number": 123}
TEMP_FILE_CONTENT = "Hello from file!"


@pytest.mark.unit
class TestStringOperations:
    """
    Tests for basic string operations functionality.
    Functions under test: str.upper, str.lower, len, str.__contains__
    """

    def test_when_string_upper_called_then_returns_uppercase(self):
        """
        GIVEN a string with mixed case
        WHEN upper method is called
        THEN expect string with all uppercase letters
        """
        result = HELLO_WORLD_TEXT.upper()
        
        assert result == HELLO_WORLD_UPPER, f"Expected {HELLO_WORLD_UPPER}, got {result}"

    def test_when_string_lower_called_then_returns_lowercase(self):
        """
        GIVEN a string with mixed case
        WHEN lower method is called
        THEN expect string with all lowercase letters
        """
        result = HELLO_WORLD_TEXT.lower()
        
        assert result == HELLO_WORLD_LOWER, f"Expected {HELLO_WORLD_LOWER}, got {result}"

    def test_when_string_length_checked_then_returns_character_count(self):
        """
        GIVEN a string with known content
        WHEN len function is called on string
        THEN expect length equals character count
        """
        result = len(HELLO_WORLD_TEXT)
        
        assert result == HELLO_WORLD_LENGTH, f"Expected {HELLO_WORLD_LENGTH}, got {result}"

    def test_when_substring_searched_then_returns_true_if_found(self):
        """
        GIVEN a string with known content
        WHEN substring operator is used with existing substring
        THEN expect True is returned
        """
        result = WORLD_SUBSTRING in HELLO_WORLD_TEXT
        
        assert result is True, f"Expected True for '{WORLD_SUBSTRING}' in '{HELLO_WORLD_TEXT}', got {result}"


@pytest.mark.unit
class TestListOperations:
    """
    Tests for basic list operations functionality.
    Functions under test: len, sum, max, min
    """

    def test_when_list_length_checked_then_returns_element_count(self):
        """
        GIVEN a list with known elements
        WHEN len function is called on list
        THEN expect length equals element count
        """
        result = len(TEST_LIST)
        
        assert result == TEST_LIST_LENGTH, f"Expected {TEST_LIST_LENGTH}, got {result}"

    def test_when_list_sum_calculated_then_returns_total(self):
        """
        GIVEN a list with numeric elements
        WHEN sum function is called on list
        THEN expect sum equals total of all elements
        """
        result = sum(TEST_LIST)
        
        assert result == TEST_LIST_SUM, f"Expected {TEST_LIST_SUM}, got {result}"

    def test_when_list_max_found_then_returns_largest_element(self):
        """
        GIVEN a list with numeric elements
        WHEN max function is called on list
        THEN expect max equals largest element
        """
        result = max(TEST_LIST)
        
        assert result == TEST_LIST_MAX, f"Expected {TEST_LIST_MAX}, got {result}"

    def test_when_list_min_found_then_returns_smallest_element(self):
        """
        GIVEN a list with numeric elements
        WHEN min function is called on list
        THEN expect min equals smallest element
        """
        result = min(TEST_LIST)
        
        assert result == TEST_LIST_MIN, f"Expected {TEST_LIST_MIN}, got {result}"

    @pytest.mark.parametrize("input_val,expected", [
        (2, 4),
        (3, 9), 
        (4, 16),
        (5, 25)
    ])
    def test_when_number_squared_then_returns_square_value(self, input_val, expected):
        """
        GIVEN a numeric input value
        WHEN number is squared using exponentiation operator
        THEN expect result equals expected square value
        """
        result = input_val ** 2
        
        assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.unit
class TestDictionaryOperations:
    """
    Tests for basic dictionary operations functionality.
    Functions under test: dict.__getitem__, dict.get, dict.__contains__, dict.keys
    """

    def test_when_dictionary_key_accessed_then_returns_value(self):
        """
        GIVEN a dictionary with known key-value pairs
        WHEN key is accessed using bracket notation
        THEN expect value associated with key
        """
        data = {"name": TEST_DICT_NAME, "value": TEST_DICT_VALUE}
        result = data["name"]
        
        assert result == TEST_DICT_NAME, f"Expected {TEST_DICT_NAME}, got {result}"

    def test_when_dictionary_get_used_then_returns_value(self):
        """
        GIVEN a dictionary with known key-value pairs
        WHEN get method is called with existing key
        THEN expect value associated with key
        """
        data = {"name": TEST_DICT_NAME, "value": TEST_DICT_VALUE}
        result = data.get("value")
        
        assert result == TEST_DICT_VALUE, f"Expected {TEST_DICT_VALUE}, got {result}"

    def test_when_dictionary_contains_checked_then_returns_true_if_key_exists(self):
        """
        GIVEN a dictionary with known keys
        WHEN in operator is used with existing key
        THEN expect True is returned
        """
        data = {"name": TEST_DICT_NAME, "value": TEST_DICT_VALUE}
        result = "name" in data
        
        assert result is True, f"Expected True for 'name' in dictionary, got {result}"

    def test_when_dictionary_keys_accessed_then_returns_key_set(self):
        """
        GIVEN a dictionary with known keys
        WHEN keys method is called
        THEN expect set containing all dictionary keys
        """
        data = {"name": TEST_DICT_NAME, "value": TEST_DICT_VALUE}
        result = data.keys()
        
        assert result == {"name", "value"}, f"Expected {{'name', 'value'}}, got {result}"


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