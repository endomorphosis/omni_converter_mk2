"""
Factory module for creating format handlers and registries.

This module provides factory functions for creating format handlers and assembling
them into a format registry. It centralizes the creation of these components
and manages their dependencies.
"""
from typing import Any, Callable, Dict, List, Optional, Set, Union

from configs import Configs
from logger import logger
from core.format_detector import format_detector

from format_handlers.constants import Constants


# Import handler factory functions
from format_handlers.audio_handler import create_audio_handler
from format_handlers.image_handler import create_image_handler
from format_handlers.text_handler import create_text_handler
from format_handlers.video_handler import create_video_handler
from format_handlers.application_handler import create_application_handler
from format_handlers.unified_handler import map_extension_to_format
from format_handlers.format_registry import create_format_registry


def _snake_to_pascal_case(name: str) -> str:
    """
    Convert a snake_case string to PascalCase.
    
    Args:
        name: The snake_case string to convert.
        
    Returns:
        The converted PascalCase string.
    """
    return ''.join(word.capitalize() for word in name.split('_'))


import importlib
from unittest.mock import MagicMock
from typing import TypeVar


Processor = TypeVar('Processor')


def make_processor(
    processor: str = None,
    resources: dict[str, Any] = None,
    dependencies: dict[str, bool] = None,
    supported_formats: set[str] = None,
    critical_resources: list[str] = None,
    configs= None,
) -> 'Processor':
    """
    Factory function to create an instance of XlsxProcessor.
    
    Returns:
        An instance of XlsxProcessor, or a MagicMock if the processor is not available.
    """
    by_ability_folder = 'format_handlers.processors.by_ability'
    by_mime_type_folder = 'format_handlers.processors.by_mime_type'
    dependency_folder = 'format_handlers.dependency_modules'

    processor_module = None

    resources = {
        "supported_formats": supported_formats,
        "processor_name": processor,
        "processor_available": True,
        "can_process": True,
    }

    # Import the processor module dynamically based on the processor name.
    for folder in [by_ability_folder, by_mime_type_folder]:
        try:
            processor_module = importlib.import_module(f'{folder}.{processor}')
            processor = getattr(processor_module, _snake_to_pascal_case(processor), None)
            break
        except ImportError:
            continue

    # Try dependencies in order until one works
    dependency_found = False
    for name, dependency in dependencies.items():
        if dependency:  # Check if this dependency is available
            file_name = f'_{name}_processor'
            try:
                # Try to import the dependency module
                module = importlib.import_module(f'{dependency_folder}.{file_name}')
                
                # Add critical resources from this dependency module
                for func in critical_resources:
                    match func:
                        case str():
                            resources[func] = getattr(module, func, None)
                        case tuple():
                            # If it's a tuple, assume it contains the processor name and function.
                            func_name, processor_ref = func
                            resources[func_name] = getattr(processor_ref, func_name, None)
                        case _:
                            logger.error(f"Unknown resource type: {func}")
                            raise ValueError(f"Unknown resource type: {func}")
                
                resources["processor_name"] = name
                dependency_found = True
                break  # Found working dependency, stop trying others
                
            except ImportError as e:
                logger.debug(f"Dependency module {file_name} not found: {e}")
                continue  # Try next dependency
            except Exception as e:
                logger.exception(f"Unexpected {type(e).__name__} importing {file_name}: {e}")
                continue  # Try next dependency

    # If no dependencies were found, return a mock
    if not dependency_found:
        return _mock_processor(processor)
    
    # Create and return the processor instance
    return processor(resources=resources, configs=configs)

def _mock_processor(processor: str) -> MagicMock:
    logger.warning(f"{processor} processor not available, returning mock processor instead.")
    mock_processor = MagicMock(spec=processor)
    mock_processor.processor_name.return_value = "mock"
    mock_processor.can_process.return_value = False
    return mock_processor

