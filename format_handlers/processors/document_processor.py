"""
Document processor interfaces for application format handlers.

This module provides specialized interfaces for document processors that handle
application formats like PDF, DOCX, XLSX, etc.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Tuple, Optional, BinaryIO

from format_handlers.processors.base_processor import BaseProcessor

class DocumentProcessor(BaseProcessor):
    """
    Interface for document processors.
    
    This abstract class extends BaseProcessor with methods specific to document processing.
    """
    
    @abstractmethod
    def extract_text(self, data: bytes, options: Dict[str, Any]) -> str:
        """
        Extract plain text from a document.
        
        Args:
            data: The binary data of the document.
            options: Processing options.
            
        Returns:
            Extracted text from the document.
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, data: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from a document.
        
        Args:
            data: The binary data of the document.
            options: Processing options.
            
        Returns:
            Metadata extracted from the document.
        """
        pass
    
    @abstractmethod
    def extract_structure(self, data: bytes, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract structural elements from a document.
        
        Args:
            data: The binary data of the document.
            options: Processing options.
            
        Returns:
            A list of structural elements extracted from the document.
        """
        pass
    
    @abstractmethod
    def process_document(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process a document completely, extracting text, metadata, and structure.
        
        Args:
            data: The binary data of the document.
            options: Processing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        pass