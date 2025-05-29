
from typing import Callable


from configs import configs
from processors import make_processors
from ._text_handler import TextHandler
from ._application_handler import ApplicationHandler
from ._audio_handler import AudioHandler
from ._image_handler import ImageHandler
from ._video_handler import VideoHandler
from ._handler_capabilities import HandlerCapabilities

from supported_formats import SupportedFormats


def create_text_handler(processors):
    """
    Factory function to create a TextHandler instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of TextHandler.
    """
    resources ={
        "html_processor": processors["html_processor"],
        "xml_processor": processors["xml_processor"],
        "calendar_processor": processors["calendar_processor"],
        "plaintext_processor": processors["plaintext_processor"],
        "csv_processor": processors["csv_processor"],
        "format_extensions": SupportedFormats.TEXT_FORMAT_EXTENSIONS,
        "supported_formats": SupportedFormats.SUPPORTED_TEXT_FORMATS,
        "capabilities": HandlerCapabilities.TEXT_HANDLER_CAPABILITIES,
    }

    # Create and return the TextHandler instance
    return TextHandler(resources=resources, configs=configs)


def create_application_handler(processors) -> ApplicationHandler:
    """
    Factory function to create an ApplicationHandler instance.
    
    Returns:
        An instance of ApplicationHandler.
    """
    resources = {
        "pdf_processor": processors["pdf_processor"],
        "json_processor": processors["json_processor"],
        "docx_processor": processors["docx_processor"],
        "xlsx_processor": processors["xlsx_processor"],
        "zip_processor": processors["zip_processor"],
        "format_extensions": SupportedFormats.APPLICATION_FORMAT_EXTENSIONS,
        "supported_formats": SupportedFormats.SUPPORTED_APPLICATION_FORMATS,
        "capabilities": HandlerCapabilities.APPLICATION_HANDLER_CAPABILITIES,
    }
    return ApplicationHandler(resources=resources, configs=configs)


def create_audio_handler(processors):
    """
    Factory function to create an AudioHandler instance.
    
    Returns:
        An instance of AudioHandler.
    """
    resources = {
        "audio_processor": processors["audio_processor"],
        "transcription_processor": processors["transcription_processor"],
        "format_extensions": SupportedFormats.AUDIO_FORMAT_EXTENSIONS,
        "supported_formats": SupportedFormats.SUPPORTED_AUDIO_FORMATS,
        "capabilities": HandlerCapabilities.AUDIO_HANDLER_CAPABILITIES
    }
    
    # Create and return the AudioHandler instance
    return AudioHandler(resources=resources, configs=configs)

def create_video_handler(processors):
    """
    Factory function to create a VideoHandler instance.

    Returns:
        An instance of VideoHandler.
    """
    resources = {
        "video_processor": processors["video_processor"],
        "transcription_processor": processors["transcription_processor"],
        "format_extensions": SupportedFormats.VIDEO_FORMAT_EXTENSIONS,
        "supported_formats": SupportedFormats.SUPPORTED_VIDEO_FORMATS,
        "capabilities": HandlerCapabilities.VIDEO_HANDLER_CAPABILITIES,
    }
    # Create and return the VideoHandler instance
    return VideoHandler(resources=resources, configs=configs)


def create_image_handler(processors):
    resources = {
        "image_processor": processors["image_processor"],
        "svg_processor": processors["svg_processor"], 
        "ocr_processor": processors["ocr_processor"],
        "format_extensions": SupportedFormats.IMAGE_FORMAT_EXTENSIONS,
        "supported_formats": SupportedFormats.SUPPORTED_IMAGE_FORMATS,
        "capabilities": HandlerCapabilities.IMAGE_HANDLER_CAPABILITIES
    }
    return ImageHandler(resources=resources, configs=configs)


def make_all_handlers() -> dict[str, Callable]:
    """
    Create factory functions for all format handlers.
    
    Args:
        resources: Optional additional resources to provide to handlers.
        configs: Configuration settings.
        
    Returns:
        Dictionary mapping handler types to factory functions.
    """
    # Initialize processors for dependency injection
    processors = make_processors()

    # Create a dictionary of factory functions for each handler type
    handler_factories = {
        "audio": create_audio_handler(processors),
        "image": create_image_handler(processors),
        "text": create_text_handler(processors),
        "video": create_video_handler(processors),
        "application": create_application_handler(processors),
    }

    # Return the factory functions
    return handler_factories