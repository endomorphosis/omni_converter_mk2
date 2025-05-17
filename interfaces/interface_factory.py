"""
Interface Factory for the Omni-Converter.

This module provides a factory for creating interface instances, such as the CLI and Python API.
This allows for centralized configuration and management of interfaces.
"""

from typing import Any, Dict, Optional

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
    
    def __init__(self, custom_config_manager=None):
        """
        Initialize the interface factory.
        
        Args:
            custom_config_manager: Custom configuration manager to use.
                If None, the global configs will be used.
        """
        self.configs = custom_config_manager or configs
    
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
        return PythonAPI(custom_config_manager=self.configs)
    
    def get_config_manager(self) -> Configs:
        """
        Get the configuration manager used by this factory.
        
        Returns:
            The configuration manager instance.
        """
        return self.configs
    
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
        if interface_type.lower() == 'cli':
            return self.create_cli()
        elif interface_type.lower() == 'api':
            return self.create_api()
        else:
            raise ValueError(f"Unsupported interface type: {interface_type}")


# Global interface factory instance
interface_factory = InterfaceFactory()