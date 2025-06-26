import unittest
from unittest.mock import Mock, MagicMock, patch
import threading
import time
import os
from concurrent.futures import Future, TimeoutError

from batch_processor._batch_processor import BatchProcessor

import datetime
import glob
import os
import time
from typing import Any, Callable, Optional, Union
import tempfile


from logger import logger
from configs import configs
from core import make_processing_pipeline
from monitors import make_error_monitor, make_resource_monitor, make_security_monitor
from monitors._error_monitor import ErrorMonitor
from monitors._resource_monitor import ResourceMonitor
from monitors.security_monitor._security_monitor import SecurityMonitor
from core._processing_pipeline import ProcessingPipeline
from core._processing_result import ProcessingResult


from batch_processor._batch_result import BatchResult


from types_ import Logger, TypedDict



class TestBatchProcessorInitialization(unittest.TestCase):
    """Test BatchProcessor initialization and configuration."""

    def test_init_with_all_parameters(self):
        """
        GIVEN valid configs and resources
        WHEN BatchProcessor is initialized
        THEN expect:
            - All attributes properly set from configs and resources
            - pipeline, error_monitor, resource_monitor, security_monitor assigned
            - max_batch_size, max_threads, continue_on_error set from configs
            - cancel_requested is False
            - _lock is a threading.RLock instance
        """
        # Arrange
        mock_configs = MagicMock()
        mock_configs.resources.max_batch_size = 100
        mock_configs.resources.max_threads = 4
        mock_configs.processing.continue_on_error = True
        
        resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }

        mock_pipeline = MagicMock(spec=ProcessingPipeline)
        mock_error_monitor = MagicMock(spec=ErrorMonitor)
        mock_resource_monitor = MagicMock(spec=ResourceMonitor)
        mock_security_monitor = MagicMock(spec=SecurityMonitor)
        mock_logger = MagicMock(spec=Logger)
        mock_processing_result = MagicMock(spec=ProcessingResult)
        mock_batch_result = MagicMock(spec=BatchResult)
        
        resources = {
            'processing_pipeline': mock_pipeline,
            'error_monitor': mock_error_monitor,
            'resource_monitor': mock_resource_monitor,
            'security_monitor': mock_security_monitor,
            'logger': mock_logger,
            'processing_result': mock_processing_result,
            'batch_result': mock_batch_result,
        }
        
        # Act
        processor = BatchProcessor(configs=mock_configs, resources=resources)
        
        # Assert
        self.assertEqual(processor.configs, mock_configs)
        self.assertEqual(processor.resources, resources)
        self.assertEqual(processor.pipeline, mock_pipeline)
        self.assertEqual(processor.error_monitor, mock_error_monitor)
        self.assertEqual(processor.resource_monitor, mock_resource_monitor)
        self.assertEqual(processor.security_monitor, mock_security_monitor)
        self.assertEqual(processor._logger, mock_logger)
        self.assertEqual(processor._processing_result, mock_processing_result)
        self.assertEqual(processor.max_batch_size, 100)
        self.assertEqual(processor.max_threads, 4)
        self.assertTrue(processor.continue_on_error)
        self.assertFalse(processor.cancel_requested)
        self.assertIsInstance(processor._lock, type(threading.RLock()))

    def test_init_with_none_configs(self):
        """
        GIVEN None configs parameter
        WHEN BatchProcessor is initialized
        THEN expect:
            - AttributeError
        """
        # Arrange
        resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        # Act & Assert
        with self.assertRaises(AttributeError):
            BatchProcessor(configs=None, resources=resources)

    def test_init_with_none_resources(self):
        """
        GIVEN None resources parameter
        WHEN BatchProcessor is initialized
        THEN expect:
            - TypeError
        """
        # Arrange
        mock_configs = MagicMock()
        mock_configs.resources.max_batch_size = 100
        mock_configs.resources.max_threads = 4
        mock_configs.processing.continue_on_error = True
        
        # Act & Assert
        with self.assertRaises(TypeError):
            BatchProcessor(configs=mock_configs, resources=None)

    def test_init_with_missing_required_resources(self):
        """
        GIVEN resources dict missing required keys (pipeline, monitors, logger)
        WHEN BatchProcessor is initialized
        THEN expect:
            - KeyError for missing resource
        """
        # Arrange
        mock_configs = MagicMock()
        mock_configs.resources.max_batch_size = 100
        mock_configs.resources.max_threads = 4
        mock_configs.processing.continue_on_error = True
        
        incomplete_resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock()
            # Missing other required resources
        }
        
        # Act & Assert
        with self.assertRaises(KeyError):
            BatchProcessor(configs=mock_configs, resources=incomplete_resources)



