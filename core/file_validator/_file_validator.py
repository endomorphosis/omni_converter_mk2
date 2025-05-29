"""
Validation module for the Omni-Converter.

This module provides validation functionality for files and formats.
"""
from typing import Callable, Optional

from configs import Configs
from core.file_validator._validation_result import ValidationResult

from utils.filesystem import FileSystem


from types_ import Logger


class FileValidator:
    """
    File validator for the Omni-Converter.
    
    Validates files for processing, checking for issues like:
    - File exists and is readable
    - File size is within limits
    - File format is supported
    - File is not corrupted
    """

    def __init__(self,
                 resources: dict[str, Callable] = None, 
                 configs: Configs = None
                 ):
        """Initialize the basic validator."""
        self.configs = configs
        self.resources = resources

        # Load validation rules from config
        self.max_file_size_mb: int = self.configs.get_config_value('security.max_file_size_mb', 100)
        self.allowed_formats: list[str] = self.configs.get_config_value('security.allowed_formats', [])

        self._file_exists: Callable = self.resources['file_exists']
        self._get_file_info: Callable = self.resources['get_file_info']
        self._validation_result: Callable = self.resources['validation_result']
        self._format_detector = self.resources['file_format_detector']
        self._logger: Logger = self.resources['logger']


    def validate_file(self, file_path: str, format_name: Optional[str] = None) -> ValidationResult:
        """
        Validate a file for processing.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known. Will be detected if not provided.
            
        Returns:
            A validation result.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        # Create validation result
        result = self._validation_result()
        
        try:
            # Check if file exists
            if not self._file_exists(file_path):
                result.add_error(f"File does not exist: {file_path}")
                return result
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            # Check if file is readable
            if not file_info.is_readable:
                result.add_error(f"File is not readable: {file_path}")
                return result
            
            # Check file size
            max_size_bytes = self.max_file_size_mb * 1024 * 1024
            if file_info.size > max_size_bytes:
                result.add_error(
                    f"File size ({file_info.size} bytes) exceeds maximum allowed "
                    f"({max_size_bytes} bytes): {file_path}"
                )
                return result
            
            # Detect format if not provided
            if not format_name:
                format_name, category = self._format_detector.detect_format(file_path)
                if not format_name:
                    result.add_error(f"Unable to detect format for file: {file_path}")
                    return result
                
                result.add_context('format', format_name)
                result.add_context('category', category)
            else:
                # Check if provided format is supported
                category = self._format_detector.get_format_category(format_name)
                if not category:
                    result.add_error(f"Format '{format_name}' is not supported")
                    return result
                
                result.add_context('format', format_name)
                result.add_context('category', category)
            
            # Check if format is allowed
            if self.allowed_formats and format_name not in self.allowed_formats:
                result.add_error(f"Format '{format_name}' is not allowed")
                return result
            
            # Check for file corruption (basic check only)
            # In a real implementation, this would do more thorough checks
            if file_info.size == 0:
                result.add_error(f"File is empty: {file_path}")
                return result
            
            # Add file metadata to result
            result.add_context('file_size', file_info.size)
            result.add_context('mime_type', file_info.mime_type)
            result.add_context('extension', file_info.extension)
            
            # All checks passed
            result.is_valid = True
            
        except Exception as e:
            result.add_error(f"Validation error: {e}")
            self._logger.error(f"Validation error for file: {file_path}", {'error': str(e)})
        
        return result
    
    def is_valid_for_processing(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if a file is valid for processing.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known. Will be detected if not provided.
            
        Returns:
            True if the file is valid for processing, False otherwise.
        """
        result = self.validate_file(file_path, format_name)
        return result.is_valid
    
    def get_validation_errors(self, file_path: str, format_name: Optional[str] = None) -> list[str]:
        """
        Get validation errors for a file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known. Will be detected if not provided.
            
        Returns:
            A list of validation errors.
        """
        result = self.validate_file(file_path, format_name)
        return result.errors

# Factory function is now in core/factory.py to maintain separation of concerns

def make_file_validator() -> FileValidator:... # TODO