"""
Processing pipeline module for the Omni-Converter.

This module provides the ProcessingPipeline class for orchestrating the conversion
of files to plaintext.
"""
import hashlib
from typing import Any, Callable, Optional

from types_ import Configs, Logger, StatusListenerFunc


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
        resources: dict[str, Callable] = None,
        configs: Configs = None,
    ):
        """
        Initialize a processing pipeline.
        
        Args:
            configs: A pydantic model containing configuration settings.
            resources: A dictionary of callable classes and functions for the class to use.
        """
        self.configs = configs
        self.resources = resources

        self._format_detector = self.resources['file_format_detector']
        self._file_validator = self.resources['file_validator']
        self._content_extractor = self.resources['content_extractor']
        self._text_normalizer = self.resources['text_normalizer']
        self._output_formatter = self.resources['output_formatter']
        self._processing_result = self.resources['processing_result']
        self._logger: Logger = self.resources['logger']

        self._status = self.resources['pipeline_status']
        self._listeners: list[StatusListenerFunc] = []

    def _create_failure_result(self, 
                               file_path: str,
                               output_path: str = None,
                               format_name: str = None,
                               errors: list[str] = None
                               ) -> Any:
        if isinstance(errors, str):
            errors = [errors]
        # Create failure result
        result = self._processing_result(
            success=False,
            file_path=file_path,
            output_path=output_path,
            format=format_name,
            errors=errors
        )
        self._status.failed_files += 1
        return result


    def process_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        options: Optional[dict[str, Any]] = None
    ) -> Any:
        """
        Process a single file.
        
        Args:
            file_path: The path to the file to process.
            output_path: The path to write the output to. If None, the output
                will not be written to a file.
            options: Optional processing options.
            
        Returns:
            ProcessingResult: The result of processing the file.
            
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
        self._status.is_processing = True
        self._status.current_file = file_path
        self._status.total_files += 1
        self._notify_listeners("processing_started", {'file_path': file_path})
        
        try:
            # Detect format
            self._logger.debug(f"Detecting format for {file_path}")
            format_name, category = self._format_detector.detect_format(file_path)
            if not format_name:
                errors =  ValueError(f"Unable to detect format for {file_path}")

            self._logger.info(f"Detected format: {format_name} ({category})", {'file_path': file_path})

            # Validate file
            self._logger.debug(f"Validating file {file_path}")
            validation_result = self._file_validator.validate_file(file_path, format_name)
            if not validation_result.is_valid:
                error_message = f"Validation failed: {', '.join(validation_result.errors)}"
                self._logger.error(error_message, {'file_path': file_path})
                
                # Create failure result
                self._create_failure_result(
                    file_path=file_path,
                    output_path=output_path,
                    format_name=format_name,
                    errors=validation_result.errors
                )

                self._notify_listeners("processing_failed", {
                    'file_path': file_path,
                    'errors': validation_result.errors
                })
                
                return result
            
            # Extract content
            self._logger.debug(f"Extracting content from {file_path}")
            content = self._content_extractor.extract_content(file_path, format_name, options)
            
            # Normalize text
            self._logger.debug(f"Normalizing text from {file_path}")
            normalized_content = self._text_normalizer.normalize_text(content, normalizers)
            
            # Format output
            self._logger.debug(f"Formatting output for {file_path}")
            try:
                formatted_output = self._output_formatter.format_output(
                    normalized_content,
                    output_format,
                    options,
                    output_path
                )
            except ValueError as e:
                self._logger.warning(f"Format error: {e}, falling back to txt format")
                # Fall back to txt format if the specified format fails
                formatted_output = self._output_formatter.format_output(
                    normalized_content,
                    'txt',
                    options,
                    output_path
                )
            
            # Write output to file if output_path is provided
            if output_path:
                self._logger.debug(f"Writing output to {output_path}")
                formatted_output.write_to_file(output_path)
            
            # Calculate content hash for verification # TODO Change to Ipfs CID
            content_hash = hashlib.md5(formatted_output.content.encode('utf-8')).hexdigest()
            
            # Create success result
            result = self._processing_result(
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
            
            self._status.successful_files += 1
            self._notify_listeners("processing_succeeded", {
                'file_path': file_path,
                'output_path': output_path,
                'format': format_name
            })
            
            return result
            
        except Exception as e:
            self._logger.exception(f"Error processing {file_path}: {e}")
            
            # Create failure result
            result = self._processing_result(
                success=False,
                file_path=file_path,
                output_path=output_path,
                format=format_name if 'format_name' in locals() else None,
                errors=[str(e)]
            )
            
            self._status.failed_files += 1
            self._notify_listeners("processing_failed", {
                'file_path': file_path,
                'error': str(e)
            })
            
            return result
        
        finally:
            # Reset status
            self._status.is_processing = False
            self._status.current_file = ""
            self._notify_listeners("processing_completed", {'file_path': file_path})
    
    @property
    def status(self) -> dict[str, Any]:
        """
        Get the current status of the pipeline.
        
        Returns:
            The current pipeline status as a dictionary.
        """
        return self._status.to_dict()
    
    def register_listener(self, listener: StatusListenerFunc) -> None:
        """
        Register a status listener.
        
        Args:
            listener: The listener function to register.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

    def _notify_listeners(self, event: str, data: dict[str, Any]) -> None:
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
                self._logger.exception(f"Error in listener: {e}")
