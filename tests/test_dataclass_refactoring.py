"""
Tests for dataclass refactoring compatibility.

This module contains tests to ensure that refactoring classes to dataclasses
preserves all existing functionality and behavior.
"""

import unittest
from datetime import datetime, timedelta
import json
import os
import tempfile
from typing import Any, Optional

# Original class imports
from core.processing_pipeline.processing_result import ProcessingResult
from monitors.batch_result import BatchResult
from core.output_formatter._output_formatter import FormattedOutput
from core.content_extractor.base_handler import Content
from core.text_normalizer._text_normalizer import NormalizedContent


class TestProcessingResultCompatibility(unittest.TestCase):
    """
    Test suite to ensure that ProcessingResult dataclass refactoring maintains compatibility.
    
    These tests verify that all functionality of the original ProcessingResult class
    is preserved when refactored to a dataclass.
    """
    
    def setUp(self):
        """Set up test cases."""
        self.success_result = ProcessingResult(
            success=True,
            file_path="/path/to/file.txt",
            output_path="/path/to/output.txt",
            format="text/plain",
            metadata={"size": 1024, "encoding": "utf-8"}
        )
        
        self.failure_result = ProcessingResult(
            success=False,
            file_path="/path/to/file.jpg",
            errors=["File format not supported"]
        )
    
    def test_initialization(self):
        """Test initialization with various parameter combinations."""
        # Test with minimum required parameters
        result = ProcessingResult(success=True, file_path="/path/to/file.txt")
        self.assertTrue(result.success)
        self.assertEqual(result.file_path, "/path/to/file.txt")
        self.assertEqual(result.output_path, "")
        self.assertEqual(result.format, "")
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metadata, {})
        self.assertEqual(result.content_hash, "")
        self.assertIsInstance(result.timestamp, datetime)
        
        # Test with all parameters
        now = datetime.now()
        custom_result = ProcessingResult(
            success=True,
            file_path="/path/to/file.txt",
            output_path="/path/to/output.txt",
            format="text/plain",
            errors=["Warning: file is large"],
            metadata={"size": 1024},
            content_hash="abc123"
        )
        
        self.assertEqual(custom_result.output_path, "/path/to/output.txt")
        self.assertEqual(custom_result.format, "text/plain")
        self.assertEqual(custom_result.errors, ["Warning: file is large"])
        self.assertEqual(custom_result.metadata, {"size": 1024})
        self.assertEqual(custom_result.content_hash, "abc123")
        
        # Verify timestamp is recent
        self.assertLess((datetime.now() - custom_result.timestamp).total_seconds(), 5)
    
    def test_add_error(self):
        """Test adding errors and its effect on success status."""
        result = ProcessingResult(success=True, file_path="/path/to/file.txt")
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        
        result.add_error("Error occurred")
        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Error occurred")
        
        result.add_error("Another error")
        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.errors[1], "Another error")
    
    def test_add_metadata(self):
        """Test adding metadata."""
        result = ProcessingResult(success=True, file_path="/path/to/file.txt")
        self.assertEqual(result.metadata, {})
        
        result.add_metadata("size", 1024)
        self.assertEqual(result.metadata, {"size": 1024})
        
        result.add_metadata("encoding", "utf-8")
        self.assertEqual(result.metadata, {"size": 1024, "encoding": "utf-8"})
        
        # Overwrite existing metadata
        result.add_metadata("size", 2048)
        self.assertEqual(result.metadata, {"size": 2048, "encoding": "utf-8"})
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result_dict = self.success_result.to_dict()
        
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["file_path"], "/path/to/file.txt")
        self.assertEqual(result_dict["output_path"], "/path/to/output.txt")
        self.assertEqual(result_dict["format"], "text/plain")
        self.assertEqual(result_dict["errors"], [])
        self.assertEqual(result_dict["metadata"], {"size": 1024, "encoding": "utf-8"})
        self.assertEqual(result_dict["content_hash"], "")
        self.assertIsInstance(result_dict["timestamp"], str)
    
    def test_get_error_string(self):
        """Test formatting errors as a string."""
        # No errors
        self.assertEqual(self.success_result.error_string, "No errors")
        
        # One error
        self.assertEqual(self.failure_result.error_string, "- File format not supported")
        
        # Multiple errors
        result = ProcessingResult(
            success=False,
            file_path="/path/to/file.txt",
            errors=["Error 1", "Error 2", "Error 3"]
        )
        expected = "- Error 1\n- Error 2\n- Error 3"
        self.assertEqual(result.error_string, expected)
    
    def test_string_representation(self):
        """Test string representation of the result."""
        # Success result
        str_repr = str(self.success_result)
        self.assertIn("Processing /path/to/file.txt - SUCCESS", str_repr)
        self.assertIn("Output: /path/to/output.txt", str_repr)
        self.assertIn("Format: text/plain", str_repr)
        self.assertIn("Errors: No errors", str_repr)
        self.assertIn("Timestamp:", str_repr)
        
        # Failure result
        str_repr = str(self.failure_result)
        self.assertIn("Processing /path/to/file.jpg - FAILED", str_repr)
        self.assertIn("Output: None", str_repr)
        self.assertIn("Format: Unknown", str_repr)
        self.assertIn("Errors: - File format not supported", str_repr)


