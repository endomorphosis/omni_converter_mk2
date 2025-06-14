# """
# Image format handlers for the Omni-Converter.

# This module provides handlers for image formats like JPEG, PNG, GIF, etc.
# It uses a combination of basic metadata extraction and OCR (Optical Character Recognition)
# for extracting text from images.
# """

# import os
# import io
# from datetime import datetime
# from typing import Any, Dict, List, Optional, Set, Tuple, Union

# from PIL import Image
# from PIL.ExifTags import TAGS

# from utils.filesystem import FileSystem
# from logger import logger
# from core.format_detector import format_detector
# from extractors.base_handler import BaseFormatHandler, Content
# from extractors.processors.by_ability.ocr_processor import ocr_processor

# from utils.common.try_except_decorator import try_except


# class ImageHandler(BaseFormatHandler):
#     """
#     Handler for image-based formats.
    
#     Handles common image formats like JPEG, PNG, GIF, WebP, and SVG.
#     Extracts metadata and generates basic descriptions for images.
    
#     # TODO: Implement full OCR functionality for text extraction from images.
#     Note: For full OCR functionality, additional packages would be required.
#     This is a simplified implementation focused on metadata extraction.
#     """
    
#     def __init__(self):
#         """Initialize the image handler."""
#         super().__init__(
#             handler_name="ImageHandler",
#             supported_formats={"jpeg", "png", "gif", "webp", "svg"},
#             capabilities={
#                 'category': 'image',
#                 'preserves_structure': False,
#                 'extracts_metadata': True,
#                 'supports_ocr': True if ocr_processor.supported_formats else 'basic'
#             }
#         )
    
#     def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
#         """
#         Extract content from an image file.
        
#         Args:
#             file_path: The path to the file.
#             options: Extraction options.
            
#         Returns:
#             The extracted content.
            
#         Raises:
#             ValueError: If the file format is not supported.
#             Exception: If an error occurs during extraction.
#         """
#         # Detect format if not provided in options
#         format_name = options.get('format')
#         if not format_name:
#             format_name, _ = format_detector.detect_format(file_path)
            
#             # Override format detection based on file extension if needed
#             _, ext = os.path.splitext(file_path)
#             ext = ext.lower().lstrip('.')
            
#             # Handle special cases
#             match ext:
#                 case 'jpg' | 'jpeg':
#                     format_name = 'jpeg'
#                 case 'png' | 'gif' | 'webp' | 'svg':
#                     format_name = ext
#                 case _:
#                     pass

#         if not format_name or format_name not in self.supported_formats:
#             raise ValueError(f"Unsupported format: {format_name}")
        
#         logger.debug(f"Extracting content from {format_name} image: {file_path}")
        
#         # Special handling for SVG since it's text-based
#         if format_name == 'svg':
#             return self._extract_svg_content(file_path, format_name)
        
#         # For other image formats, use PIL
#         try:
#             # Use a context manager to ensure file is closed
#             with Image.open(file_path) as img:
#                 width, height = img.size
#                 img_format = img.format
#                 img_mode = img.mode
                
#                 # Extract EXIF data if available (primarily for JPEG)
#                 exif_data = {}
#                 if format_name == 'jpeg' and hasattr(img, '_getexif') and img._getexif():
#                     exif = img._getexif()
#                     if exif:
#                         for tag_id, value in exif.items():
#                             tag = TAGS.get(tag_id, tag_id)
#                             exif_data[tag] = str(value)
                
#                 # Create a basic text description of the image
#                 text_content = [f"Image: {os.path.basename(file_path)}"]
#                 text_content.append(f"Format: {img_format}")
#                 text_content.append(f"Dimensions: {width}x{height} pixels")
#                 text_content.append(f"Color Mode: {img_mode}")
                
#                 # Add key EXIF data to the description
#                 if exif_data:
#                     text_content.append("\nMetadata:")
#                     for key in ['Make', 'Model', 'DateTime', 'ExposureTime', 
#                             'FNumber', 'ISOSpeedRatings', 'FocalLength']:
#                         if key in exif_data:
#                             text_content.append(f"  {key}: {exif_data[key]}")
                
#                 # Create metadata
#                 metadata = {
#                     'format': format_name,
#                     'width': width,
#                     'height': height,
#                     'color_mode': img_mode,
#                     'exif': exif_data
#                 }
                
#                 # Create sections
#                 sections = [
#                     {
#                         'type': 'image_info',
#                         'content': f"Image: {width}x{height} {img_mode}"
#                     }
#                 ]
                
#                 if exif_data:
#                     sections.append({
#                         'type': 'metadata',
#                         'content': exif_data
#                     })
                
#                 # Add OCR section using the OCR processor if available
#                 ocr_text = None
#                 if ocr_processor.can_process(format_name):
#                     try:
#                         # Read file as binary for OCR processing
#                         file_data = FileSystem.read_file(file_path, 'rb').as_binary
                        
