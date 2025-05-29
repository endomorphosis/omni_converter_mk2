"""
Factory module for creating format handlers and registries.

This module provides factory functions for creating format handlers and assembling
them into a format registry. It centralizes the creation of these components
and manages their dependencies.
"""
from configs import configs
from logger import logger

from .format_registry import FormatRegistry

from handlers import make_all_handlers
from supported_formats import SupportedFormats

from utils.filesystem import FileSystem

from file_format_detector import make_file_format_detector 
from ._map_extension_to_format import map_extension_to_format
from .content_extractor import ContentExtractor


def make_content_extractor(): # TODO
    resources = {
        "handlers": {
            "application": create_application_handler(),
            "text": create_text_handler(),
            "audio": create_audio_handler(),
            "video": create_video_handler(),
            "image": create_image_handler(),
        },
        "file_format_detector": make_file_format_detector(),
        "supported_formats": SupportedFormats.SUPPORTED_FORMATS,
        "map_extension_to_format": map_extension_to_format,
        "read_file": FileSystem.read_file,
    }
    return ContentExtractor(resources=resources, configs=configs)


def make_format_registry():
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
    handler_factories = make_all_handlers()

    # Prepare resources for the registry
    registry_resources = {
        "file_format_detector": make_file_format_detector(),
        "map_extension_to_format": map_extension_to_format,
        "handler_factories": handler_factories,
    }

    # Create and return the registry
    logger.info("Initializing format registry...")
    return FormatRegistry(registry_resources, configs)

