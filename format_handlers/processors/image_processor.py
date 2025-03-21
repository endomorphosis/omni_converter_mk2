"""
Image processor interfaces for image format handlers.

This module provides specialized interfaces for image processors that handle
image formats like JPEG, PNG, GIF, WebP, SVG, etc.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Tuple, Optional, BinaryIO

from format_handlers.processors.base_processor import BaseProcessor

class ImageProcessor(BaseProcessor):
    """
    Interface for image processors.
    
    This abstract class extends BaseProcessor with methods specific to image processing.
    """
    
    @abstractmethod
    def extract_text(self, data: bytes, options: Dict[str, Any]) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            data: The binary data of the image.
            options: Processing options.
            
        Returns:
            Extracted text from the image.
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, data: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from an image.
        
        Args:
            data: The binary data of the image.
            options: Processing options.
            
        Returns:
            Metadata extracted from the image.
        """
        pass
    
    @abstractmethod
    def extract_features(self, data: bytes, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract visual features from an image.
        
        Args:
            data: The binary data of the image.
            options: Processing options.
            
        Returns:
            A list of features extracted from the image.
        """
        pass
    
    @abstractmethod
    def process_image(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process an image completely, extracting text, metadata, and features.
        
        Args:
            data: The binary data of the image.
            options: Processing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        pass