"""
Interface Factory for the Omni-Converter.

This module provides a factory for creating interface instances, such as the CLI and Python API.
This allows for centralized configuration and management of interfaces.
"""
from typing import Callable




class InterfaceFactory:
    """
    Factory for creating interfaces to the Omni-Converter.
    
    This class provides methods for creating command-line and programmatic interfaces
    to the Omni-Converter, with shared configuration and resources.
    
    Attributes:
        configs: Configuration settings used across all interfaces
        resources: Dictionary of resource providers available to interfaces
        python_api: Reference to the Python API implementation
        cli: Reference to the CLI implementation
    """
    from types_ import DataClass, PythonAPI, Cli # Prevent circular import issues

    def __init__(self, 
                 resources: dict[str, Callable] = None, 
                 configs: 'DataClass' = None
                 ):
        """
        Initialize the interface factory.
        
        Args:
            resources: Dictionary of resource providers for interfaces
            configs: Configuration settings to use across interfaces.
                If None, default configs will be used.
        """
        self.configs = configs
        self.resources = resources

        self.python_api = self.resources['python_api']
        self.cli = self.resources['cli']
    
    def create_cli(self, resources: dict[str, Callable]) -> Cli:
        """
        Create a command-line interface.
        
        Returns:
            A CLI instance for command-line interaction.
            
        Raises:
            NotImplementedError: Currently not implemented as CLI is in main.py
        """
        # The CLI is currently implemented directly in main.py # TODO Extract CLI to a separate module 'interfaces/cli.py'
        # This is a placeholder for future refactoring
        return self.cli(resources=resources, configs=self.configs)

    def create_api(self, resources: dict[str, Callable]) -> PythonAPI:
        """
        Create a Python API interface.
        
        Creates and configures a Python API instance with access to necessary
        resources like batch processing and resource monitoring.
        
        Returns:
            A fully configured PythonAPI instance
        """
        return self.python_api(resources=resources, configs=self.configs)

def interface_factory(
    resources: dict[str, Callable] = None,
    configs: 'DataClass' = None
) -> InterfaceFactory:
    """
    Create an interface factory instance.
    
    Args:
        interface_type: The type of interface to create ('cli' or 'api').
        resources: Custom resources to use for the interface.
        configs: Custom configuration manager to use.
        
    Returns:
        An InterfaceFactory instance with the specified configuration and resources.
    """
    return InterfaceFactory(resources=resources, configs=configs)



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
    from batch_processor import make_batch_processor
    from monitors._resource_monitor import resource_monitor




    import monitors
    from core.content_extractor.format_registry import format_registry
    from core.processing_pipeline import processing_pipeline
    return {
        'format_registry': format_registry,
        'processing_pipeline': processing_pipeline,
        'batch_processor': monitors.batch_processor.batch_processor,
        'resource_monitor': monitors.resource_monitor.resource_monitor,
    }

def _make_cli_resources():
    import tqdm
    import monitors
    from core.content_extractor.text_handler import text_handler
    from core.content_extractor.image_handler import image_handler
    from core.content_extractor.application_handler import application_handler
    from core import make_processing_pipeline
    import utils
    import utils.main_
    import extractors
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
        'audio_handler': core.content_extractor.audio_handler.create_audio_handler(dummy_dict),
        'video_handler': core.content_extractor.video_handler.create_video_handler(dummy_dict),
        'format_registry': core.content_extractor.format_registry.format_registry,
        'processing_pipeline': make_processing_pipeline(),
        'batch_processor': monitors.batch_processor.batch_processor,
        'resource_monitor': monitors.resource_monitor.resource_monitor,
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