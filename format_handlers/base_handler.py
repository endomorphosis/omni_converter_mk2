"""
Base handler interface for the Omni-Converter.

This module provides the base interface and abstract classes for format handlers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union


class Content:
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
    
    def __init__(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
        source_format: Optional[str] = None,
        source_path: Optional[str] = None
    ):
        """
        Initialize content.
        
        Args:
            text: The extracted text content.
            metadata: Metadata about the content.
            sections: Sections of the content (if applicable).
            source_format: The format of the source file.
            source_path: The path to the source file.
        """
        self.text = text
        self.metadata = metadata or {}
        self.sections = sections or []
        self.source_format = source_format or ""
        self.source_path = source_path or ""
        self.extraction_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the content.
        """
        return {
            'text': self.text,
            'metadata': self.metadata,
            'sections': self.sections,
            'source_format': self.source_format,
            'source_path': self.source_path,
            'extraction_time': self.extraction_time.isoformat()
        }


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
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
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
        supported_formats: Optional[Set[str]] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a format handler.
        
        Args:
            handler_name: The name of the handler.
            supported_formats: Formats supported by this handler.
            capabilities: Capabilities of this handler.
        """
        self.handler_name = handler_name
        self.supported_formats = supported_formats or set()
        self.capabilities = capabilities or {}
    
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
        if format_name:
            return format_name in self.supported_formats
        
        # Otherwise, validate input and try to determine format
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
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        return {
            'handler_name': self.handler_name,
            'supported_formats': list(self.supported_formats),
            **self.capabilities
        }
    
    def validate_input(self, file_path: str) -> bool:
        """
        Validate that the file can be processed by this handler.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file is valid for this handler, False otherwise.
        """
        # This is a basic implementation, subclasses should override
        from utils.format_detector import format_detector
        
        try:
            format_name, _ = format_detector.detect_format(file_path)
            return format_name in self.supported_formats
        except Exception:
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