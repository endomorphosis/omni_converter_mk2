"""
Application format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for application-based formats like PDF, JSON, DOCX, XLSX, and ZIP
using dependency injection for better modularity and testability, without inheritance.
"""
import os
from typing import Any, Callable, Optional


from types_ import Configs, Logger


class ApplicationHandler:
    """
    Framework class for handling application-based formats using IoC pattern.
    
    This class only contains orchestration logic and delegates all format-specific
    processing to injected processors via the resources dictionary.
    """
    
    def __init__(self, 
                 resources: dict[str, Callable], 
                 configs: Configs
                 ):
        """
        Initialize the application handler with injected dependencies.
        
        Args:
            resources: Dictionary of callable resources including processors and utilities.
            configs: Configuration settings.
        """
        self.resources = resources
        self.configs = configs

        # Extract required resources - fail fast if missing
        self._pdf_processor: Callable = self.resources["pdf_processor"]
        self._json_processor: Callable = self.resources["json_processor"]
        self._docx_processor: Callable = self.resources["docx_processor"]
        self._xlsx_processor: Callable = self.resources["xlsx_processor"]
        self._zip_processor: Callable = self.resources["zip_processor"]
        self._logger: Logger = self.resources["logger"]

        self._format_extensions: dict = self.resources["format_extensions"]
        self._supported_formats: set = self.resources["supported_formats"]
        self._capabilities: dict = self.resources["capabilities"]

    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file format.
        
        Args:
            file_path: Path to the file.
            format_name: Format of the file, if known.
            
        Returns:
            True if this handler can process the format, False otherwise.
        """
        if format_name:
            return format_name in self._supported_formats
        
        # If no format provided, check file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        for format_type, extensions in self._format_extensions.items():
            if ext in extensions and format_type in self._supported_formats:
                return True
        
        return False
    
    def extract_content(self, file_path: str, format_name: str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """
        Extract content from an application file using the appropriate processor.
        
        Args:
            file_path: Path to the file.
            format_name: Format of the file.
            options: Processing options.
            
        Returns:
            Tuple of (text content, metadata, sections).
        """
        # Delegate to appropriate processor based on format
        match format_name:
            case 'pdf':
                processor = self._pdf_processor
            case 'json':
                processor = self._json_processor
            case 'docx':
                processor = self._docx_processor
            case 'xlsx':
                processor = self._xlsx_processor
            case 'zip':
                processor = self._zip_processor
            case _:
                raise ValueError(f"Unsupported application format: {format_name}")
        
        try:
            # Call the processor function
            return processor(file_path, options)
        except Exception as e:
            self._logger.error(f"Error processing {format_name} file '{file_path}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to process {format_name} file: {file_path}") from e

    @property
    def capabilities(self) -> dict[str, Any]:
        """Get handler capabilities."""
        return self._capabilities


