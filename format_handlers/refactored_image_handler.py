"""
Image format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for image formats like JPEG, PNG, GIF, WebP, and SVG
using dependency injection for better modularity and testability, without inheritance.
"""

import os
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from utils.configs import Configs
from utils.logger import logger
from format_handlers.unified_handler import BaseFormatHandler, Content, create_handler, map_extension_to_format
from format_handlers.constants import Constants
from utils.format_detector import format_detector


def create_image_handler(resources: Dict[str, Any], configs: Optional[Configs] = None) -> BaseFormatHandler:
    """
    Create an image handler instance with injected dependencies.
    
    Args:
        resources: Resources dictionary with dependencies.
            Must contain:
            - pil_processor: PIL-based image processor
            - svg_processor: SVG-specific processor
            - ocr_processor: OCR processor for text extraction
        configs: Configuration settings.
        
    Returns:
        BaseFormatHandler instance configured for image formats.
    """
    # Format-specific file extensions
    format_extensions = {
        'jpeg': ['.jpg', '.jpeg'],
        'png': ['.png'],
        'gif': ['.gif'],
        'webp': ['.webp'],
        'svg': ['.svg']
    }
    
    # Prepare parsers with the appropriate functions
    parsers = {
        "image": {
            "jpeg": process_image_file,
            "png": process_image_file,
            "gif": process_image_file,
            "webp": process_image_file,
            "svg": process_svg_file
        }
    }
    
    # Extract required processors from resources - fail fast if missing
    pil_processor = resources["pil_processor"]
    svg_processor = resources["svg_processor"]
    ocr_processor = resources["ocr_processor"]
    
    # Define capabilities based on available processors
    capabilities = dict(Constants.IMAGE_HANDLER_CAPABILITIES)
    capabilities['supports_ocr'] = True
    
    # Additional resources specific to image handling
    image_resources = {
        "pil_processor": pil_processor,
        "svg_processor": svg_processor,
        "ocr_processor": ocr_processor,
        "format_extensions": format_extensions
    }
    
    # Create and return the handler
    return create_handler(
        handler_name="ImageHandler",
        format_detector=format_detector,
        ext_to_format=map_extension_to_format,
        supported_formats=Constants.SUPPORTED_IMAGE_FORMATS_SET,
        capabilities=capabilities,
        parsers=parsers,
        resources_extra=image_resources,
        configs=configs
    )


def process_image_file(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an image file and extract content.
    
    Args:
        file_content: The file content to process (typically binary).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the image file
            - format: Format of the image file
            - pil_processor: PIL-based image processor
        
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options - fail fast if missing
    file_path = options["file_path"]
    format_name = options["format"]
    pil_processor = options["pil_processor"]
    
    try:
        # Extract metadata using PIL
        metadata, sections = pil_processor.extract_image_metadata(file_path, format_name, options)
        
        # Generate text description
        text_content = pil_processor.generate_image_description(file_path, metadata)
        
        # Use OCR processor if available
        ocr_processor = options["ocr_processor"]
        ocr_text = None
        ocr_sections = []
        
        if ocr_processor.can_process(format_name):
            try:
                # Read file as binary for OCR processing
                ocr_options = {
                    'language': 'eng',  # Default to English if not specified
                    'include_boxes': False  # Default to no bounding boxes
                }
                
                # Override defaults with provided options if they exist
                if 'language' in options:
                    ocr_options['language'] = options['language']
                if 'include_text_boxes' in options:
                    ocr_options['include_boxes'] = options['include_text_boxes']
                
                # Extract text with OCR
                ocr_text = ocr_processor.extract_text(file_content.as_binary, ocr_options)
                
                # Add OCR text to sections
                if ocr_text:
                    ocr_sections.append({
                        'type': 'ocr_text',
                        'content': ocr_text
                    })
                    
                    # Try to extract additional features if requested
                    if 'extract_features' in options and options['extract_features']:
                        try:
                            features = ocr_processor.extract_features(
                                file_content.as_binary, 
                                {**ocr_options, 'include_boxes': True}
                            )
                            ocr_sections.extend(features)
                        except Exception as e:
                            logger.warning(f"Failed to extract image features: {e}")
            except Exception as e:
                logger.warning(f"OCR processing failed: {e}")
                ocr_sections.append({
                    'type': 'ocr_text',
                    'content': f"OCR processing failed: {e}"
                })
        else:
            # Add a placeholder if OCR is not available for this format
            ocr_sections.append({
                'type': 'ocr_text',
                'content': f"OCR text extraction not available for {format_name} format."
            })
        
        # Add OCR text to content if available
        if ocr_text:
            text_content.append("\nOCR Text:")
            text_content.append(ocr_text)
        
        # Add OCR sections to sections
        sections.extend(ocr_sections)
        
        return "\n".join(text_content), metadata, sections
        
    except Exception as e:
        logger.error(f"Error extracting content from {format_name} image: {file_path}\n{e}")
        raise


def process_svg_file(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an SVG file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the SVG file
            - svg_processor: SVG-specific processor
        
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options - fail fast if missing
    file_path = options["file_path"]
    svg_processor = options["svg_processor"]
    
    try:
        # Process SVG using the dedicated processor
        return svg_processor.process_svg_file(file_content, options)
        
    except Exception as e:
        logger.error(f"Error extracting content from SVG image: {file_path}\n{e}")
        raise


def extract_basic(file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Basic extraction when specific processors are not available.
    
    Args:
        file_path: The path to the image file.
        format_name: The format of the image file.
        
    Returns:
        A tuple of (text content, metadata, sections).
    """
    # Get basic file information
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    # Build basic metadata
    metadata = {
        'format': format_name,
        'file_size_bytes': file_size,
        'file_name': file_name
    }
    
    # Generate basic description
    text_content = [f"Image File: {file_name}"]
    text_content.append(f"Format: {format_name.upper()}")
    text_content.append(f"File Size: {file_size} bytes")
    text_content.append("")
    text_content.append("Note: Detailed image information not available.")
    if format_name != 'svg':
        text_content.append("Install PIL for enhanced image metadata extraction.")
    
    # Create basic sections
    sections = [
        {
            'type': 'image_info',
            'content': {
                'format': format_name,
                'file_size': file_size
            }
        }
    ]
    
    return "\n".join(text_content), metadata, sections