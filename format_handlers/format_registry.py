"""
Format registry for the Omni-Converter using IoC pattern.

This module provides a centralized registry for format handlers using dependency injection,
making it easy to find the appropriate handler for a given file format.
"""
import os
from typing import Any, Callable, Dict, List, Optional, Set, Union

from configs import Configs
from logger import logger
from core.format_detector import format_detector
from format_handlers.unified_handler import BaseFormatHandler, Content, map_extension_to_format


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
    
    def __init__(self, resources: Dict[str, Any], configs: Optional[Configs] = None) -> None:
        """
        Initialize the format registry with injected dependencies.
        
        Args:
            resources: Dictionary containing:
                - handler_factories: Dict mapping handler types to factory functions
                - format_detector: Utility for detecting file formats
                - ext_to_format: Function to map extensions to formats
            configs: Configuration settings.
        """
        self.resources = resources
        self.configs = configs
        
        # Extract key resources
        self.format_detector = resources["format_detector"]
        self.ext_to_format = resources["ext_to_format"]
        self.handler_factories = resources["handler_factories"]
        
        # Initialize internal state
        self.handlers: Dict[str, BaseFormatHandler] = {}
        self.format_to_handler_map: Dict[str, str] = {}
        
        # Create and register handlers from factories
        self._register_handlers_from_factories()
    
    def _register_handlers_from_factories(self) -> None:
        """Create and register handlers using the provided factories."""
        logger.info("Registering format handlers from factories")
        
        for handler_type, factory in self.handler_factories.items():
            try:
                # Create handler using the factory function
                handler = factory(self.resources, self.configs)
                
                # Register the handler
                self.register_handler(handler)
                logger.debug(f"Created and registered handler: {handler_type}")
            except Exception as e:
                logger.error(f"Failed to create handler '{handler_type}': {e}")
    
    def register_handler(self, handler: BaseFormatHandler) -> None:
        """
        Register a format handler.
        
        Args:
            handler: The handler to register.
        """
        # Get handler name and capabilities
        handler_name = handler.handler_name
        capabilities = handler.capabilities
        
        if not handler_name:
            logger.warning("Attempted to register handler without a name")
            return
        
        # Register handler by name
        self.handlers[handler_name] = handler
        
        # Register formats
        supported_formats = capabilities.get('supported_formats', [])
        for format_name in supported_formats:
            self.register_format(format_name, handler_name)
        
        logger.info(f"Registered handler: {handler_name}", {'formats': supported_formats})
    
    def register_format(self, format_name: str, handler_name: str) -> None:
        """
        Register a format to be handled by a specific handler.
        
        Args:
            format_name: The format to register.
            handler_name: The name of the handler.
        """
        if handler_name not in self.handlers:
            logger.warning(f"Attempted to register format {format_name} to unknown handler: {handler_name}")
            return
        
        self.format_to_handler_map[format_name] = handler_name
        logger.debug(f"Registered format: {format_name} -> {handler_name}")
    
    def get_handler(self, format_name: str) -> Optional[BaseFormatHandler]:
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
    
    def get_handler_for_file(self, file_path: str) -> Optional[BaseFormatHandler]:
        """
        Get the appropriate handler for a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The handler for the file, or None if no handler is found.
        """
        # First try to detect the format
        format_name, _ = self.format_detector.detect_format(file_path)
        
        # If format detection fails, try using file extension
        if not format_name:
            _, ext = os.path.splitext(file_path)
            # Map extension to format
            format_name = self.ext_to_format(ext.lower().lstrip('.'))
        
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
    
    def extract_content(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Content:
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
    def supported_formats(self) -> List[str]:
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
    
    def get_formats_by_category(self) -> Dict[str, List[str]]:
        """
        Get formats grouped by category.
        
        Returns:
            A dictionary mapping categories to lists of formats.
        """
        categories: Dict[str, List[str]] = {}
        
        for format_name, handler_name in self.format_to_handler_map.items():
            handler = self.handlers.get(handler_name)
            if not handler:
                continue
            
            category = handler.capabilities.get('category', 'unknown')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(format_name)
        
        return categories


def create_format_registry(resources: Dict[str, Any], configs: Optional[Configs] = None) -> FormatRegistry:
    """
    Create a format registry with the specified resources and configuration.
    
    Args:
        resources: Dictionary of resources including handler factories.
        configs: Configuration settings.
        
    Returns:
        Configured FormatRegistry instance.
    """
    # Ensure required resources are present
    required_resources = {
        "format_detector": format_detector,
        "ext_to_format": map_extension_to_format,
        "handler_factories": {},  # Will be populated with actual factories
    }
    
    # Merge provided resources with required ones
    registry_resources = {**required_resources}
    if resources:
        registry_resources.update(resources)
    
    # Create and return the registry
    return FormatRegistry(registry_resources, configs)
