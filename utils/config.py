"""
Configuration manager for the Omni-Converter.

This module provides a configuration manager that handles loading, saving, and validating
configuration settings for the Omni-Converter.
"""

import json
import os
from typing import Any, Dict, Optional, Union


class ConfigManager:
    """
    Configuration manager for the Omni-Converter.
    
    Handles loading, saving, and validating configuration settings.
    
    Attributes:
        default_config (dict): The default configuration settings.
        config_path (str): The path to the configuration file.
        current_config (dict): The current configuration settings.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: The path to the configuration file. If None, uses the default path.
        """
        # Default configuration settings
        self.default_config: Dict[str, Any] = {
            # Resource limits
            'resources': {
                'memory_limit_gb': 6,        # 6GB RAM limit
                'cpu_limit_percent': 80,     # 80% CPU utilization limit
                'timeout_seconds': 3600,     # 1 hour timeout
                'batch_size': 100            # Maximum number of files to process in one batch
            },
            
            # Format support settings
            'formats': {
                'text': ['html', 'xml', 'plain', 'calendar', 'csv'],
                'image': ['jpeg', 'png', 'gif', 'webp', 'svg'],
                'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
                'video': ['mp4', 'webm', 'avi', 'mkv', 'mov'],
                'application': ['pdf', 'json', 'zip', 'docx', 'xlsx']
            },
            
            # Security settings
            'security': {
                'max_file_size_mb': 100,     # Maximum file size in MB
                'sandbox_enabled': True,     # Enable sandbox for file processing
                'allowed_formats': [],       # Empty list means all formats in the 'formats' section are allowed
                'sanitize_output': True      # Sanitize output to remove potential security risks
            },
            
            # Processing settings
            'processing': {
                'continue_on_error': True,   # Continue processing batch even if some files fail
                'extract_metadata': True,    # Extract metadata from files
                'normalize_text': True,      # Normalize extracted text
                'quality_threshold': 0.9     # Minimum quality score for text extraction
            },
            
            # Output settings
            'output': {
                'format': 'txt',             # Default output format
                'include_metadata': True,    # Include metadata in output
                'preserve_structure': True,  # Attempt to preserve document structure
                'encoding': 'utf-8'          # Output file encoding
            }
        }
        
        # Set config path
        self.config_path = config_path or os.path.join(os.path.expanduser('~'), '.omni_converter', 'config.json')
        
        # Load the configuration or use defaults
        try:
            self.current_config = self.load_config(self.config_path)
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_config = self.default_config.copy()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: The path to the configuration file.
            
        Returns:
            The loaded configuration as a dictionary.
            
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file is not valid JSON.
        """
        # Check if the file exists
        if not os.path.exists(config_path):
            return self.default_config.copy()
        
        # Load the configuration
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        # Merge with defaults to ensure all required settings are present
        merged_config = self.default_config.copy()
        self._recursive_update(merged_config, loaded_config)
        
        return merged_config
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save the current configuration to a file.
        
        Args:
            config_path: The path to save the configuration to. If None, uses the current path.
            
        Returns:
            True if the configuration was saved successfully, False otherwise.
        """
        path = config_path or self.config_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        try:
            with open(path, 'w') as f:
                json.dump(self.current_config, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The key to get the value for, using dot notation for nested keys.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value, or the default if the key is not found.
        """
        # Split the key by dots to handle nested keys
        keys = key.split('.')
        
        # Start with the current config
        value = self.current_config
        
        # Traverse the nested dictionaries
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.
        
        Args:
            key: The key to set the value for, using dot notation for nested keys.
            value: The value to set.
        """
        # Split the key by dots to handle nested keys
        keys = key.split('.')
        
        # Start with the current config
        config = self.current_config
        
        # Traverse the nested dictionaries
        for i, k in enumerate(keys[:-1]):
            # Create intermediate dictionaries if they don't exist
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def reset_to_defaults(self) -> None:
        """Reset the configuration to default values."""
        self.current_config = self.default_config.copy()
    
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if the configuration is valid, False otherwise.
        """
        # Implement validation logic here
        # For now, just check if all required keys are present
        try:
            # Check resource limits
            assert isinstance(self.current_config['resources']['memory_limit_gb'], (int, float))
            assert isinstance(self.current_config['resources']['cpu_limit_percent'], (int, float))
            assert isinstance(self.current_config['resources']['timeout_seconds'], (int, float))
            assert isinstance(self.current_config['resources']['batch_size'], int)
            
            # Check format support
            assert isinstance(self.current_config['formats'], dict)
            for category, formats in self.current_config['formats'].items():
                assert isinstance(formats, list)
            
            # Check security settings
            assert isinstance(self.current_config['security']['max_file_size_mb'], (int, float))
            assert isinstance(self.current_config['security']['sandbox_enabled'], bool)
            assert isinstance(self.current_config['security']['allowed_formats'], list)
            assert isinstance(self.current_config['security']['sanitize_output'], bool)
            
            # Check processing settings
            assert isinstance(self.current_config['processing']['continue_on_error'], bool)
            assert isinstance(self.current_config['processing']['extract_metadata'], bool)
            assert isinstance(self.current_config['processing']['normalize_text'], bool)
            assert isinstance(self.current_config['processing']['quality_threshold'], (int, float))
            
            # Check output settings
            assert isinstance(self.current_config['output']['format'], str)
            assert isinstance(self.current_config['output']['include_metadata'], bool)
            assert isinstance(self.current_config['output']['preserve_structure'], bool)
            assert isinstance(self.current_config['output']['encoding'], str)
            
            return True
        except (KeyError, AssertionError):
            return False
    
    def _recursive_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a dictionary with values from another dictionary.
        
        Args:
            target: The dictionary to update.
            source: The dictionary to get values from.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._recursive_update(target[key], value)
            else:
                target[key] = value


# Global configuration manager instance
config_manager = ConfigManager()