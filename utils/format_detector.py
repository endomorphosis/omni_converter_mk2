"""
Format detection module for the Omni-Converter.

This module provides functionality for detecting the format of files.
"""

import os
import magic
import mimetypes
from typing import Dict, List, Optional, Set, Tuple, Any

from utils.config import config_manager
from utils.filesystem import FileInfo, FileSystem
from utils.logger import logger


class FormatDetector:
    """
    Format detector for the Omni-Converter.
    
    Detects the format of files based on their content and extension.
    """
    
    def __init__(self):
        """Initialize the format detector."""
        # Load format registry from config
        self.format_registry = config_manager.get_config_value('formats', {})
        
        # Initialize format signatures
        self._init_format_signatures()
        
        # Initialize format extensions
        self._init_format_extensions()
    
    def _init_format_signatures(self) -> None:
        """Initialize the format signatures."""
        # Map of MIME types to formats
        self.format_signatures = {
            # Text formats
            'text/html': 'html',
            'application/xhtml+xml': 'html',
            'text/xml': 'xml',
            'application/xml': 'xml',
            'text/plain': 'plain',
            'text/calendar': 'calendar',
            'text/csv': 'csv',
            
            # Image formats
            'image/jpeg': 'jpeg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'image/svg+xml': 'svg',
            
            # Audio formats
            'audio/mpeg': 'mp3',
            'audio/mp3': 'mp3',
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/flac': 'flac',
            'audio/aac': 'aac',
            
            # Video formats
            'video/mp4': 'mp4',
            'video/webm': 'webm',
            'video/x-msvideo': 'avi',
            'video/x-matroska': 'mkv',
            'video/quicktime': 'mov',
            
            # Application formats
            'application/pdf': 'pdf',
            'application/json': 'json',
            'application/zip': 'zip',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
        }
    
    def _init_format_extensions(self) -> None:
        """Initialize the format extensions."""
        # Map of extensions to formats
        self.format_extensions = {
            # Text formats
            'html': 'html',
            'htm': 'html',
            'xhtml': 'html',
            'xml': 'xml',
            'txt': 'plain',
            'text': 'plain',
            'ics': 'calendar',
            'csv': 'csv',
            
            # Image formats
            'jpg': 'jpeg',
            'jpeg': 'jpeg',
            'png': 'png',
            'gif': 'gif',
            'webp': 'webp',
            'svg': 'svg',
            
            # Audio formats
            'mp3': 'mp3',
            'wav': 'wav',
            'ogg': 'ogg',
            'flac': 'flac',
            'aac': 'aac',
            
            # Video formats
            'mp4': 'mp4',
            'webm': 'webm',
            'avi': 'avi',
            'mkv': 'mkv',
            'mov': 'mov',
            
            # Application formats
            'pdf': 'pdf',
            'json': 'json',
            'zip': 'zip',
            'docx': 'docx',
            'xlsx': 'xlsx'
        }
    
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
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
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


# Global format detector instance
format_detector = FormatDetector()