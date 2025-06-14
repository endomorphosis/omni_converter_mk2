"""
Image format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for image formats like JPEG, PNG, GIF, WebP, and SVG
using dependency injection for better modularity and testability, without inheritance.
"""
from types_ import Configs, Logger, Any, Optional, Callable


class ImageHandler:
    """
    Framework class for handling image-based formats using IoC pattern.
    
    This class only contains orchestration logic and delegates all format-specific
    processing to injected processors via the resources dictionary.
    """
    
    def __init__(self, 
                 resources: dict[str, Callable], 
                 configs: Configs
                 ):
        """
        Initialize the image handler with injected dependencies.
        
        Args:
            resources: Dictionary of callable resources including processors and utilities.
            configs: Configuration settings.
        """
        self.resources = resources
        self.configs = configs

        # Extract required resources - fail fast if missing
        # NOTE Some of these processors may support related formats,
        # Example: pil processor handles jpeg, png, gif, webp
        self._image_processor: Callable = self.resources["image_processor"]
        self._svg_processor: Callable = self.resources["svg_processor"]
        self._ocr_processor: Callable = self.resources["ocr_processor"]

        self._format_extensions: dict = self.resources["format_extensions"]
        self._supported_formats: set = self.resources["supported_formats"]
        self._capabilities: dict = self.resources["capabilities"]
        self._logger: Logger = self.resources["logger"]
        self._splitext: Callable = self.resources["splitext"]

    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file format.
        
        Args:
            file_path: Path to the file.
            format_name: Format of the file, if known.
            
        Returns:
            True if this handler can process the format, False otherwise.
        """
        if format_name:
            return format_name in self._supported_formats
        
        # If no format provided, check file extension
        _, ext = self._splitext(file_path)
        ext = ext.lower()
        
        for format_type, extensions in self._format_extensions.items():
            if ext in extensions and format_type in self._supported_formats:
                return True
        
        return False
    
    def extract_content(self, file_path: str, format_name: str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """
        Extract content from an image file using the appropriate processor.
        
        Args:
            file_path: Path to the file.
            format_name: Format of the file.
            options: Processing options.
            
        Returns:
            Tuple of (text content, metadata, sections).
        """
        # Delegate to appropriate processor based on format
        match format_name:
            case 'svg':
                processor = self._svg_processor
            case 'jpeg' | 'png' | 'gif' | 'webp':
                processor = self._image_processor
            case _:
                raise ValueError(f"Unsupported image format: {format_name}")
        
        try:
            # Call the processor function
            return processor(file_path, options)
        except Exception as e:
            self._logger.error(f"Error processing {format_name} file '{file_path}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to process {format_name} file: {file_path}") from e

    @property
    def capabilities(self) -> dict[str, Any]:
        """Get handler capabilities."""
        return self._capabilities


