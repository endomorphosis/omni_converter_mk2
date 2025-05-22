"""
Factory module for creating format handlers and registries.

This module provides factory functions for creating format handlers and assembling
them into a format registry. It centralizes the creation of these components
and manages their dependencies.
"""
from typing import Any, Callable, Dict, List, Optional, Set, Union

from utils.configs import Configs
from utils.format_detector import format_detector
from utils.logger import logger

# Import handler factory functions
from format_handlers.refactored_audio_handler import create_audio_handler
from format_handlers.refactored_image_handler import create_image_handler
from format_handlers.refactored_text_handler import create_text_handler
from format_handlers.unified_handler import map_extension_to_format
from format_handlers.refactored_format_registry import create_format_registry

# Import processor modules
from utils.dependency_modules.pil_processor import PIL_AVAILABLE
from utils.dependency_modules.svg_processor import (
    extract_svg_metadata, 
    generate_svg_description, 
    process_svg_file
)
from utils.dependency_modules.pytesseract_processor import (
    OCR_AVAILABLE,
    can_process as ocr_can_process,
    extract_text as ocr_extract_text,
    extract_features as ocr_extract_features
)

# Import text processor modules
try:
    from utils.dependency_modules.beautiful_soup_processor import (
        SOUP_AVAILABLE
    )
except ImportError:
    SOUP_AVAILABLE = False
    logger.info("BeautifulSoup processor not available")

try:
    from utils.dependency_modules.lxml_processor import (
        LXML_AVAILABLE
    )
except ImportError:
    LXML_AVAILABLE = False
    logger.info("lxml processor not available")

try:
    from utils.dependency_modules.icalendar_processor import (
        ICALENDAR_AVAILABLE
    )
except ImportError:
    ICALENDAR_AVAILABLE = False
    logger.info("icalendar processor not available")

try:
    from utils.dependency_modules.csv_processor import (
        PANDAS_AVAILABLE
    )
except ImportError:
    PANDAS_AVAILABLE = False
    logger.info("pandas processor not available")


def initialize_processors(resources: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize processor dependencies for handlers.
    
    Args:
        resources: Resources dictionary with dependencies.
        
    Returns:
        Dictionary of processor instances.
    """
    processors = {}
    
    # === Image Processors ===
    
    # PIL processor
    if PIL_AVAILABLE:
        from utils.dependency_modules.pil_processor import (
            extract_image_metadata,
            generate_image_description,
            process_image_file
        )
        processors["pil_processor"] = {
            "extract_image_metadata": extract_image_metadata,
            "generate_image_description": generate_image_description,
            "process_image_file": process_image_file
        }
    else:
        logger.warning("PIL not available, using basic image processing")
        processors["pil_processor"] = None
    
    # SVG processor
    processors["svg_processor"] = {
        "extract_svg_metadata": extract_svg_metadata,
        "generate_svg_description": generate_svg_description,
        "process_svg_file": process_svg_file
    }
    
    # OCR processor
    if OCR_AVAILABLE:
        processors["ocr_processor"] = {
            "can_process": ocr_can_process,
            "extract_text": ocr_extract_text,
            "extract_features": ocr_extract_features
        }
    else:
        logger.warning("OCR not available, text extraction from images will be limited")
        processors["ocr_processor"] = None
    
    # === Text Processors ===
    
    # BeautifulSoup processor
    if SOUP_AVAILABLE:
        from utils.dependency_modules.beautiful_soup_processor import process_html
        processors["beautiful_soup_processor"] = {
            "process_html": process_html
        }
    else:
        logger.warning("BeautifulSoup not available, using basic HTML processing")
        processors["beautiful_soup_processor"] = None
    
    # lxml processor
    if LXML_AVAILABLE:
        from utils.dependency_modules.lxml_processor import process_xml
        processors["lxml_processor"] = {
            "process_xml": process_xml
        }
    else:
        logger.warning("lxml not available, using basic XML processing")
        processors["lxml_processor"] = None
    
    # icalendar processor
    if ICALENDAR_AVAILABLE:
        from utils.dependency_modules.icalendar_processor import process_calendar
        processors["icalendar_processor"] = {
            "process_calendar": process_calendar
        }
    else:
        logger.warning("icalendar not available, using basic calendar processing")
        processors["icalendar_processor"] = None
    
    # CSV processor
    if PANDAS_AVAILABLE:
        from utils.dependency_modules.csv_processor import process_csv
        processors["csv_processor"] = {
            "process_csv": process_csv
        }
    else:
        logger.warning("pandas not available, using basic CSV processing")
        processors["csv_processor"] = None
    
    return processors


def create_all_handlers(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None) -> Dict[str, Callable]:
    """
    Create factory functions for all format handlers.
    
    Args:
        resources: Optional additional resources to provide to handlers.
        configs: Configuration settings.
        
    Returns:
        Dictionary mapping handler types to factory functions.
    """
    # Initialize resources if not provided
    resources = resources or {}
    
    # Initialize processors for dependency injection
    processors = initialize_processors(resources)
    resources.update(processors)
    
    # Create a dictionary of factory functions for each handler type
    handler_factories = {
        "audio": create_audio_handler,
        "image": create_image_handler,
        "text": create_text_handler,
        # TODO Add other handlers as they are refactored
        # "video": create_video_handler,
        # "application": create_application_handler,
    }
    
    # Add any additional resources
    handler_resources = {
        "format_detector": format_detector,
        "ext_to_format": map_extension_to_format,
    }
    
    # Merge with provided resources
    if resources:
        handler_resources.update(resources)
    
    # Return the factory functions
    return handler_factories


def initialize_format_registry(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Initialize the format registry with all available handlers.
    
    Args:
        resources: Optional additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        Configured FormatRegistry instance.
    """
    # Create handler factories
    handler_factories = create_all_handlers(resources, configs)
    
    # Prepare resources for the registry
    registry_resources = {
        "format_detector": format_detector,
        "ext_to_format": map_extension_to_format,
        "handler_factories": handler_factories,
    }
    
    # Add any additional resources
    if resources:
        for key, value in resources.items():
            if key not in registry_resources:
                registry_resources[key] = value
    
    # Create and return the registry
    logger.info("Initializing format registry with IoC pattern")
    return create_format_registry(registry_resources, configs)