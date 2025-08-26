import pytest
from pathlib import Path
import os

# Make sure the input file and documentation file exist.
cwd = os.getcwd()
assert os.path.exists(f'{cwd}/utils/filesystem.py'), "utils/filesystem.py does not exist at the specified directory."
assert os.path.exists(f'{cwd}/utils/filesystem_stubs.md'), "Documentation for utils/filesystem.py does not exist at the specified directory."

from utils.filesystem import FileContent


class TestFileContentInit:
    """Test FileContent initialization and configuration."""

    def test_init_with_valid_raw_content_and_defaults(self):
        """
        GIVEN valid raw_content as bytes
        AND default encoding 'utf-8'
        AND default mime_type None
        WHERE:
            - valid_raw_content = b"Hello, World!"
            - custom_encoding = "utf-8" (default)
            - explicit_mime_type = None (default)
        WHEN FileContent is initialized
        THEN expect:
            - Instance created without exceptions
            - as_binary property == b"Hello, World!"
            - encoding attribute == "utf-8"
            - mime_type determined using MIME detection
            - size attribute == 13
            - text_content attribute available for conversion
        """
        valid_raw_content = b"Hello, World!"
        
        file_content = FileContent(valid_raw_content)
        
        assert file_content.as_binary == b"Hello, World!"
        assert file_content.encoding == "utf-8"
        assert file_content.mime_type is not None
        assert file_content.size == 13
        assert isinstance(file_content.text_content, str)

    def test_init_with_custom_encoding(self):
        """
        GIVEN valid raw_content as bytes
        AND custom encoding parameter
        AND default mime_type None
        WHERE:
            - valid_raw_content = b"Hello, World!"
            - custom_encoding = "latin-1"
            - explicit_mime_type = None (default)
        WHEN FileContent is initialized
        THEN expect:
            - Instance created without exceptions
            - encoding attribute == "latin-1"
            - text_content uses latin-1 for conversion
        """
        valid_raw_content = b"Hello, World!"
        custom_encoding = "latin-1"
        
        file_content = FileContent(valid_raw_content, encoding=custom_encoding)
        
        assert file_content.encoding == "latin-1"
        # Verify text_content uses the correct encoding
        expected_text = valid_raw_content.decode("latin-1")
        assert file_content.text_content == expected_text

    def test_init_with_explicit_mime_type(self):
        """
        GIVEN valid raw_content as bytes
        AND default encoding
        AND explicit mime_type parameter
        WHERE:
            - valid_raw_content = b"Hello, World!"
            - custom_encoding = "utf-8" (default)
            - explicit_mime_type = "text/plain"
        WHEN FileContent is initialized
        THEN expect:
            - Instance created without exceptions
            - mime_type attribute == "text/plain"
            - MIME detection bypassed
        """
        valid_raw_content = b"Hello, World!"
        explicit_mime_type = "text/plain"
        
        file_content = FileContent(valid_raw_content, mime_type=explicit_mime_type)
        
        assert file_content.mime_type == "text/plain"

    def test_init_with_empty_raw_content(self):
        """
        GIVEN empty raw_content
        AND default parameters
        WHERE:
            - empty_raw_content = b""
            - custom_encoding = "utf-8" (default)
            - explicit_mime_type = None (default)
        WHEN FileContent is initialized
        THEN expect:
            - Instance created without exceptions
            - size attribute == 0
            - text_content == ""
        """
        empty_raw_content = b""
        
        file_content = FileContent(empty_raw_content)
        
        assert file_content.size == 0
        assert file_content.text_content == ""

    @pytest.mark.parametrize("invalid_content", ["string", 123, None, [1, 2, 3]])
    def test_init_with_invalid_raw_content_type(self, invalid_content):
        """
        GIVEN raw_content that is not bytes (test string, int, None, and list types)
        WHERE:
            - invalid_types = ["string", 123, None, [1, 2, 3]]
        WHEN FileContent is initialized with each invalid type
        THEN expect TypeError to be raised for each case
        """
        with pytest.raises(TypeError):
            FileContent(invalid_content)

    def test_init_with_invalid_encoding(self):
        """
        GIVEN valid raw_content
        AND invalid encoding name
        WHERE:
            - valid_raw_content = b"Hello, World!"
            - invalid_encoding = "nonexistent-encoding"
        WHEN FileContent is initialized
        THEN expect LookupError to be raised
        """
        valid_raw_content = b"Hello, World!"
        invalid_encoding = "nonexistent-encoding"
        
        with pytest.raises(LookupError):
            FileContent(valid_raw_content, encoding=invalid_encoding)


