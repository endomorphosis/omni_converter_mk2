"""
Python API for the Omni-Converter.

This module provides a programmatic interface to the Omni-Converter functionality,
allowing Python applications to convert files to text without using the command-line interface.
"""
import os
from pathlib import Path
from typing import Any, Callable, Optional, Union


from types_ import Configs, Logger, BatchResult, ProcessingResult


from logger import logger



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
            custom_resource_monitor: Custom resource monitor to use.
                If None, the global resource_monitor will be used.
        """
        self.configs = configs
        self.resources = resources

        self._batch_processor = self.resources['batch_processor']
        self._resource_monitor = self.resources['resource_monitor']
        self._format_registry = self.resources['format_registry']
        self._processing_pipeline = self.resources['processing_pipeline']
        self._logger: Logger = self.resources['logger']

    def convert_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        options: Optional[dict[str, Any]] = None
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
        file_paths: Union[list[str], str],
        output_dir: Optional[str] = None,
        options: Optional[dict[str, Any]] = None,
        show_progress: bool = False # TODO Unused argument. Implement.
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
                    logger.warning(f"Memory limit of {memory_limit}MB exceeds maximum reasonable value. "
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
    
    @property
    def supported_formats(self) -> dict[str, list[str]]:
        """
        Get all supported formats, organized by category.
        
        Returns:
            A dictionary mapping format categories to lists of supported formats.
        """
        return self._format_registry.get_formats_by_category()
    
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
            "format": self.configs.get_config_value("output.format", "txt"),
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



class Convert(PythonAPI):
    """
    Public class for object-oriented access to the Omni-Converter.
    Similar to Pathlib's Path class, this class provides a simple interface.
    """




    
    def __init__(self, path=None, *args, **kwargs):
        """
        Initialize the Convert class.
        
        Args:
            args: Positional arguments for PythonAPI.
            kwargs: Keyword arguments for PythonAPI.
        """
        from batch_processor import make_batch_processor
        from monitors._resource_monitor import make_resource_monitor

        resources = {
            "batch_processor": make_batch_processor(),
            "resource_monitor": make_resource_monitor(),
        }
        super().__init__(resources=resources, configs=configs)
        
        self.target_file = None
        self.target_dir = None

        if path:
            path = Path(path)
            if path.is_file():
                self.target_file = path
            elif path.is_dir():
                self.target_dir = path
            else:
                raise ValueError(f"Invalid path: {path}. Must be a valid file or directory.")

    def walk_and_convert(self, path: str = None, recursive: bool = False) -> None:
        """
        Walk through a directory and convert all files.
        
        Args:
            path: The path to the directory to convert. If None, uses the current target directory.
            recursive: Whether to walk through subdirectories. Default is False.
        """
        # TODO Implement this method
        pass

    def estimate_file_count(self, path: str = None, recursive: bool = False) -> int:
        """
        Estimate the number of files in a directory that can potentially be converted.
        
        Args:
            path: The path to the directory to convert. If None, uses the current target directory.
            recursive: Whether to walk through subdirectories. Default is False.
        """
        # TODO Implement this method
        pass
    
    def convert(self, path: str = None, output_path: str = None, options: Optional[dict[str, Any]] = None) -> Any:
        """
        Convert a file or directory to text.
        
        Args:
        """
        return super().convert_file(
            file_path=path or self.target_file,
            output_path=output_path,
            options=options
        )
