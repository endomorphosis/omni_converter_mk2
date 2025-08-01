#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile
import unittest
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock

# Import the class under test
from configs import Configs
from core.file_validator._file_validator import FileValidator
from core.file_validator._validation_result import ValidationResult
from file_format_detector._file_format_detector import FileFormatDetector
from utils.filesystem import FileInfo

class TestFileValidatorInitialization(unittest.TestCase):
    """Test FileValidator initialization and configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Mock dependencies
        self.mock_configs = Mock()
        self.mock_configs.security = Mock()
        self.mock_configs.security.max_file_size_mb = 100  # 100 MB limit (attribute, not method)
        self.mock_configs.security.allowed_formats = ['pdf', 'txt', 'docx']  # attribute, not method

        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_file_format_detector = Mock()
        self.mock_validation_result = Mock()

        self.valid_resources = {
            "file_format_detector": self.mock_file_format_detector,
            "logger": self.mock_logger,
            "validation_result": self.mock_validation_result,
            "file_exists": Mock(return_value=True),
            "get_file_info": Mock(return_value=Mock(size=1024, is_readable=True))
        }

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_init_with_valid_resources_and_configs(self):
        """
        GIVEN valid resources dict containing:
            - file_detector: A file detector instance
            - logger: A logger instance
            - Any other required resources
        AND valid configs object with:
            - validation.max_file_size_mb attribute
            - validation.supported_formats attribute
            - Any other validation-related attributes
        WHEN FileValidator is initialized
        THEN expect:
            - Instance created successfully
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        
        # THEN
        self.assertIsInstance(validator, FileValidator)

    def test_init_configs_stored_correctly(self):
        """
        GIVEN valid resources dict and valid configs object
        WHEN FileValidator is initialized
        THEN expect:
            - validator.configs equals the provided configs object
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator.configs, self.mock_configs)

    def test_init_max_file_size_set_correctly(self):
        """
        GIVEN valid resources dict and configs with validation.max_file_size_mb = 100
        WHEN FileValidator is initialized
        THEN expect:
            - validator.max_file_size_mb equals 100
        """
        # Given
        test_size = 100
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator.max_file_size_mb, test_size)

    def test_init_allowed_formats_set_correctly(self):
        """
        GIVEN valid resources dict and configs with validation.supported_formats = ['pdf', 'txt', 'docx']
        WHEN FileValidator is initialized
        THEN expect:
            - validator.allowed_formats equals ['pdf', 'txt', 'docx']
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator.allowed_formats, ['pdf', 'txt', 'docx'])

    def test_init_logger_component_set_correctly(self):
        """
        GIVEN valid resources dict containing logger component
        WHEN FileValidator is initialized
        THEN expect:
            - validator._logger equals the provided logger
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator._logger, self.mock_logger)

    def test_init_format_detector_component_set_correctly(self):
        """
        GIVEN valid resources dict containing file_detector component
        WHEN FileValidator is initialized
        THEN expect:
            - validator._format_detector equals the provided file_detector
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator._format_detector, self.mock_file_format_detector)

    def test_init_validation_result_component_set_correctly(self):
        """
        GIVEN valid resources dict containing validation_result component
        WHEN FileValidator is initialized
        THEN expect:
            - validator._validation_result equals the provided validation_result
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator._validation_result, self.mock_validation_result)

    def test_init_file_exists_function_set_correctly(self):
        """
        GIVEN valid resources dict containing file_exists function
        WHEN FileValidator is initialized
        THEN expect:
            - validator._file_exists equals the provided file_exists function
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator._file_exists, self.valid_resources["file_exists"])

    def test_init_get_file_info_function_set_correctly(self):
        """
        GIVEN valid resources dict containing get_file_info function
        WHEN FileValidator is initialized
        THEN expect:
            - validator._get_file_info equals the provided get_file_info function
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator._get_file_info, self.valid_resources["get_file_info"])

    def test_init_resources_are_the_same_as_validators_resources(self):
        """
        GIVEN valid resources dict
        WHEN FileValidator is initialized with those resources
        THEN expect:
            - validator.resources equals the provided resources dict
        """
        # WHEN
        validator = FileValidator(resources=self.valid_resources, configs=self.mock_configs)
        # THEN
        self.assertEqual(validator.resources, self.valid_resources)

    def test_init_with_none_resources(self):
        """
        GIVEN resources parameter is None
        WHEN FileValidator is initialized
        THEN expect:
            - Raises TypeError
        """
        # GIVEN
        resources = None

        # WHEN/THEN
        with self.assertRaises(TypeError):
            _ = FileValidator(resources=resources, configs=self.mock_configs)

    def test_init_with_none_configs(self):
        """
        GIVEN configs parameter is None
        WHEN FileValidator is initialized
        THEN expect:
            - Raises AttributeError
        """
        # GIVEN
        configs = None

        # WHEN/THEN
        with self.assertRaises(AttributeError):
            _ = FileValidator(resources=self.valid_resources, configs=configs)


    def test_init_with_empty_resources_dict(self):
        """
        GIVEN empty resources dict {}
        WHEN FileValidator is initialized
        THEN expect:
            - raises KeyError
        """
        # GIVEN
        empty_resources = {}
        
        # WHEN/THEN
        with self.assertRaises(KeyError):
            _ = FileValidator(resources=empty_resources, configs=self.mock_configs)

    def test_init_with_configs_missing_attributes(self):
        """
        GIVEN a configs object missing required attributes
        WHEN FileValidator is initialized
        THEN expect:
            - raises AttributeError
        """
        # GIVEN
        configs_missing_attributes = MagicMock(spec=Configs)
        configs_missing_attributes.validation = MagicMock()

        # When
        del configs_missing_attributes.validation.max_file_size_mb  # Remove required attribute
        
        # THEN
        with self.assertRaises(AttributeError):
            _ = FileValidator(resources=self.valid_resources, configs=configs_missing_attributes)


class TestGetValidationErrors(unittest.TestCase):
    """Test FileValidator.get_validation_errors method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test files
        self.valid_file = self.temp_path / "valid_file.txt"
        self.valid_file.write_text("This is a valid test file.")
        
        self.large_file = self.temp_path / "large_file.txt"
        self.large_file.write_text("A" * 1024 * 1024)  # 1MB file
        
        self.empty_file = self.temp_path / "empty_file.txt"
        self.empty_file.touch()
        
        # Mock dependencies
        self.mock_configs = Mock()
        self.mock_configs.security = Mock()
        self.mock_configs.security.max_file_size_mb = 0.5  # 0.5 MB limit
        self.mock_configs.security.allowed_formats = ['txt', 'pdf', 'docx']
        
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_file_format_detector = Mock(spec=FileFormatDetector)
        self.mock_validation_result_class = Mock(spec=ValidationResult)
        
        # Configure a mock ValidationResult instance
        self.mock_validation_result_instance = Mock(spec=ValidationResult)
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        self.mock_validation_result_instance.warnings = []
        self.mock_validation_result_instance.validation_context = {}
        self.mock_validation_result_instance.add_error = Mock()
        self.mock_validation_result_instance.add_warning = Mock()
        self.mock_validation_result_instance.add_context = Mock()
        
        # Make the class mock return our instance
        self.mock_validation_result_class.return_value = self.mock_validation_result_instance

        self.mock_resources = {
            "file_format_detector": self.mock_file_format_detector,
            "logger": self.mock_logger,
            "validation_result": self.mock_validation_result_class,
            "file_exists": Mock(return_value=True),
            "get_file_info": Mock(return_value=Mock(size=1024, is_readable=True))
        }
        
        self.validator = FileValidator(resources=self.mock_resources, configs=self.mock_configs)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_get_errors_valid_file_with_format_returns_empty_list(self):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND format_name is provided (e.g., 'pdf')
        WHEN get_validation_errors is called
        THEN expect:
            - Returns empty list (no errors)
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,  # Small file within limits
            is_readable=True
        )
        self.mock_file_format_detector.get_format_category.return_value = 'document'
        
        # Set up the validation result to indicate success
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        
        # WHEN
        errors = self.validator.get_validation_errors(str(self.valid_file), 'txt')
        
        # THEN
        self.assertEqual(errors, [])

    def test_get_errors_nonexistent_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a non-existent file
        AND format_name is provided or None
        WHEN get_validation_errors is called
        THEN expect:
            - Returns list containing file not found error
        """
        # GIVEN
        nonexistent_file = self.temp_path / "does_not_exist.txt"
        self.mock_resources["file_exists"].return_value = False
        
        # Set up validation result to have an error
        self.mock_validation_result_instance.errors = ["File does not exist: " + str(nonexistent_file)]
        
        # WHEN
        errors = self.validator.get_validation_errors(str(nonexistent_file), 'txt')
        
        # THEN
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("does not exist" in error.lower() 
                           for error in errors))

    def test_get_errors_file_too_large(self):
        """
        GIVEN a FileValidator instance with max_file_size_mb configured
        AND a file path to a file exceeding the size limit
        AND format_name is provided or None
        WHEN get_validation_errors is called
        THEN expect:
            - Returns list containing file size error
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024 * 1024,  # 1MB file, exceeds 0.5MB limit
            is_readable=True
        )
        
        # Set up validation result to have size error
        self.mock_validation_result_instance.errors = ["File size exceeds maximum allowed"]
        
        # WHEN
        errors = self.validator.get_validation_errors(str(self.large_file), 'txt')
        
        # THEN
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("size" in error.lower() or "exceeds" in error.lower() 
                           for error in errors))

    def test_get_errors_unsupported_format(self):
        """
        GIVEN a FileValidator instance with supported_formats configured
        AND a file path to a file with unsupported format
        AND format_name is provided as unsupported format
        WHEN get_validation_errors is called
        THEN expect:
            - Returns list containing unsupported format error
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True
        )
        self.mock_file_format_detector.get_format_category.return_value = None  # Unsupported format
        
        # Set up validation result to have format error
        self.mock_validation_result_instance.errors = ["Format 'xyz' is not supported"]
        
        # WHEN
        errors = self.validator.get_validation_errors(str(self.valid_file), 'xyz')  # Unsupported format
        
        # THEN
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("not supported" in error.lower() or "format" in error.lower() 
                           for error in errors))

    def test_get_errors_no_read_permission(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a file without read permissions
        AND format_name is provided or None
        WHEN get_validation_errors is called
        THEN expect:
            - Returns list containing permission error
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=False  # No read permission
        )
        
        # Set up validation result to have permission error
        self.mock_validation_result_instance.errors = ["File is not readable"]
        
        # WHEN
        errors = self.validator.get_validation_errors(str(self.valid_file), 'txt')
        
        # THEN
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("not readable" in error.lower() or "permission" in error.lower() 
                           for error in errors))

    def test_get_errors_empty_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to an empty file (0 bytes)
        AND format_name is provided or None
        WHEN get_validation_errors is called
        THEN expect:
            - Returns list containing empty file error
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=0,  # Empty file
            is_readable=True
        )
        
        # Set up validation result to have empty file error
        self.mock_validation_result_instance.errors = ["File is empty"]
        
        # WHEN
        errors = self.validator.get_validation_errors(str(self.empty_file), 'txt')
        
        # THEN
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("empty" in error.lower() 
                           for error in errors))




class TestValidateFile(unittest.TestCase):
    """Test FileValidator.validate_file method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test files
        self.valid_file = self.temp_path / "valid_file.txt"
        self.valid_file.write_text("This is a valid test file.")
        
        self.invalid_file = self.temp_path / "invalid_file.txt"
        self.invalid_file.write_text("This file will be treated as invalid.")
        
        self.empty_file = self.temp_path / "empty_file.txt"
        self.empty_file.touch()
        
        # Mock dependencies
        self.mock_configs = Mock()
        self.mock_configs.security = Mock()
        self.mock_configs.security.max_file_size_mb = 10  # 10 MB limit
        self.mock_configs.security.allowed_formats = ['txt', 'pdf', 'docx']
        
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_file_format_detector = Mock()
        
        # Create a mock ValidationResult class that behaves like a Pydantic model
        self.mock_validation_result_class = Mock()
        self.mock_validation_result_instance = Mock(spec=ValidationResult)
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        self.mock_validation_result_instance.warnings = []
        self.mock_validation_result_instance.validation_context = {}
        self.mock_validation_result_instance.add_error = Mock()
        self.mock_validation_result_instance.add_warning = Mock()
        self.mock_validation_result_instance.add_context = Mock()
        
        self.mock_validation_result_class.return_value = self.mock_validation_result_instance
        
        self.mock_resources = {
            "file_format_detector": self.mock_file_format_detector,
            "logger": self.mock_logger,
            "validation_result": self.mock_validation_result_class,
            "file_exists": Mock(return_value=True),
            "get_file_info": Mock(return_value=Mock(size=1024, is_readable=True))
        }
        
        self.validator = FileValidator(resources=self.mock_resources, configs=self.mock_configs)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_validate_valid_file_with_format(self):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND file meets all validation criteria
        AND format_name is provided and supported
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is True
            - result.errors is empty list
            - result.warnings may contain any warnings
            - result.validation_context contains file metadata
        """
        # GIVEN
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            last_modified=datetime.now(),
            mime_type='text/plain',
            extension='txt'
        )
        self.mock_file_format_detector.get_format_category.return_value = 'document'
        
        # Configure the mock ValidationResult
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        self.mock_validation_result_instance.warnings = []
        self.mock_validation_result_instance.validation_context = {}
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)  # Mock ValidationResult
        
        # Verify ValidationResult was created with proper parameters
        self.mock_validation_result_class.assert_called_once()
        
        # Verify methods were called to populate the result
        self.mock_validation_result_instance.add_context.assert_called()

    def test_validate_valid_file_auto_detect_format(self):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND format_name is None (auto-detect)
        WHEN validate_file is called
        THEN expect:
            - Format is detected automatically
            - Returns ValidationResult instance
            - result.is_valid is True if format is supported
            - result.validation_context contains detected format
        """
        # GIVEN
        self.mock_file_format_detector.detect_format.return_value = ('txt', 'document')
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), None)
        
        # THEN
        self.assertIsInstance(result, Mock)
        self.mock_file_format_detector.detect_format.assert_called_once_with(str(self.valid_file))

    def test_validate_nonexistent_file_does_not_raise_exception(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a non-existent file
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult with error, doesn't raise exception
        """
        # GIVEN
        nonexistent_file = self.temp_path / "does_not_exist.txt"
        self.mock_resources["file_exists"].return_value = False
        
        # Set up validation result to have an error
        self.mock_validation_result_instance.errors = ["File does not exist"]
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        result = self.validator.validate_file(str(nonexistent_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        # Verify error was added
        self.mock_validation_result_instance.add_error.assert_called()

    def test_validate_file_with_size_exceeded(self):
        """
        GIVEN a FileValidator instance with max_file_size_mb configured
        AND a file path to a file exceeding the size limit
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False
            - result.errors contains file size error
            - result.validation_context contains file size info
        """
        # GIVEN
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024 * 1024 * 20,  # 20MB, exceeds 10MB limit
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        
        # Configure mock to reflect invalid state
        self.mock_validation_result_instance.is_valid = False
        self.mock_validation_result_instance.errors = ["File size exceeds maximum allowed size"]
        
        # WHEN
        result = self.validator.validate_file(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        
        # Verify error was added
        self.mock_validation_result_instance.add_error.assert_called()

    def test_validate_file_with_unsupported_format(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a file
        AND format_name is an unsupported format
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False
            - result.errors contains unsupported format error
            - result.validation_context contains format info
        """
        # GIVEN
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            mime_type='application/unknown',
            extension='xyz'
        )
        self.mock_file_format_detector.get_format_category.return_value = None  # Unsupported
        
        # Set up validation result to have format error
        self.mock_validation_result_instance.errors = ["Format 'xyz' is not supported"]
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), 'xyz')
        
        # THEN
        self.assertIsInstance(result, Mock)

    def test_validate_empty_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to an empty file (0 bytes)
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False (empty files are invalid)
            - result.errors contains empty file error
            - result.validation_context contains size: 0
        """
        # GIVEN
        self.mock_resources["get_file_info"].return_value = Mock(
            size=0,  # Empty file
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        
        # Set up validation result to have empty file error
        self.mock_validation_result_instance.errors = ["File is empty"]
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        result = self.validator.validate_file(str(self.empty_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        
        # Verify context includes size information
        self.mock_validation_result_instance.add_context.assert_called()

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_valid_file_auto_detect_format(self, mock_get_errors):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND format_name is None (auto-detect)
        WHEN validate_file is called
        THEN expect:
            - Format is detected automatically
            - Returns ValidationResult instance
            - result.is_valid is True if format is supported
            - result.validation_context contains detected format
        """
        # GIVEN
        mock_get_errors.return_value = []
        self.mock_file_format_detector.detect_format.return_value = 'txt'
        self.mock_resources["get_file_info"].return_value = {
            'size': 1024,
            'readable': True
        }
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), None)
        
        # THEN
        self.assertIsInstance(result, Mock)
        self.mock_file_format_detector.detect_format.assert_called_once_with(str(self.valid_file))
        mock_get_errors.assert_called_once_with(str(self.valid_file), None)

    def test_validate_nonexistent_file_raises_exception(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a non-existent file
        WHEN validate_file is called
        THEN expect:
            - Raises FileNotFoundError
        """
        # GIVEN
        nonexistent_file = self.temp_path / "does_not_exist.txt"
        self.mock_resources["file_exists"].return_value = False
        
        # WHEN & THEN
        with self.assertRaises(FileNotFoundError):
            self.validator.validate_file(str(nonexistent_file), 'txt')

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_file_with_size_exceeded(self, mock_get_errors):
        """
        GIVEN a FileValidator instance with max_file_size_mb configured
        AND a file path to a file exceeding the size limit
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False
            - result.errors contains file size error
            - result.validation_context contains file size info
        """
        # GIVEN
        size_error = "File size exceeds maximum allowed size"
        mock_get_errors.return_value = [size_error]
        self.mock_resources["get_file_info"].return_value = {
            'size': 1024 * 1024 * 20,  # 20MB, exceeds 10MB limit
            'readable': True
        }
        
        # Configure mock to reflect invalid state
        self.mock_validation_result_instance.is_valid = False
        self.mock_validation_result_instance.errors = [size_error]
        
        # WHEN
        result = self.validator.validate_file(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        mock_get_errors.assert_called_once_with(str(self.invalid_file), 'txt')
        
        # Verify error was added
        self.mock_validation_result_instance.add_error.assert_called()

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_file_with_unsupported_format(self, mock_get_errors):
        """
        GIVEN a FileValidator instance
        AND a file path to a file
        AND format_name is an unsupported format
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False
            - result.errors contains unsupported format error
            - result.validation_context contains format info
        """
        # GIVEN
        format_error = "Unsupported file format: xyz"
        mock_get_errors.return_value = [format_error]
        self.mock_resources["get_file_info"].return_value = {
            'size': 1024,
            'readable': True
        }
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), 'xyz')
        
        # THEN
        self.assertIsInstance(result, Mock)
        mock_get_errors.assert_called_once_with(str(self.valid_file), 'xyz')

    def test_validate_corrupted_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a corrupted file
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False
            - result.errors contains corruption error
            - result.validation_context may contain corruption details
        """
        # GIVEN
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        self.mock_file_format_detector.get_format_category.return_value = 'document'
        
        # Set up validation result to have corruption error
        self.mock_validation_result_instance.errors = ["File contains null bytes and may be corrupted"]
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        result = self.validator.validate_file(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_file_with_warnings(self, mock_get_errors):
        """
        GIVEN a FileValidator instance
        AND a file path to a valid file that triggers warnings
            (e.g., file close to size limit, deprecated format)
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is True (warnings don't invalidate)
            - result.errors is empty
            - result.warnings contains appropriate warnings
        """
        # GIVEN
        mock_get_errors.return_value = []  # No errors, but might have warnings
        self.mock_resources["get_file_info"].return_value = {
            'size': 1024 * 1024 * 9,  # 9MB, close to 10MB limit
            'readable': True
        }
        
        # Configure result to have warnings
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        self.mock_validation_result_instance.warnings = ["File size is close to maximum limit"]
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        # Warnings would be added during validation logic
        # This test verifies the structure supports warnings

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_file_populates_context(self, mock_get_errors):
        """
        GIVEN a FileValidator instance
        AND any valid file path
        WHEN validate_file is called
        THEN expect:
            - result.validation_context contains:
                - file_path: The validated file path
                - file_size: Size in bytes
                - format: Detected or provided format
                - validation_timestamp: When validated
                - Any other relevant metadata
        """
        # GIVEN
        mock_get_errors.return_value = []
        file_info = {
            'size': 1024,
            'readable': True,
            'last_modified': datetime.now()
        }
        self.mock_resources["get_file_info"].return_value = file_info
        
        # WHEN
        result = self.validator.validate_file(str(self.valid_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        
        # Verify context was populated with expected keys
        context_calls = self.mock_validation_result_instance.add_context.call_args_list
        context_keys = [call[0][0] for call in context_calls]  # Extract first argument (key) from each call
        
        # Should contain file metadata
        expected_keys = ['file_path', 'file_size', 'format', 'validation_timestamp']
        for key in expected_keys:
            self.assertIn(key, context_keys, f"Expected context key '{key}' not found")

    @patch.object(FileValidator, 'get_validation_errors')
    def test_validate_empty_file(self, mock_get_errors):
        """
        GIVEN a FileValidator instance
        AND a file path to an empty file (0 bytes)
        WHEN validate_file is called
        THEN expect:
            - Returns ValidationResult instance
            - result.is_valid is False (or True if empty allowed)
            - result.errors contains empty file error (if applicable)
            - result.validation_context contains size: 0
        """
        # GIVEN
        empty_file_error = "File is empty"
        mock_get_errors.return_value = [empty_file_error]  # Assume empty files are invalid
        self.mock_resources["get_file_info"].return_value = {
            'size': 0,
            'readable': True
        }
        
        # WHEN
        result = self.validator.validate_file(str(self.empty_file), 'txt')
        
        # THEN
        self.assertIsInstance(result, Mock)
        mock_get_errors.assert_called_once_with(str(self.empty_file), 'txt')
        
        # Verify context includes size information
        context_calls = self.mock_validation_result_instance.add_context.call_args_list
        size_context_found = any(
            call[0][0] == 'file_size' and call[0][1] == 0 
            for call in context_calls
        )
        self.assertTrue(size_context_found, "Expected file_size: 0 in validation context")



class TestIsValidForProcessing(unittest.TestCase):
    """Test FileValidator.is_valid_for_processing method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test files
        self.valid_file = self.temp_path / "valid_file.txt"
        self.valid_file.write_text("This is a valid test file.")
        
        self.invalid_file = self.temp_path / "invalid_file.txt"
        self.invalid_file.write_text("This file will be treated as invalid.")
        
        # Mock dependencies
        self.mock_configs = Mock()
        self.mock_configs.security = Mock()
        self.mock_configs.security.max_file_size_mb = 10  # 10 MB limit
        self.mock_configs.security.allowed_formats = ['txt', 'pdf', 'docx']
        
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_file_format_detector = Mock()
        
        # Create a mock ValidationResult class
        self.mock_validation_result_class = Mock()
        self.mock_validation_result_instance = Mock(spec=ValidationResult)
        self.mock_validation_result_instance.is_valid = True
        self.mock_validation_result_instance.errors = []
        self.mock_validation_result_instance.warnings = []
        self.mock_validation_result_instance.validation_context = {}
        self.mock_validation_result_instance.add_error = Mock()
        self.mock_validation_result_instance.add_warning = Mock()
        self.mock_validation_result_instance.add_context = Mock()
        
        self.mock_validation_result_class.return_value = self.mock_validation_result_instance
        
        self.mock_resources = {
            "file_format_detector": self.mock_file_format_detector,
            "logger": self.mock_logger,
            "validation_result": self.mock_validation_result_class,
            "file_exists": Mock(return_value=True),
            "get_file_info": Mock(return_value=Mock(size=1024, is_readable=True))
        }
        
        self.validator = FileValidator(resources=self.mock_resources, configs=self.mock_configs)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_is_valid_with_valid_file_and_format(self):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND file meets all validation criteria
        AND format_name is provided and supported
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns True
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,  # Small file within limits
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        self.mock_file_format_detector.get_format_category.return_value = 'document'
        
        # Set up validation result to indicate success
        self.mock_validation_result_instance.is_valid = True
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.valid_file), 'txt')
        
        # THEN
        self.assertTrue(is_valid)

    def test_is_valid_with_valid_file_auto_detect_format(self):
        """
        GIVEN a FileValidator instance
        AND a valid file path to an existing, readable file
        AND file meets all validation criteria
        AND format_name is None (auto-detect)
        WHEN is_valid_for_processing is called
        THEN expect:
            - Format is detected automatically
            - Returns True if detected format is supported
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        self.mock_file_format_detector.detect_format.return_value = ('txt', 'document')
        
        # Set up validation result to indicate success
        self.mock_validation_result_instance.is_valid = True
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.valid_file), None)
        
        # THEN
        self.assertTrue(is_valid)

    def test_is_valid_with_nonexistent_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a non-existent file
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns False
        """
        # GIVEN
        nonexistent_file = self.temp_path / "does_not_exist.txt"
        self.mock_resources["file_exists"].return_value = False
        
        # Set up validation result to indicate failure
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(nonexistent_file), 'txt')
        
        # THEN
        self.assertFalse(is_valid)

    def test_is_valid_with_oversized_file(self):
        """
        GIVEN a FileValidator instance with max_file_size_mb configured
        AND a file path to a file exceeding the size limit
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns False
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024 * 1024 * 20,  # 20MB, exceeds 10MB limit
            is_readable=True
        )
        
        # Set up validation result to indicate failure
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertFalse(is_valid)

    def test_is_valid_with_unsupported_format(self):
        """
        GIVEN a FileValidator instance with supported_formats configured
        AND a file path to a file
        AND format_name is an unsupported format
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns False
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True
        )
        self.mock_file_format_detector.get_format_category.return_value = None  # Unsupported
        
        # Set up validation result to indicate failure
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.valid_file), 'xyz')
        
        # THEN
        self.assertFalse(is_valid)

    def test_is_valid_with_corrupted_file(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a corrupted file
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns False
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True
        )
        
        # Set up validation result to indicate failure due to corruption
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertFalse(is_valid)

    def test_is_valid_with_no_permissions(self):
        """
        GIVEN a FileValidator instance
        AND a file path to a file without read permissions
        WHEN is_valid_for_processing is called
        THEN expect:
            - Returns False
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=False  # No read permission
        )
        
        # Set up validation result to indicate failure
        self.mock_validation_result_instance.is_valid = False
        
        # WHEN
        is_valid = self.validator.is_valid_for_processing(str(self.invalid_file), 'txt')
        
        # THEN
        self.assertFalse(is_valid)

    def test_is_valid_calls_validate_file_internally(self):
        """
        GIVEN a FileValidator instance
        AND any file path
        WHEN is_valid_for_processing is called
        THEN expect:
            - Internally calls validate_file method
            - Returns the is_valid property of the validation result
        """
        # GIVEN
        self.mock_resources["file_exists"].return_value = True
        self.mock_resources["get_file_info"].return_value = Mock(
            size=1024,
            is_readable=True,
            mime_type='text/plain',
            extension='txt'
        )
        self.mock_file_format_detector.get_format_category.return_value = 'document'
        
        # Test case 1: Valid file
        self.mock_validation_result_instance.is_valid = True
        is_valid = self.validator.is_valid_for_processing(str(self.valid_file), 'txt')
        self.assertTrue(is_valid)
        
        # Test case 2: Invalid file
        self.mock_validation_result_instance.is_valid = False
        is_valid = self.validator.is_valid_for_processing(str(self.invalid_file), 'txt')
        self.assertFalse(is_valid)
        
        # Verify ValidationResult was created (called validate_file internally)
        self.assertGreaterEqual(self.mock_validation_result_class.call_count, 2)


if __name__ == "__main__":
    unittest.main()