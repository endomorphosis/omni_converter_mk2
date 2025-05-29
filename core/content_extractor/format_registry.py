"""
Format registry for the Omni-Converter using IoC pattern.

This module provides a centralized registry for format handlers using dependency injection,
making it easy to find the appropriate handler for a given file format.
"""
import os
from typing import Any, Callable, Optional


from content_extractor.content_extractor import ContentExtractor

from types_ import Configs, Content, Logger


class FormatRegistry:
    """
    Registry for format handlers using IoC pattern.
    
    The registry maintains mappings between file formats and the handlers that can process them.
    It provides a central point for finding appropriate handlers for a given file.
    
    Attributes:
        resources (dict): Resources and dependencies for the registry.
        configs (Configs): Configuration settings.
        handlers (dict): Dictionary of handlers keyed by handler name.
        format_to_handler_map (dict): Mapping from format name to handler name.
    """
    
    def __init__(self, 
                 resources: dict[str, Callable] = None, 
                 configs: Configs= None
                 ) -> None:
        """
        Initialize the format registry with injected dependencies.
        
        Args:
            resources: Dictionary containing:
                - handler_factories: dict mapping handler types to factory functions
                - file_format_detector: Utility for detecting file formats
                - map_extension_to_format: Function to map extensions to formats
            configs: Configuration settings.
        """
        self.resources = resources
        self.configs = configs
        
        # Extract key resources
        self._file_format_detector = resources["file_format_detector"]
        self._ext_to_format = resources["map_extension_to_format"]
        self._handler_factories = resources["handler_factories"]
        self._processors = resources["processors"]
        self._logger: Logger = resources["logger"]
        
        # Initialize internal state
        self.handlers: dict[str, ContentExtractor] = {}
        self.format_to_handler_map: dict[str, str] = {}
        
        # Create and register handlers from factories
        self._register_handlers_from_factories()
    
    def _register_handlers_from_factories(self) -> None:
        """Create and register handlers using the provided factories."""
        self._logger.info("Registering format handlers from factories")
        
        for handler_type, factory in self._handler_factories.items():
            try:
                # Create handler using the factory function
                handler = factory(self.resources, self.configs)
                
                # Register the handler
                self.register_handler(handler)
                self._logger.debug(f"Created and registered handler: {handler_type}")
            except Exception as e:
                self._logger.error(f"Failed to create handler '{handler_type}': {e}")
    
    def register_handler(self, handler: ContentExtractor) -> None:
        """
        Register a format handler.
        
        Args:
            handler: The handler to register.
        """
        # Get handler name and capabilities
        handler_name = handler.handler_name
        capabilities = handler.capabilities
        
        if not handler_name:
            self._logger.warning("Attempted to register handler without a name")
            return
        
        # Register handler by name
        self.handlers[handler_name] = handler
        
        # Register formats
        supported_formats = capabilities.get('supported_formats', [])
        for format_name in supported_formats:
            self.register_format(format_name, handler_name)
        
        self._logger.info(f"Registered handler: {handler_name}", {'formats': supported_formats})
    
    def register_format(self, format_name: str, handler_name: str) -> None:
        """
        Register a format to be handled by a specific handler.
        
        Args:
            format_name: The format to register.
            handler_name: The name of the handler.
        """
        if handler_name not in self.handlers:
            self._logger.warning(f"Attempted to register format {format_name} to unknown handler: {handler_name}")
            return
        
        self.format_to_handler_map[format_name] = handler_name
        self._logger.debug(f"Registered format: {format_name} -> {handler_name}")
    
    def get_handler(self, format_name: str) -> Optional[ContentExtractor]:
        """
        Get the handler for a specific format.
        
        Args:
            format_name: The format to get the handler for.
            
        Returns:
            The handler for the format, or None if no handler is found.
        """
        handler_name = self.format_to_handler_map.get(format_name)
        if not handler_name:
            return None
        
        return self.handlers.get(handler_name)
    
    def get_handler_for_file(self, file_path: str) -> Optional[ContentExtractor]:
        """
        Get the appropriate handler for a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The handler for the file, or None if no handler is found.
        """
        # First try to detect the format
        format_name, _ = self._file_format_detector.detect_format(file_path)
        
        # If format detection fails, try using file extension
        if not format_name:
            _, ext = os.path.splitext(file_path)
            # Map extension to format
            format_name = self._ext_to_format(ext.lower().lstrip('.'))
        
        if not format_name:
            return None
        
        # Get handler for the format
        handler = self.get_handler(format_name)
        
        # If no handler is found, try to find a handler that can handle the file
        if not handler:
            for h in self.handlers.values():
                if h.can_handle(file_path, format_name):
                    handler = h
                    break
        
        return handler
    
    def extract_content(self, file_path: str, options: Optional[dict[str, Any]] = None) -> Content:
        """
        Extract content from a file using the appropriate handler.
        
        Args:
            file_path: The path to the file.
            options: Optional extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If no handler is found for the file.
            Exception: If an error occurs during extraction.
        """
        handler = self.get_handler_for_file(file_path)
        
        if not handler:
            raise ValueError(f"No handler found for file: {file_path}")
        
        return handler.extract_content(file_path, options or {})
    
    @property
    def supported_formats(self) -> list[str]:
        """
        Get all supported formats.
        
        Returns:
            A list of supported formats.
        """
        return list(self.format_to_handler_map.keys())
    
    def is_format_supported(self, format_name: str) -> bool:
        """
        Check if a format is supported.
        
        Args:
            format_name: The format to check.
            
        Returns:
            True if the format is supported, False otherwise.
        """
        return format_name in self.format_to_handler_map
    
    def get_formats_by_category(self) -> dict[str, list[str]]:
        """
        Get formats grouped by category.
        
        Returns:
            A dictionary mapping categories to lists of formats.
        """
        categories: dict[str, list[str]] = {}
        
        for format_name, handler_name in self.format_to_handler_map.items():
            handler = self.handlers.get(handler_name)
            if not handler:
                continue
            
            category = handler.capabilities.get('category', 'unknown')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(format_name)
        
        return categories



