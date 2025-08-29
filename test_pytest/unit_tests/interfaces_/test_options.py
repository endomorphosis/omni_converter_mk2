"""
Test suite for interfaces/options.py converted from unittest to pytest.
"""
import pytest
from unittest.mock import patch, MagicMock
import argparse
import tempfile
import os
from pathlib import Path
from enum import StrEnum

# Import the actual modules - adjust imports based on your project structure
from logger import test_logger as logger
from interfaces.options import (
    _validate_max_workers,
    _validate_max_memory,
    _validate_max_vram,
    Options,
    OutputFormat
)

try:
    from pydantic import ValidationError
    import psutil
except ImportError:
    pytest.skip("Required modules pydantic and psutil are not installed", allow_module_level=True)


@pytest.mark.unit
class TestValidateMaxWorkers:
    """Test the _validate_max_workers function."""

    @patch('os.cpu_count')
    def test_validate_max_workers_valid(self, mock_cpu_count):
        """
        GIVEN a max_threads value less than CPU cores
        WHEN _validate_max_workers(4) is called
        THEN expect:
            - Returns the same value
            - No ValidationError raised
        """
        mock_cpu_count.return_value = 8
        result = _validate_max_workers(4)
        assert result == 4

    @patch('os.cpu_count')
    def test_validate_max_workers_exceeds_cpu_cores(self, mock_cpu_count):
        """
        GIVEN a max_threads value greater than available CPU cores
        WHEN _validate_max_workers(1000) is called
        THEN expect:
            - Raises ValueError
            - Error message mentions CPU cores limit
        """
        mock_cpu_count.return_value = 8
        with pytest.raises(ValueError) as exc_info:
            _validate_max_workers(1000)
        assert "cpu" in str(exc_info.value).lower()


@pytest.mark.unit
class TestValidateMaxMemory:
    """Test the _validate_max_memory function."""

    @patch('interfaces.options.Hardware.get_total_memory_in_gb')
    def test_validate_max_memory_valid(self, mock_get_memory):
        """
        GIVEN a max_memory value less than current total memory
        WHEN _validate_max_memory(1) is called
        THEN expect:
            - Returns the same value
            - No ValidationError raised
        """
        mock_get_memory.return_value = 6  # 6 GiB
        
        result = _validate_max_memory(1)
        assert result == 1

    @patch('interfaces.options.Hardware.get_total_memory_in_gb')
    def test_validate_max_memory_below_current_usage(self, mock_get_memory):
        """
        GIVEN a max_memory value greater than current total memory
        WHEN _validate_max_memory(100) is called
        THEN expect:
            - Raises ValueError
            - Error message contains current RSS usage
        """
        mock_get_memory.return_value = 6  # 6 GiB

        try:
            result = _validate_max_memory(100)
            logger.debug(f"Unexpected success: returned {result}")
        except Exception as e:
            logger.debug(f"Exception raised: {type(e).__name__}: {e}")
        
        with pytest.raises(ValueError):
            _validate_max_memory(100)


@pytest.mark.unit
class TestValidateMaxVram:
    """Test the _validate_max_vram function."""

    def test_validate_max_vram_any_positive_value(self):
        """
        GIVEN any positive max_vram value
        WHEN _validate_max_vram(6144) is called
        THEN expect:
            - Returns the same value
            - No ValidationError raised (TODO: validation not implemented)
        """
        result = _validate_max_vram(6144)
        assert result == 6144


@pytest.mark.unit
class TestOutputFormat:
    """Test the OutputFormat enum."""

    def test_output_format_txt_value(self):
        """
        GIVEN the OutputFormat enum
        WHEN accessing OutputFormat.TXT
        THEN expect:
            - Value equals "txt"
            - Is instance of StrEnum
        """
        assert OutputFormat.TXT == "txt"
        assert isinstance(OutputFormat.TXT, StrEnum)

    def test_output_format_md_value(self):
        """
        GIVEN the OutputFormat enum
        WHEN accessing OutputFormat.MD
        THEN expect:
            - Value equals "md"
            - Is instance of StrEnum
        """
        assert OutputFormat.MD == "md"
        assert isinstance(OutputFormat.MD, StrEnum)

    def test_output_format_json_value(self):
        """
        GIVEN the OutputFormat enum
        WHEN accessing OutputFormat.JSON
        THEN expect:
            - Value equals "json"
            - Is instance of StrEnum
        """
        assert OutputFormat.JSON == "json"
        assert isinstance(OutputFormat.JSON, StrEnum)


