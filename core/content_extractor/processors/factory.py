from contextlib import contextmanager
import importlib
import os
from typing import Any, TypeVar, TypedDict
from unittest.mock import MagicMock



from core.content_extractor._content_extractor_constants import Constants
from supported_formats import SupportedFormats
from external_programs import ExternalPrograms
from logger import logger

from types_ import Callable, Configs, Logger, ModuleType


Processor = TypeVar('Processor')

class _ProcessorConstructionError(Exception):
    """Custom exception for processor construction errors."""
    pass

@contextmanager
def _try_except_processor_construction_error():
    """
    Context manager to handle exceptions.
    Because screw adding try/except blocks everywhere.
    
    Yields:
        None
    """
    try:
        yield
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise _ProcessorConstructionError(f"Failed to construct processor occurred: {e}") from e


def _snake_to_pascal_case(name: str) -> str:
    """
    Convert a snake_case string to PascalCase.
    
    Args:
        name: The snake_case string to convert.
        
    Returns:
        The converted PascalCase string.
    """
    return ''.join(word.capitalize() for word in name.split('_'))


def _get_processor_names() -> set[str]:
    """
    Get a set of processor names in the current directory.
    
    Returns:
        A set of processor names without extensions.
    """
    # Get the absolute path of the current file and its directory
    this_dir = os.path.dirname(os.path.abspath(__file__))
    temp_set = set(
        os.path.splitext(file)[0]
        for file in os.listdir(
            os.path.join(this_dir)
        )
        if file.endswith('.py') and not file.startswith('_')
    )
    output_set = set(
        file[:-len('_processor')] 
        for file in temp_set
        if file.endswith('_processor.py')
    )
    return output_set

def _make_processor(
    processor: str = None,
    resources: dict[str, Any] = None,
    dependencies: dict[str, ModuleType] = None,
    supported_formats: set[str] = None,
    critical_resources: list[str] = None,
    logger: Logger = None,
    configs: 'Configs' = None,
) -> Processor | MagicMock:
    """
    Factory function to create processors en-masse.
    
    Returns:
        An instance of XlsxProcessor, or a MagicMock if the processor is not available.
    """
    by_ability_folder = 'core.content_extractor.processors.by_ability'
    by_mime_type_folder = 'core.content_extractor.processors.by_mime_type'
    dependency_folder = 'core.content_extractor.processors.by_dependency'
    fallbacks_folder = 'core.content_extractor.processors.fallbacks'
    processor_module = None

    resources = {
        "supported_formats": supported_formats,
        "processor_name": processor,
        "processor_available": True,
    }
    methods: dict[str, Callable] = {}
    if logger is None:
        from logger import logger

    # Add critical resource names as keys to the resources dictionary.
    for func in critical_resources:
        if isinstance(func, str):
            methods[func] = None

    # Import the processor module dynamically based on the processor name.
    for folder in [by_ability_folder, by_mime_type_folder]:
        try:
            processor_string = f'{folder}.{processor}'
            logger.debug(f"Trying to import processor module: {processor_string}")
            processor_module = importlib.import_module(processor_string)
            processor = getattr(processor_module, _snake_to_pascal_case(processor), None)
            break
        except ImportError:
            continue
    else:
        raise ImportError(f"Processor '{processor}' not found in any of the processor directories.")

    # Cycle through available dependencies until we have all the methods we need.
    # First come, first served.
    # We do this for a variety of reasons, such as:
    # - Some dependencies only provide certain methods. For example, PIL does not have text processing methods.
    # - Some dependencies may not be available or corrupted (e.g., OpenAI API).
    # - Some dependencies may possess more desirable characteristics than others, such as resource use, size, and complexity.

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
                            methods[func] = getattr(module, func, None)
                        case tuple():
                            # If it's a tuple, assume it contains the processor name and function.
                            func_name, processor_ref = func
                            methods[func_name] = getattr(processor_ref, func_name, None)
                        case _:
                            logger.error(f"Unknown resource type: {func}")
                            raise ValueError(f"Unknown resource type: {func}")
                # Update the resources dictionary with the methods
                resources.update(methods)
                resources["processor_name"] = name
                break  # Found working dependency, stop trying others

            except ImportError as e:
                logger.debug(f"Failed to import module '{file_name}' not found: {e}")
                continue  # Try next dependency
            except ModuleNotFoundError as e:
                logger.debug(f"Module '{file_name}' not found: {e}")
                continue
            except Exception as e:
                logger.debug(f"Unexpected {type(e).__name__} importing module '{file_name}': {e}")
                continue  # Try next dependency

    # If we lack any methods, return a mock instead.
    if not any(methods.values()):
        return _mock_processor(processor_module, methods)

    # If we have a processor, try to create an instance of it
    try:
        logger.debug(f"resources: {resources}")
        return processor(resources=resources, configs=configs)
    except Exception as e:
        logger.exception(f"Failed to create processor instance: {e}")
        return _mock_processor(processor_module, methods)

