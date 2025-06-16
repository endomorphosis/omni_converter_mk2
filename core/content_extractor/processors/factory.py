
from __future__ import annotations
from contextlib import contextmanager
import importlib
from io import BytesIO
import os
from typing import Any, TypeVar, TypedDict
from unittest.mock import MagicMock

from core.content_extractor._content_extractor_constants import Constants
from supported_formats import SupportedFormats
from external_programs import ExternalPrograms
from logger import logger


from types_ import Any, TypeVar, TypedDict, Callable, Configs, Logger, ModuleType, Union, Processor, Optional

from .fallbacks.fallback_processor import FallbackProcessor


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

# class _MakeProcessor:

#     def __init__(
#         self,
#         processor: str = None,
#         resources: dict[str, Callable] = None,
#         dependencies: dict[str, ModuleType] = None,
#         supported_formats: set[str] = None,
#         critical_resources: list[str] = None,
#         optional_resources: list[str] = None,
#         logger: Optional[Logger] = None,
#         configs: Configs = None,
#     ) -> None:
#         self.processor = processor
#         self.resources = resources
#         self.dependencies = dependencies
#         self.supported_formats = supported_formats
#         self.critical_resources = critical_resources
#         self.optional_resources = optional_resources
#         self.logger = logger
#         self.configs = configs

#         self.by_ability_dir = 'core.content_extractor.processors.by_ability'
#         self.by_mime_type_dir = 'core.content_extractor.processors.by_mime_type'
#         self.dependency_folder = 'core.content_extractor.processors.by_dependency'
#         self.fallbacks_dir = 'core.content_extractor.processors.fallbacks'

#     def make(self):
#         processor_module: ModuleType | str = None
#         methods: dict[str, Callable] = {}



def _make_processor(
    processor: str = None,
    resources: dict[str, Callable] = None,
    dependencies: dict[str, ModuleType] = None,
    supported_formats: set[str] = None,
    critical_resources: list[str] = None,
    optional_resources: list[str] = None,
    logger: Optional[Logger] = None,
    configs: Configs = None,
) -> Processor | MagicMock:
    """
    Factory function to create processors en-masse.

    Args:
        processor: The name of the processor to create.
        resources: Dictionary of callables.
        dependencies: Class of cached dependencies.
        supported_formats: Set of formats supported by this processor.
        critical_resources: List of critical resources required by the processor.
        optional_resources: List of optional resources for the processor.
        logger: Logger instance.
        configs: Pydantic BaseModel of external configurations.

    Returns:
        An instance of processor, or a MagicMock if the processor is not available.
    """
    by_ability_dir = 'core.content_extractor.processors.by_ability'
    by_mime_type_dir = 'core.content_extractor.processors.by_mime_type'
    dependency_folder = 'core.content_extractor.processors.by_dependency'
    fallbacks_dir = 'core.content_extractor.processors.fallbacks'
    processor_module: ModuleType | str = None

    resources = {
        "supported_formats": supported_formats,
        "processor_name": processor,
        "processor_available": True,
    }
    methods: dict[str, Callable] = {}
    if logger is None:
        from logger import logger
    resources["logger"] = logger

    # Add critical resource names as keys to the resources dictionary.
    for func in critical_resources:
        if isinstance(func, str):
            methods[func] = None

    # Import the processor module dynamically based on the processor name.
    for folder in [by_ability_dir, by_mime_type_dir]:
        try:
            processor_string = f'{folder}.{processor}'
            logger.debug(f"Trying to import processor module: {processor_string}")
            processor_module = importlib.import_module(processor_string)
            processor = getattr(processor_module, _snake_to_pascal_case(processor), None)
            break
        except ImportError:
            continue
    else:
        processor_module = processor
        return _mock_processor(processor_module, methods)

    # Cycle through available dependencies until we have all the methods we need.
    # First come, first served.
    # We do this for a variety of reasons, such as:
    # - Some dependencies only provide certain methods. For example, PIL does not have text processing methods.
    # - Some dependencies may not be available, corrupted, or out-of-date (e.g., OpenAI API).
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

    if processor is not None:
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
    processor_name = processor if isinstance(processor, str) else processor.__name__

    logger.warning(f"'{processor_name}' processor not available, returning mock instead.")
    try:
        mock_processor = MagicMock(spec=processor)
    except Exception as e:
        logger.error(f"Failed to create spec mock processor for '{processor}': {e}")
        mock_processor = MagicMock()

    # Mock the processor methods.
    for method_name in methods.keys():
        # Heuristic approach based on method name
        if method_name not in mock_map:
            if "process" in method_name:
                mock_map[method_name] = "Mocked process result"
            elif "extract" in method_name:
                mock_map[method_name] = "Mocked extract result"
            elif "open" in method_name:
                mock_map[method_name] = "Mocked open result"

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



