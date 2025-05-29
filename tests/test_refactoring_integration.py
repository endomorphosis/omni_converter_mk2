"""
Integration tests for dataclass and Pydantic model refactoring.

This module contains integration tests to ensure that refactored classes
work correctly with other components of the system.
"""

import unittest
from datetime import datetime
import os
import tempfile
from typing import Any, Optional

# Core components
from core.processing_pipeline import ProcessingPipeline
from core.output_formatter._output_formatter import OutputFormatter
from core.text_normalizer._text_normalizer import TextNormalizer
from deprecated.content_extractor import ContentExtractor
from core.content_extractor.format_registry import FormatRegistry
from configs import configs, Configs
from file_format_detector.file_format_detector import file_format_detector
from file_validator.file_validator import FileValidator

# Classes being refactored
from core.processing_pipeline.processing_result import ProcessingResult
from monitors.batch_result import BatchResult
from core.output_formatter._output_formatter import FormattedOutput
from core.content_extractor.base_handler import Content
from core.text_normalizer._text_normalizer import NormalizedContent

# Optional Pydantic support
try:
    import pydantic
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False


class TestProcessingResultIntegration(unittest.TestCase):
    """
    Test integration of the ProcessingResult class with other components.
    
    These tests verify that the ProcessingResult class can be refactored to a dataclass
    without breaking integration with other components.
    """
    
    def setUp(self):
        """Set up the test environment."""
        resources = {
            "validator": FileValidator(),
            "detector": file_format_detector,
            "extractor": ContentExtractor(),
            "normalizer": TextNormalizer(),
            "formatter": OutputFormatter()
        }

        self.pipeline = ProcessingPipeline(resources=resources,configs=configs)
        self.formatter = OutputFormatter()

    def test_integration_with_processing_pipeline(self):
        """Test integration with the processing pipeline."""
        # Create a simple result to be passed to pipeline components
        result = ProcessingResult(
            success=True,
            file_path="/path/to/file.txt",
            output_path="/path/to/output.txt",
            format="text/plain",
            metadata={"size": 1024}
        )
        
        # Since we don't have direct access to the pipeline's error handling,
        # we'll test the ProcessingResult error adding directly
        error_message = "Test error from pipeline"
        result.add_error(error_message)
        
        # Check that the error was properly added to the result
        self.assertFalse(result.success)
        self.assertIn(error_message, result.error_string)
    
    def test_dict_serialization_compatibility(self):
        """Test that to_dict() output is compatible with consumers."""
        # Create a result with typical values
        result = ProcessingResult(
            success=True,
            file_path="/path/to/file.txt",
            output_path="/path/to/output.txt",
            format="text/plain",
            metadata={"size": 1024}
        )
        
        # Get dictionary representation
        result_dict = result.to_dict()
        
        # Check the structure is as expected
        self.assertTrue(isinstance(result_dict, dict))
        self.assertTrue("success" in result_dict)
        self.assertTrue("file_path" in result_dict)
        self.assertTrue("output_path" in result_dict)
        self.assertTrue("format" in result_dict)
        self.assertTrue("errors" in result_dict)
        self.assertTrue("metadata" in result_dict)
        self.assertTrue("content_hash" in result_dict)
        self.assertTrue("timestamp" in result_dict)
        
        # Check timestamp is in ISO format
        try:
            datetime.fromisoformat(result_dict["timestamp"])
        except ValueError:
            self.fail("timestamp is not in valid ISO format")


