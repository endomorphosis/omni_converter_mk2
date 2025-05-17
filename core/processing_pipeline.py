"""
Processing pipeline module for the Omni-Converter.

This module provides the ProcessingPipeline class for orchestrating the conversion
of files to plaintext.
"""

import os
import hashlib
from typing import Any, Callable, Dict, List, Optional, Set, Union

from utils.format_detector import format_detector
from utils.validator import BasicValidator
from utils.logger import logger
from format_handlers.format_registry import format_registry
from core.content_extractor import ContentExtractor
from core.text_normalizer import TextNormalizer, NormalizedContent
from core.output_formatter import OutputFormatter
from core.processing_result import ProcessingResult


# Type for status listener functions
StatusListenerFunc = Callable[[str, Dict[str, Any]], None]


class PipelineStatus:
    """
    Status of the processing pipeline.
    
    This class represents the current status of the processing pipeline,
    including statistics and the current state.
    
    Attributes:
        total_files (int): Total number of files processed.
        successful_files (int): Number of files processed successfully.
        failed_files (int): Number of files that failed processing.
        current_file (str): Path to the file currently being processed.
        is_processing (bool): Whether the pipeline is currently processing a file.
    """
    
    def __init__(self):
        """Initialize pipeline status."""
        self.total_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.current_file = ""
        self.is_processing = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the pipeline status.
        """
        return {
            'total_files': self.total_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'current_file': self.current_file,
            'is_processing': self.is_processing
        }


class ProcessingPipeline:
    """
    Processing pipeline for the Omni-Converter.
    
    This class orchestrates the conversion of files to plaintext, using various
    components like the format detector, validator, content extractor, text normalizer,
    and output formatter.
    
    Attributes:
        detector: The format detector to use.
        validator: The validator to use for validating input files.
        extractor: The content extractor to use.
        normalizer: The text normalizer to use.
        formatter: The output formatter to use.
        status: The current status of the pipeline.
    """
    
    def __init__(
        self,
        detector=None,
        validator=None,
        extractor=None,
        normalizer=None,
        formatter=None
    ):
        """
        Initialize a processing pipeline.
        
        Args:
            detector: The format detector to use. If None, the global format_detector
                will be used.
            validator: The validator to use for validating input files. If None, a
                new BasicValidator will be created.
            extractor: The content extractor to use. If None, a new ContentExtractor
                will be created.
            normalizer: The text normalizer to use. If None, a new TextNormalizer
                will be created.
            formatter: The output formatter to use. If None, a new OutputFormatter
                will be created.
        """
        self.detector = detector or format_detector
        self.validator = validator or BasicValidator()
        self.extractor = extractor or ContentExtractor()
        self.normalizer = normalizer or TextNormalizer()
        self.formatter = formatter or OutputFormatter()
        self.status = PipelineStatus()
        self._listeners: List[StatusListenerFunc] = []
    
    def process_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process a single file.
        
        Args:
            file_path: The path to the file to process.
            output_path: The path to write the output to. If None, the output
                will not be written to a file.
            options: Optional processing options.
            
        Returns:
            The result of processing the file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
            ValueError: If the file format is not supported.
        """
        # Initialize options
        options = options or {}
        output_format = options.get('format', 'txt')
        normalizers = options.get('normalizers')
        
        # Update status
        self.status.is_processing = True
        self.status.current_file = file_path
        self.status.total_files += 1
        self._notify_listeners("processing_started", {'file_path': file_path})
        
        try:
            # Detect format
            logger.debug(f"Detecting format for {file_path}")
            format_name, category = self.detector.detect_format(file_path)
            if not format_name:
                raise ValueError(f"Unable to detect format for {file_path}")
            
            logger.info(f"Detected format: {format_name} ({category})", {'file_path': file_path})
            
            # Validate file
            logger.debug(f"Validating file {file_path}")
            validation_result = self.validator.validate_file(file_path, format_name)
            if not validation_result.is_valid:
                error_message = f"Validation failed: {', '.join(validation_result.errors)}"
                logger.error(error_message, {'file_path': file_path})
                
                # Create failure result
                result = ProcessingResult(
                    success=False,
                    file_path=file_path,
                    output_path=output_path,
                    format=format_name,
                    errors=validation_result.errors
                )
                
                self.status.failed_files += 1
                self._notify_listeners("processing_failed", {
                    'file_path': file_path,
                    'errors': validation_result.errors
                })
                
                return result
            
            # Extract content
            logger.debug(f"Extracting content from {file_path}")
            content = self.extractor.extract_content(file_path, format_name, options)
            
            # Normalize text
            logger.debug(f"Normalizing text from {file_path}")
            normalized_content = self.normalizer.normalize_text(content, normalizers)
            
            # Format output
            logger.debug(f"Formatting output for {file_path}")
            try:
                formatted_output = self.formatter.format_output(
                    normalized_content,
                    output_format,
                    options,
                    output_path
                )
            except ValueError as e:
                logger.warning(f"Format error: {e}, falling back to txt format")
                # Fall back to txt format if the specified format fails
                formatted_output = self.formatter.format_output(
                    normalized_content,
                    'txt',
                    options,
                    output_path
                )
            
            # Write output to file if output_path is provided
            if output_path:
                logger.debug(f"Writing output to {output_path}")
                formatted_output.write_to_file(output_path)
            
            # Calculate content hash for verification
            content_hash = hashlib.md5(formatted_output.content.encode('utf-8')).hexdigest()
            
            # Create success result
            result = ProcessingResult(
                success=True,
                file_path=file_path,
                output_path=output_path,
                format=format_name,
                metadata={
                    'category': category,
                    'normalized_by': normalized_content.normalized_by,
                    'output_format': output_format,
                    'content_size': len(formatted_output.content)
                },
                content_hash=content_hash
            )
            
            self.status.successful_files += 1
            self._notify_listeners("processing_succeeded", {
                'file_path': file_path,
                'output_path': output_path,
                'format': format_name
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", {'error': str(e)})
            
            # Create failure result
            result = ProcessingResult(
                success=False,
                file_path=file_path,
                output_path=output_path,
                format=format_name if 'format_name' in locals() else None,
                errors=[str(e)]
            )
            
            self.status.failed_files += 1
            self._notify_listeners("processing_failed", {
                'file_path': file_path,
                'error': str(e)
            })
            
            return result
        
        finally:
            # Reset status
            self.status.is_processing = False
            self.status.current_file = ""
            self._notify_listeners("processing_completed", {'file_path': file_path})
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the pipeline.
        
        Returns:
            The current pipeline status as a dictionary.
        """
        return self.status.to_dict()
    
    def register_listener(self, listener: StatusListenerFunc) -> None:
        """
        Register a status listener.
        
        Args:
            listener: The listener function to register.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def _notify_listeners(self, event: str, data: Dict[str, Any]) -> None:
        """
        Notify all registered listeners of an event.
        
        Args:
            event: The event type.
            data: The event data.
        """
        for listener in self._listeners:
            try:
                listener(event, data)
            except Exception as e:
                logger.error(f"Error in listener: {e}")


# Global pipeline instance
processing_pipeline = ProcessingPipeline()