#                         # Process with OCR
#                         ocr_options = {
#                             'language': options.get('language', 'eng'),
#                             'include_boxes': options.get('include_text_boxes', False)
#                         }
                        
#                         # Extract text with OCR
#                         ocr_text = ocr_processor.extract_text(file_data, ocr_options)
                        
#                         # Add OCR text to the content
#                         if ocr_text:
#                             text_content.append("\nOCR Text:")
#                             text_content.append(ocr_text)
                            
#                             # Add OCR text to sections
#                             sections.append({
#                                 'type': 'ocr_text',
#                                 'content': ocr_text
#                             })
                            
#                             # Try to extract additional features if requested
#                             if options.get('extract_features', False):
#                                 try:
#                                     features = ocr_processor.extract_features(
#                                         file_data, 
#                                         {**ocr_options, 'include_boxes': True}
#                                     )
#                                     sections.extend(features)
#                                 except Exception as e:
#                                     logger.warning(f"Failed to extract image features: {e}")
#                     except Exception as e:
#                         logger.warning(f"OCR processing failed: {e}")
#                         sections.append({
#                             'type': 'ocr_text',
#                             'content': f"OCR processing failed: {e}"
#                         })
#                 else:
#                     # Add a placeholder if OCR is not available
#                     sections.append({
#                         'type': 'ocr_text',
#                         'content': "OCR text extraction not available for this format."
#                     })
                
#                 # Create content object
#                 content = Content(
#                     text="\n".join(text_content),
#                     metadata=metadata,
#                     sections=sections,
#                     source_format=format_name,
#                     source_path=file_path
#                 )
                
#                 return content
            
#         except Exception as e:
#             logger.error(f"Error extracting content from {format_name} image: {file_path}\n{e}")
#             raise e

#     def _extract_svg_content(self, file_path: str, format_name: str) -> Content:
#         """
#         Extract content from an SVG file.
        
#         SVG is a text-based XML format, so we can extract more meaningful content.
        
#         Args:
#             file_path: The path to the file.
#             format_name: The format of the file.
            
#         Returns:
#             The extracted content.
#         """
#         try:
#             # Read the SVG file
#             file_content = FileSystem.read_file(file_path, 'r')
#             svg_text = file_content.get_as_text()
            
#             # Extract basic info from the SVG
#             import re
            
#             # Try to extract dimensions
#             width = height = "Unknown"
#             width_match = re.search(r'width="([^"]*)"', svg_text)
#             if width_match:
#                 width = width_match.group(1)
            
#             height_match = re.search(r'height="([^"]*)"', svg_text)
#             if height_match:
#                 height = height_match.group(1)
            
#             # Extract text content from SVG tags that might contain text
#             text_elements = re.findall(r'<text[^>]*>(.*?)</text>', svg_text, re.DOTALL)
#             title_elements = re.findall(r'<title[^>]*>(.*?)</title>', svg_text, re.DOTALL)
#             desc_elements = re.findall(r'<desc[^>]*>(.*?)</desc>', svg_text, re.DOTALL)
            
#             # Create a text description
#             text_content = [f"SVG Image: {os.path.basename(file_path)}"]
#             text_content.append(f"Dimensions: {width}x{height}")
            
#             if title_elements:
#                 text_content.append(f"Title: {title_elements[0]}")
            
#             if desc_elements:
#                 text_content.append(f"Description: {desc_elements[0]}")
            
#             if text_elements:
#                 text_content.append("\nText content:")
#                 for text in text_elements:
#                     text_content.append(text.strip())
            
#             # Create metadata
#             metadata = {
#                 'format': format_name,
#                 'width': width,
#                 'height': height,
#                 'title': title_elements[0] if title_elements else None,
#                 'description': desc_elements[0] if desc_elements else None
#             }
            
#             # Create sections
#             sections = [
#                 {
#                     'type': 'image_info',
#                     'content': f"SVG Image: {width}x{height}"
#                 }
#             ]
            
#             if title_elements or desc_elements:
#                 sections.append({
#                     'type': 'metadata',
#                     'content': {
#                         'title': title_elements[0] if title_elements else None,
#                         'description': desc_elements[0] if desc_elements else None
#                     }
#                 })
            
#             if text_elements:
#                 sections.append({
#                     'type': 'text_content',
#                     'content': text_elements
#                 })
            
#             # Create content object
#             content = Content(
#                 text="\n".join(text_content),
#                 metadata=metadata,
#                 sections=sections,
#                 source_format=format_name,
#                 source_path=file_path
#             )
            
#             return content
            
#         except Exception as e:
#             logger.error(f"Error extracting content from SVG image: {file_path}\n{e}")
#             raise e


# # Global image handler instance
# image_handler = ImageHandler()
