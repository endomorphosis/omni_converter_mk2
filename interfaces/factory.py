"""
Interface Factory for the Omni-Converter.

This module provides a factory for creating interface instances, such as the CLI and Python API.
This allows for centralized configuration and management of interfaces.
"""
from typing import Callable


from types_ import Configs, Cli, Gui  # Prevent circular import issues


# class InterfaceFactory:
#     """
#     Factory for creating interfaces to the Omni-Converter.
    
#     This class provides methods for creating command-line and programmatic interfaces
#     to the Omni-Converter, with shared configuration and resources.
    
#     Attributes:
#         configs: Configuration settings used across all interfaces
#         resources: Dictionary of resource providers available to interfaces
#         python_api: Reference to the Python API implementation
#         cli: Reference to the CLI implementation
#     """
#     def __init__(self, 
#                  resources: dict[str, Callable] = None, 
#                  configs: Configs = None
#                  ):
#         """
#         Initialize the interface factory.
        
#         Args:
#             resources: Dictionary of resource providers for interfaces
#             configs: Configuration settings to use across interfaces.
#                 If None, default configs will be used.
#         """
#         self.configs = configs
#         self.resources = resources

#         self.python_api = self.resources['python_api']
#         self.cli = self.resources['cli']
    
#     def create_cli(self, resources: dict[str, Callable]) -> Cli:
#         """
#         Create a command-line interface.
        
#         Returns:
#             A CLI instance for command-line interaction.
            
#         Raises:
#             NotImplementedError: Currently not implemented as CLI is in main.py
#         """
#         # The CLI is currently implemented directly in main.py 
#         # # TODO Extract CLI to a separate module 'interfaces/cli.py'
#         # This is a placeholder for future refactoring
#         return self.cli(resources=resources, configs=self.configs)

#     def create_api(self, resources: dict[str, Callable]) -> PythonAPI:
#         """
#         Create a Python API interface.
        
#         Creates and configures a Python API instance with access to necessary
#         resources like batch processing and resource monitoring.
        
#         Returns:
#             A fully configured PythonAPI instance
#         """
#         return self.python_api(resources=resources, configs=self.configs)

# def interface_factory(
#     resources: dict[str, Callable] = None,
#     configs: Configs = None
# ) -> InterfaceFactory:
#     """
#     Create an interface factory instance.
    
#     Args:
#         interface_type: The type of interface to create ('cli' or 'api').
#         resources: Custom resources to use for the interface.
#         configs: Custom configuration manager to use.
        
#     Returns:
#         An InterfaceFactory instance with the specified configuration and resources.
#     """
#     return InterfaceFactory(resources=resources, configs=configs)


from batch_processor import make_batch_processor
from monitors import make_resource_monitor
from core import make_processing_pipeline
from supported_formats import SupportedFormats

from interfaces._python_api import PythonAPI
from interfaces._cli import CLI

from configs import configs
from logger import logger
from dependencies import dependencies

def make_cli() -> CLI:
    """
    Create a Python API for the Omni-Converter.
    """
    from utils.main_ import (
        list_normalizers, 
        list_output_formats, 
        show_version, 
        progress_callback, 
        list_supported_formats
    )
    resources = {
        'supported_formats': SupportedFormats.SUPPORTED_FORMATS,
        'processing_pipeline': make_processing_pipeline(),
        'batch_processor': make_batch_processor(),
        'resource_monitor': make_resource_monitor(),
        'list_supported_formats': list_supported_formats,
        'list_normalizers': list_normalizers,
        'list_output_formats': list_output_formats,
        'processing_pipeline': make_processing_pipeline(),
        'show_version': show_version,
        'progress_callback': progress_callback,
        'tqdm': dependencies.tqdm,
        'logger': logger,
    }
    return CLI(resources=resources, configs=configs)

def make_api() -> PythonAPI:
    """
    Create a Python API for the Omni-Converter.
    """
    resources = {
        'supported_formats': SupportedFormats.SUPPORTED_FORMATS,
        'processing_pipeline': make_processing_pipeline(),
        'batch_processor': make_batch_processor(),
        'resource_monitor': make_resource_monitor(),
        'logger': logger,
    }
    return PythonAPI(resources=resources,configs=configs)

def make_gui() -> None:
    """
    Create a GUI interface for the Omni-Converter.

    This function initializes the GUI with necessary resources and configurations.
    Currently, the GUI is not implemented, but this function serves as a placeholder
    for future development.
    """
    raise NotImplementedError("GUI is not implemented yet. Please use CLI or API interfaces.")