def _mock_callable(mock_obj: MagicMock, name: str):
    """
    Create a mock callable object and dynamically set its return value.
    
    Returns:
        A MagicMock object that can be called like a function.
    """
    mock_map = { # TODO Make this dynamic based on all unique methods in the processor.
        "extract_text": "Mocked text content",
        "extract_metadata": {"mocked": "metadata"},
        "extract_structure": [{"mocked": "structure"}],
        "get_version": "1.0.0",
        "can_process": False,
        "process": ("Mocked process result", {"mocked": "metadata"}, [{"mocked": "structure"}]),
        "open_file": BytesIO(b'Mocked binary data'),
        "extract_images": "Mocked image content",
        "extract_frames": "Mocked frame content",
        "process_video_frames": "Mocked video frame content",
        "extract_features": "Mocked features",
        "open_xlsx_file": BytesIO(b'Mocked xlsx data'),
    }
    if name not in mock_map:
        if "process" in name:
            mock_map[name] = "Mocked process result"
        elif "extract" in name:
            mock_map[name] = "Mocked extract result"
        elif "open" in name:
            mock_map[name] = mock_map["open_file"]

    mock_callable_return = MagicMock(return_value=mock_map[name])
    setattr(mock_obj, name, mock_callable_return)
    return mock_obj


class ProcessorResources(TypedDict):
    supported_formats: set[str]
    processor_name: str
    dependencies: dict[str, Any]
    critical_resources: list[str]
    optional_resources: list[str] | None