class TestFileContentAsBinary:
    """Test FileContent.as_binary property."""

    def test_as_binary_returns_original_raw_content(self):
        """
        GIVEN FileContent instance initialized with specific raw_content bytes
        WHERE:
            - specific_raw_content = b"test content for binary access"
        WHEN as_binary property is accessed
        THEN expect:
            - Returned value is specific_raw_content using `is` operator
            - Returned value type == bytes
            - No modification or copying of the original content
        """
        specific_raw_content = b"test content for binary access"
        
        file_content = FileContent(specific_raw_content)
        binary_result = file_content.as_binary
        
        assert binary_result is specific_raw_content
        assert isinstance(binary_result, bytes)

    def test_as_binary_with_empty_content(self):
        """
        GIVEN FileContent instance initialized with empty raw_content
        WHERE:
            - empty_content = b""
        WHEN as_binary property is accessed
        THEN expect:
            - Returned value == b""
            - Type == bytes
        """
        empty_content = b""
        
        file_content = FileContent(empty_content)
        binary_result = file_content.as_binary
        
        assert binary_result == b""
        assert isinstance(binary_result, bytes)

    @pytest.mark.slow
    def test_as_binary_with_large_content(self):
        """
        GIVEN FileContent instance initialized with large raw_content (5MB)
        WHERE:
            - large_content = b"x" * (5 * 1024 * 1024)  # 5MB
        WHEN as_binary property is accessed multiple times
        THEN expect:
            - Each access returns the same content using `==`
            - Each access returns the same object reference using `is`
            - Multiple accesses complete without memory leaks
        """
        large_content = b"x" * (5 * 1024 * 1024)  # 5MB
        
        file_content = FileContent(large_content)
        
        # First access
        binary_result1 = file_content.as_binary
        # Second access
        binary_result2 = file_content.as_binary
        # Third access
        binary_result3 = file_content.as_binary
        
        # Content equality check
        assert binary_result1 == large_content
        assert binary_result2 == large_content
        assert binary_result3 == large_content
        
        # Object reference check
        assert binary_result1 is binary_result2
        assert binary_result2 is binary_result3
        assert binary_result1 is large_content

    def test_as_binary_immutability(self):
        """
        GIVEN FileContent instance with raw_content
        WHERE:
            - specific_raw_content = b"test content for binary access"
        WHEN as_binary property is accessed and attempts are made to modify via slicing
        THEN expect:
            - Original raw_content in FileContent remains unchanged
            - Subsequent calls to as_binary return original content
        """
        specific_raw_content = b"test content for binary access"
        
        file_content = FileContent(specific_raw_content)
        binary_result = file_content.as_binary
        
        # Attempt to create a modified version (this doesn't modify the original bytes object)
        modified_binary = binary_result[5:] + b" modified"
        
        # Verify original content is unchanged
        assert file_content.as_binary == specific_raw_content
        assert file_content.as_binary != modified_binary
        
        # Verify subsequent calls return original content
        subsequent_result = file_content.as_binary
        assert subsequent_result == specific_raw_content
        assert subsequent_result is specific_raw_content