class TestBatchProcessorProcessBatch(unittest.TestCase):
    """Test the main process_batch method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    def test_process_batch_with_file_list(self):
        """
        GIVEN a list of valid file paths
        WHEN process_batch is called
        THEN expect:
            - BatchResult object returned
            - All files processed
            - Results contain entries for each file
            - Progress callback called with correct counts
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        progress_callback = MagicMock()
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock(), MagicMock(), MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths=file_paths,
                    progress_callback=progress_callback
                )
                
                # Assert
                self.assertIsNotNone(result)
                mock_process_chunk.assert_called_once()
                self.processor._resolve_paths.assert_called_once_with(file_paths)

    def test_process_batch_with_directory_path(self):
        """
        GIVEN a directory path string
        WHEN process_batch is called
        THEN expect:
            - Directory is recursively scanned
            - All files within processed
            - BatchResult contains all discovered files
        """
        # Arrange
        directory_path = '/path/to/directory'
        discovered_files = ['/path/to/directory/file1.txt', '/path/to/directory/file2.txt']
        
        with patch.object(self.processor, '_resolve_paths', return_value=discovered_files):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock(), MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(file_paths=directory_path)
                
                # Assert
                self.assertIsNotNone(result)
                self.processor._resolve_paths.assert_called_once_with(directory_path)
                mock_process_chunk.assert_called_once()

    def test_process_batch_with_empty_list(self):
        """
        GIVEN an empty list of file paths
        WHEN process_batch is called
        THEN expect:
            - BatchResult with empty results
            - No errors raised
            - Progress callback not called
        """
        # Arrange
        file_paths = []
        progress_callback = MagicMock()
        
        with patch.object(self.processor, '_resolve_paths', return_value=[]):
            # Act
            result = self.processor.process_batch(
                file_paths=file_paths,
                progress_callback=progress_callback
            )
            
            # Assert
            self.assertIsNotNone(result)
            progress_callback.assert_not_called()

    def test_process_batch_with_invalid_directory(self):
        """
        GIVEN a non-existent directory path
        WHEN process_batch is called
        THEN expect:
            - Appropriate error in BatchResult
            - Error logged through error_monitor
            - No crash
        """
        # Arrange
        invalid_path = '/nonexistent/directory'
        
        with patch.object(self.processor, '_resolve_paths', side_effect=FileNotFoundError("Directory not found")):
            # Act
            result = self.processor.process_batch(file_paths=invalid_path)
            
            # Assert
            self.assertIsNotNone(result)
            self.resources['error_monitor'].handle_error.assert_called()

    def test_process_batch_with_output_dir(self):
        """
        GIVEN valid files and output directory
        WHEN process_batch is called
        THEN expect:
            - Files processed and written to output_dir
            - Output paths correctly generated
            - Directory created if it doesn't exist
        """
        # Arrange
        file_paths = ['/path/file1.txt']
        output_dir = '/output/directory'
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths=file_paths,
                    output_dir=output_dir
                )
                
                # Assert
                self.assertIsNotNone(result)
                args, kwargs = mock_process_chunk.call_args
                self.assertEqual(args[1], output_dir)  # output_dir argument

    def test_process_batch_without_output_dir(self):
        """
        GIVEN valid files and output_dir=None
        WHEN process_batch is called
        THEN expect:
            - Files processed but not written to disk
            - Results still returned in BatchResult
            - No file I/O operations performed
        """
        # Arrange
        file_paths = ['/path/file1.txt']
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths=file_paths,
                    output_dir=None
                )
                
                # Assert
                self.assertIsNotNone(result)
                args, kwargs = mock_process_chunk.call_args
                self.assertIsNone(args[1])  # output_dir argument

    def test_process_batch_with_custom_options(self):
        """
        GIVEN custom processing options dict
        WHEN process_batch is called
        THEN expect:
            - Options passed to pipeline for each file
            - Options affect processing behavior
            - Results reflect applied options
        """
        # Arrange
        file_paths = ['/path/file1.txt']
        custom_options = {'format': 'pdf', 'quality': 'high'}
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths=file_paths,
                    options=custom_options
                )
                
                # Assert
                self.assertIsNotNone(result)
                args, kwargs = mock_process_chunk.call_args
                self.assertEqual(args[2], custom_options)  # options argument

    def test_process_batch_with_progress_callback(self):
        """
        GIVEN a progress callback function
        WHEN process_batch is called
        THEN expect:
            - Callback called for each file
            - Correct current_count, total_count, current_file passed
            - Callback errors don't crash processing
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        progress_callback = MagicMock()
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock(), MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths=file_paths,
                    progress_callback=progress_callback
                )
                
                # Assert
                self.assertIsNotNone(result)
                args, kwargs = mock_process_chunk.call_args
                self.assertEqual(args[3], progress_callback)  # progress_callback argument

    def test_process_batch_exceeding_max_batch_size(self):
        """
        GIVEN more files than max_batch_size
        WHEN process_batch is called
        THEN expect:
            - Files processed in chunks
            - Each chunk size <= max_batch_size
            - All files eventually processed
        """
        # Arrange
        self.processor.max_batch_size = 2
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt', '/path/file4.txt', '/path/file5.txt']
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_process_chunk.return_value = [MagicMock(), MagicMock()]
                
                # Act
                result = self.processor.process_batch(file_paths=file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                # Should be called multiple times for chunks
                self.assertGreater(mock_process_chunk.call_count, 1)

    def test_process_batch_with_cancellation(self):
        """
        GIVEN batch processing in progress
        WHEN cancel_processing() is called
        THEN expect:
            - Processing stops gracefully
            - Partial results returned
            - cancel_requested flag set to True
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        
        def side_effect(*args, **kwargs):
            self.processor.cancel_requested = True
            return [MagicMock()]
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk', side_effect=side_effect):
                # Act
                self.processor.cancel_processing()
                result = self.processor.process_batch(file_paths=file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                self.assertTrue(self.processor.cancel_requested)



class TestBatchProcessorChunkProcessing(unittest.TestCase):
    """Test internal chunk processing methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    def test_process_chunk_sequential(self):
        """
        GIVEN a chunk of files and max_threads=1
        WHEN _process_chunk is called
        THEN expect:
            - Files processed sequentially
            - _process_files_sequential called
            - Results returned in order
        """
        # Arrange
        self.processor.max_threads = 1
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 2
        current_index = 0
        
        with patch.object(self.processor, '_process_files_sequential') as mock_sequential:
            mock_results = [MagicMock(), MagicMock()]
            mock_sequential.return_value = mock_results
            
            # Act
            result = self.processor._process_chunk(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )
            
            # Assert
            self.assertEqual(result, mock_results)
            mock_sequential.assert_called_once_with(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )

    def test_process_chunk_parallel(self):
        """
        GIVEN a chunk of files and max_threads>1
        WHEN _process_chunk is called
        THEN expect:
            - Files processed in parallel
            - _process_files_parallel called
            - ThreadPoolExecutor used with correct max_workers
        """
        # Arrange
        self.processor.max_threads = 4
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        with patch.object(self.processor, '_process_files_parallel') as mock_parallel:
            mock_results = [MagicMock(), MagicMock(), MagicMock()]
            mock_parallel.return_value = mock_results
            
            # Act
            result = self.processor._process_chunk(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )
            
            # Assert
            self.assertEqual(result, mock_results)
            mock_parallel.assert_called_once_with(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )

    def test_process_chunk_with_resource_constraints(self):
        """
        GIVEN resource_monitor indicating high usage
        WHEN _process_chunk is called
        THEN expect:
            - Processing adapts to resource constraints
            - Possible throttling or sequential fallback
            - No resource exhaustion
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 2
        current_index = 0
        
        # Mock resource monitor to indicate high usage
        self.resources['resource_monitor'].get_resource_usage.return_value = {
            'memory_percent': 95,
            'cpu_percent': 90
        }
        
        with patch.object(self.processor, '_process_files_sequential') as mock_sequential:
            mock_results = [MagicMock(), MagicMock()]
            mock_sequential.return_value = mock_results
            
            # Act
            result = self.processor._process_chunk(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )
            
            # Assert
            self.assertEqual(result, mock_results)
            # Should check resource usage
            self.resources['resource_monitor'].get_resource_usage.assert_called()

    def test_process_chunk_with_mixed_file_types(self):
        """
        GIVEN files of different types in chunk
        WHEN _process_chunk is called
        THEN expect:
            - Each file processed according to its type
            - Appropriate converters selected by pipeline
            - Results reflect different processing paths
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.pdf', '/path/file3.docx']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        with patch.object(self.processor, '_process_files_sequential') as mock_sequential:
            # Mock different results for different file types
            mock_result1 = MagicMock()
            mock_result1.file_type = 'txt'
            mock_result2 = MagicMock()
            mock_result2.file_type = 'pdf'
            mock_result3 = MagicMock()
            mock_result3.file_type = 'docx'
            
            mock_sequential.return_value = [mock_result1, mock_result2, mock_result3]
            
            # Act
            result = self.processor._process_chunk(
                file_paths, output_dir, options, progress_callback, total_count, current_index
            )
            
            # Assert
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0].file_type, 'txt')
            self.assertEqual(result[1].file_type, 'pdf')
            self.assertEqual(result[2].file_type, 'docx')


class TestBatchProcessorParallelProcessing(unittest.TestCase):
    """Test parallel file processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 4
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_process_files_parallel_basic(self, mock_executor_class):
        """
        GIVEN a list of files and max_threads>1
        WHEN _process_files_parallel is called
        THEN expect:
            - ThreadPoolExecutor created with max_threads workers
            - Files submitted to executor
            - All futures completed and results collected
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        # Mock executor and futures
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        mock_future1 = Mock(spec=Future)
        mock_future2 = Mock(spec=Future)
        mock_future3 = Mock(spec=Future)
        
        mock_result1 = MagicMock()
        mock_result2 = MagicMock()
        mock_result3 = MagicMock()
        
        mock_future1.result.return_value = mock_result1
        mock_future2.result.return_value = mock_result2
        mock_future3.result.return_value = mock_result3
        
        mock_executor.submit.side_effect = [mock_future1, mock_future2, mock_future3]
        
        # Act
        result = self.processor._process_files_parallel(
            file_paths, output_dir, options, progress_callback, total_count, current_index
        )
        
        # Assert
        mock_executor_class.assert_called_once_with(max_workers=4)
        self.assertEqual(mock_executor.submit.call_count, 3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, [mock_result1, mock_result2, mock_result3])

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_process_files_parallel_with_thread_exception(self, mock_executor_class):
        """
        GIVEN one file that causes exception in thread
        WHEN _process_files_parallel is called
        THEN expect:
            - Exception caught and handled
            - Other files still processed
            - Error recorded in results
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        # Mock executor and futures
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        mock_future1 = Mock(spec=Future)
        mock_future2 = Mock(spec=Future)
        mock_future3 = Mock(spec=Future)
        
        mock_result1 = MagicMock()
        mock_result3 = MagicMock()
        
        mock_future1.result.return_value = mock_result1
        mock_future2.result.side_effect = Exception("Processing error")
        mock_future3.result.return_value = mock_result3
        
        mock_executor.submit.side_effect = [mock_future1, mock_future2, mock_future3]
        
        # Act
        result = self.processor._process_files_parallel(
            file_paths, output_dir, options, progress_callback, total_count, current_index
        )
        
        # Assert
        self.assertEqual(len(result), 3)
        # Should handle the exception and continue processing
        self.resources['error_monitor'].handle_error.assert_called()

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_process_files_parallel_with_cancellation(self, mock_executor_class):
        """
        GIVEN parallel processing in progress
        WHEN cancel_requested set to True
        THEN expect:
            - Pending futures cancelled
            - Running threads complete or stop gracefully
            - Partial results returned
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        # Set cancellation flag
        self.processor.cancel_requested = True
        
        # Mock executor and futures
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        mock_future1 = Mock(spec=Future)
        mock_future2 = Mock(spec=Future)
        mock_future3 = Mock(spec=Future)
        
        mock_future1.cancelled.return_value = False
        mock_future2.cancelled.return_value = True
        mock_future3.cancelled.return_value = True
        
        mock_result1 = MagicMock()
        mock_future1.result.return_value = mock_result1
        
        mock_executor.submit.side_effect = [mock_future1, mock_future2, mock_future3]
        
        # Act
        result = self.processor._process_files_parallel(
            file_paths, output_dir, options, progress_callback, total_count, current_index
        )
        
        # Assert
        # Should attempt to cancel futures
        mock_future2.cancel.assert_called()
        mock_future3.cancel.assert_called()

    def test_process_files_parallel_thread_safety(self):
        """
        GIVEN multiple threads processing files
        WHEN accessing shared resources (progress_callback, monitors)
        THEN expect:
            - No race conditions
            - Thread-safe access via _lock
            - Consistent state maintained
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 2
        current_index = 0
        
        # Mock the _lock to verify it's used
        with patch.object(self.processor, '_lock') as mock_lock:
            with patch.object(self.processor, '_process_single_file') as mock_process_single:
                mock_process_single.return_value = MagicMock()
                
                # Act
                result = self.processor._process_files_parallel(
                    file_paths, output_dir, options, progress_callback, total_count, current_index
                )
                
                # Assert
                # Lock should be used for thread-safe operations
                mock_lock.__enter__.assert_called()

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_process_files_parallel_with_timeout(self, mock_executor_class):
        """
        GIVEN a file that takes too long to process
        WHEN _process_files_parallel is called
        THEN expect:
            - Timeout detected
            - Thread terminated or skipped
            - Error logged with timeout info
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 2
        current_index = 0
        
        # Mock executor and futures
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        mock_future1 = Mock(spec=Future)
        mock_future2 = Mock(spec=Future)
        
        mock_result1 = MagicMock()
        mock_future1.result.return_value = mock_result1
        
        # Simulate timeout
        mock_future2.result.side_effect = TimeoutError("Task timed out")
        
        mock_executor.submit.side_effect = [mock_future1, mock_future2]
        
        # Act
        result = self.processor._process_files_parallel(
            file_paths, output_dir, options, progress_callback, total_count, current_index
        )
        
        # Assert
        self.assertEqual(len(result), 2)
        # Should handle timeout and log error
        self.resources['error_monitor'].handle_error.assert_called()


class TestBatchProcessorSequentialProcessing(unittest.TestCase):
    """Test sequential file processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 1
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    def test_process_files_sequential_basic(self):
        """
        GIVEN a list of files
        WHEN _process_files_sequential is called
        THEN expect:
            - Files processed one by one in order
            - Results returned in same order as input
            - Progress callback called for each file
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        with patch.object(self.processor, '_process_single_file') as mock_process_single:
            with patch.object(self.processor, '_get_output_path') as mock_get_output:
                mock_result1 = MagicMock()
                mock_result2 = MagicMock()
                mock_result3 = MagicMock()
                
                mock_process_single.side_effect = [mock_result1, mock_result2, mock_result3]
                mock_get_output.side_effect = ['/output/file1.txt', '/output/file2.txt', '/output/file3.txt']
                
                # Act
                result = self.processor._process_files_sequential(
                    file_paths, output_dir, options, progress_callback, total_count, current_index
                )
                
                # Assert
                self.assertEqual(len(result), 3)
                self.assertEqual(result, [mock_result1, mock_result2, mock_result3])
                self.assertEqual(mock_process_single.call_count, 3)
                self.assertEqual(progress_callback.call_count, 3)
                
                # Verify order of processing
                calls = mock_process_single.call_args_list
                self.assertEqual(calls[0][0][0], '/path/file1.txt')
                self.assertEqual(calls[1][0][0], '/path/file2.txt')
                self.assertEqual(calls[2][0][0], '/path/file3.txt')

    def test_process_files_sequential_with_error_continue(self):
        """
        GIVEN continue_on_error=True and a file that fails
        WHEN _process_files_sequential is called
        THEN expect:
            - Error logged for failed file
            - Processing continues with next file
            - Results include both successes and failures
        """
        # Arrange
        self.processor.continue_on_error = True
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        with patch.object(self.processor, '_process_single_file') as mock_process_single:
            with patch.object(self.processor, '_get_output_path') as mock_get_output:
                mock_result1 = MagicMock()
                mock_result3 = MagicMock()
                
                # Second file fails
                mock_process_single.side_effect = [
                    mock_result1,
                    Exception("Processing failed"),
                    mock_result3
                ]
                mock_get_output.side_effect = ['/output/file1.txt', '/output/file2.txt', '/output/file3.txt']
                
                # Act
                result = self.processor._process_files_sequential(
                    file_paths, output_dir, options, progress_callback, total_count, current_index
                )
                
                # Assert
                self.assertEqual(len(result), 3)
                # Should continue processing after error
                self.assertEqual(mock_process_single.call_count, 3)
                self.resources['error_monitor'].handle_error.assert_called()

    def test_process_files_sequential_with_error_stop(self):
        """
        GIVEN continue_on_error=False and a file that fails
        WHEN _process_files_sequential is called
        THEN expect:
            - Processing stops at first error
            - Results include files processed before error
            - Error details in final result
        """
        # Arrange
        self.processor.continue_on_error = False
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        with patch.object(self.processor, '_process_single_file') as mock_process_single:
            with patch.object(self.processor, '_get_output_path') as mock_get_output:
                mock_result1 = MagicMock()
                
                # Second file fails
                mock_process_single.side_effect = [
                    mock_result1,
                    Exception("Processing failed")
                ]
                mock_get_output.side_effect = ['/output/file1.txt', '/output/file2.txt']
                
                # Act
                result = self.processor._process_files_sequential(
                    file_paths, output_dir, options, progress_callback, total_count, current_index
                )
                
                # Assert
                # Should stop processing after error
                self.assertEqual(mock_process_single.call_count, 2)
                self.resources['error_monitor'].handle_error.assert_called()
                # Should only have processed first file successfully
                self.assertEqual(len([r for r in result if r == mock_result1]), 1)

    def test_process_files_sequential_with_cancellation_check(self):
        """
        GIVEN sequential processing of multiple files
        WHEN cancel_requested becomes True during processing
        THEN expect:
            - Processing stops after current file
            - Partial results returned
            - No new files started
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt', '/path/file3.txt']
        output_dir = '/output'
        options = {}
        progress_callback = MagicMock()
        total_count = 3
        current_index = 0
        
        def cancel_after_first(*args, **kwargs):
            if mock_process_single.call_count == 1:
                self.processor.cancel_requested = True
            return MagicMock()
        
        with patch.object(self.processor, '_process_single_file', side_effect=cancel_after_first) as mock_process_single:
            with patch.object(self.processor, '_get_output_path') as mock_get_output:
                mock_get_output.side_effect = ['/output/file1.txt', '/output/file2.txt', '/output/file3.txt']
                
                # Act
                result = self.processor._process_files_sequential(
                    file_paths, output_dir, options, progress_callback, total_count, current_index
                )
                
                # Assert
                # Should stop processing after cancellation
                self.assertTrue(self.processor.cancel_requested)
                # Should only process first file
                self.assertEqual(mock_process_single.call_count, 1)


class TestBatchProcessorSingleFileProcessing(unittest.TestCase):
    """Test single file processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(), # Remove spec for ProcessingPipeline to have dynamic attributes
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(), # Ditto for ResourceMonitor
            'security_monitor': MagicMock(), # Ditto for SecurityMonitor
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    def test_process_single_file_success(self):
        """
        GIVEN a valid file path and output path
        WHEN _process_single_file is called
        THEN expect:
            - File processed through pipeline
            - ProcessingResult with success status
            - Output written to specified path
        """
        # Arrange
        file_path = '/path/input/file.txt'
        output_path = '/path/output/file.txt'
        options = {'format': 'pdf'}
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output_path = output_path
        
        self.resources['security_monitor'].validate_security.return_value = True
        self.resources['processing_pipeline'].process_file.return_value = mock_result
        
        # Act
        result = self.processor._process_single_file(file_path, output_path, options)
        
        # Assert
        self.assertEqual(result, mock_result)
        self.resources['security_monitor'].validate_security.assert_called_once_with(file_path)
        self.resources['processing_pipeline'].process_file.assert_called_once_with(
            file_path, output_path, options
        )

    def test_process_single_file_with_security_violation(self):
        """
        GIVEN a file that fails security validation
        WHEN _process_single_file is called
        THEN expect:
            - Security monitor rejects file
            - ProcessingResult with security error
            - No output written
        """
        # Arrange
        file_path = '/path/suspicious/file.txt'
        output_path = '/path/output/file.txt'
        options = {}
        
        self.resources['security_monitor'].validate_security.return_value = False
        
        # Act
        result = self.processor._process_single_file(file_path, output_path, options)
        
        # Assert
        self.resources['security_monitor'].validate_security.assert_called_once_with(file_path)
        self.resources['processing_pipeline'].process_file.assert_not_called()
        # Should return error result
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    def test_process_single_file_with_pipeline_error(self):
        """
        GIVEN a file that causes pipeline error
        WHEN _process_single_file is called
        THEN expect:
            - Error caught and logged
            - ProcessingResult with error details
            - Error monitor handles exception
        """
        # Arrange
        file_path = '/path/corrupted/file.txt'
        output_path = '/path/output/file.txt'
        options = {}
        
        self.resources['security_monitor'].validate_security.return_value = True
        self.resources['processing_pipeline'].process_file.side_effect = Exception("Pipeline failed")
        
        # Act
        result = self.processor._process_single_file(file_path, output_path, options)
        
        # Assert
        self.resources['security_monitor'].validate_security.assert_called_once_with(file_path)
        self.resources['processing_pipeline'].process_file.assert_called_once()
        self.resources['error_monitor'].handle_error.assert_called()
        # Should return error result
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    def test_process_single_file_with_resource_exhaustion(self):
        """
        GIVEN resource monitor indicates exhaustion
        WHEN _process_single_file is called
        THEN expect:
            - Processing deferred or rejected
            - Appropriate error in result
            - System resources protected
        """
        # Arrange
        file_path = '/path/large/file.txt'
        output_path = '/path/output/file.txt'
        options = {}
        
        # Mock resource exhaustion
        self.resources['resource_monitor'].check_resources.return_value = False
        self.resources['resource_monitor'].get_resource_usage.return_value = {
            'memory_percent': 98,
            'cpu_percent': 95
        }
        
        # Act
        result = self.processor._process_single_file(file_path, output_path, options)
        
        # Assert
        self.resources['resource_monitor'].check_resources.assert_called()
        # Should not proceed with processing due to resource constraints
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    def test_process_single_file_without_output_path(self):
        """
        GIVEN output_path=None
        WHEN _process_single_file is called
        THEN expect:
            - File processed normally
            - No write operations performed
            - Result contains processed data
        """
        # Arrange
        file_path = '/path/input/file.txt'
        output_path = None
        options = {}
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output_path = None
        mock_result.data = "processed content"
        
        self.resources['security_monitor'].validate_security.return_value = True
        self.resources['processing_pipeline'].process_file.return_value = mock_result
        
        # Act
        result = self.processor._process_single_file(file_path, output_path, options)
        
        # Assert
        self.assertEqual(result, mock_result)
        self.resources['processing_pipeline'].process_file.assert_called_once_with(
            file_path, None, options
        )
        self.assertIsNone(result.output_path)
        self.assertEqual(result.data, "processed content")


class TestBatchProcessorPathHandling(unittest.TestCase):
    """Test path resolution and output path generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    @patch('os.path.abspath')
    @patch('os.path.exists')
    def test_resolve_paths_with_file_list(self, mock_exists, mock_abspath):
        """
        GIVEN a list of file paths (absolute and relative)
        WHEN _resolve_paths is called
        THEN expect:
            - All paths resolved to absolute paths
            - Non-existent files filtered or flagged
            - Original order preserved
        """
        # Arrange
        file_paths = ['./file1.txt', '/absolute/file2.txt', '../file3.txt']
        
        mock_exists.side_effect = [True, True, False]  # file3.txt doesn't exist
        mock_abspath.side_effect = [
            '/current/file1.txt',
            '/absolute/file2.txt',
            '/parent/file3.txt'
        ]
        
        # Act
        result = self.processor._resolve_paths(file_paths)
        
        # Assert
        self.assertEqual(len(result), 2)  # Only existing files
        self.assertIn('/current/file1.txt', result)
        self.assertIn('/absolute/file2.txt', result)
        self.assertNotIn('/parent/file3.txt', result)
        
        # Verify order is preserved for existing files
        self.assertEqual(result[0], '/current/file1.txt')
        self.assertEqual(result[1], '/absolute/file2.txt')

    @patch('os.walk')
    @patch('os.path.isdir')
    def test_resolve_paths_with_directory(self, mock_isdir, mock_walk):
        """
        GIVEN a directory path
        WHEN _resolve_paths is called
        THEN expect:
            - Directory walked recursively
            - All files discovered and returned
            - Hidden files handled per configuration
        """
        # Arrange
        directory_path = '/path/to/directory'
        mock_isdir.return_value = True
        
        # Mock os.walk to return files
        mock_walk.return_value = [
            ('/path/to/directory', ['subdir'], ['file1.txt', 'file2.pdf']),
            ('/path/to/directory/subdir', [], ['file3.docx', '.hidden.txt'])
        ]
        
        # Act
        result = self.processor._resolve_paths(directory_path)
        
        # Assert
        mock_walk.assert_called_once_with(directory_path)
        self.assertEqual(len(result), 4)
        self.assertIn('/path/to/directory/file1.txt', result)
        self.assertIn('/path/to/directory/file2.pdf', result)
        self.assertIn('/path/to/directory/subdir/file3.docx', result)
        self.assertIn('/path/to/directory/subdir/.hidden.txt', result)

    @patch('os.path.islink')
    @patch('os.path.realpath')
    @patch('os.path.exists')
    def test_resolve_paths_with_symlinks(self, mock_exists, mock_realpath, mock_islink):
        """
        GIVEN paths containing symlinks
        WHEN _resolve_paths is called
        THEN expect:
            - Symlinks resolved or handled per policy
            - No infinite loops with circular symlinks
            - Security validation of resolved paths
        """
        # Arrange
        file_paths = ['/path/symlink.txt', '/path/regular.txt']
        
        mock_islink.side_effect = [True, False]
        mock_realpath.side_effect = ['/path/real_file.txt', '/path/regular.txt']
        mock_exists.return_value = True
        
        # Act
        result = self.processor._resolve_paths(file_paths)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn('/path/real_file.txt', result)
        self.assertIn('/path/regular.txt', result)
        mock_realpath.assert_called_with('/path/symlink.txt')

    @patch('glob.glob')
    def test_resolve_paths_with_glob_patterns(self, mock_glob):
        """
        GIVEN file paths with glob patterns (*.txt)
        WHEN _resolve_paths is called
        THEN expect:
            - Patterns expanded to matching files
            - Multiple matches handled correctly
            - No matches returns empty or logs warning
        """
        # Arrange
        file_paths = ['/path/*.txt', '/path/*.pdf']
        
        mock_glob.side_effect = [
            ['/path/file1.txt', '/path/file2.txt'],
            []  # No PDF files found
        ]
        
        # Act
        result = self.processor._resolve_paths(file_paths)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn('/path/file1.txt', result)
        self.assertIn('/path/file2.txt', result)
        
        # Verify glob was called for each pattern
        self.assertEqual(mock_glob.call_count, 2)

    @patch('os.path.join')
    @patch('os.path.basename')
    @patch('os.path.splitext')
    def test_get_output_path_with_directory(self, mock_splitext, mock_basename, mock_join):
        """
        GIVEN input path and output directory
        WHEN _get_output_path is called
        THEN expect:
            - Output path in specified directory
            - Original filename preserved or modified per options
            - Correct file extension based on conversion
        """
        # Arrange
        input_path = '/input/document.docx'
        output_dir = '/output'
        options = {'format': 'pdf'}
        
        mock_basename.return_value = 'document.docx'
        mock_splitext.return_value = ('document', '.docx')
        mock_join.return_value = '/output/document.pdf'
        
        # Act
        result = self.processor._get_output_path(input_path, output_dir, options)
        
        # Assert
        self.assertEqual(result, '/output/document.pdf')
        mock_basename.assert_called_once_with(input_path)
        mock_splitext.assert_called_once_with('document.docx')
        mock_join.assert_called_once_with(output_dir, 'document.pdf')

    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('os.path.basename')
    @patch('os.path.splitext')
    def test_get_output_path_with_name_collision(self, mock_splitext, mock_basename, mock_join, mock_exists):
        """
        GIVEN output path that already exists
        WHEN _get_output_path is called
        THEN expect:
            - Collision handled per configuration
            - Possible strategies: overwrite, rename, error
            - Consistent behavior across files
        """
        # Arrange
        input_path = '/input/document.txt'
        output_dir = '/output'
        options = {'format': 'pdf', 'collision_strategy': 'rename'}
        
        mock_basename.return_value = 'document.txt'
        mock_splitext.return_value = ('document', '.txt')
        mock_exists.side_effect = [True, True, False]  # First two paths exist, third doesn't
        mock_join.side_effect = [
            '/output/document.pdf',
            '/output/document_1.pdf',
            '/output/document_2.pdf'
        ]
        
        # Act
        result = self.processor._get_output_path(input_path, output_dir, options)
        
        # Assert
        self.assertEqual(result, '/output/document_2.pdf')
        self.assertEqual(mock_exists.call_count, 3)

    @patch('os.path.join')
    @patch('datetime.datetime')
    def test_get_output_path_with_custom_naming(self, mock_datetime, mock_join):
        """
        GIVEN options with custom output naming pattern
        WHEN _get_output_path is called
        THEN expect:
            - Pattern applied correctly
            - Variables substituted (date, index, etc.)
            - Invalid patterns handled gracefully
        """
        # Arrange
        input_path = '/input/document.txt'
        output_dir = '/output'
        options = {
            'format': 'pdf',
            'naming_pattern': '{name}_{date}_{index}.{ext}',
            'index': 1
        }
        
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = '20231225'
        mock_join.return_value = '/output/document_20231225_1.pdf'
        
        # Act
        result = self.processor._get_output_path(input_path, output_dir, options)
        
        # Assert
        self.assertEqual(result, '/output/document_20231225_1.pdf')
        mock_join.assert_called_once()




class TestBatchProcessorStatusAndControl(unittest.TestCase):
    """Test status reporting and control methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    def test_processing_status_idle(self):
        """
        GIVEN BatchProcessor not processing
        WHEN processing_status property accessed
        THEN expect:
            - Status indicates idle/ready
            - No active files or threads
            - Previous results summary available
        """
        # Arrange
        self.processor.cancel_requested = False
        
        # Act
        status = self.processor.processing_status
        
        # Assert
        self.assertIsInstance(status, dict)
        self.assertEqual(status['state'], 'idle')
        self.assertEqual(status['active_threads'], 0)
        self.assertEqual(status['files_processing'], 0)
        self.assertIn('last_batch_summary', status)

    def test_processing_status_active(self):
        """
        GIVEN BatchProcessor actively processing
        WHEN processing_status property accessed
        THEN expect:
            - Current progress information
            - Active thread count
            - Files completed/remaining
            - Estimated time remaining
        """
        # Arrange
        # Mock active processing state
        self.processor._current_batch_size = 10
        self.processor._files_completed = 3
        self.processor._active_threads = 2
        
        with patch('threading.active_count', return_value=4):
            # Act
            status = self.processor.processing_status
            
            # Assert
            self.assertIsInstance(status, dict)
            self.assertEqual(status['state'], 'processing')
            self.assertEqual(status['files_completed'], 3)
            self.assertEqual(status['total_files'], 10)
            self.assertEqual(status['active_threads'], 2)
            self.assertIn('progress_percent', status)

    def test_cancel_processing_immediate(self):
        """
        GIVEN no active processing
        WHEN cancel_processing is called
        THEN expect:
            - cancel_requested set to True
            - No errors raised
            - Ready for next batch
        """
        # Arrange
        self.processor.cancel_requested = False
        
        # Act
        self.processor.cancel_processing()
        
        # Assert
        self.assertTrue(self.processor.cancel_requested)
        
        # Should be able to process next batch
        status = self.processor.processing_status
        self.assertEqual(status['state'], 'idle')

    def test_cancel_processing_during_batch(self):
        """
        GIVEN active batch processing
        WHEN cancel_processing is called
        THEN expect:
            - cancel_requested set to True
            - Current file completes
            - Remaining files skipped
            - Partial results available
        """
        # Arrange
        self.processor.cancel_requested = False
        self.processor._current_batch_size = 5
        self.processor._files_completed = 2
        
        # Act
        self.processor.cancel_processing()
        
        # Assert
        self.assertTrue(self.processor.cancel_requested)
        
        # Status should reflect cancellation request
        status = self.processor.processing_status
        self.assertTrue(status['cancellation_requested'])

    def test_set_max_batch_size_validation(self):
        """
        GIVEN various size values (valid and invalid)
        WHEN set_max_batch_size is called
        THEN expect:
            - Positive integers accepted
            - Zero or negative rejected
            - Size updated for future batches
        """
        # Arrange & Act & Assert
        # Valid positive integer
        self.processor.set_max_batch_size(50)
        self.assertEqual(self.processor.max_batch_size, 50)
        
        # Zero should be rejected
        with self.assertRaises(ValueError):
            self.processor.set_max_batch_size(0)
        
        # Negative should be rejected
        with self.assertRaises(ValueError):
            self.processor.set_max_batch_size(-1)
        
        # Non-integer should be rejected
        with self.assertRaises(TypeError):
            self.processor.set_max_batch_size("10")

    def test_set_continue_on_error_effect(self):
        """
        GIVEN different boolean values
        WHEN set_continue_on_error is called
        THEN expect:
            - Flag updated correctly
            - Behavior changes in next batch
            - Current batch unaffected
        """
        # Arrange
        original_value = self.processor.continue_on_error
        
        # Act & Assert
        self.processor.set_continue_on_error(True)
        self.assertTrue(self.processor.continue_on_error)
        
        self.processor.set_continue_on_error(False)
        self.assertFalse(self.processor.continue_on_error)
        
        # Non-boolean should be rejected
        with self.assertRaises(TypeError):
            self.processor.set_continue_on_error("true")

    def test_set_max_workers_validation(self):
        """
        GIVEN various worker counts
        WHEN set_max_workers is called
        THEN expect:
            - Positive integers accepted
            - Upper limit enforced (CPU count?)
            - Zero means sequential processing
        """
        # Arrange & Act & Assert
        # Valid positive integer
        self.processor.set_max_workers(4)
        self.assertEqual(self.processor.max_threads, 4)
        
        # Zero should be accepted (sequential processing)
        self.processor.set_max_workers(0)
        self.assertEqual(self.processor.max_threads, 0)
        
        # Negative should be rejected
        with self.assertRaises(ValueError):
            self.processor.set_max_workers(-1)
        
        # Non-integer should be rejected
        with self.assertRaises(TypeError):
            self.processor.set_max_workers(2.5)
        
        # Upper limit should be enforced
        with patch('os.cpu_count', return_value=8):
            with self.assertRaises(ValueError):
                self.processor.set_max_workers(16)  # More than 2x CPU count




class TestBatchProcessorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

    @patch('os.walk')
    @patch('os.path.realpath')
    @patch('os.path.islink')
    def test_process_batch_with_circular_directory_structure(self, mock_islink, mock_realpath, mock_walk):
        """
        GIVEN directory with circular symlinks
        WHEN process_batch is called with directory
        THEN expect:
            - No infinite recursion
            - Each file processed once
            - Warning logged about circular reference
        """
        # Arrange
        directory_path = '/path/with/circular/symlinks'
        
        # Mock circular symlink detection
        visited_paths = set()
        
        def mock_walk_side_effect(path):
            real_path = os.path.realpath(path)
            if real_path in visited_paths:
                # Circular reference detected
                return []
            visited_paths.add(real_path)
            return [
                (path, ['subdir'], ['file1.txt']),
                (path + '/subdir', [], ['file2.txt'])
            ]
        
        mock_walk.side_effect = mock_walk_side_effect
        mock_realpath.side_effect = lambda x: x  # Simplified realpath
        mock_islink.return_value = True
        
        with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
            mock_process_chunk.return_value = [MagicMock(), MagicMock()]
            
            # Act
            result = self.processor.process_batch(directory_path)
            
            # Assert
            self.assertIsNotNone(result)
            # Should log warning about circular reference
            self.resources['logger'].warning.assert_called()

    @patch('os.access')
    def test_process_batch_with_no_permissions(self, mock_access):
        """
        GIVEN files without read permissions
        WHEN process_batch is called
        THEN expect:
            - Permission errors handled gracefully
            - Error logged with file path
            - Other files still processed if continue_on_error
        """
        # Arrange
        file_paths = ['/restricted/file1.txt', '/accessible/file2.txt']
        
        # Mock permission check
        mock_access.side_effect = lambda path, mode: not path.startswith('/restricted')
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_single_file') as mock_process_single:
                # First file fails with permission error, second succeeds
                mock_process_single.side_effect = [
                    PermissionError("Permission denied"),
                    MagicMock()
                ]
                
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                self.resources['error_monitor'].handle_error.assert_called()
                # Should continue processing if continue_on_error is True
                self.assertEqual(mock_process_single.call_count, 2)

    def test_process_batch_with_corrupted_file(self):
        """
        GIVEN a corrupted/unreadable file
        WHEN process_batch is called
        THEN expect:
            - Corruption detected by pipeline
            - Error result for that file
            - No crash or memory issues
        """
        # Arrange
        file_paths = ['/path/corrupted.file']
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_single_file') as mock_process_single:
                # Mock corruption detection
                mock_result = MagicMock()
                mock_result.success = False
                mock_result.error = "File appears to be corrupted"
                mock_process_single.return_value = mock_result
                
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                self.assertFalse(result.results[0].success)
                self.assertIn("corrupted", result.results[0].error)

    def test_process_batch_with_extremely_large_file(self):
        """
        GIVEN a file exceeding size limits
        WHEN process_batch is called
        THEN expect:
            - Size limit enforced
            - Appropriate error or chunked processing
            - Memory usage stays within bounds
        """
        # Arrange
        file_paths = ['/path/huge_file.txt']
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch('os.path.getsize', return_value=1024*1024*1024*5):  # 5GB file
                with patch.object(self.processor, '_process_single_file') as mock_process_single:
                    # Mock size limit check
                    mock_result = MagicMock()
                    mock_result.success = False
                    mock_result.error = "File exceeds maximum size limit"
                    mock_process_single.return_value = mock_result
                    
                    # Act
                    result = self.processor.process_batch(file_paths)
                    
                    # Assert
                    self.assertIsNotNone(result)
                    self.assertFalse(result.results[0].success)
                    self.assertIn("size limit", result.results[0].error)

    def test_process_batch_with_unicode_filenames(self):
        """
        GIVEN files with unicode characters in names
        WHEN process_batch is called
        THEN expect:
            - Names handled correctly
            - Output files preserve unicode
            - No encoding errors
        """
        # Arrange
        file_paths = ['/path/文档.txt', '/path/résumé.pdf', '/path/файл.docx']
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock() for _ in file_paths]
                for i, result in enumerate(mock_results):
                    result.input_path = file_paths[i]
                    result.success = True
                
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                for i, res in enumerate(result.results):
                    self.assertEqual(res.input_path, file_paths[i])
                    self.assertTrue(res.success)

    def test_concurrent_batch_processing_attempts(self):
        """
        GIVEN BatchProcessor already processing
        WHEN process_batch called again
        THEN expect:
            - Second call rejected or queued
            - Clear error message
            - First batch continues unaffected
        """
        # Arrange
        file_paths1 = ['/path/file1.txt']
        file_paths2 = ['/path/file2.txt']
        
        # Mock processing state
        self.processor._is_processing = True
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths2):
            # Act
            result = self.processor.process_batch(file_paths2)
            
            # Assert
            self.assertIsNotNone(result)
            self.assertFalse(result.success)
            self.assertIn("already processing", result.error.lower())

    def test_progress_callback_exception_handling(self):
        """
        GIVEN progress_callback that raises exception
        WHEN process_batch is called
        THEN expect:
            - Exception caught and logged
            - Processing continues
            - Callback disabled or retried
        """
        # Arrange
        file_paths = ['/path/file1.txt', '/path/file2.txt']
        
        def failing_callback(current, total, filename):
            if current == 1:  # Fail on first call
                raise Exception("Callback error")
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_chunk') as mock_process_chunk:
                mock_results = [MagicMock(), MagicMock()]
                mock_process_chunk.return_value = mock_results
                
                # Act
                result = self.processor.process_batch(
                    file_paths, 
                    progress_callback=failing_callback
                )
                
                # Assert
                self.assertIsNotNone(result)
                # Should log callback error but continue processing
                self.resources['error_monitor'].handle_error.assert_called()

    def test_resource_monitor_communication_failure(self):
        """
        GIVEN resource_monitor that fails to respond
        WHEN processing files
        THEN expect:
            - Timeout or default behavior
            - Processing continues with defaults
            - Error logged but not fatal
        """
        # Arrange
        file_paths = ['/path/file1.txt']
        
        # Mock resource monitor failure
        self.resources['resource_monitor'].check_resources.side_effect = Exception("Monitor unavailable")
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_process_single_file') as mock_process_single:
                mock_result = MagicMock()
                mock_result.success = True
                mock_process_single.return_value = mock_result
                
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                # Should continue processing despite monitor failure
                self.assertTrue(result.results[0].success)
                self.resources['error_monitor'].handle_error.assert_called()



class TestBatchProcessorIntegration(unittest.TestCase):
    """Test integration with other components."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configs = MagicMock()
        self.mock_configs.resources.max_batch_size = 10
        self.mock_configs.resources.max_threads = 2
        self.mock_configs.processing.continue_on_error = True
        
        self.resources = {
            'processing_pipeline': MagicMock(spec=ProcessingPipeline),
            'error_monitor': MagicMock(spec=ErrorMonitor),
            'resource_monitor': MagicMock(spec=ResourceMonitor),
            'security_monitor': MagicMock(spec=SecurityMonitor),
            'logger': MagicMock(spec=Logger),
            'processing_result': MagicMock(spec=ProcessingResult),
            'batch_result': MagicMock(spec=BatchResult),
        }
        
        self.processor = BatchProcessor(configs=self.mock_configs, resources=self.resources)

        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()

    def test_integration_with_pipeline(self):
        """
        GIVEN BatchProcessor with real pipeline
        WHEN processing various file types
        THEN expect:
            - Correct converters selected
            - Pipeline options respected
            - Results match pipeline output
        """
        # Arrange
        file_paths = ['/path/document.docx', '/path/image.jpg', '/path/spreadsheet.xlsx']
        options = {'format': 'pdf', 'quality': 'high'}
        
        # Mock pipeline responses for different file types
        mock_results = []
        for i, path in enumerate(file_paths):
            result = MagicMock()
            result.success = True
            result.input_path = path
            result.output_format = 'pdf'
            result.converter_used = f'converter_{i}'
            mock_results.append(result)
        
        self.resources['processing_pipeline'].process_file.side_effect = mock_results
        self.resources['security_monitor'].validate_security.return_value = True
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_get_output_path', side_effect=[
                '/output/document.pdf', '/output/image.pdf', '/output/spreadsheet.pdf'
            ]):
                # Act
                result = self.processor.process_batch(file_paths, '/output', options)
                
                # Assert
                self.assertIsNotNone(result)
                self.assertEqual(len(result.results), 3)
                
                # Verify pipeline was called with correct options for each file
                calls = self.resources['processing_pipeline'].process_file.call_args_list
                for call in calls:
                    self.assertEqual(call[0][2], options)  # options parameter

    def test_integration_with_error_monitor(self):
        """
        GIVEN BatchProcessor with real error monitor
        WHEN errors occur during processing
        THEN expect:
            - Errors logged to monitor
            - Error aggregation works
            - Error reports generated correctly
        """
        # Arrange
        file_paths = ['/path/good_file.txt', '/path/bad_file.txt', '/path/another_good_file.txt']
        
        def mock_process_file(file_path, output_path, options):
            if 'bad_file' in file_path:
                raise ValueError("File processing failed")
            result = MagicMock()
            result.success = True
            return result
        
        self.resources['processing_pipeline'].process_file.side_effect = mock_process_file
        self.resources['security_monitor'].validate_security.return_value = True
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_get_output_path', return_value='/output/file.txt'):
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                # Error monitor should have been called for the failed file
                self.resources['error_monitor'].handle_error.assert_called()
                
                # Should have error details in result
                error_results = [r for r in result.results if not r.success]
                self.assertGreater(len(error_results), 0)

    def test_integration_with_resource_monitor(self):
        """
        GIVEN BatchProcessor with real resource monitor
        WHEN processing resource-intensive files
        THEN expect:
            - Resource usage tracked
            - Throttling applied when needed
            - Memory limits respected
        """
        # Arrange
        file_paths = ['/path/large_file1.pdf', '/path/large_file2.pdf']
        
        # Mock resource monitor to simulate high usage after first file
        resource_usage_calls = 0
        def mock_check_resources():
            nonlocal resource_usage_calls
            resource_usage_calls += 1
            return resource_usage_calls <= 1  # First call OK, second call indicates high usage
        
        def mock_get_resource_usage():
            return {
                'memory_percent': 85 if resource_usage_calls > 1 else 45,
                'cpu_percent': 90 if resource_usage_calls > 1 else 30
            }
        
        self.resources['resource_monitor'].check_resources.side_effect = mock_check_resources
        self.resources['resource_monitor'].get_resource_usage.side_effect = mock_get_resource_usage
        self.resources['processing_pipeline'].process_file.return_value = Mock(success=True)
        self.resources['security_monitor'].validate_security.return_value = True
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_get_output_path', return_value='/output/file.pdf'):
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                # Resource monitor should have been consulted
                self.resources['resource_monitor'].check_resources.assert_called()
                self.resources['resource_monitor'].get_resource_usage.assert_called()

    def test_integration_with_security_monitor(self):
        """
        GIVEN BatchProcessor with real security monitor
        WHEN processing files with security concerns
        THEN expect:
            - Security validation performed
            - Dangerous files rejected
            - Security events logged
        """
        # Arrange
        file_paths = ['/path/safe_file.txt', '/path/suspicious_file.exe', '/path/another_safe_file.pdf']
        
        def mock_validate_file(file_path):
            return not file_path.endswith('.exe')  # Reject .exe files
        
        self.resources['security_monitor'].validate_security.side_effect = mock_validate_file
        self.resources['processing_pipeline'].process_file.return_value = Mock(success=True)
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_get_output_path', return_value='/output/file.txt'):
                # Act
                result = self.processor.process_batch(file_paths)
                
                # Assert
                self.assertIsNotNone(result)
                
                # Security monitor should have been called for each file
                self.assertEqual(self.resources['security_monitor'].validate_security.call_count, 3)
                
                # Suspicious file should have been rejected
                rejected_results = [r for r in result.results if not r.success]
                self.assertGreater(len(rejected_results), 0)
                
                # Safe files should have been processed
                successful_results = [r for r in result.results if r.success]
                self.assertEqual(len(successful_results), 2)

    def test_full_workflow_simulation(self):
        """
        GIVEN complete system setup
        WHEN processing mixed batch of files
        THEN expect:
            - All components work together
            - Results match expectations
            - Performance within targets
        """
        # Arrange
        file_paths = [
            '/input/document.docx',
            '/input/image.jpg',
            '/input/spreadsheet.xlsx',
            '/input/presentation.pptx'
        ]
        output_dir = '/output'
        options = {'format': 'pdf', 'quality': 'high'}
        
        # Mock all components to simulate realistic behavior
        self.resources['security_monitor'].validate_security.return_value = True
        self.resources['resource_monitor'].check_resources.return_value = True
        self.resources['resource_monitor'].get_resource_usage.return_value = {
            'memory_percent': 45,
            'cpu_percent': 30
        }
        
        # Mock pipeline results
        pipeline_results = []
        for i, path in enumerate(file_paths):
            result = MagicMock()
            result.success = True
            result.input_path = path
            result.output_path = f'/output/file_{i}.pdf'
            result.processing_time = 0.5 + (i * 0.1)  # Simulate varying processing times
            result.file_size_mb = 1.2 + (i * 0.3)
            pipeline_results.append(result)
        
        self.resources['processing_pipeline'].process_file.side_effect = pipeline_results
        
        progress_calls = []
        def track_progress(current, total, filename):
            progress_calls.append((current, total, filename))
        
        with patch.object(self.processor, '_resolve_paths', return_value=file_paths):
            with patch.object(self.processor, '_get_output_path', side_effect=[
                r.output_path for r in pipeline_results
            ]):
                start_time = time.time()
                
                # Act
                result = self.processor.process_batch(
                    file_paths,
                    output_dir,
                    options,
                    progress_callback=track_progress
                )
                
                end_time = time.time()
                
                # Assert
                self.assertIsNotNone(result)
                self.assertTrue(result.success)
                self.assertEqual(len(result.results), 4)
                
                # All files should have been processed successfully
                for res in result.results:
                    self.assertTrue(res.success)

                # Progress callback should have been called for each file
                self.assertEqual(len(progress_calls), 4)

                # Performance check - should complete within reasonable time
                processing_time = end_time - start_time
                self.assertLess(processing_time, 5.0)  # Should complete in under 5 seconds

                # All components should have been involved
                self.resources['security_monitor'].validate_security.assert_called()
                self.resources['resource_monitor'].check_resources.assert_called()
                self.resources['processing_pipeline'].process_file.assert_called()
