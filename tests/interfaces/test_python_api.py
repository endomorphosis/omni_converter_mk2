"""
Tests for the Python API module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from core.processing_result import ProcessingResult
from managers.batch_result import BatchResult
from interfaces.python_api import PythonAPI


class TestPythonAPI(unittest.TestCase):
    """Test the PythonAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_config_manager = MagicMock()
        self.mock_batch_processor = MagicMock()
        
        # Configure mock config_manager
        self.mock_config_manager.get_config_value.return_value = "default_value"
        self.mock_config_manager.current_config = {
            'output': {'format': 'txt'},
            'processing': {'normalize_text': True},
            'resources': {'memory_limit_gb': 6, 'cpu_limit_percent': 80}
        }
        
        # Create API with mocked dependencies
        self.api = PythonAPI(
            custom_config_manager=self.mock_config_manager,
            custom_batch_processor=self.mock_batch_processor
        )
        
        # Create sample test file
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('Test content')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test file
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    @patch('interfaces.python_api.processing_pipeline')
    def test_convert_file(self, mock_pipeline):
        """Test converting a single file."""
        # Configure mock
        mock_result = ProcessingResult(
            success=True,
            file_path=self.test_file_path,
            format="txt",
            metadata={"key": "value"}
        )
        mock_pipeline.process_file.return_value = mock_result
        
        # Convert file
        result = self.api.convert_file(self.test_file_path)
        
        # Check that pipeline was called
        mock_pipeline.process_file.assert_called_once_with(
            self.test_file_path, None, self.api._get_default_options()
        )
        
        # Check result
        self.assertEqual(result, mock_result)
    
    def test_convert_file_not_found(self):
        """Test converting a file that doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.api.convert_file("/path/to/nonexistent/file.txt")
    
    @patch('interfaces.python_api.resource_monitor')
    def test_convert_batch(self, mock_resource_monitor):
        """Test batch conversion."""
        # Configure mocks
        mock_batch_result = BatchResult()
        self.mock_batch_processor.process_batch.return_value = mock_batch_result
        
        # Convert batch
        result = self.api.convert_batch([self.test_file_path])
        
        # Check that batch processor was called
        self.mock_batch_processor.process_batch.assert_called_once()
        
        # Check that batch processor was configured
        self.mock_batch_processor.set_max_batch_size.assert_called()
        self.mock_batch_processor.set_continue_on_error.assert_called()
        
        # Check result
        self.assertEqual(result, mock_batch_result)
    
    @patch('interfaces.python_api.format_registry')
    def test_get_supported_formats(self, mock_registry):
        """Test getting supported formats."""
        # Configure mock
        mock_formats = {
            'text': ['html', 'xml'],
            'image': ['jpeg', 'png']
        }
        mock_registry.get_formats_by_category.return_value = mock_formats
        
        # Get formats
        formats = self.api.get_supported_formats()
        
        # Check result
        self.assertEqual(formats, mock_formats)
        mock_registry.get_formats_by_category.assert_called_once()
    
    def test_set_config(self):
        """Test setting configuration."""
        # Set config
        result = self.api.set_config({
            'output.format': 'json',
            'processing.normalize_text': False
        })
        
        # Check result
        self.assertTrue(result)
        
        # Check that config_manager was called for each key
        self.assertEqual(self.mock_config_manager.set_config_value.call_count, 2)
    
    def test_get_config(self):
        """Test getting configuration."""
        # Get config
        config = self.api.get_config()
        
        # Check result
        self.assertEqual(config, self.mock_config_manager.current_config)
    
    def test_get_default_options(self):
        """Test getting default options."""
        # Configure mock to return different values for different keys
        def mock_get_config_value(key, default):
            if key == "output.format":
                return "json"
            elif key == "processing.normalize_text":
                return False
            else:
                return default
        
        self.mock_config_manager.get_config_value.side_effect = mock_get_config_value
        
        # Get default options
        options = self.api._get_default_options()
        
        # Check options
        self.assertEqual(options["format"], "json")
        self.assertEqual(options["normalize_text"], False)
        self.assertIn("batch_size", options)
        self.assertIn("max_cpu", options)
        self.assertIn("max_memory", options)


if __name__ == "__main__":
    unittest.main()