import inspect

def _mock_processor(processor: ModuleType, methods: dict[str, Callable]) -> MagicMock:

    processor_methods: dict[str, Callable] = {}

    # Get the function signatures of the processor methods
    processor_methods = inspect.getmembers(processor, predicate=inspect.isfunction)
    processor_async_methods = inspect.getmembers(processor, predicate=inspect.iscoroutinefunction)
    processor_methods = {name: func for name, func in processor_methods if name in methods}
    processor_async_methods = {name: func for name, func in processor_async_methods if name in methods}
    processor_methods.update(processor_async_methods)

    mock_map = { # TODO Make this dynamic based on all unique methods in the processor.
        "extract_text": "Mocked text content",
        "extract_metadata": {"mocked": "metadata"},
        "extract_structure": {"mocked": "structure"},
        "get_version": "1.0.0",
        "can_process": False,
        "open_file": "Mocked file content",
        "extract_images": "Mocked image content",
        "extract_frames": "Mocked frame content",
        "process_video_frames": "Mocked video frame content",
        "extract_features": "Mocked features",
        "open_xlsx_file": "Mocked xlsx file content",
    }

    logger.warning(f"'{processor}' processor not available, returning mock instead.")
    try:
        mock_processor = MagicMock(spec=processor)
    except Exception as e:
        logger.error(f"Failed to create spec mock processor for '{processor}': {e}")
        mock_processor = MagicMock()

    # Mock the processor methods.
    for method_name in methods.keys():
        if isinstance(method_name, str) and method_name in mock_map:
            mock_method = MagicMock(return_value=mock_map[method_name])
            setattr(mock_processor, method_name, mock_method)

        elif isinstance(method_name, tuple) and method_name[0] in mock_map:
            # For tuple, use the first element as the method name
            actual_method_name = method_name[0]
            mock_method = MagicMock(return_value=mock_map[actual_method_name])
            setattr(mock_processor, actual_method_name, mock_method)
        else:
            logger.error(f"Unknown method type: {method_name}")
            raise ValueError(f"Unknown method type: {method_name}")

    return mock_processor


