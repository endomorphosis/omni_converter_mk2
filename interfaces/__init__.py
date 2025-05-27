"""
Interfaces package for the Omni-Converter.

This package contains the interfaces used by the Omni-Converter, including:
- Python API for programmatic access
- Configuration manager for handling settings
"""
from interfaces.interface_factory import interface_factory

from configs import configs as _configs
from .python_api import PythonAPI
from .cli import CLI


def _make_resources():
    """
    Create a dictionary of resources for the interfaces.
    """
    return {
        'python_api': PythonAPI,
        'cli': CLI,  # TODO CLI is in the process of being implemented
    }

def _make_api_resources():
    """
    Create a dictionary of API resources for the interfaces.
    """
    import managers
    from format_handlers.format_registry import format_registry
    from core.processing_pipeline import processing_pipeline
    return {
        'format_registry': format_registry,
        'processing_pipeline': processing_pipeline,
        'batch_processor': managers.batch_processor.batch_processor,
        'resource_monitor': managers.resource_monitor.resource_monitor,
    }

def _make_cli_resources():
    import tqdm
    import managers
    from format_handlers.text_handler import text_handler
    from format_handlers.image_handler import image_handler
    from format_handlers.application_handler import application_handler
    from core import processing_pipeline
    import utils
    import utils.main_
    import format_handlers
    from logger import logger
    dummy_dict = {
        "pymediainfo_processor": None,
        "ffmpeg_processor": None,
        "ffprobe_processor": None,
        "cv2_processor": None,
        "pytesseract_processor": None,
        "whisper_processor": None,
        "pydub_processor": None,
    }
    return {
        'text_handler': text_handler,
        'image_handler': image_handler,
        'application_handler': application_handler,
        'audio_handler': format_handlers.audio_handler.create_audio_handler(dummy_dict),
        'video_handler': format_handlers.video_handler.create_video_handler(dummy_dict),
        'format_registry': format_handlers.format_registry.format_registry,
        'processing_pipeline': processing_pipeline.processing_pipeline,
        'batch_processor': managers.batch_processor.batch_processor,
        'resource_monitor': managers.resource_monitor.resource_monitor,
        'list_supported_formats': utils.main_.list_supported_formats.list_supported_formats,
        'show_version': utils.main_.show_version.show_version,
        'progress_callback': utils.main_.progress_callback.progress_callback,
        'list_output_formats': utils.main_.list_output_formats.list_output_formats,
        'list_normalizers': utils.main_.list_normalizers.list_normalizers,
        'tqdm': tqdm,
        'logger': logger,
    }

_factory = interface_factory(resources=_make_resources(), configs=_configs)
cli = _factory.create_cli(_make_cli_resources())
python_api = _factory.create_api(_make_api_resources())

__all__ = [
    "python_api",
    "cli,"
    "PythonAPI", # For type hinting and documentation purposes
    "CLI", # For type hinting and documentation purposes
]
