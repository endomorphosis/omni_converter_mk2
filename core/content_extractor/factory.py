"""
Factory module for creating format handlers and registries.

This module provides factory functions for creating format handlers and assembling
them into a format registry. It centralizes the creation of these components
and manages their dependencies.
"""
import os
from types_ import Callable, Logger, TypedDict

from configs import configs
from logger import logger


from ._content_extractor import ContentExtractor
from ._map_extension_to_format import map_extension_to_format
from .handlers import make_all_handlers
from file_format_detector import make_file_format_detector 
from supported_formats import SupportedFormats
from utils.filesystem import FileSystem


class _ContentExtractorResources(TypedDict):
    handlers: dict[str, str]
    file_format_detector: str
    supported_formats: set[str]
    map_extension_to_format: Callable
    read_file: Callable
    splitext: Callable
    logger: Logger


def make_content_extractor():

    handlers = make_all_handlers()

    resources: _ContentExtractorResources = {
        "capabilities": {
            "application": handlers["application"],
            "text": handlers["text"],
            "audio": handlers["audio"],
            "video": handlers["video"],
            "image": handlers["image"],
        },
        "file_format_detector": make_file_format_detector(),
        "supported_formats": SupportedFormats.SUPPORTED_FORMATS,
        "map_extension_to_format": map_extension_to_format,
        "read_file": FileSystem.read_file,
        "splitext": os.path.splitext,
        "logger": logger,
    }
    return ContentExtractor(resources=resources, configs=configs)


# def make_format_registry():
#     """
#     Initialize the format registry with all available handlers.

#     Args:
#         resources: Optional additional resources to provide.
#         configs: Configuration settings.
        
#     Returns:
#         Configured FormatRegistry instance.
#     """
#     # Create handler factories
#     logger.debug("Creating handler factories...")
#     handler_factories = make_all_handlers()

#     # Prepare resources for the registry
#     registry_resources = {
#         "file_format_detector": make_file_format_detector(),
#         "map_extension_to_format": map_extension_to_format,
#         "handler_factories": handler_factories,
#     }

#     # Create and return the registry
#     logger.info("Initializing format registry...")
#     return FormatRegistry(registry_resources, configs)

