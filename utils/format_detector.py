"""
Format detection module for the Omni-Converter.

This module provides functionality for detecting the format of files.
"""

import os
import magic
import mimetypes
from typing import Dict, List, Optional, Set, Tuple, Any


import pydantic
from pydantic import BaseModel


from utils.configs import configs, Configs
from utils.filesystem import FileInfo, FileSystem
from utils.logger import logger
from .constants import FORMAT_SIGNATURES, FORMAT_EXTENSIONS


class FormatDetector:
    """
    Format detector for the Omni-Converter.
    
    Detects the format of files based on their content and extension.
    """

    def __init__(self, 
                 resources: Dict[str, Any] = None, 
                 configs: Configs = None
                 ) -> None:
        """
        Initialize the format detector.
        Args:
            resources: A dictionary of Callables.
            configs: A pydantic model with configurations from configs.yaml.
        """
        self.configs = configs or {}
        self.resources = resources

        # Load format registry from config
        self.format_registry = configs.get_config_value('formats', {})

        self.format_signatures: Dict[str, str] = self.resources['format_signatures']
        self.format_extensions: Dict[str, str] = self.resources['format_extensions']
        
        # Initialize format signatures
        self._init_format_signatures()
        
        # Initialize format extensions
        self._init_format_extensions()
    
    def _init_format_signatures(self) -> None:
        """Initialize the format signatures."""
        self.format_signatures = FORMAT_SIGNATURES.copy()

    
    def _init_format_extensions(self) -> None:
        """Initialize the format extensions."""
        # Map of extensions to formats

    
    def detect_format(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect the format of a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            A tuple of (format, category) if the format is detected, (None, None) otherwise.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
        """
        # Ensure the path is absolute
        file_path = os.path.abspath(file_path)
        
        # Get file information
        file_info = FileSystem.get_file_info(file_path)
        
        # Try to detect format based on MIME type
        format_name = self.format_signatures.get(file_info.mime_type)
        
        # If MIME type detection failed, try extension
        if not format_name:
            extension = file_info.extension.lower()
            format_name = self.format_extensions.get(extension)
        
        # If format detection failed entirely, return None
        if not format_name:
            logger.warning(f"Format detection failed for file: {file_path}", 
                           {'mime_type': file_info.mime_type, 'extension': file_info.extension})
            return None, None
        
        # Find the category for this format
        category = self._get_category_for_format(format_name)
        
        # If the category is not found, this is an unsupported format
        if not category:
            logger.warning(f"Format '{format_name}' is not in any supported category for file: {file_path}")
            return format_name, None
        
        logger.debug(f"Detected format '{format_name}' in category '{category}' for file: {file_path}")
        return format_name, category
    
    def _get_category_for_format(self, format_name: str) -> Optional[str]:
        """
        Get the category for a format.
        
        Args:
            format_name: The format name.
            
        Returns:
            The category if found, None otherwise.
        """
        for category, formats in self.format_registry.items():
            if format_name in formats:
                return category
        return None

    @property
    def supported_formats(self) -> Dict[str, List[str]]:
        """
        Get the supported formats.
        
        Returns:
            A dictionary of categories to lists of supported formats.
        """
        return self.format_registry
    
    def is_format_supported(self, format_name: str) -> bool:
        """
        Check if a format is supported.
        
        Args:
            format_name: The format name.
            
        Returns:
            True if the format is supported, False otherwise.
        """
        return self._get_category_for_format(format_name) is not None
    
    def get_format_category(self, format_name: str) -> Optional[str]:
        """
        Get the category for a format.
        
        Args:
            format_name: The format name.
            
        Returns:
            The category if the format is supported, None otherwise.
        """
        return self._get_category_for_format(format_name)

resources = {
    "format_signatures": FORMAT_SIGNATURES,
    "format_extensions": FORMAT_EXTENSIONS
}


# Global format detector instance
format_detector = FormatDetector(resources=resources, configs=configs)
