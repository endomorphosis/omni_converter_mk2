"""
PIL-dependent image processing utilities.

This module contains image processing functions that rely on the PIL (Pillow) library.
These functions are isolated to make dependencies explicit and easily swappable.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
from io import BytesIO

from utils.logger import logger

# Import PIL conditionally
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available, image processing will be limited")
    PIL_AVAILABLE = False


def extract_image_metadata(
    file_path: str,
    format_name: str,
    options: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extract metadata from an image file using PIL.
    
    Args:
        file_path: The path to the image file.
        format_name: The format of the image file.
        options: Optional extraction options.
        
    Returns:
        A tuple of (metadata, sections).
        
    Raises:
        ValueError: If PIL is not available.
        Exception: If an error occurs during extraction.
    """
    if not PIL_AVAILABLE:
        raise ValueError("PIL is not available for image metadata extraction")
    
    options = options or {}
    
    try:
        # Use a context manager to ensure file is closed
        with Image.open(file_path) as img:
            width, height = img.size
            img_format = img.format
            img_mode = img.mode
            
            # Extract EXIF data if available (primarily for JPEG)
            exif_data = {}
            if format_name == 'jpeg' and hasattr(img, '_getexif') and img._getexif():
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
            
            # Create metadata
            metadata = {
                'format': format_name,
                'width': width,
                'height': height,
                'color_mode': img_mode,
                'exif': exif_data
            }
            
            # Create sections
            sections = [
                {
                    'type': 'image_info',
                    'content': f"Image: {width}x{height} {img_mode}"
                }
            ]
            
            if exif_data:
                sections.append({
                    'type': 'metadata',
                    'content': exif_data
                })
            
            return metadata, sections
            
    except Exception as e:
        logger.error(f"Error extracting metadata from {format_name} image: {file_path}\n{e}")
        raise


def generate_image_description(
    file_path: str,
    metadata: Dict[str, Any]
) -> List[str]:
    """
    Generate a human-readable description of an image based on its metadata.
    
    Args:
        file_path: The path to the image file.
        metadata: The metadata dictionary.
        
    Returns:
        A list of text lines describing the image.
    """
    text_content = [f"Image: {os.path.basename(file_path)}"]
    
    # Add format info
    if 'format' in metadata:
        text_content.append(f"Format: {metadata['format'].upper()}")
    
    # Add dimensions
    if 'width' in metadata and 'height' in metadata:
        text_content.append(f"Dimensions: {metadata['width']}x{metadata['height']} pixels")
    
    # Add color mode
    if 'color_mode' in metadata:
        text_content.append(f"Color Mode: {metadata['color_mode']}")
    
    # Add key EXIF data to the description
    if 'exif' in metadata and metadata['exif']:
        exif_data = metadata['exif']
        text_content.append("\nMetadata:")
        for key in ['Make', 'Model', 'DateTime', 'ExposureTime', 
                'FNumber', 'ISOSpeedRatings', 'FocalLength']:
            if key in exif_data:
                text_content.append(f"  {key}: {exif_data[key]}")
    
    return text_content


def process_image_file(
    file_content: Any,
    options: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an image file and extract content using PIL.
    
    Args:
        file_content: The file content to process.
        options: Processing options including format information.
        
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If PIL is not available or the file format is not supported.
        Exception: If an error occurs during processing.
    """
    if not PIL_AVAILABLE:
        raise ValueError("PIL is not available for image processing")
    
    # Get key information from the options
    file_path = options.get("file_path", "")
    format_name = options.get("format", "")
    
    if not file_path or not format_name:
        raise ValueError("File path and format are required for image processing")
    
    # Special handling for SVG since it's text-based
    if format_name == 'svg':
        raise ValueError("SVG files should be processed by the svg_processor")
    
    try:
        # Extract metadata
        metadata, sections = extract_image_metadata(file_path, format_name, options)
        
        # Generate text description
        text_content = generate_image_description(file_path, metadata)
        
        # Handle OCR text if available from options
        ocr_text = options.get("ocr_text")
        ocr_sections = options.get("ocr_sections", [])
        
        if ocr_text:
            text_content.append("\nOCR Text:")
            text_content.append(ocr_text)
            
        # Add OCR sections if available
        sections.extend(ocr_sections)
        
        return "\n".join(text_content), metadata, sections
        
    except Exception as e:
        logger.error(f"Error processing image file: {file_path}\n{e}")
        raise