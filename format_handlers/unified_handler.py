"""
Unified handler interface for the Omni-Converter.

This module provides an orchestration class for format handlers,
because re-using orchestration logic is dumb.
"""
from datetime import datetime
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field
from pydantic.types import PastDatetime

from utils.filesystem import FileSystem
from configs import Configs, configs
from logger import logger
from utils.common.try_except_decorator import try_except
from core.format_detector import format_detector

class Content(BaseModel):
    """
    Content extracted from a file.
    
    Attributes:
        text (str): The extracted text content.
        metadata (dict): Metadata about the content.
        sections (list): Sections of the content (if applicable).
        source_format (str): The format of the source file.
        source_path (str): The path to the source file.
        extraction_time (datetime): The time the content was extracted.
    """
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    source_format: str = ""
    source_path: str = ""
    extraction_time: PastDatetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the content.
        """
        # Use Pydantic's model_dump with custom handling for datetime
        data = self.model_dump()
        data['extraction_time'] = self.extraction_time.isoformat()
        return data

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class FormatHandler:
    """
    Interface for format handlers.
    
    Format handlers are responsible for extracting content from files of specific formats.
    """
    
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement can_handle")
    
    def extract_content(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Content:
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
        raise NotImplementedError("Subclasses must implement extract_content")

    @property
    def capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        raise NotImplementedError("Subclasses must implement capabilities")


class BaseFormatHandler:
    """
    Base implementation of a format handler without inheritance.
    
    Provides common functionality for format handlers.
    
    Attributes:
        resources (dict): Dictionary of resources and dependencies.
        configs (Configs): Configuration settings.
        format_parsers (dict): Parser functions for different formats.
    """
    
    def __init__(
        self,
        resources: dict[str, Callable] = None,
        configs: Optional[Configs] = None
    ):
        """
        Initialize a format handler.
        
        Args:
            resources: Dictionary of resources including parsers and services.
                Must contain:
                - handler_name: Name of the handler
                - supported_formats: Set of formats supported by this handler
                - capabilities: Dictionary of handler capabilities
                - format_detector: Format detection utility
                - ext_to_format: Function to map extensions to formats
                - parsers: Dictionary of parser functions
            configs: Configuration settings.
        """
        # Store the original resources dictionary
        self.resources = resources
        self.configs = configs
        
        # Extract resources directly - fail fast if any are missing
        self.handler_name = resources["handler_name"]
        self.supported_formats = resources["supported_formats"]
        self._capabilities = resources["capabilities"]
        self.format_detector = resources["format_detector"]
        self.ext_to_format = resources["ext_to_format"]
        
        # Initialize format parsers from resources
        self.format_parsers = {}
        if "parsers" in resources:
            for category, parsers in resources["parsers"].items():
                self.format_parsers.update(parsers)
    
    def can_handle(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if this handler can process the given file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if this handler can process the file, False otherwise.
        """
        logger.debug(f"Checking if handler '{self.handler_name}' can handle file: {file_path}\nformat_name: {format_name}")

        if format_name:
            # If format is provided, check against supported formats
            if format_name in self.supported_formats:
                logger.debug(f"Handler '{self.handler_name}' can handle file: {file_path}")
                return True
            else:
                logger.debug(f"Handler '{self.handler_name}' cannot handle file: {file_path}\nHandler supports: {self.supported_formats}")
                return False
        else:
            # Otherwise, validate input and try to determine format
            logger.debug(f"Format name not provided. Validating input for handler '{self.handler_name}'")
            return self.validate_input(file_path)
    
    def extract_content(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Content:
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
        # Validate input
        if not self.validate_input(file_path):
            raise ValueError(f"File is not valid for handler: {self.handler_name}")
        
        # Extract content
        return self.do_extraction(file_path, options or {})
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this handler.
        
        Returns:
            A dictionary of capabilities, such as supported formats and extraction options.
        """
        return {
            'handler_name': self.handler_name,
            'supported_formats': list(self.supported_formats),
            **self._capabilities
        }

    def validate_input(self, file_path: str) -> bool:
        """
        Validate that the file can be processed by this handler.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file is valid for this handler, False otherwise.
        """
        logger.debug(f"Validating input '{file_path}' for handler '{self.handler_name}'")
        
        try:
            logger.debug(f"Detecting format for file: {file_path}")
            format_name, _ = self.format_detector.detect_format(file_path)
            if format_name in self.supported_formats:
                return True
            else:
                return False
        except Exception as e:
            logger.exception(f"Error detecting format for file '{file_path}': {e}")
            return False

    def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
        """
        Perform the actual extraction of content from a file.
        
        Args:
            file_path: The path to the file.
            options: Extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            Exception: If an error occurs during extraction.
        """
        # Detect format if not provided in options
        format_name = options.get('format')
        if not format_name:
            format_name, _ = self.format_detector.detect_format(file_path)
            
            # Override format detection based on file extension if needed
            if not format_name:
                _, ext = os.path.splitext(file_path)
                # Map extension to format
                format_name = self.ext_to_format(ext)

        # Verify format is supported
        if not format_name or format_name not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")

        # Get parser for this format
        parser = self.format_parsers.get(format_name)
        if not parser:
            raise ValueError(f"No parser available for format: {format_name}")
        
        logger.debug(f"Extracting content from {format_name} file: {file_path}")

        # Get file content - use binary mode by default
        file_content = FileSystem.read_file(file_path, 'rb')

        # Ensure file_path is included in options for processors that need it
        processor_options = dict(options)
        processor_options["file_path"] = file_path
        processor_options["format"] = format_name

        try:  # Extract content using the parser
            text, metadata, sections = parser(file_content, processor_options)
            
            # Create content object
            content = Content(
                text=text,
                metadata=metadata,
                sections=sections,
                source_format=format_name,
                source_path=file_path
            )
            
            return content

        except Exception as e:
            logger.error(f"Error extracting content from {format_name}: {file_path}\n{e}")
            raise


# Shared extraction functions
def extract_with_format_handler(
    file_path: str, 
    options: Dict[str, Any],
    handler: BaseFormatHandler
) -> Content:
    """
    Extract content using a format handler.
    
    Args:
        file_path: The path to the file.
        options: Extraction options.
        handler: The format handler to use.
        
    Returns:
        The extracted content.
        
    Raises:
        Exception: If an error occurs during extraction.
    """
    return handler.extract_content(file_path, options)


def create_handler(
    handler_name: str,
    format_detector: Any,
    ext_to_format: Callable,
    supported_formats: Set[str],
    capabilities: Dict[str, Any],
    parsers: Dict[str, Dict[str, Callable]],
    resources_extra: Optional[Dict[str, Any]] = None,
    configs: Optional[Configs] = None
) -> BaseFormatHandler:
    """
    Create a new format handler.
    
    Args:
        handler_name: The name of the handler.
        format_detector: Format detection utility.
        ext_to_format: Function to map extensions to formats.
        supported_formats: Formats supported by the handler.
        capabilities: Capabilities of the handler.
        parsers: Dictionary of parser functions by category.
        resources_extra: Additional resources to include.
        configs: Configuration settings.
        
    Returns:
        A new format handler.
    """
    # Prepare the resources dictionary
    resources = {
        "handler_name": handler_name,
        "format_detector": format_detector,
        "ext_to_format": ext_to_format,
        "supported_formats": supported_formats,
        "capabilities": capabilities,
        "parsers": parsers
    }
    
    # Add any additional resources
    if resources_extra:
        resources.update(resources_extra)
    
    return BaseFormatHandler(
        resources=resources,
        configs=configs
    )


def map_extension_to_format(ext: str) -> str:
    """
    Map a file extension to its corresponding format.
    
    Args:
        ext: The file extension (with or without leading dot)
        
    Returns:
        The format name for the given extension
    """
    # Clean the extension by removing any leading dot and converting to lowercase
    clean_ext = ext.strip('.').lower().strip() 
    
    match clean_ext:
        # Application formats
        case 'pdf':
            format_name = 'pdf'
        case 'json' | 'jsonl':
            format_name = 'json'
        case 'docx':
            format_name = 'docx'
        case 'xlsx':
            format_name = 'xlsx'
        case 'zip':
            format_name = 'zip'
        case 'xml':
            format_name = 'xml'
        case 'ics':
            format_name = 'calendar'
        case 'csv':
            format_name = 'csv'
        # Text formats
        case 'txt' | 'text':
            format_name = 'plain'
        case 'html' | 'htm':
            format_name = 'html'
        # Video formats
        case 'mp4' | 'm4v':
            format_name = 'mp4'
        case 'webm':
            format_name = 'webm'
        case 'mkv':
            format_name = 'mkv'
        case 'avi':
            format_name = 'avi'
        case 'mov' | 'qt':
            format_name = 'mov'
        # Image formats
        case 'jpg' | 'jpeg':
            format_name = 'jpeg'
        case 'png' | 'gif' | 'webp' | 'svg':
            format_name = clean_ext
        # Audio formats
        case 'mp3':
            format_name = 'mp3'
        case 'wav' | 'wave':
            format_name = 'wav'
        case "ogg" | "oga":
            format_name = 'ogg'
        case "aac" | "m4a":  # Fixed "acc" typo
            format_name = 'aac'
        case "flac":
            format_name = 'flac'
        case _:
            format_name = clean_ext
    
    return format_name


from .constants import Constants


supported_formats = set()
supported_formats.update(Constants.SUPPORTED_AUDIO_FORMATS_SET)
supported_formats.update(Constants.SUPPORTED_VIDEO_FORMATS_SET)
supported_formats.update(Constants.SUPPORTED_IMAGE_FORMATS_SET)
supported_formats.update(Constants.SUPPORTED_TEXT_FORMATS_SET)
supported_formats.update(Constants.SUPPORTED_APPLICATION_FORMATS_SET)


# This is just a placeholder for the resources dictionary
# It will be properly initialized when the unified handler is instantiated
# with resources injected by the caller

from .dependency_modules import (
    _bs4_processor,
    calibre_processor,
    cv2_processor,
    factory,
    ffmpeg_processor,
    generic_html_processor,
    generic_svg_processor,
    icalendar_processor,
    lxml_processor,
    openai_processor,
    openpyxl_processor,
    pandas_processor,
    pil_processor,
    pymediainfo_processor,
    pypdf2_processor,
    pytesseract_processor,
    skeleton_vllm_processor,
    skeleton_xml_processor,
)

resources = {
    "parsers": {
        "application": {},  # Will contain parsers for application formats (pdf, json, docx, etc.)
        "text": {},         # Will contain parsers for text formats (html, xml, plain, etc.)
        "audio": {},        # Will contain parsers for audio formats (mp3, wav, etc.)
        "video": {},        # Will contain parsers for video formats (mp4, webm, etc.)
        "image": {},        # Will contain parsers for image formats (jpeg, png, etc.)
    },
    "format_detector": format_detector,
    "supported_formats": supported_formats,
    "ext_to_format": map_extension_to_format
}

