"""
Format registry for the Omni-Converter.

This module provides a centralized registry for format handlers, making it easy to
find the appropriate handler for a given file format.
"""

import os
from typing import Any, Dict, List, Optional, Set, Type, Union

from utils.logger import logger
from utils.format_detector import format_detector
from format_handlers.base_handler import FormatHandler, Content
from format_handlers.text_handler import text_handler
from format_handlers.image_handler import image_handler
from format_handlers.application_handler import application_handler
from format_handlers.audio_handler import audio_handler
from format_handlers.video_handler import video_handler


class FormatRegistry:
    """
    Registry for format handlers.
    
    The registry maintains mappings between file formats and the handlers that can process them.
    It provides a central point for finding appropriate handlers for a given file.
    
    Attributes:
        handlers (dict): Dictionary of handlers keyed by handler name.
        format_to_handler_map (dict): Mapping from format name to handler name.
    """
    
    def __init__(self, configs=None,resources=None):
        """Initialize the format registry."""
        self.handlers: Dict[str, FormatHandler] = {}
        self.format_to_handler_map: Dict[str, str] = {}
        
        # Register default handlers
        self._register_default_handlers(resources)
    
    def _register_default_handlers(self, resources: dict[str, Any]) -> None:
        """Register the default format handlers."""
        for handler in resources['handlers'].values():
            if not isinstance(handler, FormatHandler):
                logger.warning(f"Handler {handler} is not a valid FormatHandler")
                continue
            self.register_handler(handler)

    def register_handler(self, handler: FormatHandler) -> None:
        """
        Register a format handler.
        
        Args:
            handler: The handler to register.
        """
        capabilities = handler.get_capabilities()
        handler_name = capabilities.get('handler_name')
        
        if not handler_name:
            logger.warning("Attempted to register handler without a name")
            return
        
        # Register handler by name
        self.handlers[handler_name] = handler
        
        # Register formats
        supported_formats = capabilities.get('supported_formats', [])
        for format_name in supported_formats:
            self.register_format(format_name, handler_name)
        
        logger.info(f"Registered handler: {handler_name}", 
                   {'formats': supported_formats})
    
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
    
    def get_handler(self, format_name: str) -> Optional[FormatHandler]:
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
    
    def get_handler_for_file(self, file_path: str) -> Optional[FormatHandler]:
        """
        Get the appropriate handler for a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The handler for the file, or None if no handler is found.
        """
        # First try to detect the format
        format_name, _ = format_detector.detect_format(file_path)
        
        # If format detection fails, try using file extension
        if not format_name:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            # Map common extensions to formats
            ext_to_format = {
                'html': 'html', 'htm': 'html', 
                'xml': 'xml',
                'txt': 'text', 'text': 'text',
                'csv': 'csv',
                'ics': 'calendar',
                'jpg': 'jpeg', 'jpeg': 'jpeg', 
                'png': 'png', 
                'gif': 'gif',
                'webp': 'webp',
                'svg': 'svg',
                'pdf': 'pdf',
                'json': 'json',
                'docx': 'docx',
                'xlsx': 'xlsx',
                'zip': 'zip',
                'mp3': 'mp3',
                'wav': 'wav', 'wave': 'wav',
                'ogg': 'ogg', 'oga': 'ogg',
                'flac': 'flac',
                'aac': 'aac', 'm4a': 'aac',
                'mp4': 'mp4', 'm4v': 'mp4',
                'webm': 'webm',
                'avi': 'avi',
                'mkv': 'mkv',
                'mov': 'mov', 'qt': 'mov'
            }
            format_name = ext_to_format.get(ext)
        
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
        
        return handler.extract_content(file_path, options)
    
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
            
            capabilities = handler.get_capabilities()
            category = capabilities.get('category', 'unknown')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(format_name)
        
        return categories

resources = {
    "handlers": {
        "text": text_handler,
        "image": image_handler,
        "application": application_handler,
        "audio": audio_handler,
        "video": video_handler
    }
}

# Global format registry instance
format_registry = FormatRegistry(resources=resources)