class TestFileContentGetAsText:
    """Test FileContent.get_as_text method."""

    def test_get_as_text_with_default_encoding(self):
        """
        GIVEN FileContent instance with text content
        WHERE:
            - raw_content = b"Hello, World!"
            - encoding = "utf-8" (default)
        WHEN get_as_text() is called without parameters
        THEN expect:
            - Returned value == "Hello, World!"
            - No encoding errors
        """
        raw_content = b"Hello, World!"
        
        file_content = FileContent(raw_content)
        text_result = file_content.get_as_text()
        
        assert text_result == "Hello, World!"

    def test_get_as_text_with_custom_encoding(self):
        """
        GIVEN FileContent instance with text content
        WHERE:
            - raw_content = b"Hello, World!"
            - instance_encoding = "utf-8"
        WHEN get_as_text(encoding="latin-1") is called
        THEN expect:
            - Text decoded using latin-1 encoding
            - Returned value matches manual decoding
        """
        raw_content = b"Hello, World!"
        
        file_content = FileContent(raw_content)
        text_result = file_content.get_as_text(encoding="latin-1")
        expected_text = raw_content.decode("latin-1")
        
        assert text_result == expected_text

    def test_get_as_text_with_invalid_encoding(self):
        """
        GIVEN FileContent instance
        WHERE:
            - raw_content = b"Hello, World!"
        WHEN get_as_text(encoding="invalid-encoding") is called
        THEN expect:
            - LookupError to be raised
        """
        raw_content = b"Hello, World!"
        
        file_content = FileContent(raw_content)
        
        with pytest.raises(LookupError):
            file_content.get_as_text(encoding="invalid-encoding")

    def test_get_as_text_with_decoding_errors(self):
        """
        GIVEN FileContent instance with binary data that can't be decoded as text
        WHERE:
            - binary_data = b"\\x80\\x81\\x82"  # Invalid UTF-8 bytes
        WHEN get_as_text() is called
        THEN expect:
            - UnicodeDecodeError to be raised
        """
        binary_data = b"\x80\x81\x82"  # Invalid UTF-8 bytes
        
        file_content = FileContent(binary_data)
        
        with pytest.raises(UnicodeDecodeError):
            file_content.get_as_text()

    def test_get_as_text_error_handling_ignore(self):
        """
        GIVEN FileContent instance with problematic binary data
        WHERE:
            - binary_data = b"Hello\\x80World"  # Mixed valid/invalid UTF-8
        WHEN get_as_text(errors="ignore") is called
        THEN expect:
            - Invalid bytes ignored
            - Valid text returned without invalid sequences
        """
        binary_data = b"Hello\x80World"  # Mixed valid/invalid UTF-8
        
        file_content = FileContent(binary_data)
        text_result = file_content.get_as_text(errors="ignore")
        
        assert text_result == "HelloWorld"

    def test_get_as_text_error_handling_replace(self):
        """
        GIVEN FileContent instance with problematic binary data
        WHERE:
            - binary_data = b"Hello\\x80World"  # Mixed valid/invalid UTF-8
        WHEN get_as_text(errors="replace") is called
        THEN expect:
            - Invalid bytes replaced with Unicode replacement character
            - Result contains replacement character for invalid sequence
        """
        binary_data = b"Hello\x80World"  # Mixed valid/invalid UTF-8
        
        file_content = FileContent(binary_data)
        text_result = file_content.get_as_text(errors="replace")
        
        assert "Hello" in text_result
        assert "World" in text_result
        assert "\ufffd" in text_result  # Unicode replacement character

    def test_get_as_text_empty_content(self):
        """
        GIVEN FileContent instance with empty content
        WHERE:
            - raw_content = b""
        WHEN get_as_text() is called
        THEN expect:
            - Empty string returned
            - No errors raised
        """
        raw_content = b""
        
        file_content = FileContent(raw_content)
        text_result = file_content.get_as_text()
        
        assert text_result == ""