@pytest.fixture
def temp_files():
    """Create temporary files and directories for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_file.txt")
    with open(temp_file, 'w') as f:
        f.write("test content")
    
    yield {'temp_dir': temp_dir, 'temp_file': temp_file}
    
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.mark.unit
class TestOptionsModel:
    """Test the Options Pydantic model."""

    def test_options_creation_minimal(self, temp_files):
        """
        GIVEN only required input parameter
        WHEN Options(input="/path/to/file") is created
        THEN expect:
            - Instance created successfully
            - All default values are set correctly
            - input field contains the provided path
        """
        options = Options(input=temp_files['temp_file'])
        assert isinstance(options, Options)
        assert str(options.input) == temp_files['temp_file']
        assert options.output == Path.home()
        assert options.walk is False
        assert options.normalize is True

    def test_options_creation_with_all_fields(self, temp_files):
        """
        GIVEN all possible parameters
        WHEN Options instance is created with all fields specified
        THEN expect:
            - Instance created successfully
            - All fields contain provided values
            - No validation errors
        """
        options = Options(
            input=temp_files['temp_file'],
            output=temp_files['temp_dir'],
            walk=True,
            normalize=False,
            security_checks=False,
            metadata=False,
            structure=False,
            format=OutputFormat.JSON,
            max_threads=2,
            max_memory=4,
            max_vram=4,
            budget_in_usd=10.0,
            normalizers="test",
            max_cpu=50,
            quality_threshold=0.5,
            continue_on_error=False,
            parallel=True,
            follow_symlinks=True,
            include_metadata=False,
            lossy=True,
            normalize_text=False,
            sanitize=False,
            show_options=True,
            show_progress=True,
            verbose=True,
            list_formats=True,
            version=True,
            batch_size=50,
            retries=3
        )
        assert isinstance(options, Options)
        assert str(options.input) == temp_files['temp_file']
        assert str(options.output) == temp_files['temp_dir']
        assert options.walk is True
        assert options.normalize is False
        assert options.format == OutputFormat.JSON
        assert options.max_threads == 2

    def test_options_input_file_path(self, temp_files):
        """
        GIVEN a valid file path
        WHEN Options(input="/existing/file.txt") is created
        THEN expect:
            - input field is FilePath type
            - Path exists validation passes
        """
        options = Options(input=temp_files['temp_file'])
        assert Path(options.input).exists()
        assert Path(options.input).is_file()

    def test_options_input_directory_path(self, temp_files):
        """
        GIVEN a valid directory path
        WHEN Options(input="/existing/directory") is created
        THEN expect:
            - input field is DirectoryPath type
            - Directory exists validation passes
        """
        options = Options(input=temp_files['temp_dir'])
        assert Path(options.input).exists()
        assert Path(options.input).is_dir()

    def test_options_input_list_of_files(self, temp_files):
        """
        GIVEN a list of valid file paths
        WHEN Options(input=["/file1.txt", "/file2.txt"]) is created
        THEN expect:
            - input field accepts list[FilePath]
            - All files exist validation passes
        """
        temp_file2 = os.path.join(temp_files['temp_dir'], "test_file2.txt")
        with open(temp_file2, 'w') as f:
            f.write("test content 2")
        
        try:
            options = Options(input=[temp_files['temp_file'], temp_file2])
            assert isinstance(options.input, list)
            assert len(options.input) == 2
        finally:
            if os.path.exists(temp_file2):
                os.remove(temp_file2)

    def test_options_output_default(self, temp_files):
        """
        GIVEN no output parameter specified
        WHEN Options instance is created
        THEN expect:
            - output defaults to Path.home()
            - Is DirectoryPath type
        """
        options = Options(input=temp_files['temp_file'])
        assert options.output == Path.home()

    def test_options_format_validation(self, temp_files):
        """
        GIVEN an invalid format value
        WHEN Options(input="/file", format="invalid") is created
        THEN expect:
            - ValidationError is raised
            - Error mentions valid formats
        """
        with pytest.raises(ValidationError) as exc_info:
            Options(input=temp_files['temp_file'], format="invalid")
        assert "format" in str(exc_info.value).lower()

    def test_options_max_cpu_range(self, temp_files):
        """
        GIVEN max_cpu value over 100
        WHEN Options(input="/file", max_cpu=150) is created
        THEN expect:
            - ValidationError is raised
            - Error mentions maximum of 100
        """
        with pytest.raises(ValidationError) as exc_info:
            Options(input=temp_files['temp_file'], max_cpu=150)
        assert "100" in str(exc_info.value)

    def test_options_quality_threshold_range(self, temp_files):
        """
        GIVEN quality_threshold value over 1.0
        WHEN Options(input="/file", quality_threshold=1.5) is created
        THEN expect:
            - ValidationError is raised
            - Error mentions maximum of 1.0
        """
        with pytest.raises(ValidationError) as exc_info:
            Options(input=temp_files['temp_file'], quality_threshold=1.5)
        assert "1" in str(exc_info.value)


@pytest.mark.unit
class TestOptionsToDict:
    """Test the to_dict method of Options."""

    def test_to_dict_all_fields(self, temp_files):
        """
        GIVEN an Options instance with all fields set
        WHEN to_dict() is called
        THEN expect:
            - Returns dictionary with all fields
            - Values match instance attributes
            - No missing fields
        """
        options = Options(
            input=temp_files['temp_file'],
            output=temp_files['temp_dir'],
            walk=True,
            normalize=False,
            format=OutputFormat.JSON
        )
        result_dict = options.to_dict()
        logger.debug(f"Options to_dict result: {result_dict}")
        
        assert isinstance(result_dict, dict)
        assert 'input' in result_dict
        assert 'output' in result_dict
        assert 'walk' in result_dict
        assert 'normalize' in result_dict
        assert 'format' in result_dict

        # Check values match instance attributes
        assert result_dict['walk'] is True
        assert result_dict['normalize'] is False

    def test_to_dict_defaults_only(self, temp_files):
        """
        GIVEN an Options instance with only defaults
        WHEN to_dict() is called
        THEN expect:
            - Returns dictionary with all fields
            - All values are defaults
        """
        options = Options(input=temp_files['temp_file'])
        result_dict = options.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['walk'] is False
        assert result_dict['normalize'] is True
        assert result_dict['format'] == OutputFormat.TXT


@pytest.mark.unit
class TestOptionsPrintOptions:
    """Test the print_options method of Options."""

    @patch('builtins.print')
    def test_print_options_defaults(self, mock_print, temp_files):
        """
        GIVEN an Options instance
        WHEN print_options(type_="defaults") is called
        THEN expect:
            - Prints default values for all fields
            - Includes field descriptions
            - Output formatted correctly
        """
        options = Options(input=temp_files['temp_file'])
        options.print_options(type_="defaults")
        
        mock_print.assert_called()
        # Check that print was called with some expected content
        printed_content = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
        assert "default" in printed_content.lower()

    @patch('builtins.print')
    def test_print_options_current(self, mock_print, temp_files):
        """
        GIVEN an Options instance with custom values
        WHEN print_options(type_="current") is called
        THEN expect:
            - Prints current values for all fields
            - Shows both current and default values
            - Output formatted correctly
        """
        options = Options(input=temp_files['temp_file'], walk=True, normalize=False)
        options.print_options(type_="current")
        
        mock_print.assert_called()
        printed_content = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
        assert "current" in printed_content.lower()

    def test_print_options_invalid_type(self, temp_files):
        """
        GIVEN an Options instance
        WHEN print_options(type_="invalid") is called
        THEN expect:
            - Raises ValueError
            - Error message mentions valid types
        """
        options = Options(input=temp_files['temp_file'])
        with pytest.raises(ValueError) as exc_info:
            options.print_options(type_="invalid")
        assert "valid" in str(exc_info.value).lower()


@pytest.mark.unit
class TestOptionsMakeArgparse:
    """Test the add_arguments_to_parser method of Options."""

    @pytest.fixture
    def parser(self):
        """Create a fresh ArgumentParser for each test."""
        return argparse.ArgumentParser()

    def test_make_argparse_all_arguments(self, temp_files, parser):
        """
        GIVEN an Options instance and ArgumentParser
        WHEN add_arguments_to_parser(parser) is called
        THEN expect:
            - All fields added as arguments
            - Correct types assigned
            - Help text included
        """
        options = Options(input=temp_files['temp_file'])
        result_parser = options.add_arguments_to_parser(parser)
        
        assert isinstance(result_parser, argparse.ArgumentParser)
        
        # Check that some key arguments were added
        help_text = result_parser.format_help()
        assert "input" in help_text.lower()
        assert "output" in help_text.lower()
        assert "walk" in help_text.lower()

    def test_make_argparse_defaults(self, temp_files, parser):
        """
        GIVEN an Options instance and ArgumentParser
        WHEN add_arguments_to_parser(parser) is called
        THEN expect:
            - All arguments have correct defaults
            - Defaults match field definitions
        """
        options = Options(input=temp_files['temp_file'])
        result_parser = options.add_arguments_to_parser(parser)
        
        # Parse with minimal required args to get defaults
        args = result_parser.parse_args(['--input', temp_files['temp_file']])
        print(f"args: {args}")
        
        # Check all default values
        assert args.input == temp_files['temp_file']  # Required field, provided
        assert str(args.output) == str(Path.home())
        assert args.walk is False
        assert args.normalize is True
        assert args.security_checks is True
        assert args.metadata is True
        assert args.structure is True
        assert args.format == OutputFormat.TXT.value  # Note: will be string value
        assert args.max_threads == 4
        assert args.max_memory == 6
        assert args.max_vram == 6
        assert args.budget_in_usd == 0.0
        assert args.normalizers is None
        assert args.max_cpu == 80
        assert args.quality_threshold == 0.9
        assert args.continue_on_error is True
        assert args.parallel is False
        assert args.follow_symlinks is False
        assert args.include_metadata is True
        assert args.lossy is False
        assert args.normalize_text is True
        assert args.sanitize is True
        assert args.show_options is False
        assert args.show_progress is False
        assert args.verbose is False
        assert args.list_formats is False
        assert args.version is False
        assert args.max_batch_size == 100
        assert args.retries == 0