def make_processors() -> dict[str, Any]: # TODO Figure out the orchestration logic of this class.
    """
    Initialize processor dependencies for handlers.

    Args:
        resources: Resources dictionary with dependencies.
        
    Returns:
        Dictionary of processor instances.
    """
    # NOTE order of dependency dictionaries are *important*.
    # Specialized dependencies are checked first, then more general ones.
    processors: dict[str, Processor] = {}

    # === Ability Processors ===
    from configs import configs
    from logger import logger
    from dependencies import dependencies

    class ProcessorResources(TypedDict):
        supported_formats: set[str]
        processor_name: str
        dependencies: dict[str, bool]
        critical_resources: list[str]

    text_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_TEXT_FORMATS,
        "processor_name": 'text_processor',
        "dependencies": {
            "generic_text": Constants.GENERIC_PLAINTEXT_PROCESSOR_AVAILABLE,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    image_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_IMAGE_FORMATS,
        "processor_name": 'image_processor',
        "dependencies": {
            "pil": dependencies.pil,
            "openai": dependencies.openai,
            "pytesseract": dependencies.pytesseract,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    video_resources = {
        "supported_formats": SupportedFormats.SUPPORTED_VIDEO_FORMATS,
        "processor_name": 'video_processor',
        "dependencies": {
            "ffmpeg": ExternalPrograms.ffmpeg,
            "ffprobe": ExternalPrograms.ffprobe,
            "cv2": dependencies.cv2,
            "pymediainfo": dependencies.pymediainfo,
        },
        "critical_resources": [
            "extract_metadata", "extract_frames", "extract_text", 
            "process_video_frames", "get_version", "open_file"
        ],
    }
    document_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.DOCUMENT_FORMAT_EXTENSIONS,
        "processor_name": 'document_processor',
        "dependencies": {
            "libreoffice": ExternalPrograms.libreoffice,
            "python_docx": dependencies.python_docx,
            "generic_text": Constants.GENERIC_PLAINTEXT_PROCESSOR_AVAILABLE,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    ebook_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.EBOOK_FORMAT_EXTENSIONS,
        "processor_name": 'ebook_processor',
        "dependencies": {
            "calibre": ExternalPrograms.calibre,
            "7-zip": ExternalPrograms.seven_zip,
            "openai": dependencies.openai,
            "pytesseract": dependencies.pytesseract,
            "generic_text": Constants.GENERIC_PLAINTEXT_PROCESSOR_AVAILABLE,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }

    resource_list = [
        image_resources, ebook_resources
    ]

    for resources in resource_list:
        try:
            temp_dict = {
                resources["processor_name"]: _make_processor(
                    processor=resources["processor_name"],
                    dependencies=resources["dependencies"],
                    supported_formats=resources["supported_formats"],
                    critical_resources=resources["critical_resources"],
                    configs=configs,
                    logger=logger,
                )
            }
        except Exception as e:
            continue
        processors.update(temp_dict)

    # Image processor (ability)
    if Constants.IMAGE_PROCESSOR_AVAILABLE:
        image_resources = {
            "supported_formats": SupportedFormats.SUPPORTED_IMAGE_FORMATS,
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
        processors["image_processor"] = _make_processor(
            processor=image_resources["processor_name"],
            dependencies=image_resources["dependencies"],
            supported_formats=image_resources["supported_formats"],
            critical_resources=image_resources["critical_resources"],
            configs=configs,
        )

    # Video processor
    if Constants.VIDEO_PROCESSOR_AVAILABLE:
        video_frame_resources = {
            "supported_formats": SupportedFormats.SUPPORTED_VIDEO_FORMATS,
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
        processors["video_processor"] = _make_processor(
            processor=video_frame_resources["processor_name"],
            dependencies=video_frame_resources["dependencies"],
            supported_formats=video_frame_resources["supported_formats"],
            critical_resources=video_frame_resources["critical_resources"],
            configs=configs,
        )

    # OCR processor (ability)
    if Constants.OCR_PROCESSOR_AVAILABLE:
        ocr_resources = {
            "supported_formats": SupportedFormats.SUPPORTED_IMAGE_FORMATS,
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
        processors["ocr_processor"] = _make_processor(
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
            "supported_formats": SupportedFormats.APPLICATION_FORMAT_EXTENSIONS['xlsx'],
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

        processors["xlsx_processor"] = _make_processor(
            processor=xlsx_resources["processor_name"],
            dependencies=xlsx_resources["dependencies"],
            supported_formats=xlsx_resources["supported_formats"],
            critical_resources=xlsx_resources["critical_resources"],
            configs=configs,
        )

    # # SVG processor # TODO Make SVG processor.
    # if Constants.SVG_PROCESSOR_AVAILABLE:
    #     svg_resources = {
    #         "supported_formats": SupportedFormats.SUPPORTED_SVG_FORMATS,
    #         "processor_name": 'svg_processor',
    #         "dependencies": {
    #             "generic_svg": SupportedFormats.GENERIC_SVG_AVAILABLE,
    #         },
    #         "critical_resources": [
    #             "extract_svg_metadata", "generate_svg_description", "process_svg_file", "get_version"
    #         ],
    #     }
    #     processors["svg_processor"] = _make_processor(
    #         processor=svg_resources["processor_name"],
    #         dependencies=svg_resources["dependencies"],
    #         supported_formats=svg_resources["supported_formats"],
    #         critical_resources=svg_resources["critical_resources"],
    #         configs=configs,
    #     )
    
    # === Text Processors ===
    
    # HTML processor
    if Constants.HTML_PROCESSOR_AVAILABLE:
        html_resources = {
            "supported_formats": SupportedFormats.SUPPORTED_HTML_FORMATS,
            "processor_name": 'html_processor',
            "dependencies": {
                "bs4": Constants.BS4_AVAILABLE,
                "generic_html": Constants.GENERIC_HTML_PROCESSOR_AVAILABLE,
            },
            "critical_resources": [
                "process_html", "get_version"
            ],
        }
        processors["html_processor"] = _make_processor(
            processor=html_resources["processor_name"],
            dependencies=html_resources["dependencies"],
            supported_formats=html_resources["supported_formats"],
            critical_resources=html_resources["critical_resources"],
            configs=configs,
        )
    
    # XML processor
    if Constants.XML_PROCESSOR_AVAILABLE:
        xml_resources = {
            "supported_formats": SupportedFormats.SUPPORTED_XML_FORMATS_SET,
            "processor_name": 'xml_processor',
            "dependencies": {
                "lxml": Constants.LXML_AVAILABLE,
            },
            "critical_resources": [
                "process_xml", "get_version"
            ],
        }
        processors["xml_processor"] = _make_processor(
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
        processors["calendar_processor"] = _make_processor(
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
        processors["csv_processor"] = _make_processor(
            processor=csv_resources["processor_name"],
            dependencies=csv_resources["dependencies"],
            supported_formats=csv_resources["supported_formats"],
            critical_resources=csv_resources["critical_resources"],
            configs=configs,
        )

    # === Application Processors ===

    # PDF processor
    processors["pdf_processor"] = _make_processor(
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
    processors["docx_processor"] = _make_processor(
        processor="docx_processor",
        resources={},
        dependencies={
            "python_docx": Constants.PYTHON_DOCX_AVAILABLE,
        },
        supported_formats={"docx"},
        critical_resources=[
            "extract_text", "extract_metadata", "extract_structure", 
            "get_version"
        ],
        configs=configs,
    )

    return processors