class TestBatchResultCompatibility(unittest.TestCase):
    """
    Test suite to ensure that BatchResult dataclass refactoring maintains compatibility.
    
    These tests verify that all functionality of the original BatchResult class
    is preserved when refactored to a dataclass.
    """
    
    def setUp(self):
        """Set up test cases."""
        # Create some processing results
        self.success_result1 = ProcessingResult(
            success=True,
            file_path="/path/to/file1.txt",
            output_path="/path/to/output1.txt",
            format="text/plain"
        )
        
        self.success_result2 = ProcessingResult(
            success=True,
            file_path="/path/to/file2.txt",
            output_path="/path/to/output2.txt",
            format="text/plain"
        )
        
        self.failure_result = ProcessingResult(
            success=False,
            file_path="/path/to/file3.jpg",
            errors=["File format not supported"]
        )
        
        # Create a batch result with some results
        self.start_time = datetime.now() - timedelta(minutes=5)
        self.batch_result = BatchResult(
            results=[self.success_result1, self.failure_result],
            statistics={"processing_speed": "10 files/min"},
            start_time=self.start_time
        )
    
    def test_initialization(self):
        """Test initialization with various parameter combinations."""
        # Test with default parameters
        result = BatchResult()
        self.assertEqual(result.results, [])
        self.assertEqual(result.statistics, {})
        self.assertIsInstance(result.start_time, datetime)
        self.assertIsNone(result.end_time)
        self.assertEqual(result.total_files, 0)
        self.assertEqual(result.successful_files, 0)
        self.assertEqual(result.failed_files, 0)
        
        # Test with explicit parameters
        custom_result = BatchResult(
            results=[self.success_result1, self.success_result2, self.failure_result],
            statistics={"processing_speed": "15 files/min"},
            start_time=self.start_time
        )
        
        self.assertEqual(len(custom_result.results), 3)
        self.assertEqual(custom_result.statistics, {"processing_speed": "15 files/min"})
        self.assertEqual(custom_result.start_time, self.start_time)
        self.assertIsNone(custom_result.end_time)
        self.assertEqual(custom_result.total_files, 3)
        self.assertEqual(custom_result.successful_files, 2)
        self.assertEqual(custom_result.failed_files, 1)
        
        # Test with timestamp as start_time
        timestamp_result = BatchResult(
            start_time=self.start_time.timestamp()
        )
        self.assertIsInstance(timestamp_result.start_time, datetime)
        # Allow for tiny differences due to floating point precision
        self.assertLess(abs((timestamp_result.start_time - self.start_time).total_seconds()), 1)
    
    def test_add_result(self):
        """Test adding results and updating counts."""
        # Start with an empty batch
        batch = BatchResult()
        self.assertEqual(batch.total_files, 0)
        self.assertEqual(batch.successful_files, 0)
        self.assertEqual(batch.failed_files, 0)
        
        # Add a success result
        batch.add_result(self.success_result1)
        self.assertEqual(batch.total_files, 1)
        self.assertEqual(batch.successful_files, 1)
        self.assertEqual(batch.failed_files, 0)
        
        # Add a failure result
        batch.add_result(self.failure_result)
        self.assertEqual(batch.total_files, 2)
        self.assertEqual(batch.successful_files, 1)
        self.assertEqual(batch.failed_files, 1)
        
        # Add another success result
        batch.add_result(self.success_result2)
        self.assertEqual(batch.total_files, 3)
        self.assertEqual(batch.successful_files, 2)
        self.assertEqual(batch.failed_files, 1)
    
    def test_complete(self):
        """Test marking a batch as complete."""
        batch = BatchResult(
            results=[self.success_result1, self.success_result2, self.failure_result],
            start_time=datetime.now() - timedelta(seconds=10)
        )
        
        self.assertIsNone(batch.end_time)
        self.assertNotIn('duration_seconds', batch.statistics)
        self.assertNotIn('success_rate', batch.statistics)
        
        batch.complete()
        
        self.assertIsNotNone(batch.end_time)
        self.assertIn('duration_seconds', batch.statistics)
        self.assertIn('success_rate', batch.statistics)
        
        # Check that duration is sensible
        self.assertGreaterEqual(batch.statistics['duration_seconds'], 9.5)  # Allow for small timing differences
        self.assertLessEqual(batch.statistics['duration_seconds'], 20)
        
        # Check success rate
        self.assertEqual(batch.statistics['success_rate'], (2/3) * 100)
    
    def test_get_summary(self):
        """Test getting a summary of the batch processing."""
        # Complete the batch
        self.batch_result.complete()
        
        summary = self.batch_result.get_summary()
        
        self.assertEqual(summary['total_files'], 2)
        self.assertEqual(summary['successful_files'], 1)
        self.assertEqual(summary['failed_files'], 1)
        self.assertEqual(summary['success_rate_percent'], 50.0)
        self.assertEqual(summary['start_time'], self.start_time.isoformat())
        self.assertIsNotNone(summary['end_time'])
        self.assertIsNotNone(summary['duration_seconds'])
        self.assertEqual(summary['statistics']['processing_speed'], "10 files/min")
        
        # Test with empty batch
        empty_batch = BatchResult()
        empty_summary = empty_batch.get_summary()
        self.assertEqual(empty_summary['success_rate_percent'], 0)
    
    def test_get_failed_files(self):
        """Test getting a list of failed files."""
        failed_files = self.batch_result.get_failed_files()
        self.assertEqual(failed_files, ['/path/to/file3.jpg'])
        
        # Add another failure
        another_failure = ProcessingResult(
            success=False,
            file_path="/path/to/file4.png",
            errors=["Another error"]
        )
        self.batch_result.add_result(another_failure)
        
        failed_files = self.batch_result.get_failed_files()
        self.assertEqual(failed_files, ['/path/to/file3.jpg', '/path/to/file4.png'])
    
    def test_get_successful_files(self):
        """Test getting a list of successful files."""
        successful_files = self.batch_result.get_successful_files()
        self.assertEqual(successful_files, ['/path/to/file1.txt'])
        
        # Add another success
        self.batch_result.add_result(self.success_result2)
        
        successful_files = self.batch_result.get_successful_files()
        self.assertEqual(successful_files, ['/path/to/file1.txt', '/path/to/file2.txt'])
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        # Complete the batch
        self.batch_result.complete()
        
        result_dict = self.batch_result.to_dict()
        
        self.assertEqual(result_dict['total_files'], 2)
        self.assertEqual(result_dict['successful_files'], 1)
        self.assertEqual(result_dict['failed_files'], 1)
        self.assertEqual(len(result_dict['results']), 2)
        self.assertEqual(result_dict['statistics']['processing_speed'], "10 files/min")
        self.assertEqual(result_dict['start_time'], self.start_time.isoformat())
        self.assertIsNotNone(result_dict['end_time'])
        
        # Check that results are properly converted
        self.assertTrue(result_dict['results'][0]['success'])
        self.assertEqual(result_dict['results'][0]['file_path'], '/path/to/file1.txt')
        self.assertFalse(result_dict['results'][1]['success'])
        self.assertEqual(result_dict['results'][1]['file_path'], '/path/to/file3.jpg')
    
    def test_string_representation(self):
        """Test string representation of the batch result."""
        # In-progress batch
        str_repr = str(self.batch_result)
        self.assertIn("Batch Processing Result:", str_repr)
        self.assertIn("Total Files: 2", str_repr)
        self.assertIn("Successful: 1", str_repr)
        self.assertIn("Failed: 1", str_repr)
        self.assertIn("Success Rate: 50.0%", str_repr)
        self.assertIn("Status: In Progress", str_repr)
        
        # Completed batch
        self.batch_result.complete()
        str_repr = str(self.batch_result)
        self.assertIn("Duration:", str_repr)
        self.assertIn("seconds", str_repr)
        
        # Empty batch
        empty_batch = BatchResult()
        str_repr = str(empty_batch)
        self.assertIn("Total Files: 0", str_repr)
        self.assertIn("Success Rate: N/A", str_repr)


