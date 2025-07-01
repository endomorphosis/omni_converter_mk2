"""
Unified handler interface for the Omni-Converter.

This module provides an orchestration class for format handlers,
because re-using orchestration logic is dumb.
"""
from __future__ import annotations


from types_ import Any, Callable, Optional, Configs, Content, Logger, FileFormatDetector, SupportedFormats, Processor


class ContentExtractor:
    """
    Framework for extracting content from files.
    This class provides the logic for orchestrating format handlers

    Base implementation of a format handler without inheritance.
    
    Provides common functionality for format handlers.
    
    Attributes:
        resources (dict): Dictionary of resources and dependencies.
        configs (Configs): Configuration settings.
        format_processors (dict): Processors for different formats.
        supported_formats (set): Set of formats supported by this handler.
    """
    
    def __init__(
        self, 
        resources: dict[str, Callable] = None, 
        configs: Configs = None
        ) -> None:
        """Initialize the content extractor.
        
        Args:
            resources: Dictionary of callables and services used by the extractor.
            configs: Pydantic BaseModel containing configuration settings. Settings are accessed via attributes.
        """
        self.resources = resources
        self.configs = configs

        # Built-in libraries
        self._splitext = self.resources['splitext']

        self._processors:              dict[str, Processor] = self.resources["processors"]
        self._supported_formats:       SupportedFormats     = self.resources["supported_formats"]
        self._capabilities:            dict[str, Callable]  = self.resources["capabilities"]
        self._format_detector:        'FileFormatDetector'  = self.resources["file_format_detector"]
        self._map_extension_to_format: Callable             = self.resources["map_extension_to_format"]
        self._read_file:               Callable             = self.resources["read_file"]
        self._logger:                  Logger               = self.resources["logger"]
        self._content:                 'Content'            = self.resources["content"]

        for value in self._processors.values():
            assert isinstance(value, tuple) and len(value) == 3, \
                f"Processor value must be a tuple of (name, processor, supported_formats), got: {value}"

    # TODO can_handle is not used anywhere, remove it?
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if extractor can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        for handler_name in self._capabilities.keys():
            self._logger.debug(f"Checking if handler '{handler_name}' can handle file: {file_path}\nformat_name: {format_name}")

            if format_name:
                # If format is provided, check against supported formats
                if format_name in self._supported_formats:
                    self._logger.debug(f"Handler '{handler_name}' can handle file: {file_path}")
                    return True
                else:
                    self._logger.debug(f"Handler '{handler_name}' cannot handle file: {file_path}\nHandler supports: {self.supported_formats}")
                    return False
            else:
                # Otherwise, validate input and try to determine format
                self._logger.debug(f"Format name not provided. Validating input for handler '{handler_name}'")
                return self.validate_input(file_path, handler_name)
        else:
            self._logger.debug(f"Handler '{handler_name}' cannot handle file: {file_path}\nHandler supports: {self.supported_formats}")
            return False

    def extract_content(self, file_path: str, format_name: str, options: Optional[dict[str, Any]] = None) -> Content:
        """
        Extract content from a file.
        
        Args:
            file_path: The path to the file.
            options: Optional extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If the file is not valid for this handler.
            Exception: If an error occurs during extraction.
        """
        handler_format_mapping = {
            "application": self._supported_formats.SUPPORTED_APPLICATION_FORMATS,
            "text": self._supported_formats.SUPPORTED_TEXT_FORMATS,
            "audio": self._supported_formats.SUPPORTED_AUDIO_FORMATS,
            "video": self._supported_formats.SUPPORTED_VIDEO_FORMATS,
            "image": self._supported_formats.SUPPORTED_IMAGE_FORMATS,
        }

        # Validate input
        for handler_name in self._capabilities.keys():
            format_set = handler_format_mapping[handler_name]
            if not self.validate_input(file_path, format_name, handler_name, format_set):
                continue
            else:
                break
        else:
            raise ValueError(f"File is not valid for handler: {handler_name}")

        # Extract content
        return self.do_extraction(file_path, options or {})

    @property
    def capabilities(self) -> dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        # TODO Defining _handler_name like this is really hacky and needs to be removed after more refactoring.
        _handler_name = ",".join([key for key in self.capabilities.keys()])
        return {
            'handler_name': _handler_name,
            'supported_formats': list(self._supported_formats),
            **self._capabilities
        }

    def validate_input(self, file_path: str, format_name: str, handler_name: str, format_set: set) -> bool:
        """
        Validate that the file can be processed by this handler.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file is valid for this handler, False otherwise.
        """
        self._logger.debug(f"Validating input '{file_path}' with format name '{format_name}' for handler '{handler_name}'")

        try:
            # TODO This is done again?!??!
            self._logger.debug(f"Detecting if {format_name} if in {format_set}")
            if format_name in format_set:
                self._logger.debug(f"Format '{format_name}' is supported by handler '{handler_name}'")
                return True
            else:
                self._logger.debug(f"Format '{format_name}' is not supported by handler '{handler_name}'")
                return False
        except Exception as e:
            self._logger.exception(f"Error detecting format for file '{file_path}': {e}")
            return False

    def do_extraction(self, file_path: str, options: dict[str, Any]) -> Content:
        """
        Perform the actual extraction of content from a file.
        
        Args:
            file_path: The path to the file.
            options: Extraction options. These include:
                - format: The format of the file (if not provided, it will be detected).
                - other options specific to the processor.
            
        Returns:
            The extracted content.
            
        Raises:
            Exception: If an error occurs during extraction.
        """
        # Detect format if not provided in options
        format_name = options.get('format')
        if not format_name:
            format_name, _ = self._format_detector.detect_format(file_path)
            
            # Override format detection based on file extension if needed
            if not format_name:
                _, ext = self._splitext(file_path)
                # Map extension to format
                format_name = self._map_extension_to_format(ext)

        # Verify format is supported
        if not format_name: #or format_name not in self._supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")
        else:
            self._logger.debug(f"Extracting content from file: {file_path} with format: {format_name}")

        # Get parser for this format
        processor = None
        #self._logger.debug(f"Getting processor for format: {format_name}\nprocessors: {self._processors.items()}")
        for proc_name, values in self._processors.items():
            self._logger.debug(values)
            _, available_processor, set_ = values
            if format_name in set_:
                self._logger.debug(f"Processor '{proc_name}' supports format '{format_name}'")
                processor = available_processor
                break

        # processor = self._processors.get(format_name)
        self._logger.debug(f"Processor for format '{format_name}': {processor}")
        if not processor:
            raise ValueError(f"No processor available for format: {format_name}")

        self._logger.debug(f"Extracting content from {format_name} file: {file_path}")

        # Get file content in binary format.
        # This allows for more robust handling of different file types and saves on memory.
        try:
            file_content: bytes = self._read_file(file_path, 'rb')
        except Exception as e:
            self._logger.error(f"Error reading file: {file_path}\n{e}")
            raise

        # Ensure file_path is included in options for processors that need it
        processor_options = dict(options)
        processor_options["file_path"] = file_path
        processor_options["format"] = format_name

        try:  # Extract content using the parser
            text: str
            metadata: dict[str, Any]
            sections: list[dict[str, Any]]

            self._logger.debug(f"Processing file content with processor: {processor}")
            text, metadata, sections = processor(file_content, processor_options)

            # Create content object
            content: Content = self._content(
                text=text,
                metadata=metadata,
                sections=sections,
                source_format=format_name,
                source_path=file_path
            )
            return content

        except Exception as e:
            self._logger.exception(f"Error extracting content from {format_name}: {file_path}\n{e}")
            raise
