# """
# Document processor interfaces for application format handlers.

# This module provides specialized interfaces for document processors that handle
# application formats like PDF, DOCX, XLSX, etc.
# """

# from abc import abstractmethod
# from typing import Any, Optional, BinaryIO


# from pydantic import BaseModel, Field


# from deprecated.processors.base_processor import BaseProcessor


# class Metadata(BaseModel):
#     """
#     Metadata class for processing.
    
#     This class is used to define the metadata structure for documents.
#     """
#     title: Optional[str] = Field(None, description="Title of the document")



# class DocumentProcessor(BaseProcessor):
#     """
#     Interface for document processors.
    
#     This abstract class extends BaseProcessor with methods specific to document processing.
#     """
    
#     @abstractmethod
#     def extract_text(self, data: bytes, options: dict[str, Any]) -> str:
#         """
#         Extract plain text from a document.
        
#         Args:
#             data: The binary data of the document.
#             options: Processing options.
            
#         Returns:
#             Extracted text from the document.
#         """
#         pass
    
#     @abstractmethod
#     def extract_metadata(self, data: bytes, options: dict[str, Any]) -> dict[str, Any]:
#         """
#         Extract metadata from a document.
        
#         Args:
#             data: The binary data of the document.
#             options: Processing options.
            
#         Returns:
#             Metadata extracted from the document.
#         """
#         pass
    
#     @abstractmethod
#     def extract_structure(self, data: bytes, options: dict[str, Any]) -> list[dict[str, Any]]:
#         """
#         Extract structural elements from a document.
        
#         Args:
#             data: The binary data of the document.
#             options: Processing options.
            
#         Returns:
#             A list of structural elements extracted from the document.
#         """
#         pass
    
#     @abstractmethod
#     def process_document(self, data: bytes, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
#         """
#         Process a document completely, extracting text, metadata, and structure.
        
#         Args:
#             data: The binary data of the document.
#             options: Processing options.
            
#         Returns:
#             A tuple of (text content, metadata, sections).
#         """
#         pass