def make_processors() -> dict[str, Processor]: # TODO Figure out the orchestration logic of this class.
    """
    Initialize processor dependencies for handlers.

    Returns:
        Dictionary of processor instances.
    """
    # NOTE order of dependency dictionaries are *important*.
    # Specialized dependencies are checked first, then more general ones.
    processors: dict[str, Processor] = {}

    # === Ability Processors ===
    # These processors are composite processors that are not specific to a MIME type or file format.
    # Instead, they are based on specific abilities or functionalities, such as OCR, Transcription, etc.
    from configs import configs
    from logger import logger
    from dependencies import dependencies

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
            "anthropics": dependencies.anthropic,
            "pytesseract": dependencies.pytesseract,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    audio_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_AUDIO_FORMATS,
        "processor_name": 'audio_processor',
        "dependencies": {
            "pydub": dependencies.pydub,
            "openai": dependencies.openai,
            "whisper": dependencies.whisper,
            # "pyaudio": Constants.PYAUDIO_AVAILABLE,
            # "speech_recognition": Constants.SPEECH_RECOGNITION_AVAILABLE,
            # "generic_audio": Constants.GENERIC_AUDIO_PROCESSOR_AVAILABLE,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    video_resources: ProcessorResources = {
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
    # Ex: Microsoft document formats docx, doc
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
    # Ex: ebook formats like epub, mobi, azw3, etc.
    # NOTE Does not include PDF, DOCX, or other document formats.
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

    html_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_HTML_FORMATS,
        "processor_name": 'html_processor',
        "dependencies": {
            "bs4": dependencies.bs4,
            "generic_html": Constants.GENERIC_HTML_PROCESSOR_AVAILABLE,
        },
        "critical_resources": [
            "process_html", "get_version"
        ],
    }
    plaintext_resources: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_PLAINTEXT_FORMATS,
        "processor_name": 'plaintext_processor',
        "dependencies": {
            "generic_text": FallbackProcessor,
        },
    }

    only_mocks: ProcessorResources = {
        "supported_formats": SupportedFormats.SUPPORTED_FORMATS,
        "processor_name": 'only_mocks',
        "dependencies": {
            "mock": True,
        },
        "critical_resources": [
            "extract_text", "extract_metadata", "extract_structure",
            "get_version", "open_file"
        ],
    }
    # TODO Undo these mocks when the processors are implemented.
    transcription_resources = only_mocks.copy()
    transcription_resources["processor_name"] = 'transcription_processor'
    svg_resources = only_mocks.copy()
    svg_resources["processor_name"] = 'svg_processor'
    xml_resources = only_mocks.copy()
    xml_resources["processor_name"] = 'xml_processor'
    calendar_resources = only_mocks.copy()
    calendar_resources["processor_name"] = 'calendar_processor'
    csv_resources = only_mocks.copy()
    csv_resources["processor_name"] = 'csv_processor'
    plaintext_resources = only_mocks.copy()
    plaintext_resources["processor_name"] = 'plaintext_processor'
    pdf_resources = only_mocks.copy()
    pdf_resources["processor_name"] = 'pdf_processor'
    json_processor_resources = only_mocks.copy()
    json_processor_resources["processor_name"] = 'json_processor'
    docx_processor_resources = only_mocks.copy()
    docx_processor_resources["processor_name"] = 'docx_processor'
    zip_processor_resources = only_mocks.copy()
    zip_processor_resources["processor_name"] = 'zip_processor'
    raster_image_resources = only_mocks.copy()
    raster_image_resources["processor_name"] = 'raster_image_processor'
    vector_image_resources = only_mocks.copy()
    vector_image_resources["processor_name"] = 'vector_image_processor'

    resource_list = [
        image_resources, audio_resources, text_resources, video_resources,
        html_resources, xml_resources, calendar_resources, csv_resources, plaintext_resources,
        ebook_resources, transcription_resources, svg_resources, pdf_resources,
        json_processor_resources, docx_processor_resources, zip_processor_resources,
        raster_image_resources, vector_image_resources
    ]

    for resources in resource_list:
        try:
            temp_dict = {
                resources["processor_name"]: _make_processor(
                    processor=resources["processor_name"],
                    dependencies=resources["dependencies"],
                    supported_formats=resources["supported_formats"],
                    critical_resources=resources["critical_resources"],
                    optional_resources=resources.get("optional_resources", None),
                    configs=configs,
                    logger=logger,
                )
            }
        except Exception as e:
            continue
            #raise RuntimeError(f"Error making processor: {e}") from e
        processors.update(temp_dict)

    # === MIME-Type Specific Processors ===
    # These processors are specific to MIME types or file formats.
    # They can use ability processors to augment their functionality.
    # However, these are optional and not required for basic functionality.


    for resources in resource_list:
        try:
            temp_dict = {
                resources["processor_name"]: _make_processor(
                    processor=resources["processor_name"],
                    dependencies=resources["dependencies"],
                    supported_formats=resources["supported_formats"],
                    critical_resources=resources["critical_resources"],
                    optional_resources=resources.get("optional_resources", None),
                    configs=configs,
                    logger=logger,
                )
            }
        except Exception as e:
            continue
        processors.update(temp_dict)

    # === Mocked Processors ===
    # These processors are used for testing and development purposes.
    # Since they lack implementations, we intentionally mock them to prevent errors.

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

    # XML processor
    # if Constants.XML_PROCESSOR_AVAILABLE:
    #     xml_resources = {
    #         "supported_formats": SupportedFormats.SUPPORTED_XML_FORMATS_SET,
    #         "processor_name": 'xml_processor',
    #         "dependencies": {
    #             "lxml": Constants.LXML_AVAILABLE,
    #         },
    #         "critical_resources": [
    #             "process_xml", "get_version"
    #         ],
    #     }
    #     processors["xml_processor"] = _make_processor(
    #         processor=xml_resources["processor_name"],
    #         dependencies=xml_resources["dependencies"],
    #         supported_formats=xml_resources["supported_formats"],
    #         critical_resources=xml_resources["critical_resources"],
    #         configs=configs,
    #     )
    
    # Calendar processor
    # if Constants.CALENDAR_PROCESSOR_AVAILABLE:
    #     calendar_resources = {
    #         "supported_formats": Constants.SUPPORTED_CALENDAR_FORMATS_SET,
    #         "processor_name": 'calendar_processor',
    #         "dependencies": {
    #             "icalendar": Constants.ICALENDAR_AVAILABLE,
    #         },
    #         "critical_resources": [
    #             "process_calendar", "get_version"
    #         ],
    #     }
    #     processors["calendar_processor"] = _make_processor(
    #         processor=calendar_resources["processor_name"],
    #         dependencies=calendar_resources["dependencies"],
    #         supported_formats=calendar_resources["supported_formats"],
    #         critical_resources=calendar_resources["critical_resources"],
    #         configs=configs,
    #     )
    
    # CSV processor
    # if Constants.CSV_PROCESSOR_AVAILABLE:
    #     csv_resources = {
    #         "supported_formats": Constants.SUPPORTED_CSV_FORMATS_SET,
    #         "processor_name": 'csv_processor',
    #         "dependencies": {
    #             "pandas": Constants.PANDAS_AVAILABLE,
    #         },
    #         "critical_resources": [
    #             "process_csv", "get_version"
    #         ],
    #     }
    #     processors["csv_processor"] = _make_processor(
    #         processor=csv_resources["processor_name"],
    #         dependencies=csv_resources["dependencies"],
    #         supported_formats=csv_resources["supported_formats"],
    #         critical_resources=csv_resources["critical_resources"],
    #         configs=configs,
    #     )

    # === Application Processors ===

    # PDF processor
    # processors["pdf_processor"] = _make_processor(
    #     processor="pdf_processor",
    #     resources={},
    #     dependencies={
    #         "pypdf2": Constants.PYPDF2_AVAILABLE,
    #     },
    #     supported_formats={"pdf"},
    #     critical_resources=[
    #         "extract_text", "extract_metadata", "extract_structure", 
    #         "get_version"
    #     ],
    #     configs=configs,
    # )

    # DOCX processor
    # processors["docx_processor"] = _make_processor(
    #     processor="docx_processor",
    #     resources={},
    #     dependencies={
    #         "python_docx": Constants.PYTHON_DOCX_AVAILABLE,
    #     },
    #     supported_formats={"docx"},
    #     critical_resources=[
    #         "extract_text", "extract_metadata", "extract_structure", 
    #         "get_version"
    #     ],
    #     configs=configs,
    # )

    return processors
