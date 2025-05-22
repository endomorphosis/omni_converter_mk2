"""
Interface Factory for the Omni-Converter.

This module provides a factory for creating interface instances, such as the CLI and Python API.
This allows for centralized configuration and management of interfaces.
"""
from typing import Any, Callable, Optional


from utils.configs import Configs, configs
from interfaces.python_api import PythonAPI





class InterfaceFactory:
    """
    Factory for creating interfaces to the Omni-Converter.
    
    This class provides methods for creating command-line and programmatic interfaces
    to the Omni-Converter, with shared configuration and resources.
    
    Attributes:
        configs: The configuration manager to use for all interfaces.
    """
    
    def __init__(self, 
                 resources: dict[str, Callable] = None, 
                 configs: Configs = None
                 ):
        """
        Initialize the interface factory.
        
        Args:
            custom_config_manager: Custom configuration manager to use.
                If None, the global configs will be used.
        """
        self.configs = configs
        self.resources = resources

        self.python_api = self.resources['python_api']
        self.cli = self.resources['cli']
    
    def create_cli(self):
        """
        Create a command-line interface.
        
        Returns:
            A CommandLineInterface instance. Currently, this is implemented directly 
            in main.py, so this method is a placeholder for future refactoring.
        """
        # The CLI is currently implemented directly in main.py
        # This is a placeholder for future refactoring
        raise NotImplementedError(
            "The CLI is currently implemented directly in main.py. "
            "Use python main.py --help for CLI usage."
        )

    def create_api(self) -> PythonAPI:
        """
        Create a Python API.
        
        Returns:
            A PythonAPI instance with the factory's configuration manager.
        """
        from managers.batch_processor import batch_processor
        from managers.resource_monitor import resource_monitor
        resources = {
            'batch_processor': batch_processor,
            'resource_monitor': resource_monitor,
        }
        return PythonAPI(resources=resources, configs=self.configs)

    def create_interface(self, interface_type: str, **kwargs: Any):
        """
        Create an interface of the specified type.
        
        Args:
            interface_type: The type of interface to create ('cli' or 'api').
            **kwargs: Additional keyword arguments to pass to the interface constructor.
            
        Returns:
            An interface instance of the specified type.
            
        Raises:
            ValueError: If the interface type is not supported.
        """
        match interface_type.lower():
            case 'cli':
                return self.create_cli()
            case 'api':
                return self.create_api()
            case _:
                raise ValueError(f"Unsupported interface type: {interface_type}")

resources = {
    'python_api': PythonAPI,
    'cli': None,  # TODO CLI is not implemented yet
}

# Global interface factory instance
interface_factory = InterfaceFactory(resources=resources,configs=configs)
