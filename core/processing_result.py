"""
Processing result module for the Omni-Converter.

This module provides the ProcessingResult class for tracking the result of processing a file.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ProcessingResult:
    """
    Result of processing a file.
    
    This class represents the result of processing a file, including success status,
    file paths, errors, and metadata.
    
    Attributes:
        success (bool): Whether the processing was successful.
        file_path (str): The path to the input file.
        output_path (str): The path to the output file.
        format (str): The detected format of the input file.
        errors (List[str]): List of errors encountered during processing.
        metadata (Dict[str, Any]): Metadata about the processing.
        content_hash (str): Hash of the content for verification.
        timestamp (datetime): Time when the processing was completed.
    """
    
    def __init__(
        self,
        success: bool,
        file_path: str,
        output_path: Optional[str] = None,
        format: Optional[str] = None,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_hash: Optional[str] = None
    ):
        """
        Initialize a processing result.
        
        Args:
            success: Whether the processing was successful.
            file_path: The path to the input file.
            output_path: The path to the output file.
            format: The detected format of the input file.
            errors: List of errors encountered during processing.
            metadata: Metadata about the processing.
            content_hash: Hash of the content for verification.
        """
        self.success = success
        self.file_path = file_path
        self.output_path = output_path or ""
        self.format = format or ""
        self.errors = errors or []
        self.metadata = metadata or {}
        self.content_hash = content_hash or ""
        self.timestamp = datetime.now()
    
    def add_error(self, error: str) -> None:
        """
        Add an error to the result.
        
        Args:
            error: The error message to add.
        """
        self.errors.append(error)
        self.success = False
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the result.
        
        Args:
            key: The metadata key.
            value: The metadata value.
        """
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the processing result.
        """
        return {
            'success': self.success,
            'file_path': self.file_path,
            'output_path': self.output_path,
            'format': self.format,
            'errors': self.errors,
            'metadata': self.metadata,
            'content_hash': self.content_hash,
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_error_string(self) -> str:
        """
        Get the errors as a formatted string.
        
        Returns:
            A formatted string of errors.
        """
        if not self.errors:
            return "No errors"
        
        return "\n".join(f"- {error}" for error in self.errors)
    
    def __str__(self) -> str:
        """
        Get a string representation of the result.
        
        Returns:
            A string representation of the processing result.
        """
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"Processing {self.file_path} - {status}\n"
            f"Output: {self.output_path or 'None'}\n"
            f"Format: {self.format or 'Unknown'}\n"
            f"Errors: {self.get_error_string()}\n"
            f"Timestamp: {self.timestamp.isoformat()}"
        )