"""
Batch processor module for the Omni-Converter.

This module provides the BatchProcessor class for processing multiple files in batches.
"""

import os
import glob
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from utils.logger import logger
from utils.filesystem import FileSystem
from utils.format_detector import format_detector
from core.processing_pipeline import processing_pipeline
from core.processing_result import ProcessingResult
from managers.batch_result import BatchResult
from managers.error_handler import error_handler
from managers.resource_monitor import resource_monitor
from managers.security_manager import security_manager


# Type for progress callback function
ProgressCallback = Callable[[int, int, str], None]


class BatchProcessor:
    """
    Batch processor for the Omni-Converter.
    
    This class orchestrates the processing of multiple files in batches, handling
    resource management, error handling, and security validation.
    
    Attributes:
        pipeline: The processing pipeline to use.
        error_handler: The error handler to use.
        resource_monitor: The resource monitor to use.
        security_manager: The security manager to use.
        max_batch_size (int): Maximum number of files to process in a single batch.
        continue_on_error (bool): Whether to continue processing if errors occur.
        max_workers (int): Maximum number of worker threads for parallel processing.
        cancel_requested (bool): Whether processing cancellation has been requested.
    """
    
    def __init__(
        self,
        pipeline=None,
        error_handler=None,
        resource_monitor=None,
        security_manager=None,
        max_batch_size: int = 100,
        continue_on_error: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize a batch processor.
        
        Args:
            pipeline: The processing pipeline to use. If None, the global pipeline will be used.
            error_handler: The error handler to use. If None, the global error handler will be used.
            resource_monitor: The resource monitor to use. If None, the global resource monitor will be used.
            security_manager: The security manager to use. If None, the global security manager will be used.
            max_batch_size: Maximum number of files to process in a single batch.
            continue_on_error: Whether to continue processing if errors occur.
            max_workers: Maximum number of worker threads for parallel processing.
        """
        # Import these locally to avoid circular imports
        from managers.error_handler import error_handler as global_error_handler
        from managers.resource_monitor import resource_monitor as global_resource_monitor
        from managers.security_manager import security_manager as global_security_manager
        
        self.pipeline = pipeline or processing_pipeline
        self.error_handler = error_handler or global_error_handler
        self.resource_monitor = resource_monitor or global_resource_monitor
        self.security_manager = security_manager or global_security_manager
        self.max_batch_size = max_batch_size
        self.continue_on_error = continue_on_error
        self.max_workers = max_workers
        self.cancel_requested = False
        self._lock = threading.RLock()  # For thread safety
    
    def process_batch(
        self,
        file_paths: Union[List[str], str],
        output_dir: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None
    ) -> BatchResult:
        """
        Process a batch of files.
        
        Args:
            file_paths: List of file paths to process, or a directory path to
                recursively process all files within.
            output_dir: Directory to write output files to. If None, files will
                be processed but output will not be written to disk.
            options: Processing options to pass to the pipeline.
            progress_callback: Optional callback function for reporting progress.
                The function should accept current_count, total_count, and current_file.
                
        Returns:
            A BatchResult object with the results of the batch processing.
        """
        # Reset cancel flag
        self.cancel_requested = False
        
        # Resolve and validate input
        resolved_paths = self._resolve_paths(file_paths)
        logger.info(f"Processing batch of {len(resolved_paths)} files")
        
        # Verify output directory if provided
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                error_message = f"Failed to create output directory {output_dir}: {str(e)}"
                logger.error(error_message)
                raise ValueError(error_message)
        
        # Initialize batch result
        batch_result = BatchResult(start_time=time.time())
        
        # Start resource monitoring
        self.resource_monitor.start_monitoring()
        
        try:
            # Process files in chunks to manage memory usage
            for i in range(0, len(resolved_paths), self.max_batch_size):
                if self.cancel_requested:
                    logger.info("Batch processing cancelled")
                    break
                
                # Get chunk of files to process
                chunk = resolved_paths[i:i + self.max_batch_size]
                
                # Check resource availability
                resources_available, reason = self.resource_monitor.is_resource_available()
                if not resources_available:
                    logger.warning(f"Insufficient resources: {reason}")
                    
                    # Force memory cleanup before continuing
                    try:
                        import gc
                        # Force a full collection cycle
                        gc.collect(2)
                        
                        # Check if resources are now available
                        resources_available, reason = self.resource_monitor.is_resource_available()
                        if resources_available:
                            logger.info("Resource constraints resolved after garbage collection")
                        else:
                            # Still insufficient resources, consider reducing batch size
                            reduced_batch_size = max(1, len(chunk) // 2)
                            if reduced_batch_size < len(chunk):
                                logger.warning(f"Reducing batch size from {len(chunk)} to {reduced_batch_size} due to resource constraints")
                                chunk = chunk[:reduced_batch_size]
                    except ImportError:
                        # Continue with warning if gc module not available
                        logger.warning("Could not perform memory cleanup, continuing with caution")
                
                # Process the chunk
                chunk_results = self._process_chunk(
                    chunk, output_dir, options, progress_callback,
                    total_count=len(resolved_paths), current_index=i
                )
                
                # Add results to batch result
                for result in chunk_results:
                    batch_result.add_result(result)
                
                # Perform explicit garbage collection after processing chunk
                try:
                    import gc
                    # Force collection to clean up memory
                    gc.collect()
                    logger.debug(f"Garbage collection performed after processing chunk of {len(chunk)} files")
                except ImportError:
                    logger.debug("gc module not available, skipping explicit garbage collection")
                
                # Check if we should stop due to errors
                if not self.continue_on_error and batch_result.failed_files > 0:
                    logger.warning("Stopping batch processing due to errors")
                    break
            
            # Mark batch as complete
            batch_result.complete()
            
            # Log final results
            logger.info(
                f"Batch processing completed: {batch_result.successful_files} succeeded, "
                f"{batch_result.failed_files} failed"
            )
            
            return batch_result
            
        finally:
            # Stop resource monitoring
            self.resource_monitor.stop_monitoring()
    
    def _process_chunk(
        self,
        file_paths: List[str],
        output_dir: Optional[str],
        options: Optional[Dict[str, Any]],
        progress_callback: Optional[ProgressCallback],
        total_count: int,
        current_index: int
    ) -> List[ProcessingResult]:
        """
        Process a chunk of files.
        
        Args:
            file_paths: List of file paths to process.
            output_dir: Directory to write output files to.
            options: Processing options.
            progress_callback: Progress callback function.
            total_count: Total number of files in the full batch.
            current_index: Current index in the full batch.
            
        Returns:
            List of ProcessingResult objects for the processed files.
        """
        results = []
        options = options or {}
        
        # Determine processing mode (parallel or sequential)
        use_parallel = self.max_workers > 1 and len(file_paths) > 1
        
        if use_parallel:
            # Process files in parallel
            results = self._process_files_parallel(
                file_paths, output_dir, options, progress_callback, 
                total_count, current_index
            )
        else:
            # Process files sequentially
            results = self._process_files_sequential(
                file_paths, output_dir, options, progress_callback,
                total_count, current_index
            )
        
        return results
    
    def _process_files_parallel(
        self,
        file_paths: List[str],
        output_dir: Optional[str],
        options: Dict[str, Any],
        progress_callback: Optional[ProgressCallback],
        total_count: int,
        current_index: int
    ) -> List[ProcessingResult]:
        """
        Process files in parallel using a thread pool.
        
        Args:
            file_paths: List of file paths to process.
            output_dir: Directory to write output files to.
            options: Processing options.
            progress_callback: Progress callback function.
            total_count: Total number of files in the full batch.
            current_index: Current index in the full batch.
            
        Returns:
            List of ProcessingResult objects for the processed files.
        """
        results = []
        progress_counter = 0
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {}
            for path in file_paths:
                if self.cancel_requested:
                    break
                
                # Determine output path
                output_path = self._get_output_path(path, output_dir, options)
                
                # Submit task
                future = executor.submit(
                    self._process_single_file, path, output_path, options
                )
                future_to_path[future] = path
            
            # Process results as they complete
            for future in as_completed(future_to_path):
                if self.cancel_requested:
                    break
                
                # Get file path
                file_path = future_to_path[future]
                
                try:
                    # Get result
                    result = future.result()
                    results.append(result)
                    
                    # Update progress
                    progress_counter += 1
                    if progress_callback:
                        progress_callback(
                            current_index + progress_counter, 
                            total_count, 
                            file_path
                        )
                        
                except Exception as e:
                    # Handle errors
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    error_result = ProcessingResult(
                        success=False,
                        file_path=file_path,
                        errors=[str(e)]
                    )
                    results.append(error_result)
                    
                    # Update progress
                    progress_counter += 1
                    if progress_callback:
                        progress_callback(
                            current_index + progress_counter, 
                            total_count, 
                            file_path
                        )
        
        return results
    
    def _process_files_sequential(
        self,
        file_paths: List[str],
        output_dir: Optional[str],
        options: Dict[str, Any],
        progress_callback: Optional[ProgressCallback],
        total_count: int,
        current_index: int
    ) -> List[ProcessingResult]:
        """
        Process files sequentially.
        
        Args:
            file_paths: List of file paths to process.
            output_dir: Directory to write output files to.
            options: Processing options.
            progress_callback: Progress callback function.
            total_count: Total number of files in the full batch.
            current_index: Current index in the full batch.
            
        Returns:
            List of ProcessingResult objects for the processed files.
        """
        results = []
        
        for i, path in enumerate(file_paths):
            if self.cancel_requested:
                break
            
            # Determine output path
            output_path = self._get_output_path(path, output_dir, options)
            
            try:
                # Process file
                result = self._process_single_file(path, output_path, options)
                results.append(result)
                
                # Update progress
                if progress_callback:
                    progress_callback(current_index + i + 1, total_count, path)
                    
            except Exception as e:
                # Handle errors
                logger.error(f"Error processing {path}: {str(e)}")
                error_result = ProcessingResult(
                    success=False,
                    file_path=path,
                    errors=[str(e)]
                )
                results.append(error_result)
                
                # Update progress
                if progress_callback:
                    progress_callback(current_index + i + 1, total_count, path)
                
                # Check if we should continue
                if not self.continue_on_error:
                    break
        
        return results
    
    def _process_single_file(
        self,
        file_path: str,
        output_path: Optional[str],
        options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process a single file.
        
        Args:
            file_path: Path to the file to process.
            output_path: Path to write output to.
            options: Processing options.
            
        Returns:
            ProcessingResult object for the processed file.
        """
        try:
            # Perform security validation
            security_result = self.security_manager.validate_security(file_path)
            if not security_result.is_safe:
                # Handle security issues
                error_message = f"Security validation failed: {', '.join(security_result.issues)}"
                logger.warning(error_message, {'file_path': file_path})
                return ProcessingResult(
                    success=False,
                    file_path=file_path,
                    output_path=output_path,
                    errors=[error_message]
                )
            
            # Process the file
            result = self.pipeline.process_file(file_path, output_path, options)
            
            # If processing succeeded and content was generated, sanitize it
            if result.success and options.get('sanitize', True) and not output_path:
                # Sanitize content if this is an in-memory process (no output file)
                file_format = result.format
                format_handler = None
                
                # Additional sanitization can be applied here if needed
                pass
            
            return result
            
        except Exception as e:
            # Use the error handler to handle and log the error
            self.error_handler.handle_error(
                e, {'file_path': file_path, 'output_path': output_path}
            )
            
            # Create a failure result
            return ProcessingResult(
                success=False,
                file_path=file_path,
                output_path=output_path,
                errors=[str(e)]
            )
    
    def _resolve_paths(self, file_paths: Union[List[str], str]) -> List[str]:
        """
        Resolve file paths, expanding directories if necessary.
        
        Args:
            file_paths: List of file paths or a directory path.
            
        Returns:
            List of resolved file paths.
        """
        resolved = []
        
        # Handle string input (single file or directory)
        if isinstance(file_paths, str):
            if os.path.isdir(file_paths):
                # Recursively find files in directory
                for root, _, files in os.walk(file_paths):
                    for f in files:
                        resolved.append(os.path.join(root, f))
            elif os.path.isfile(file_paths):
                # Add single file
                resolved.append(file_paths)
            else:
                # Try to expand wildcards
                glob_matches = glob.glob(file_paths, recursive=True)
                if glob_matches:
                    for match in glob_matches:
                        if os.path.isfile(match):
                            resolved.append(match)
                else:
                    logger.warning(f"Path not found: {file_paths}")
                    
        # Handle list input
        elif isinstance(file_paths, list):
            for path in file_paths:
                if os.path.isdir(path):
                    # Recursively find files in directory
                    for root, _, files in os.walk(path):
                        for f in files:
                            resolved.append(os.path.join(root, f))
                elif os.path.isfile(path):
                    # Add single file
                    resolved.append(path)
                else:
                    # Try to expand wildcards
                    glob_matches = glob.glob(path, recursive=True)
                    if glob_matches:
                        for match in glob_matches:
                            if os.path.isfile(match):
                                resolved.append(match)
                    else:
                        logger.warning(f"Path not found: {path}")
        
        return resolved
    
    def _get_output_path(
        self,
        input_path: str,
        output_dir: Optional[str],
        options: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get the output path for a file.
        
        Args:
            input_path: Path to the input file.
            output_dir: Directory to write output to.
            options: Processing options.
            
        Returns:
            Path to write output to, or None if output should not be written.
        """
        if not output_dir:
            return None
        
        # Get output format
        output_format = options.get('format', 'txt')
        
        # Get base filename without extension
        base_name = os.path.basename(input_path)
        base_name_without_ext = os.path.splitext(base_name)[0]
        
        # Create output path
        output_name = f"{base_name_without_ext}.{output_format}"
        output_path = os.path.join(output_dir, output_name)
        
        return output_path
    
    def cancel_processing(self) -> None:
        """Cancel ongoing batch processing."""
        logger.info("Cancellation requested for batch processing")
        with self._lock:
            self.cancel_requested = True
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get the current status of batch processing.
        
        Returns:
            A dictionary with the current status.
        """
        pipeline_status = self.pipeline.get_pipeline_status()
        resource_status = self.resource_monitor.get_current_usage()
        error_stats = self.error_handler.get_error_statistics()
        
        status = {
            'pipeline': pipeline_status,
            'resources': resource_status,
            'errors': error_stats,
            'cancel_requested': self.cancel_requested
        }
        
        return status
    
    def set_max_batch_size(self, size: int) -> None:
        """
        Set the maximum batch size.
        
        Args:
            size: Maximum number of files to process in a single batch.
        """
        self.max_batch_size = max(1, size)
        logger.info(f"Max batch size set to {self.max_batch_size}")
    
    def set_continue_on_error(self, flag: bool) -> None:
        """
        Set whether to continue processing if errors occur.
        
        Args:
            flag: Whether to continue processing if errors occur.
        """
        self.continue_on_error = flag
        logger.info(f"Continue on error set to {self.continue_on_error}")
    
    def set_max_workers(self, count: int) -> None:
        """
        Set the maximum number of worker threads for parallel processing.
        
        Args:
            count: Maximum number of worker threads.
        """
        self.max_workers = max(1, count)
        logger.info(f"Max workers set to {self.max_workers}")


# Global batch processor instance
batch_processor = BatchProcessor()