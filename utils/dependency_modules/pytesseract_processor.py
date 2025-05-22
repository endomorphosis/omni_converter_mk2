"""
OCR processing utilities.

This module contains functions for Optical Character Recognition (OCR) on images.
It wraps third-party OCR dependencies to make them swappable and isolate them from
the rest of the codebase.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
from io import BytesIO

from utils.logger import logger

# Check for OCR dependencies
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("pytesseract or PIL not available, OCR functionality will be limited")


def can_process(format_name: str) -> bool:
    """
    Check if OCR processing is available for the given format.
    
    Args:
        format_name: The format of the file.
        
    Returns:
        True if OCR is available for this format, False otherwise.
    """
    if not OCR_AVAILABLE:
        return False
    
    # OCR is supported for common image formats
    return format_name in {'jpeg', 'png', 'gif', 'webp', 'tiff'}


def extract_text(
    image_data: Union[bytes, str, BytesIO],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image_data: The image data as bytes, file path, or BytesIO.
        options: Optional OCR options.
            - language: OCR language code (default: 'eng')
            - include_boxes: Whether to include text bounding boxes (default: False)
        
    Returns:
        The extracted text.
        
    Raises:
        ValueError: If OCR is not available.
        Exception: If an error occurs during OCR.
    """
    if not OCR_AVAILABLE:
        raise ValueError("OCR is not available (pytesseract or PIL missing)")
    
    options = options or {}
    language = options.get('language', 'eng')
    
    try:
        # Convert image data to PIL Image if needed
        if isinstance(image_data, (str, bytes, BytesIO)):
            if isinstance(image_data, str) and os.path.isfile(image_data):
                # It's a file path
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                # It's bytes data
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_data, BytesIO):
                # It's already a BytesIO object
                image = Image.open(image_data)
            else:
                raise ValueError(f"Unsupported image_data type: {type(image_data)}")
        else:
            raise ValueError(f"Unsupported image_data type: {type(image_data)}")
        
        # Extract text with pytesseract
        text = pytesseract.image_to_string(image, lang=language)
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error during OCR processing: {e}")
        raise


def extract_features(
    image_data: Union[bytes, str, BytesIO],
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Extract features from an image using OCR.
    
    Args:
        image_data: The image data as bytes, file path, or BytesIO.
        options: Optional OCR options.
            - language: OCR language code (default: 'eng')
            - include_boxes: Whether to include text bounding boxes (default: True)
        
    Returns:
        A list of sections with extracted features.
        
    Raises:
        ValueError: If OCR is not available.
        Exception: If an error occurs during OCR.
    """
    if not OCR_AVAILABLE:
        raise ValueError("OCR is not available (pytesseract or PIL missing)")
    
    options = options or {}
    language = options.get('language', 'eng')
    
    try:
        # Convert image data to PIL Image if needed
        if isinstance(image_data, (str, bytes, BytesIO)):
            if isinstance(image_data, str) and os.path.isfile(image_data):
                # It's a file path
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                # It's bytes data
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_data, BytesIO):
                # It's already a BytesIO object
                image = Image.open(image_data)
            else:
                raise ValueError(f"Unsupported image_data type: {type(image_data)}")
        else:
            raise ValueError(f"Unsupported image_data type: {type(image_data)}")
        
        features = []
        
        # Extract text with bounding boxes
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
        
        # Create a section for text with confidence
        confidences = []
        for i, text in enumerate(data['text']):
            if text.strip():
                confidences.append({
                    'text': text,
                    'confidence': data['conf'][i],
                    'block_num': data['block_num'][i],
                    'line_num': data['line_num'][i]
                })
        
        if confidences:
            features.append({
                'type': 'ocr_confidence',
                'content': confidences
            })
        
        return features
        
    except Exception as e:
        logger.error(f"Error extracting OCR features: {e}")
        raise