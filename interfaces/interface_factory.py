"""
Interface Factory for the Omni-Converter.

This module provides a factory for creating interface instances, such as the CLI and Python API.
This allows for centralized configuration and management of interfaces.
"""
from typing import Callable, TypeVar

DataClass = TypeVar('DataClass')
PythonAPI = TypeVar('PythonAPI') # Avoid having an extra import just for type hinting
Cli = TypeVar('CLI') # Avoid having an extra import just for type hinting

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



