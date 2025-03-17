"""
Python API for the Omni-Converter.

This module provides a programmatic interface to the Omni-Converter functionality,
allowing Python applications to convert files to text without using the command-line interface.
"""

import os
from typing import Any, Dict, List, Optional, Union

from utils.config import config_manager
from format_handlers.format_registry import format_registry
from core.processing_pipeline import processing_pipeline
from core.processing_result import ProcessingResult
from managers.batch_processor import batch_processor
from managers.batch_result import BatchResult
from managers.resource_monitor import resource_monitor


class PythonAPI:
    """
    Python API for the Omni-Converter.
    
    This class provides methods for programmatically using the Omni-Converter functionality,
    including single file conversion, batch processing, and configuration management.
    
    Attributes:
        config_manager: The configuration manager to use.
        batch_processor: The batch processor to use.
    """
    
    def __init__(
        self,
        custom_config_manager=None,
        custom_batch_processor=None,
        custom_resource_monitor=None
    ):
        """
        Initialize the Python API.
        
        Args:
            custom_config_manager: Custom configuration manager to use.
                If None, the global config_manager will be used.
            custom_batch_processor: Custom batch processor to use.
                If None, the global batch_processor will be used.
            custom_resource_monitor: Custom resource monitor to use.
                If None, the global resource_monitor will be used.
        """
        self.config_manager = custom_config_manager or config_manager
        self.batch_processor = custom_batch_processor or batch_processor
        self.resource_monitor = custom_resource_monitor or resource_monitor
    
    def convert_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Convert a single file to text.
        
        Args:
            file_path: The path to the file to convert.
            output_path: The path to write the output to.
                If None, the text is still extracted but not written to a file.
            options: Conversion options. If None, default options are used.
                
        Returns:
            A ProcessingResult object with the result of the conversion.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not valid for conversion.
        """
        # Validate file existence
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Not a file: {file_path}")
        
        # Prepare options from config if none provided
        if options is None:
            options = self._get_default_options()
        
        # Process the file using the processing pipeline
        result = processing_pipeline.process_file(file_path, output_path, options)
        
        return result
    
    def convert_batch(
        self,
        file_paths: Union[List[str], str],
        output_dir: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        show_progress: bool = False
    ) -> BatchResult:
        """
        Convert multiple files to text.
        
        Args:
            file_paths: List of file paths to convert, or a directory to recursively process.
            output_dir: Directory to write output files to. 
                If None, text is still extracted but not written to files.
            options: Conversion options. If None, default options are used.
            show_progress: Whether to show a progress bar (if in interactive environment).
            
        Returns:
            A BatchResult object with the results of the batch conversion.
        """
        # Prepare options from config if none provided
        if options is None:
            options = self._get_default_options()
        
        # Configure batch processor from options
        if "batch_size" in options:
            self.batch_processor.set_max_batch_size(options["batch_size"])
        
        if "continue_on_error" in options:
            self.batch_processor.set_continue_on_error(options["continue_on_error"])
        
        if "max_workers" in options and "parallel" in options and options["parallel"]:
            self.batch_processor.set_max_workers(options["max_workers"])
        else:
            self.batch_processor.set_max_workers(1)  # Sequential mode
        
        # Configure resource limits if specified
        if ("max_cpu" in options and options["max_cpu"] is not None) or \
           ("max_memory" in options and options["max_memory"] is not None):
            self.resource_monitor.set_resource_limits(
                cpu_limit=options.get("max_cpu"),
                memory_limit=options.get("max_memory")
            )
        
        # Process the batch
        batch_result = self.batch_processor.process_batch(
            file_paths=file_paths,
            output_dir=output_dir,
            options=options,
            progress_callback=None  # Progress callback is not used by the API
        )
        
        return batch_result
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get all supported formats, organized by category.
        
        Returns:
            A dictionary mapping format categories to lists of supported formats.
        """
        return format_registry.get_formats_by_category()
    
    def set_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        Set multiple configuration values at once.
        
        Args:
            config_dict: A dictionary of configuration values to set.
                Keys can use dot notation for nested settings.
                
        Returns:
            True if the configuration was successfully set, False otherwise.
        """
        try:
            for key, value in config_dict.items():
                self.config_manager.set_config_value(key, value)
            return True
        except Exception:
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            The current configuration as a dictionary.
        """
        return self.config_manager.current_config
    
    def _get_default_options(self) -> Dict[str, Any]:
        """
        Get default options from configuration.
        
        Returns:
            Default options as a dictionary.
        """
        options = {
            # Output options
            "format": self.config_manager.get_config_value("output.format", "txt"),
            "include_metadata": self.config_manager.get_config_value("output.include_metadata", True),
            
            # Processing options
            "extract_metadata": self.config_manager.get_config_value("processing.extract_metadata", True),
            "normalize_text": self.config_manager.get_config_value("processing.normalize_text", True),
            "quality_threshold": self.config_manager.get_config_value("processing.quality_threshold", 0.9),
            
            # Batch processing options
            "continue_on_error": self.config_manager.get_config_value("processing.continue_on_error", True),
            "batch_size": self.config_manager.get_config_value("resources.batch_size", 100),
            "parallel": self.config_manager.get_config_value("resources.parallel", False),
            "max_workers": self.config_manager.get_config_value("resources.max_workers", 4),
            
            # Security options
            "sanitize": self.config_manager.get_config_value("security.sanitize_output", True),
            
            # Resource options
            "max_cpu": self.config_manager.get_config_value("resources.cpu_limit_percent", 80),
            "max_memory": self.config_manager.get_config_value("resources.memory_limit_gb", 6) * 1024  # Convert to MB
        }
        
        return options


# Create a global API instance for easy import and use
api = PythonAPI()