# TODO 
def initialize_processors(resources: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize processor dependencies for handlers.

    Args:
        resources: Resources dictionary with dependencies.
        
    Returns:
        Dictionary of processor instances.
    """
    # NOTE order of dependency dictionaries are *important.*
    # Specialized dependencies are checked first, then more general ones.

    processors: dict[str, Processor] = {}
    
    # === Ability Processors ===
    from configs import configs

    # Text processor (ability)
    if Constants.TEXT_PROCESSOR_AVAILABLE:
        text_resources = {
            "supported_formats": Constants.SUPPORTED_TEXT_FORMATS_SET,
            "processor_name": 'text_processor',
            "dependencies": {
                "generic_text": Constants.GENERIC_TEXT_AVAILABLE,
            },
            "critical_resources": [
                "extract_text", "extract_metadata", "extract_structure",
                "get_version"
            ],
        }
        processors["text_processor"] = make_processor(
            processor=text_resources["processor_name"],
            dependencies=text_resources["dependencies"],
            supported_formats=text_resources["supported_formats"],
            critical_resources=text_resources["critical_resources"],
            configs=configs,
        )

    # Image processor (ability)
    if Constants.IMAGE_PROCESSOR_AVAILABLE:
        image_resources = {
            "supported_formats": Constants.SUPPORTED_IMAGE_FORMATS_SET,
            "processor_name": 'image_processor',
            "dependencies": {
                "pil": Constants.PIL_AVAILABLE,
                "openai": Constants.OPENAI_AVAILABLE,
                "pytesseract": Constants.PYTESSERACT_AVAILABLE,
            },
            "critical_resources": [
                "extract_text", "extract_metadata", "extract_structure",
                "get_version"
            ],
        }
        processors["image_processor"] = make_processor(
            processor=image_resources["processor_name"],
            dependencies=image_resources["dependencies"],
            supported_formats=image_resources["supported_formats"],
            critical_resources=image_resources["critical_resources"],
            configs=configs,
        )

    # Video processor
    if Constants.VIDEO_PROCESSOR_AVAILABLE:
        video_frame_resources = {
            "supported_formats": Constants.SUPPORTED_VIDEO_FORMATS_SET,
            "processor_name": 'video_processor',
            "dependencies": {
                "ffmpeg": Constants.FFMPEG_AVAILABLE,
                "cv2": Constants.CV2_AVAILABLE,
                "pymediainfo": Constants.PYMEDIAINFO_AVAILABLE,
            },
            "critical_resources": [
                "extract_metadata", "extract_frames", "extract_text", "process_video_frames", "get_version"
            ],
        }
        processors["video_processor"] = make_processor(
            processor=video_frame_resources["processor_name"],
            dependencies=video_frame_resources["dependencies"],
            supported_formats=video_frame_resources["supported_formats"],
            critical_resources=video_frame_resources["critical_resources"],
            configs=configs,
        )

    # OCR processor (ability)
    if Constants.PYTESSERACT_AVAILABLE or Constants.OPENAI_AVAILABLE:
        ocr_resources = {
            "supported_formats": Constants.SUPPORTED_IMAGE_FORMATS_SET,
            "processor_name": 'ocr_processor',
            "dependencies": {
                "openai": Constants.OPENAI_AVAILABLE,
                "pytesseract": Constants.PYTESSERACT_AVAILABLE,
            },
            "critical_resources": [
                "can_process", "extract_text", "extract_features",
                "get_version"
            ],
        }
        processors["ocr_processor"] = make_processor(
            processor=ocr_resources["processor_name"],
            dependencies=ocr_resources["dependencies"],
            supported_formats=ocr_resources["supported_formats"],
            critical_resources=ocr_resources["critical_resources"],
            configs=configs,
        )


    # === MIME-Type Specific Processors ===
    
    # XLSX processor (MIME-type specific)
    if Constants.XLSX_PROCESSOR_AVAILABLE:
        xlsx_resources = {
            "supported_formats": Constants.SUPPORTED_XLSX_FORMATS_SET,
            "processor_name": 'xlsx_processor',
            "dependencies": {
                "openpyxl": Constants.OPENPYXL_AVAILABLE,
                "pandas": Constants.PANDAS_AVAILABLE,
            },
            "critical_resources": [
                "extract_text", "extract_metadata", "extract_structure", "open_xlsx_file",
                "get_version"
            ],
        }
        if processors.get("image_processor"):
            xlsx_resources["critical_resources"].append(('extract_images', processors["image_processor"]))

        processors["xlsx_processor"] = make_processor(
            processor=xlsx_resources["processor_name"],
            dependencies=xlsx_resources["dependencies"],
            supported_formats=xlsx_resources["supported_formats"],
            critical_resources=xlsx_resources["critical_resources"],
            configs=configs,
        )

    # SVG processor
    if Constants.SVG_PROCESSOR_AVAILABLE:
        svg_resources = {
            "supported_formats": Constants.SUPPORTED_SVG_FORMATS_SET,
            "processor_name": 'svg_processor',
            "dependencies": {
                "generic_svg": Constants.GENERIC_SVG_AVAILABLE,
            },
            "critical_resources": [
                "extract_svg_metadata", "generate_svg_description", "process_svg_file", "get_version"
            ],
        }
        processors["svg_processor"] = make_processor(
            processor=svg_resources["processor_name"],
            dependencies=svg_resources["dependencies"],
            supported_formats=svg_resources["supported_formats"],
            critical_resources=svg_resources["critical_resources"],
            configs=configs,
        )
    
    # === Text Processors ===
    
    # HTML processor
    if Constants.HTML_PROCESSOR_AVAILABLE:
        html_resources = {
            "supported_formats": Constants.SUPPORTED_HTML_FORMATS_SET,
            "processor_name": 'html_processor',
            "dependencies": {
                "bs4": Constants.BS4_AVAILABLE,
            },
            "critical_resources": [
                "process_html", "get_version"
            ],
        }
        processors["html_processor"] = make_processor(
            processor=html_resources["processor_name"],
            dependencies=html_resources["dependencies"],
            supported_formats=html_resources["supported_formats"],
            critical_resources=html_resources["critical_resources"],
            configs=configs,
        )
    
    # XML processor
    if Constants.XML_PROCESSOR_AVAILABLE:
        xml_resources = {
            "supported_formats": Constants.SUPPORTED_XML_FORMATS_SET,
            "processor_name": 'xml_processor',
            "dependencies": {
                "lxml": Constants.LXML_AVAILABLE,
            },
            "critical_resources": [
                "process_xml", "get_version"
            ],
        }
        processors["xml_processor"] = make_processor(
            processor=xml_resources["processor_name"],
            dependencies=xml_resources["dependencies"],
            supported_formats=xml_resources["supported_formats"],
            critical_resources=xml_resources["critical_resources"],
            configs=configs,
        )
    
    # Calendar processor
    if Constants.CALENDAR_PROCESSOR_AVAILABLE:
        calendar_resources = {
            "supported_formats": Constants.SUPPORTED_CALENDAR_FORMATS_SET,
            "processor_name": 'calendar_processor',
            "dependencies": {
                "icalendar": Constants.ICALENDAR_AVAILABLE,
            },
            "critical_resources": [
                "process_calendar", "get_version"
            ],
        }
        processors["calendar_processor"] = make_processor(
            processor=calendar_resources["processor_name"],
            dependencies=calendar_resources["dependencies"],
            supported_formats=calendar_resources["supported_formats"],
            critical_resources=calendar_resources["critical_resources"],
            configs=configs,
        )
    
    # CSV processor
    if Constants.CSV_PROCESSOR_AVAILABLE:
        csv_resources = {
            "supported_formats": Constants.SUPPORTED_CSV_FORMATS_SET,
            "processor_name": 'csv_processor',
            "dependencies": {
                "pandas": Constants.PANDAS_AVAILABLE,
            },
            "critical_resources": [
                "process_csv", "get_version"
            ],
        }
        processors["csv_processor"] = make_processor(
            processor=csv_resources["processor_name"],
            dependencies=csv_resources["dependencies"],
            supported_formats=csv_resources["supported_formats"],
            critical_resources=csv_resources["critical_resources"],
            configs=configs,
        )

    # === Application Processors ===

    # PDF processor
    processors["pdf_processor"] = make_processor(
        processor="pdf_processor",
        resources={},
        dependencies={
            "pypdf2": Constants.PYPDF2_AVAILABLE,
        },
        supported_formats={"pdf"},
        critical_resources=[
            "extract_text", "extract_metadata", "extract_structure", 
            "get_version"
        ],
        configs=configs,
    )

    # DOCX processor
    processors["docx_processor"] = make_processor(
        processor="docx_processor",
        resources={},
        dependencies={
            "python_docx": Constants.PYTHON_DOCX_PROCESSOR_AVAILABLE,
        },
        supported_formats={"docx"},
        critical_resources=[
            "extract_text", "extract_metadata", "extract_structure", 
            "get_version"
        ],
        configs=configs,
    )
    
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
        "video": create_video_handler,
        "application": create_application_handler,
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
    logger.debug("Creating handler factories...")
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
    logger.info("Initializing format registry...")
    return create_format_registry(registry_resources, configs)
