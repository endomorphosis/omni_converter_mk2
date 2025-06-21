"""
Python API for the Omni-Converter.

This module provides a programmatic interface to the Omni-Converter functionality,
allowing Python applications to convert files to text without using the command-line interface.
"""
from functools import cached_property
import os
from pathlib import Path

from types_ import (
    Any, Callable, Optional,
    Configs, Logger, BatchProcessor, BatchResult, ProcessingResult, ProcessingPipeline, ResourceMonitor
)

from dataclasses import dataclass

try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Pydantic is required for the Python API.")


class Options(BaseModel):
    output_dir: Optional[str] = Field(default=None)
    format: str = Field(default="txt")
    include_metadata: bool = Field(default=True)
    extract_metadata: bool = Field(default=True)
    normalize_text: bool = Field(default=True)
    quality_threshold: float = Field(default=0.9)
    continue_on_error: bool = Field(default=True)
    max_batch_size: int = Field(default=100)
    parallel: bool = Field(default=False)
    max_workers: int = Field(default=4)
    sanitize: bool = Field(default=True)
    max_cpu: int = Field(default=80)
    max_memory: int = Field(default=6144)  # 6GB in MB
    show_progress: bool = Field(default=False)  # TODO Unused argument. Implement.

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary.

        Returns:
            A dictionary representation of the options.
        """
        return self.model_dump()


class PythonAPI:
    """
    Python API for the Omni-Converter.
    
    This class provides methods for programmatically using the Omni-Converter functionality,
    including single file conversion, batch processing, and configuration management.
    
    Attributes:
        configs: The configuration manager to use.
        batch_processor: The batch processor to use.
        resource_monitor: The resource monitor to use.
    """

    def __init__(
        self,
        resources: dict[str, Callable] = None,
        configs: Configs = None,
    ):
        """
        Initialize the Python API.
        
        Args:
            configs: Custom configuration manager to use.
            batch processor: Custom batch processor to use.
                If None, the global batch_processor will be used.
        """
        self.configs = configs
        self.resources = resources

        self._api_timeout = self.configs.api_timeout

        self._batch_processor: BatchProcessor = self.resources['batch_processor']
        self._resource_monitor: ResourceMonitor = self.resources['resource_monitor']
        self._supported_formats: set[str] = self.resources['supported_formats']
        self._processing_pipeline: ProcessingPipeline = self.resources['processing_pipeline']
        self._logger: Logger = self.resources['logger']

    def convert_file(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        format: str = "txt",
        include_metadata: bool = True,
        extract_metadata: bool = True,
        normalize_text: bool = True,
        quality_threshold: float = 0.9,
        continue_on_error: bool = True,
        max_batch_size: int = 100,
        parallel: bool = False,
        max_workers: int = 4,
        sanitize: bool = True,
        max_cpu: int = 80,
        max_memory: int = 6144,  # 6GB in MB
        show_progress: bool = False,  # TODO Unused argument. Implement.
        output_path: Optional[str] = None,
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
        result = self._processing_pipeline.process_file(file_path, output_path, options)
        
        return result
    
    def convert_batch(
        self,
        file_paths: list[str] | str,
        output_dir: Optional[str] = None,
        format: str = "txt",
        include_metadata: bool = True,
        extract_metadata: bool = True,
        normalize_text: bool = True,
        quality_threshold: float = 0.9,
        continue_on_error: bool = True,
        max_batch_size: int = 100,
        parallel: bool = False,
        max_workers: int = 4,
        sanitize: bool = True,
        max_cpu: int = 80,
        max_memory: int = 6144,  # 6GB in MB
        show_progress: bool = False  # TODO Unused argument. Implement.
    ) -> BatchResult:
        """
        Convert multiple files to text.
        
        Args:
            file_paths: list of file paths to convert, or a directory to recursively process.
            output_dir: Directory to write output files to. 
                If None, text is still extracted but not written to files.
            options: Conversion options. If None, default options are used.
            show_progress: Whether to show a progress bar (if in interactive environment). # TODO Implement.
            
        Returns:
            A BatchResult object with the results of the batch conversion.
        """
        # Prepare options from config if none provided
        if options is None:
            options = self._get_default_options()
        
        # Configure batch processor from options
        if "max_batch_size" in options:
            self._batch_processor.set_max_batch_size(options["max_batch_size"])
        
        if "continue_on_error" in options:
            self._batch_processor.set_continue_on_error(options["continue_on_error"])
        
        if "max_workers" in options and "parallel" in options and options["parallel"]:
            self._batch_processor.set_max_workers(options["max_workers"])
        else:
            self._batch_processor.set_max_workers(1)  # Sequential mode
        
        # Configure resource limits if specified
        if ("max_cpu" in options and options["max_cpu"] is not None) or \
           ("max_memory" in options and options["max_memory"] is not None):
            # Get memory limit in MB, ensure it's properly converted from GB if needed
            memory_limit = options.get("max_memory")
            if memory_limit is not None:
                # Verify it's a reasonable value (between 1024MB and 32GB) # TODO Magic numbers need to be checked and replaced with constants.
                if memory_limit < 1024:  # Less than 1GB, might be in GB units # TODO Check if this is correct.
                    memory_limit *= 1024  # Convert to MB
                
                # Cap at a reasonable maximum to prevent excessive values
                max_reasonable_memory = 32 * 1024  # 32GB # TODO Magic number needs to be checked and replaced with constants.
                if memory_limit > max_reasonable_memory:
                    self._logger.warning(f"Memory limit of {memory_limit}MB exceeds maximum reasonable value. "
                                  f"Capping at {max_reasonable_memory}MB")
                    memory_limit = max_reasonable_memory
            
            self._resource_monitor.set_resource_limits(
                cpu_limit_percent=options.get("max_cpu"),
                memory_limit=memory_limit
            )
        
        # Process the batch
        batch_result = self._batch_processor.process_batch(
            file_paths=file_paths,
            output_dir=output_dir,
            options=options,
            progress_callback=None  # Progress callback is not used by the API
        )
        
        return batch_result

    @cached_property
    def supported_formats(self) -> dict[str, list[str]]:
        """
        Get all supported formats, organized by category.
        
        Returns:
            A dictionary mapping format categories to lists of supported formats.
        """
        return self._supported_formats

    def set_config(self, config_dict: dict[str, Any]) -> bool:
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
                self.configs.set_config_value(key, value)
            return True
        except Exception:
            return False
    
    def get_config(self) -> dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            The current configuration as a dictionary.
        """
        return self.configs.current_config
    
    def _get_default_options(self) -> dict[str, Any]:
        """
        Get default options from configuration.
        
        Returns:
            Default options as a dictionary.
        """
        options = { # TODO All these options should be set in the config file.
            # Output options
            "format": self.configs.get_config_value("output.default_format", "txt"),
            "include_metadata": self.configs.get_config_value("output.include_metadata", True),
            
            # Processing options
            "extract_metadata": self.configs.get_config_value("processing.extract_metadata", True),
            "normalize_text": self.configs.get_config_value("processing.normalize_text", True),
            "quality_threshold": self.configs.get_config_value("processing.quality_threshold", 0.9),
            
            # Batch processing options
            "continue_on_error": self.configs.get_config_value("processing.continue_on_error", True),
            "max_batch_size": self.configs.get_config_value("resources.max_batch_size", 100),
            "parallel": self.configs.get_config_value("resources.parallel", False),
            "max_workers": self.configs.get_config_value("resources.max_workers", 4),
            
            # Security options
            "sanitize": self.configs.get_config_value("security.sanitize_output", True),
            
            # Resource options
            "max_cpu": self.configs.get_config_value("resources.cpu_limit_percent", 80),
            "max_memory": self.configs.get_config_value("resources.memory_limit_gb", 6) * 1024  # Convert to MB
        }
        
        return options



