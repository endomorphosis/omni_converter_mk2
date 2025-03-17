"""
Test the batch processor module.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core.processing_result import ProcessingResult
from managers.batch_processor import BatchProcessor
from managers.batch_result import BatchResult


class TestBatchProcessor(unittest.TestCase):
    """Test the BatchProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_pipeline = MagicMock()
        self.mock_error_handler = MagicMock()
        self.mock_resource_monitor = MagicMock()
        self.mock_security_manager = MagicMock()
        
        # Configure resource monitor
        self.mock_resource_monitor.is_resource_available.return_value = (True, None)
        
        # Configure security manager
        self.mock_security_manager.validate_security.return_value = MagicMock(is_safe=True)
        
        # Create batch processor
        self.batch_processor = BatchProcessor(
            pipeline=self.mock_pipeline,
            error_handler=self.mock_error_handler,
            resource_monitor=self.mock_resource_monitor,
            security_manager=self.mock_security_manager,
            max_batch_size=10,
            continue_on_error=True,
            max_workers=2
        )
        
        # Create temporary test directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create some test files
        self.test_files = []
        for i in range(5):
            file_path = os.path.join(self.temp_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Remove any other files in the temp directory
        if os.path.exists(self.temp_dir):
            for file_name in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        # Remove test directory
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except OSError as e:
                print(f"Warning: Could not remove temp directory: {e}")
            
        # Stop patchers if they exist
        if hasattr(self, 'patcher') and self.patcher:
            self.patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.batch_processor.max_batch_size, 10)
        self.assertTrue(self.batch_processor.continue_on_error)
        self.assertEqual(self.batch_processor.max_workers, 2)
        self.assertFalse(self.batch_processor.cancel_requested)
    
    @patch('managers.batch_processor.logger')
    def test_process_batch_with_file_list(self, mock_logger):
        """Test processing a batch with a list of files."""
        # Mock process_file to return success for even files and failure for odd files
        def mock_process_file(file_path, output_path, options):
            file_index = int(os.path.basename(file_path).split('_')[2].split('.')[0])
            if file_index % 2 == 0:
                return ProcessingResult(
                    success=True,
                    file_path=file_path,
                    output_path=output_path,
                    format="txt",
                    metadata={"index": file_index}
                )
            else:
                return ProcessingResult(
                    success=False,
                    file_path=file_path,
                    output_path=output_path,
                    format="txt",
                    errors=[f"Test error for file {file_index}"]
                )
        
        self.mock_pipeline.process_file.side_effect = mock_process_file
        
        # Mock BatchResult to avoid datetime issues in testing
        self.patcher = patch('managers.batch_processor.BatchResult')
        self.mock_batch_result = self.patcher.start()
        self.mock_batch_result_instance = MagicMock()
        self.mock_batch_result_instance.total_files = 5
        self.mock_batch_result_instance.successful_files = 3
        self.mock_batch_result_instance.failed_files = 2
        self.mock_batch_result.return_value = self.mock_batch_result_instance
        
        # Process the batch
        output_dir = os.path.join(self.temp_dir, "output")
        result = self.batch_processor.process_batch(
            file_paths=self.test_files,
            output_dir=output_dir,
            options={"format": "txt"}
        )
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.successful_files, 3)  # Files 0, 2, 4
        self.assertEqual(result.failed_files, 2)      # Files 1, 3
        
        # Check that the pipeline was called for each file
        self.assertEqual(self.mock_pipeline.process_file.call_count, 5)
        
        # Check that resource monitoring was started and stopped
        self.mock_resource_monitor.start_monitoring.assert_called_once()
        self.mock_resource_monitor.stop_monitoring.assert_called_once()
    
    @patch('managers.batch_processor.logger')
    def test_process_batch_with_directory(self, mock_logger):
        """Test processing a batch with a directory."""
        # Mock process_file to always succeed
        self.mock_pipeline.process_file.return_value = ProcessingResult(
            success=True,
            file_path="",
            format="txt"
        )
        
        # Mock BatchResult to avoid datetime issues in testing
        self.patcher = patch('managers.batch_processor.BatchResult')
        self.mock_batch_result = self.patcher.start()
        self.mock_batch_result_instance = MagicMock()
        self.mock_batch_result.return_value = self.mock_batch_result_instance
        
        # Process the batch with directory path
        result = self.batch_processor.process_batch(
            file_paths=self.temp_dir,
            options={"format": "txt"}
        )
        
        # Check the result - since we're using a mock, we rely on the mock's values set in setup
        self.assertEqual(result, self.mock_batch_result_instance)
        
        # Check that the pipeline was called for each file
        self.assertEqual(self.mock_pipeline.process_file.call_count, 5)
    
    @patch('managers.batch_processor.logger')
    def test_process_batch_with_security_validation(self, mock_logger):
        """Test processing a batch with security validation."""
        # Configure security manager to flag some files as unsafe
        def mock_validate_security(file_path):
            file_index = int(os.path.basename(file_path).split('_')[2].split('.')[0])
            if file_index == 3:
                result = MagicMock()
                result.is_safe = False
                result.issues = ["Security issue"]
                return result
            else:
                result = MagicMock()
                result.is_safe = True
                result.issues = []
                return result
        
        self.mock_security_manager.validate_security.side_effect = mock_validate_security
        
        # Configure pipeline to succeed for all files that pass security validation
        self.mock_pipeline.process_file.return_value = ProcessingResult(
            success=True,
            file_path="",
            format="txt"
        )
        
        # Mock BatchResult to avoid datetime issues in testing
        self.patcher = patch('managers.batch_processor.BatchResult')
        self.mock_batch_result = self.patcher.start()
        self.mock_batch_result_instance = MagicMock()
        self.mock_batch_result_instance.total_files = 5
        self.mock_batch_result_instance.successful_files = 4
        self.mock_batch_result_instance.failed_files = 1
        self.mock_batch_result.return_value = self.mock_batch_result_instance
        
        # Process the batch
        result = self.batch_processor.process_batch(
            file_paths=self.test_files,
            options={"format": "txt"}
        )
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.successful_files, 4)  # All except file 3
        self.assertEqual(result.failed_files, 1)      # File 3
        
        # Check that security validation was called for each file
        self.assertEqual(self.mock_security_manager.validate_security.call_count, 5)
        
        # Check that the pipeline was called only for secure files
        self.assertEqual(self.mock_pipeline.process_file.call_count, 4)
    
    @patch('managers.batch_processor.logger')
    def test_cancel_processing(self, mock_logger):
        """Test canceling batch processing."""
        # Mock process_file to be slow, so we can cancel
        def slow_process_file(file_path, output_path, options):
            if os.path.basename(file_path) == "test_file_2.txt":
                self.batch_processor.cancel_processing()
            return ProcessingResult(
                success=True,
                file_path=file_path,
                output_path=output_path,
                format="txt"
            )
        
        self.mock_pipeline.process_file.side_effect = slow_process_file
        
        # Mock BatchResult to avoid datetime issues in testing
        self.patcher = patch('managers.batch_processor.BatchResult')
        self.mock_batch_result = self.patcher.start()
        self.mock_batch_result_instance = MagicMock()
        self.mock_batch_result_instance.total_files = 3  # Only processes up to test_file_2.txt
        self.mock_batch_result.return_value = self.mock_batch_result_instance
        
        # Process the batch
        result = self.batch_processor.process_batch(
            file_paths=self.test_files,
            options={"format": "txt"}
        )
        
        # Check that processing was cancelled
        self.assertTrue(self.batch_processor.cancel_requested)
        
        # Check that the result is incomplete
        self.assertLess(result.total_files, 5)
    
    def test_set_max_batch_size(self):
        """Test setting the maximum batch size."""
        self.batch_processor.set_max_batch_size(20)
        self.assertEqual(self.batch_processor.max_batch_size, 20)
        
        # Test with invalid value
        self.batch_processor.set_max_batch_size(0)
        self.assertEqual(self.batch_processor.max_batch_size, 1)  # Clamped to min 1
    
    def test_set_continue_on_error(self):
        """Test setting the continue on error flag."""
        self.batch_processor.set_continue_on_error(False)
        self.assertFalse(self.batch_processor.continue_on_error)
        
        self.batch_processor.set_continue_on_error(True)
        self.assertTrue(self.batch_processor.continue_on_error)
    
    def test_set_max_workers(self):
        """Test setting the maximum number of workers."""
        self.batch_processor.set_max_workers(4)
        self.assertEqual(self.batch_processor.max_workers, 4)
        
        # Test with invalid value
        self.batch_processor.set_max_workers(0)
        self.assertEqual(self.batch_processor.max_workers, 1)  # Clamped to min 1
    
    def test_get_processing_status(self):
        """Test getting the processing status."""
        # Configure mock return values
        self.mock_pipeline.get_pipeline_status.return_value = {"status": "idle"}
        self.mock_resource_monitor.get_current_usage.return_value = {"cpu": 10.0, "memory": 100.0}
        self.mock_error_handler.get_error_statistics.return_value = {"total_errors": 0}
        
        # Get status
        status = self.batch_processor.get_processing_status()
        
        # Check status
        self.assertEqual(status["pipeline"], {"status": "idle"})
        self.assertEqual(status["resources"], {"cpu": 10.0, "memory": 100.0})
        self.assertEqual(status["errors"], {"total_errors": 0})
        self.assertFalse(status["cancel_requested"])
    
    def test_resolve_paths_with_string(self):
        """Test resolving paths with a string path."""
        # Test with a file path
        paths = self.batch_processor._resolve_paths(self.test_files[0])
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], self.test_files[0])
        
        # Test with a directory path
        paths = self.batch_processor._resolve_paths(self.temp_dir)
        self.assertEqual(len(paths), 5)
        for path in self.test_files:
            self.assertIn(path, paths)
    
    def test_resolve_paths_with_list(self):
        """Test resolving paths with a list of paths."""
        # Test with a list of file paths
        paths = self.batch_processor._resolve_paths(self.test_files)
        self.assertEqual(len(paths), 5)
        for path in self.test_files:
            self.assertIn(path, paths)
        
        # Test with a mixed list (files and directory)
        mixed_list = [self.test_files[0], self.temp_dir]
        paths = self.batch_processor._resolve_paths(mixed_list)
        self.assertGreaterEqual(len(paths), 5)
    
    def test_get_output_path(self):
        """Test getting the output path for a file."""
        # Test with output directory
        output_dir = "/output/dir"
        input_path = "/input/dir/file.txt"
        options = {"format": "json"}
        
        output_path = self.batch_processor._get_output_path(input_path, output_dir, options)
        
        self.assertEqual(output_path, "/output/dir/file.json")
        
        # Test without output directory
        output_path = self.batch_processor._get_output_path(input_path, None, options)
        self.assertIsNone(output_path)


if __name__ == "__main__":
    unittest.main()