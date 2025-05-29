"""
Unified handler interface for the Omni-Converter.

This module provides an orchestration class for format handlers,
because re-using orchestration logic is dumb.
"""
import os
from typing import Any, Callable, Optional


from types_ import Configs, Content, Logger


class ContentExtractor:
    """
    Framework for extracting content from files.
    This class provides the logic for orchestrating format handlers

    Base implementation of a format handler without inheritance.
    
    Provides common functionality for format handlers.
    
    Attributes:
        resources (dict): Dictionary of resources and dependencies.
        configs (Configs): Configuration settings.
        format_parsers (dict): Parser functions for different formats.
    """
    
    def __init__(
        self,
        resources: dict[str, Callable] = None,
        configs: Optional[Configs] = None
    ):
        """
        Initialize a format handler.
        
        Args:
            resources: Dictionary of resources including parsers and services.
                Must contain:
                - handler_name: Name of the handler
                - supported_formats: set of formats supported by this handler
                - capabilities: Dictionary of handler capabilities
                - file_format_detector: Format detection utility
                - map_extension_to_format: Function to map extensions to formats
                - parsers: Dictionary of parser functions
            configs: Configuration settings.
        """
        # Store the original resources dictionary
        self.resources = resources
        self.configs = configs
        
        # Extract resources directly - fail fast if any are missing
        self._handler_name = self.resources["handler_name"]
        self._supported_formats = self.resources["supported_formats"]
        self._capabilities = self.resources["capabilities"]
        self._format_detector = self.resources["file_format_detector"]
        self._map_extension_to_format = self.resources["map_extension_to_format"]
        self._read_file = self.resources["read_file"]
        self._logger: Logger = self.resources["logger"]
        self._content: Content = self.resources["content"]
        
        # Initialize format parsers from resources
        self.format_parsers = {}
        if "parsers" in resources:
            for category, parsers in self.resources["parsers"].items():
                self.format_parsers.update(parsers)
    
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if extractor can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        self._logger.debug(f"Checking if handler '{self._handler_name}' can handle file: {file_path}\nformat_name: {format_name}")

        if format_name:
            # If format is provided, check against supported formats
            if format_name in self._supported_formats:
                self._logger.debug(f"Handler '{self._handler_name}' can handle file: {file_path}")
                return True
            else:
                self._logger.debug(f"Handler '{self._handler_name}' cannot handle file: {file_path}\nHandler supports: {self.supported_formats}")
                return False
        else:
            # Otherwise, validate input and try to determine format
            self._logger.debug(f"Format name not provided. Validating input for handler '{self._handler_name}'")
            return self.validate_input(file_path)
    
    def extract_content(self, file_path: str, options: Optional[dict[str, Any]] = None) -> Content:
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
            raise ValueError(f"File is not valid for handler: {self._handler_name}")
        
        # Extract content
        return self.do_extraction(file_path, options or {})
    
    @property
    def capabilities(self) -> dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        return {
            'handler_name': self._handler_name,
            'supported_formats': list(self._supported_formats),
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
        self._logger.debug(f"Validating input '{file_path}' for handler '{self._handler_name}'")
        
        try:
            self._logger.debug(f"Detecting format for file: {file_path}")
            format_name, _ = self._format_detector.detect_format(file_path)
            if format_name in self._supported_formats:
                return True
            else:
                return False
        except Exception as e:
            self._logger.exception(f"Error detecting format for file '{file_path}': {e}")
            return False

    def do_extraction(self, file_path: str, options: dict[str, Any]) -> Content:
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
        # Detect format if not provided in options
        format_name = options.get('format')
        if not format_name:
            format_name, _ = self._format_detector.detect_format(file_path)
            
            # Override format detection based on file extension if needed
            if not format_name:
                _, ext = os.path.splitext(file_path)
                # Map extension to format
                format_name = self._map_extension_to_format(ext)

        # Verify format is supported
        if not format_name or format_name not in self._supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")

        # Get parser for this format
        parser = self.format_parsers.get(format_name)
        if not parser:
            raise ValueError(f"No parser available for format: {format_name}")
        
        self._logger.debug(f"Extracting content from {format_name} file: {file_path}")

        # Get file content - use binary mode by default
        file_content = self._read_file(file_path, 'rb')

        # Ensure file_path is included in options for processors that need it
        processor_options = dict(options)
        processor_options["file_path"] = file_path
        processor_options["format"] = format_name

        try:  # Extract content using the parser
            text, metadata, sections = parser(file_content, processor_options)
            
            # Create content object
            content = self._content(
                text=text,
                metadata=metadata,
                sections=sections,
                source_format=format_name,
                source_path=file_path
            )
            
            return content

        except Exception as e:
            self._logger.error(f"Error extracting content from {format_name}: {file_path}\n{e}")
            raise