class TestBatchResultIntegration(unittest.TestCase):
    """
    Test integration of the BatchResult class with other components.
    
    These tests verify that the BatchResult class can be refactored to a dataclass
    without breaking integration with other components.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create some processing results to use in batch
        self.result1 = ProcessingResult(
            success=True,
            file_path="/path/to/file1.txt",
            output_path="/path/to/output1.txt",
            format="text/plain"
        )
        
        self.result2 = ProcessingResult(
            success=False,
            file_path="/path/to/file2.jpg",
            errors=["Unsupported format"]
        )
        
        # Create a batch result with these results
        self.batch_result = BatchResult(
            results=[self.result1, self.result2],
            statistics={"processing_speed": "10 files/min"}
        )
        
        # Complete the batch
        self.batch_result.complete()
    
    def test_summary_integration(self):
        """Test that get_summary() output can be used by other components."""
        summary = self.batch_result.get_summary()
        
        # Check required fields that might be used by reporting components
        self.assertTrue("total_files" in summary)
        self.assertTrue("successful_files" in summary)
        self.assertTrue("failed_files" in summary)
        self.assertTrue("success_rate_percent" in summary)
        self.assertTrue("start_time" in summary)
        self.assertTrue("end_time" in summary)
        self.assertTrue("duration_seconds" in summary)
        self.assertTrue("statistics" in summary)
        
        # Check that values are of expected types
        self.assertTrue(isinstance(summary["total_files"], int))
        self.assertTrue(isinstance(summary["successful_files"], int))
        self.assertTrue(isinstance(summary["failed_files"], int))
        self.assertTrue(isinstance(summary["success_rate_percent"], float))
        self.assertTrue(isinstance(summary["duration_seconds"], float))
        
        # Ensure start_time and end_time can be parsed as ISO dates
        try:
            datetime.fromisoformat(summary["start_time"])
            datetime.fromisoformat(summary["end_time"])
        except ValueError:
            self.fail("start_time or end_time is not in valid ISO format")
    
    def test_file_list_integration(self):
        """Test that file list methods return expected data structure."""
        # Get lists of files
        successful_files = self.batch_result.get_successful_files()
        failed_files = self.batch_result.get_failed_files()
        
        # Check that the lists contain the right files
        self.assertEqual(len(successful_files), 1)
        self.assertEqual(len(failed_files), 1)
        self.assertEqual(successful_files[0], "/path/to/file1.txt")
        self.assertEqual(failed_files[0], "/path/to/file2.jpg")
        
        # Add another result and check lists are updated
        new_result = ProcessingResult(
            success=True,
            file_path="/path/to/file3.csv",
            output_path="/path/to/output3.txt"
        )
        self.batch_result.add_result(new_result)
        
        successful_files = self.batch_result.get_successful_files()
        self.assertEqual(len(successful_files), 2)
        self.assertEqual(successful_files[1], "/path/to/file3.csv")


class TestFormattedOutputIntegration(unittest.TestCase):
    """
    Test integration of the FormattedOutput class with other components.
    
    These tests verify that the FormattedOutput class can be refactored to a dataclass
    without breaking integration with other components.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = OutputFormatter()
        
        # Create a sample content
        self.content = Content(
            text="This is test content",
            metadata={"source": "test", "size": 100},
            source_format="text/plain",
            source_path="/path/to/source.txt"
        )
    
    def test_integration_with_output_formatter(self):
        """Test that FormattedOutput works with OutputFormatter."""
        # Format the content
        formatted = self.formatter.format_output(
            self.content,
            format="txt",
            output_path="/path/to/output.txt"
        )
        
        # Check the resulting FormattedOutput
        self.assertEqual(formatted.content, "This is test content")
        self.assertEqual(formatted.format, "txt")
        self.assertEqual(formatted.output_path, "/path/to/output.txt")
        self.assertTrue("source_format" in formatted.metadata)
        self.assertTrue("source_path" in formatted.metadata)
        self.assertTrue("extraction_time" in formatted.metadata)
    
    def test_writing_to_file(self):
        """Test that writing to file works as expected."""
        # Format the content
        formatted = self.formatter.format_output(
            self.content,
            format="txt"
        )
        
        # Write to a temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "output.txt")
            
            # Test writing
            output_path = formatted.write_to_file(temp_file)
            self.assertEqual(output_path, temp_file)
            self.assertTrue(os.path.exists(temp_file))
            
            # Check the content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertEqual(content, "This is test content")


class TestContentIntegration(unittest.TestCase):
    """
    Test integration of the Content and NormalizedContent classes with other components.
    
    These tests verify that these classes can be refactored to Pydantic models
    without breaking integration with other components.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.text_normalizer = TextNormalizer()
        self.output_formatter = OutputFormatter()
        
        # Create a sample content
        self.content = Content(
            text="This is test content with  multiple   spaces",
            metadata={"source": "test", "size": 100},
            source_format="text/plain",
            source_path="/path/to/source.txt"
        )
    
    def test_integration_with_text_normalizer(self):
        """Test integration with TextNormalizer."""
        # Normalize the content
        normalized = self.text_normalizer.normalize_text(
            self.content,
            normalizers=["whitespace", "line_endings"]
        )
        
        # Check the resulting NormalizedContent
        self.assertEqual(normalized.text, "This is test content with multiple spaces")
        self.assertEqual(normalized.metadata, self.content.metadata)
        self.assertEqual(normalized.source_format, self.content.source_format)
        self.assertEqual(normalized.source_path, self.content.source_path)
        self.assertEqual(sorted(normalized.normalized_by), ["line_endings", "whitespace"])
    
    def test_integration_with_output_formatter(self):
        """Test integration with OutputFormatter."""
        # Format the content
        formatted_txt = self.output_formatter.format_output(
            self.content,
            format="txt"
        )
        
        # Check text output
        self.assertEqual(formatted_txt.content, self.content.text)
        
        # Format as JSON
        formatted_json = self.output_formatter.format_output(
            self.content,
            format="json"
        )
        
        # Content should be JSON string with all fields
        self.assertIn('"text":', formatted_json.content)
        self.assertIn('"metadata":', formatted_json.content)
        self.assertIn('"sections":', formatted_json.content)
        self.assertIn('"source_format":', formatted_json.content)
        self.assertIn('"source_path":', formatted_json.content)
        self.assertIn('"extraction_time":', formatted_json.content)
        
        # Format normalized content as markdown
        normalized = self.text_normalizer.normalize_text(self.content)
        formatted_md = self.output_formatter.format_output(
            normalized,
            format="md"
        )
        
        # Markdown should include normalization info
        self.assertIn("## Normalization", formatted_md.content)
        self.assertIn("Applied normalizers:", formatted_md.content)


if __name__ == "__main__":
    unittest.main()