"""
Test the error handler module.
"""

import unittest
from unittest.mock import MagicMock, patch

from managers.error_handler import ErrorHandler


class TestErrorHandler(unittest.TestCase):
    """Test the ErrorHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = MagicMock()
        self.error_handler = ErrorHandler(custom_logger=self.mock_logger)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.error_handler.error_counters, {})
        self.assertEqual(self.error_handler.error_types, set())
        self.assertFalse(self.error_handler.suppress_errors)
    
    def test_handle_error_string(self):
        """Test handling a string error."""
        self.error_handler.handle_error("Test error")
        
        # Check error counters
        self.assertIn("StringError", self.error_handler.error_types)
        self.assertEqual(self.error_handler.error_counters["StringError"], 1)
        
        # Check that the logger was called
        self.mock_logger.error.assert_called_once()
    
    def test_handle_error_exception(self):
        """Test handling an exception."""
        test_exception = ValueError("Test exception")
        
        # With suppress_errors=False, the exception should be re-raised
        with self.assertRaises(ValueError):
            self.error_handler.handle_error(test_exception)
        
        # Check error counters
        self.assertIn("ValueError", self.error_handler.error_types)
        self.assertEqual(self.error_handler.error_counters["ValueError"], 1)
        
        # Check that the logger was called
        self.mock_logger.error.assert_called_once()
    
    def test_handle_error_suppressed(self):
        """Test handling an exception with suppress_errors=True."""
        self.error_handler.suppress_errors = True
        test_exception = ValueError("Test exception")
        
        # With suppress_errors=True, the exception should not be re-raised
        self.error_handler.handle_error(test_exception)
        
        # Check error counters
        self.assertIn("ValueError", self.error_handler.error_types)
        self.assertEqual(self.error_handler.error_counters["ValueError"], 1)
        
        # Check that the logger was called
        self.mock_logger.error.assert_called_once()
    
    def test_log_error(self):
        """Test logging an error."""
        test_exception = ValueError("Test exception")
        context = {"file_path": "/path/to/file.txt"}
        
        self.error_handler.log_error(test_exception, context)
        
        # Check that the logger was called with the correct arguments
        self.mock_logger.error.assert_called_once()
        args, kwargs = self.mock_logger.error.call_args
        self.assertIn("ValueError", args[0])
        self.assertIn("file_path", kwargs["context"])
        self.assertIn("error_type", kwargs["context"])
        self.assertIn("traceback", kwargs["context"])
    
    def test_get_error_statistics(self):
        """Test getting error statistics."""
        # Add some errors
        self.error_handler.handle_error("Error 1")
        self.error_handler.handle_error("Error 2")
        self.error_handler.handle_error(ValueError("Error 3"))
        
        # Get statistics
        stats = self.error_handler.get_error_statistics()
        
        # Check statistics
        self.assertEqual(stats["total_errors"], 3)
        self.assertEqual(len(stats["error_types"]), 2)
        self.assertIn("StringError", stats["error_types"])
        self.assertIn("ValueError", stats["error_types"])
        self.assertEqual(stats["error_counts"]["StringError"], 2)
        self.assertEqual(stats["error_counts"]["ValueError"], 1)
    
    def test_reset_error_counters(self):
        """Test resetting error counters."""
        # Add some errors
        self.error_handler.handle_error("Error 1")
        self.error_handler.handle_error(ValueError("Error 2"))
        
        # Reset counters
        self.error_handler.reset_error_counters()
        
        # Check counters
        self.assertEqual(self.error_handler.error_counters, {})
        self.assertNotEqual(self.error_handler.error_types, set())  # Error types should still be present
    
    def test_set_error_suppression(self):
        """Test setting error suppression."""
        # Default is False
        self.assertFalse(self.error_handler.suppress_errors)
        
        # Set to True
        self.error_handler.set_error_suppression(True)
        self.assertTrue(self.error_handler.suppress_errors)
        
        # Set back to False
        self.error_handler.set_error_suppression(False)
        self.assertFalse(self.error_handler.suppress_errors)
    
    def test_get_most_common_errors(self):
        """Test getting the most common errors."""
        # Add some errors with different frequencies
        for _ in range(5):
            self.error_handler.handle_error("Common error")
        
        for _ in range(3):
            self.error_handler.handle_error(ValueError("Less common"))
        
        self.error_handler.handle_error(TypeError("Rare error"))
        
        # Get most common errors
        common_errors = self.error_handler.get_most_common_errors(limit=2)
        
        # Check results
        self.assertEqual(len(common_errors), 2)
        self.assertEqual(common_errors[0]["type"], "StringError")
        self.assertEqual(common_errors[0]["count"], 5)
        self.assertEqual(common_errors[1]["type"], "ValueError")
        self.assertEqual(common_errors[1]["count"], 3)
    
    def test_has_errors(self):
        """Test checking if errors have been handled."""
        # Initially there are no errors
        self.assertFalse(self.error_handler.has_errors())
        
        # Add an error
        self.error_handler.handle_error("Test error")
        
        # Now there should be errors
        self.assertTrue(self.error_handler.has_errors())
        
        # Reset counters
        self.error_handler.reset_error_counters()
        
        # Now there should be no errors again
        self.assertFalse(self.error_handler.has_errors())
    
    def test_get_error_count(self):
        """Test getting error counts."""
        # Add some errors
        self.error_handler.handle_error("Error 1")
        self.error_handler.handle_error("Error 2")
        self.error_handler.handle_error(ValueError("Error 3"))
        self.error_handler.handle_error(ValueError("Error 4"))
        
        # Get total count
        self.assertEqual(self.error_handler.get_error_count(), 4)
        
        # Get count for specific type (by string)
        self.assertEqual(self.error_handler.get_error_count("StringError"), 2)
        
        # Get count for specific type (by exception class)
        self.assertEqual(self.error_handler.get_error_count(ValueError), 2)
        
        # Get count for non-existent type
        self.assertEqual(self.error_handler.get_error_count("NonExistentError"), 0)


if __name__ == "__main__":
    unittest.main()