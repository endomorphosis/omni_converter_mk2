"""
Base handler interface for the Omni-Converter.

This module provides the base interface and abstract classes for format handlers.
"""
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Set, Union


from pydantic import BaseModel, Field
from pydantic.types import PastDatetime


from logger import logger


class Content(BaseModel):
    """
    Content extracted from a file.
    
    Attributes:
        text (str): The extracted text content.
        metadata (dict): Metadata about the content.
        sections (list): Sections of the content (if applicable).
        source_format (str): The format of the source file.
        source_path (str): The path to the source file.
        extraction_time (datetime): The time the content was extracted.
    """
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    source_format: str = ""
    source_path: str = ""
    extraction_time: PastDatetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the content.
        """
        # Use Pydantic's model_dump with custom handling for datetime
        data = self.model_dump()
        data['extraction_time'] = self.extraction_time.isoformat()
        return data

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class FormatHandler(ABC):
    """
    Base interface for format handlers.
    
    Format handlers are responsible for extracting content from files of specific formats.
    """
    
    @abstractmethod
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        pass
    
    @abstractmethod
    def extract_content(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Content:
        """
        Extract content from a file.
        
        Args:
            file_path: The path to the file.
            options: Optional extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If the file is not valid for this handler.
            Exception: If an error occurs during extraction.
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        pass


class BaseFormatHandler(FormatHandler):
    """
    Base implementation of a format handler.
    
    Provides common functionality for format handlers.
    
    Attributes:
        handler_name (str): The name of the handler.
        supported_formats (set): Formats supported by this handler.
        capabilities (dict): Capabilities of this handler.
    """
    
    def __init__(
        self,
        handler_name: str,
        supported_formats: Optional[Set[str]] = set(),
        capabilities: Optional[Dict[str, Any]] = {}
    ):
        """
        Initialize a format handler.
        
        Args:
            handler_name: The name of the handler.
            supported_formats: Formats supported by this handler.
            capabilities: Capabilities of this handler.
        """
        self.handler_name = handler_name
        self.supported_formats = supported_formats
        self._capabilities = capabilities
    
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        # If format is provided, check if it's supported
        logger.debug(f"Checking if handler '{self.handler_name}' can handle file: {file_path}\nformat_name: {format_name}")

        if format_name:
            # If format is provided, check against supported formats
            logger.debug(f"Handler '{self.handler_name}' supports formats: {self.supported_formats}")
            return format_name in self.supported_formats
        
        # Otherwise, validate input and try to determine format
        logger.debug(f"Name not provided. Validating input for handler '{self.handler_name}'")
        return self.validate_input(file_path)
    
    def extract_content(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Content:
        """
        Extract content from a file.
        
        Args:
            file_path: The path to the file.
            options: Optional extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If the file is not valid for this handler.
            Exception: If an error occurs during extraction.
        """
        # Validate input
        if not self.validate_input(file_path):
            raise ValueError(f"File is not valid for handler: {self.handler_name}")
        
        # Extract content
        return self.do_extraction(file_path, options or {})
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        return {
            'handler_name': self.handler_name,
            'supported_formats': list(self.supported_formats),
            **self._capabilities
        }
    
    def validate_input(self, file_path: str) -> bool:
        """
        Validate that the file can be processed by this handler.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file is valid for this handler, False otherwise.
        """
        # TODO - Implement format detection logic
        # This is a basic implementation, subclasses should override
        from file_format_detector.file_format_detector import format_detector
        logger.debug(f"Validating input '{file_path}' for handler '{self.handler_name}'")
        
        try:
            logger.debug(f"Detecting format for file: {file_path}")
            format_name, _ = format_detector.detect_format(file_path)
            return format_name in self.supported_formats
        except Exception as e:
            logger.exception(f"Error detecting format for file '{file_path}': {e}")
            return False
    
    @abstractmethod
    def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
        """
        Perform the actual extraction of content from a file.
        
        Args:
            file_path: The path to the file.
            options: Extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            Exception: If an error occurs during extraction.
        """
        pass
