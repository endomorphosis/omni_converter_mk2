"""
Content extractor module for the Omni-Converter.

This module provides the ContentExtractor class for extracting content from files
based on their format.
"""

from typing import Any, Dict, Optional

from format_handlers.base_handler import Content
from format_handlers.format_registry import format_registry
from utils.logger import logger


class ContentExtractor:
    """
    Content extractor for the Omni-Converter.
    
    This class extracts content from files based on their format using the
    appropriate handler from the format registry.
    
    Attributes:
        registry: The format registry to use for extraction.
    """
    
    def __init__(self, registry=None):
        """
        Initialize a content extractor.
        
        Args:
            registry: The format registry to use for extraction. If None, the global
                registry will be used.
        """
        self.registry = registry or format_registry
    
    def extract_content(
        self, file_path: str, format_name: Optional[str] = None, options: Optional[Dict[str, Any]] = None
    ) -> Content:
        """
        Extract content from a file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known. If None, the format will be
                detected automatically.
            options: Optional extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If the file format is not supported.
            Exception: If an error occurs during extraction.
        """
        logger.debug(f"Extracting content from {file_path}", {'format': format_name})
        
        # If format is provided, use it; otherwise it will be detected by the registry
        if format_name:
            # Get handler for the specified format
            handler = self.registry.get_handler(format_name)
            if not handler:
                raise ValueError(f"No handler found for format: {format_name}")
            
            return handler.extract_content(file_path, options or {})
        else:
            # Use the registry to find the appropriate handler and extract content
            return self.registry.extract_content(file_path, options or {})
    
    def get_extraction_capabilities(self) -> Dict[str, Any]:
        """
        Get the extraction capabilities.
        
        Returns:
            A dictionary of extraction capabilities, such as supported formats.
        """
        # Get formats grouped by category
        formats_by_category = self.registry.get_formats_by_category()
        
        # Build capabilities dictionary
        capabilities = {
            'supported_formats': self.registry.get_supported_formats(),
            'categories': list(formats_by_category.keys()),
            'formats_by_category': formats_by_category
        }
        
        return capabilities
    
    def register_format_handler(self, format_name: str, handler_name: str) -> None:
        """
        Register a format handler.
        
        Args:
            format_name: The format to register.
            handler_name: The name of the handler to register for the format.
        """
        self.registry.register_format(format_name, handler_name)
        logger.debug(f"Registered handler for format: {format_name}", {'handler': handler_name})