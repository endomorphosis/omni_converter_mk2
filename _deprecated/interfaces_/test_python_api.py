# """
# Tests for the Python API module.

# This module provides comprehensive tests for the PythonAPI class, which serves as
# the primary programmatic interface for the Omni Converter system. The tests verify
# that the API correctly handles file conversion requests, batch processing, configuration
# management, and error conditions. Most tests use mock objects to isolate the API from
# its dependencies, ensuring focused unit testing of the interface layer.
# """

# import os
# import unittest
# from unittest.mock import MagicMock, patch

# from core.processing_result import ProcessingResult
# from managers.batch_result import BatchResult
# from interfaces.python_api import PythonAPI


# class TestPythonAPI(unittest.TestCase):
#     """
#     Test suite for the PythonAPI class.
    
#     This test class verifies that the PythonAPI correctly implements the public interface
#     to the Omni Converter functionality. Tests cover file conversion, batch processing,
#     configuration management, error handling, and retrieval of supported format information.
#     Most tests use mocked dependencies to isolate the API implementation from the underlying
#     processing components.
#     """
    
#     def setUp(self):
#         """
#         Set up test environment before each test.
        
#         Creates mock objects for dependencies (Configs, BatchProcessor),
#         configures the mock objects with appropriate return values, creates a
#         PythonAPI instance with the mocked dependencies, and generates a simple
#         test file for conversion tests.
#         """
#         # Mock dependencies
#         self.mock_configs = MagicMock()
#         self.mock_batch_processor = MagicMock()

#         # Configure mock configs
#         self.mock_configs.get_config_value.return_value = "default_value"
#         self.mock_configs.current_config = {
#             'output': {'format': 'txt'},
#             'processing': {'normalize_text': True},
#             'resources': {'memory_limit_gb': 6, 'cpu_limit_percent': 80}
#         }
#         from configs import configs, Configs
#         from logger import logger
#         from format_handlers.format_registry import format_registry
#         from core.processing_pipeline import processing_pipeline
#         from core.processing_result import ProcessingResult
#         from managers.batch_processor import batch_processor
#         from managers.batch_result import BatchResult
#         from managers.resource_monitor import resource_monitor

#         self.mock_resources = {
#             'batch_processor': self.mock_batch_processor,
#             'resource_monitor': MagicMock(),
#         }

#         # Create API with mocked dependencies
#         self.api = PythonAPI(
#             resources=self.mock_resources,
#             configs=self.mock_configs
#         )
        
#         # Create sample test file
#         self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
#         with open(self.test_file_path, 'w') as f:
#             f.write('Test content')
    
#     def tearDown(self):
#         """
#         Clean up the test environment after each test.
        
#         Removes the temporary test file created during setUp to ensure
#         the filesystem is returned to its original state.
#         """
#         # Remove test file
#         if os.path.exists(self.test_file_path):
#             os.remove(self.test_file_path)
    
#     @patch('interfaces.python_api.processing_pipeline')
#     def test_convert_file(self, mock_pipeline):
#         """
#         Test the convert_file method for processing a single file.
        
#         Verifies that the API correctly delegates to the processing pipeline when
#         converting a single file, providing it with the correct file path and options.
#         Also checks that the API correctly returns the ProcessingResult object from
#         the pipeline. Uses patching to mock the processing_pipeline module.
#         """
#         # Configure mock
#         mock_result = ProcessingResult(
#             success=True,
#             file_path=self.test_file_path,
#             format="txt",
#             metadata={"key": "value"}
#         )
#         mock_pipeline.process_file.return_value = mock_result
        
#         # Convert file
#         result = self.api.convert_file(self.test_file_path)
        
#         # Check that pipeline was called
#         mock_pipeline.process_file.assert_called_once_with(
#             self.test_file_path, None, self.api._get_default_options()
#         )
        
#         # Check result
#         self.assertEqual(result, mock_result)
    
#     def test_convert_file_not_found(self):
#         """
#         Test error handling when attempting to convert a non-existent file.
        
#         Verifies that the API correctly raises a FileNotFoundError when attempting
#         to convert a file that doesn't exist. This ensures proper error handling at
#         the API level rather than allowing lower-level exceptions to propagate.
#         """
#         with self.assertRaises(FileNotFoundError):
#             self.api.convert_file("/path/to/nonexistent/file.txt")
    