class TestFormattedOutputCompatibility(unittest.TestCase):
    """
    Test suite to ensure that FormattedOutput dataclass refactoring maintains compatibility.
    
    These tests verify that all functionality of the original FormattedOutput class
    is preserved when refactored to a dataclass.
    """
    
    def setUp(self):
        """Set up test cases."""
        self.content = "This is test content"
        self.format = "txt"
        self.metadata = {"source": "test", "size": 100}
        self.output_path = "/path/to/output.txt"
        
        self.formatted_output = FormattedOutput(
            content=self.content,
            format=self.format,
            metadata=self.metadata,
            output_path=self.output_path
        )
    
    def test_initialization(self):
        """Test initialization with various parameter combinations."""
        # Test with minimum required parameters
        output = FormattedOutput(content="Test", format="txt")
        self.assertEqual(output.content, "Test")
        self.assertEqual(output.format, "txt")
        self.assertEqual(output.metadata, {})
        self.assertEqual(output.output_path, "")
        
        # Test with all parameters
        full_output = FormattedOutput(
            content="Full test",
            format="json",
            metadata={"test": True},
            output_path="/path/to/file.json"
        )
        self.assertEqual(full_output.content, "Full test")
        self.assertEqual(full_output.format, "json")
        self.assertEqual(full_output.metadata, {"test": True})
        self.assertEqual(full_output.output_path, "/path/to/file.json")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        output_dict = self.formatted_output.to_dict()
        
        self.assertEqual(output_dict["content"], self.content)
        self.assertEqual(output_dict["format"], self.format)
        self.assertEqual(output_dict["metadata"], self.metadata)
        self.assertEqual(output_dict["output_path"], self.output_path)
    
    def test_write_to_file(self):
        """Test writing content to a file."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "output.txt")
            
            # Test with output_path parameter
            result_path = self.formatted_output.write_to_file(temp_file)
            self.assertEqual(result_path, temp_file)
            self.assertTrue(os.path.exists(temp_file))
            
            # Check content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertEqual(content, self.content)
            
            # Test with default output_path
            os.remove(temp_file)  # Clean up first
            output = FormattedOutput(
                content="Default path test",
                format="txt",
                output_path=temp_file
            )
            result_path = output.write_to_file()
            self.assertEqual(result_path, temp_file)
            
            # Check content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertEqual(content, "Default path test")
    
    def test_write_to_file_errors(self):
        """Test error handling when writing to a file."""
        # Test with no output path
        output = FormattedOutput(content="No path", format="txt")
        with self.assertRaises(ValueError):
            output.write_to_file()
        
        # Test with invalid output path (directory that doesn't exist)
        if os.name == 'nt':  # Windows
            invalid_path = "Z:\\nonexistent\\folder\\file.txt"
        else:  # Unix/Linux
            invalid_path = "/nonexistent/folder/that/cannot/be/created/file.txt"
            
        output = FormattedOutput(content="Invalid path", format="txt")
        with self.assertRaises(IOError):
            output.write_to_file(invalid_path)


class TestPydanticModelsCompatibility(unittest.TestCase):
    """
    Test suite to ensure that Pydantic model refactoring maintains compatibility.
    
    These tests verify that all functionality of the original Content and NormalizedContent
    classes is preserved when refactored to Pydantic models.
    """
    
    def setUp(self):
        """Set up test cases."""
        self.text = "This is test content"
        self.metadata = {"source": "test", "size": 100}
        self.sections = [
            {"type": "header", "title": "Section 1", "content": "Content 1"},
            {"type": "paragraph", "content": "Paragraph content"}
        ]
        self.source_format = "text/plain"
        self.source_path = "/path/to/source.txt"
        
        self.content = Content(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path
        )
        
        # For NormalizedContent
        self.normalized_by = ["whitespace", "line_endings"]
        self.normalized_content = NormalizedContent(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path,
            normalized_by=self.normalized_by
        )
    
    def test_content_initialization(self):
        """Test Content initialization with various parameter combinations."""
        # Test with minimum required parameters
        content = Content(text="Test")
        self.assertEqual(content.text, "Test")
        self.assertEqual(content.metadata, {})
        self.assertEqual(content.sections, [])
        self.assertEqual(content.source_format, "")
        self.assertEqual(content.source_path, "")
        self.assertIsInstance(content.extraction_time, datetime)
        
        # Test with all parameters
        full_content = Content(
            text="Full test",
            metadata={"test": True},
            sections=[{"type": "test", "content": "Test content"}],
            source_format="application/json",
            source_path="/path/to/file.json"
        )
        self.assertEqual(full_content.text, "Full test")
        self.assertEqual(full_content.metadata, {"test": True})
        self.assertEqual(full_content.sections, [{"type": "test", "content": "Test content"}])
        self.assertEqual(full_content.source_format, "application/json")
        self.assertEqual(full_content.source_path, "/path/to/file.json")
    
    def test_content_to_dict(self):
        """Test Content conversion to dictionary."""
        content_dict = self.content.to_dict()
        
        self.assertEqual(content_dict["text"], self.text)
        self.assertEqual(content_dict["metadata"], self.metadata)
        self.assertEqual(content_dict["sections"], self.sections)
        self.assertEqual(content_dict["source_format"], self.source_format)
        self.assertEqual(content_dict["source_path"], self.source_path)
        self.assertIsInstance(content_dict["extraction_time"], str)
    
    def test_normalized_content_initialization(self):
        """Test NormalizedContent initialization with various parameter combinations."""
        # Test with minimum required parameters
        content = NormalizedContent(text="Test")
        self.assertEqual(content.text, "Test")
        self.assertEqual(content.metadata, {})
        self.assertEqual(content.sections, [])
        self.assertEqual(content.source_format, "")
        self.assertEqual(content.source_path, "")
        self.assertEqual(content.normalized_by, [])
        self.assertIsInstance(content.extraction_time, datetime)
        
        # Test with all parameters
        full_content = NormalizedContent(
            text="Full test",
            metadata={"test": True},
            sections=[{"type": "test", "content": "Test content"}],
            source_format="application/json",
            source_path="/path/to/file.json",
            normalized_by=["unicode", "whitespace"]
        )
        self.assertEqual(full_content.text, "Full test")
        self.assertEqual(full_content.metadata, {"test": True})
        self.assertEqual(full_content.sections, [{"type": "test", "content": "Test content"}])
        self.assertEqual(full_content.source_format, "application/json")
        self.assertEqual(full_content.source_path, "/path/to/file.json")
        self.assertEqual(full_content.normalized_by, ["unicode", "whitespace"])
    
    def test_normalized_content_to_dict(self):
        """Test NormalizedContent conversion to dictionary."""
        content_dict = self.normalized_content.to_dict()
        
        self.assertEqual(content_dict["text"], self.text)
        self.assertEqual(content_dict["metadata"], self.metadata)
        self.assertEqual(content_dict["sections"], self.sections)
        self.assertEqual(content_dict["source_format"], self.source_format)
        self.assertEqual(content_dict["source_path"], self.source_path)
        self.assertEqual(content_dict["normalized_by"], self.normalized_by)
        self.assertIsInstance(content_dict["extraction_time"], str)


if __name__ == "__main__":
    unittest.main()