#     @patch('interfaces.python_api.resource_monitor')
#     def test_convert_batch(self, mock_resource_monitor):
#         """
#         Test the convert_batch method for processing multiple files.
        
#         Verifies that the API correctly delegates to the batch processor when
#         converting multiple files, properly configuring the processor with batch size
#         and error handling settings before processing. Confirms that the API returns
#         the BatchResult object from the processor. Uses patching to mock the
#         resource_monitor module.
#         """
#         # Configure mocks
#         mock_batch_result = BatchResult()
#         self.mock_batch_processor.process_batch.return_value = mock_batch_result
        
#         # Convert batch with proper types for resource limits and include max_batch_size param
#         result = self.api.convert_batch(
#             [self.test_file_path], 
#             options={
#                 "max_cpu": 50.0, 
#                 "max_memory": 1024,
#                 "max_batch_size": 10, 
#                 "continue_on_error": True
#             }
#         )
        
#         # Check that batch processor was called
#         self.mock_batch_processor.process_batch.assert_called_once()
        
#         # Check that batch processor was configured
#         self.mock_batch_processor.set_max_batch_size.assert_called_with(10)
#         self.mock_batch_processor.set_continue_on_error.assert_called_with(True)
        
#         # Check result
#         self.assertEqual(result, mock_batch_result)
    
#     @patch('interfaces.python_api.format_registry')
#     def test_get_supported_formats(self, mock_registry):
#         """
#         Test the supported_formats method for retrieving available format information.
        
#         Verifies that the API correctly delegates to the format registry when retrieving
#         information about supported formats. Checks that the API returns the format
#         information exactly as provided by the registry, organized by category.
#         Uses patching to mock the format_registry module.
#         """
#         # Configure mock
#         mock_formats = {
#             'text': ['html', 'xml'],
#             'image': ['jpeg', 'png']
#         }
#         mock_registry.get_formats_by_category.return_value = mock_formats
        
#         # Get formats
#         formats = self.api.supported_formats
        
#         # Check result
#         self.assertEqual(formats, mock_formats)
#         mock_registry.get_formats_by_category.assert_called_once()
    
#     def test_set_config(self):
#         """
#         Test the set_config method for updating configuration values.
        
#         Verifies that the API correctly delegates to the config manager when setting
#         configuration values using a flattened key-value dictionary. Ensures that
#         multiple configuration values can be set in a single call and that the
#         method returns a success indicator.
#         """
#         # Set config
#         result = self.api.set_config({
#             'output.format': 'json',
#             'processing.normalize_text': False
#         })
        
#         # Check result
#         self.assertTrue(result)
        
#         # Check that configs was called for each key
#         self.assertEqual(self.mock_configs.set_config_value.call_count, 2)
    
#     def test_get_config(self):
#         """
#         Test the get_config method for retrieving current configuration.
        
#         Verifies that the API correctly returns the current configuration from the
#         config manager, preserving the nested structure of configuration categories
#         and their values.
#         """
#         # Get config
#         config = self.api.get_config()
        
#         # Check result
#         self.assertEqual(config, self.mock_configs.current_config)
    
#     def test_get_default_options(self):
#         """
#         Test the _get_default_options protected method for building processing options.
        
#         Verifies that the API correctly builds a processing options dictionary from
#         configuration values, applying appropriate defaults where necessary. This test
#         ensures that configuration values are properly translated into processing
#         options used by the pipeline.
#         """
#         # Configure mock to return different values for different keys
#         def mock_get_config_value(key, default):
#             if key == "output.format":
#                 return "json"
#             elif key == "processing.normalize_text":
#                 return False
#             else:
#                 return default
        
#         self.mock_configs.get_config_value.side_effect = mock_get_config_value
        
#         # Get default options
#         options = self.api._get_default_options()
        
#         # Check options
#         self.assertEqual(options["format"], "json")
#         self.assertEqual(options["normalize_text"], False)
#         self.assertIn("max_batch_size", options)
#         self.assertIn("max_cpu", options)
#         self.assertIn("max_memory", options)


# if __name__ == "__main__":
#     unittest.main()