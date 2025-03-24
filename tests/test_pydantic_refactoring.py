"""
Tests for Pydantic model refactoring compatibility.

This module contains tests to ensure that refactoring classes to Pydantic models
preserves all existing functionality while adding validation benefits.
"""

import unittest
import json
from datetime import datetime, timedelta
import os
import tempfile
from typing import Dict, Any, List, Optional

# Install pydantic to perform validation-specific tests
try:
    import pydantic
    from pydantic import BaseModel, Field, ValidationError
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

# Original class imports
from format_handlers.base_handler import Content
from core.text_normalizer import NormalizedContent


# Sample Pydantic Content model for testing validation behavior
# Only used if pydantic is installed
if HAS_PYDANTIC:
    class ContentModel(BaseModel):
        text: str
        metadata: Dict[str, Any] = Field(default_factory=dict)
        sections: List[Dict[str, Any]] = Field(default_factory=list)
        source_format: str = ""
        source_path: str = ""
        extraction_time: datetime = Field(default_factory=datetime.now)
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat()
            }
    
    class NormalizedContentModel(ContentModel):
        normalized_by: List[str] = Field(default_factory=list)
    
    class ValidationResultModel(BaseModel):
        is_valid: bool
        errors: List[str] = Field(default_factory=list)
        warnings: List[str] = Field(default_factory=list)
        validation_context: Dict[str, Any] = Field(default_factory=dict)
        
        def add_error(self, error: str) -> None:
            self.errors.append(error)
            self.is_valid = False
        
        def add_warning(self, warning: str) -> None:
            self.warnings.append(warning)


@unittest.skipIf(not HAS_PYDANTIC, "Pydantic not installed, skipping Pydantic-specific validation tests")
class TestContentPydanticModel(unittest.TestCase):
    """
    Test suite for Content Pydantic model refactoring.
    
    These tests verify that the Pydantic model provides all existing functionality
    while adding validation benefits.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.text = "This is test content"
        self.metadata = {"source": "test", "size": 100}
        self.sections = [
            {"type": "header", "title": "Section 1", "content": "Content 1"},
            {"type": "paragraph", "content": "Paragraph content"}
        ]
        self.source_format = "text/plain"
        self.source_path = "/path/to/source.txt"
        
        # Original class instance
        self.original_content = Content(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path
        )
        
        # Pydantic model instance
        self.pydantic_content = ContentModel(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path
        )
    
    def test_initialization_compatibility(self):
        """Test that Pydantic model initialization matches original class."""
        # Compare basic properties
        self.assertEqual(self.pydantic_content.text, self.original_content.text)
        self.assertEqual(self.pydantic_content.metadata, self.original_content.metadata)
        self.assertEqual(self.pydantic_content.sections, self.original_content.sections)
        self.assertEqual(self.pydantic_content.source_format, self.original_content.source_format)
        self.assertEqual(self.pydantic_content.source_path, self.original_content.source_path)
        
        # Extraction time should be a datetime in both cases
        self.assertIsInstance(self.pydantic_content.extraction_time, datetime)
        self.assertIsInstance(self.original_content.extraction_time, datetime)
        
        # Compare with missing optional fields
        minimal_original = Content(text="Minimal content")
        minimal_pydantic = ContentModel(text="Minimal content")
        
        self.assertEqual(minimal_pydantic.text, minimal_original.text)
        self.assertEqual(minimal_pydantic.metadata, minimal_original.metadata)
        self.assertEqual(minimal_pydantic.sections, minimal_original.sections)
        self.assertEqual(minimal_pydantic.source_format, minimal_original.source_format)
        self.assertEqual(minimal_pydantic.source_path, minimal_original.source_path)
    
    def test_serialization_compatibility(self):
        """Test that serialization to dict and JSON is compatible."""
        # Dictionary conversion
        original_dict = self.original_content.to_dict()
        pydantic_dict = self.pydantic_content.model_dump(exclude={"extraction_time"})
        
        # Add extraction_time back for comparison, formatted as in the original
        pydantic_dict["extraction_time"] = self.pydantic_content.extraction_time.isoformat()
        
        # Compare dictionaries
        self.assertEqual(pydantic_dict["text"], original_dict["text"])
        self.assertEqual(pydantic_dict["metadata"], original_dict["metadata"])
        self.assertEqual(pydantic_dict["sections"], original_dict["sections"])
        self.assertEqual(pydantic_dict["source_format"], original_dict["source_format"])
        self.assertEqual(pydantic_dict["source_path"], original_dict["source_path"])
        
        # JSON serialization
        original_json = json.dumps(original_dict)
        pydantic_json = self.pydantic_content.model_dump_json()
        
        # Parse both to compare as objects (to avoid order differences)
        parsed_original = json.loads(original_json)
        parsed_pydantic = json.loads(pydantic_json)
        
        self.assertEqual(parsed_pydantic["text"], parsed_original["text"])
        self.assertEqual(parsed_pydantic["metadata"], parsed_original["metadata"])
        self.assertEqual(parsed_pydantic["sections"], parsed_original["sections"])
        self.assertEqual(parsed_pydantic["source_format"], parsed_original["source_format"])
        self.assertEqual(parsed_pydantic["source_path"], parsed_original["source_path"])
    
    def test_validation_benefits(self):
        """Test the additional validation benefits of the Pydantic model."""

        # Test required field validation
        with self.assertRaises(ValidationError):
            ContentModel()  # Missing required 'text' field
        
        # Test field type validation - adapted for Pydantic v2 compatibility
        try:
            # This should raise a ValidationError in any version
            ContentModel(text=123)  # text should be a string
            self.fail("ValidationError not raised for invalid text type")
        except ValidationError:
            pass  # Test passed
        
        # Continue with other validation tests
        try:
            ContentModel(text="Valid", metadata="not a dict")  # metadata should be a dict
            self.fail("ValidationError not raised for invalid metadata type")
        except ValidationError:
            pass
        
        try:
            ContentModel(text="Valid", sections="not a list")  # sections should be a list
            self.fail("ValidationError not raised for invalid sections type")
        except ValidationError:
            pass
            
        # Valid values should work
        valid_model = ContentModel(
            text="Valid text",
            metadata={"key": "value"},
            sections=[{"type": "header", "title": "Title", "content": "Content"}],
            source_format="application/json",
            source_path="/path/to/file.json",
            extraction_time=datetime.now()
        )
        self.assertEqual(valid_model.text, "Valid text")
    
    def test_schema_generation(self):
        """Test schema generation capabilities of Pydantic models."""
        schema = ContentModel.model_json_schema()
        
        # Check basic schema structure
        self.assertEqual(schema["title"], "ContentModel")
        self.assertEqual(schema["type"], "object")
        
        # Check properties
        self.assertIn("text", schema["properties"])
        self.assertIn("metadata", schema["properties"])
        self.assertIn("sections", schema["properties"])
        self.assertIn("source_format", schema["properties"])
        self.assertIn("source_path", schema["properties"])
        self.assertIn("extraction_time", schema["properties"])
        
        # Check required fields
        self.assertIn("text", schema["required"])
        
        # Check types
        self.assertEqual(schema["properties"]["text"]["type"], "string")
        self.assertEqual(schema["properties"]["metadata"]["type"], "object")
        self.assertEqual(schema["properties"]["sections"]["type"], "array")


@unittest.skipIf(not HAS_PYDANTIC, "Pydantic not installed, skipping Pydantic-specific validation tests")
class TestNormalizedContentPydanticModel(unittest.TestCase):
    """
    Test suite for NormalizedContent Pydantic model refactoring.
    
    These tests verify that the Pydantic model provides all existing functionality
    while adding validation benefits, and properly inherits from ContentModel.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.text = "This is normalized test content"
        self.metadata = {"source": "test", "size": 100}
        self.sections = [
            {"type": "header", "title": "Section 1", "content": "Content 1"},
            {"type": "paragraph", "content": "Paragraph content"}
        ]
        self.source_format = "text/plain"
        self.source_path = "/path/to/source.txt"
        self.normalized_by = ["whitespace", "line_endings"]
        
        # Original class instance
        self.original_content = NormalizedContent(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path,
            normalized_by=self.normalized_by
        )
        
        # Pydantic model instance
        self.pydantic_content = NormalizedContentModel(
            text=self.text,
            metadata=self.metadata,
            sections=self.sections,
            source_format=self.source_format,
            source_path=self.source_path,
            normalized_by=self.normalized_by
        )
    
    def test_initialization_compatibility(self):
        """Test that Pydantic model initialization matches original class."""
        # Compare basic properties
        self.assertEqual(self.pydantic_content.text, self.original_content.text)
        self.assertEqual(self.pydantic_content.metadata, self.original_content.metadata)
        self.assertEqual(self.pydantic_content.sections, self.original_content.sections)
        self.assertEqual(self.pydantic_content.source_format, self.original_content.source_format)
        self.assertEqual(self.pydantic_content.source_path, self.original_content.source_path)
        self.assertEqual(self.pydantic_content.normalized_by, self.original_content.normalized_by)
        
        # Extraction time should be a datetime in both cases
        self.assertIsInstance(self.pydantic_content.extraction_time, datetime)
        self.assertIsInstance(self.original_content.extraction_time, datetime)
        
        # Compare with missing optional fields
        minimal_original = NormalizedContent(text="Minimal content")
        minimal_pydantic = NormalizedContentModel(text="Minimal content")
        
        self.assertEqual(minimal_pydantic.text, minimal_original.text)
        self.assertEqual(minimal_pydantic.metadata, minimal_original.metadata)
        self.assertEqual(minimal_pydantic.sections, minimal_original.sections)
        self.assertEqual(minimal_pydantic.source_format, minimal_original.source_format)
        self.assertEqual(minimal_pydantic.source_path, minimal_original.source_path)
        self.assertEqual(minimal_pydantic.normalized_by, minimal_original.normalized_by)
    
    def test_serialization_compatibility(self):
        """Test that serialization to dict and JSON is compatible."""
        # Dictionary conversion
        original_dict = self.original_content.to_dict()
        pydantic_dict = self.pydantic_content.model_dump(exclude={"extraction_time"})
        
        # Add extraction_time back for comparison, formatted as in the original
        pydantic_dict["extraction_time"] = self.pydantic_content.extraction_time.isoformat()
        
        # Compare dictionaries
        self.assertEqual(pydantic_dict["text"], original_dict["text"])
        self.assertEqual(pydantic_dict["metadata"], original_dict["metadata"])
        self.assertEqual(pydantic_dict["sections"], original_dict["sections"])
        self.assertEqual(pydantic_dict["source_format"], original_dict["source_format"])
        self.assertEqual(pydantic_dict["source_path"], original_dict["source_path"])
        self.assertEqual(pydantic_dict["normalized_by"], original_dict["normalized_by"])
        
        # JSON serialization
        original_json = json.dumps(original_dict)
        pydantic_json = self.pydantic_content.model_dump_json()
        
        # Parse both to compare as objects (to avoid order differences)
        parsed_original = json.loads(original_json)
        parsed_pydantic = json.loads(pydantic_json)
        
        self.assertEqual(parsed_pydantic["text"], parsed_original["text"])
        self.assertEqual(parsed_pydantic["metadata"], parsed_original["metadata"])
        self.assertEqual(parsed_pydantic["sections"], parsed_original["sections"])
        self.assertEqual(parsed_pydantic["source_format"], parsed_original["source_format"])
        self.assertEqual(parsed_pydantic["source_path"], parsed_original["source_path"])
        self.assertEqual(parsed_pydantic["normalized_by"], parsed_original["normalized_by"])
    
    def test_inheritance(self):
        """Test that the inheritance relationship is properly maintained."""
        # Check that NormalizedContentModel is a subclass of ContentModel
        self.assertTrue(issubclass(NormalizedContentModel, ContentModel))
        
        # Check that NormalizedContentModel instances are instances of ContentModel
        self.assertIsInstance(self.pydantic_content, ContentModel)
        
        # Test inherited validation
        with self.assertRaises(ValidationError):
            NormalizedContentModel()  # Missing required 'text' field from parent
            
        # Test specific field validation
        with self.assertRaises(ValidationError):
            NormalizedContentModel(text="Valid", normalized_by="not a list")
            
        # Test with non-string normalizer names
        with self.assertRaises(ValidationError):
            NormalizedContentModel(text="Valid", normalized_by=[1, 2, 3])
    
    def test_schema_generation(self):
        """Test schema generation capabilities of Pydantic models."""
        schema = NormalizedContentModel.model_json_schema()
        
        # Check basic schema structure
        self.assertEqual(schema["title"], "NormalizedContentModel")
        self.assertEqual(schema["type"], "object")
        
        # Check properties include both parent and child fields
        self.assertIn("text", schema["properties"])
        self.assertIn("metadata", schema["properties"])
        self.assertIn("sections", schema["properties"])
        self.assertIn("source_format", schema["properties"])
        self.assertIn("source_path", schema["properties"])
        self.assertIn("extraction_time", schema["properties"])
        self.assertIn("normalized_by", schema["properties"])
        
        # Check required fields
        self.assertIn("text", schema["required"])
        
        # Check normalized_by field type
        self.assertEqual(schema["properties"]["normalized_by"]["type"], "array")


@unittest.skipIf(not HAS_PYDANTIC, "Pydantic not installed, skipping Pydantic-specific validation tests")
class TestValidationResultModel(unittest.TestCase):
    """
    Test suite for the new ValidationResult Pydantic model.
    
    These tests verify that the new ValidationResult model properly captures
    validation results from various components.
    """
    
    def test_validation_result_initialization(self):
        """Test initialization of ValidationResult model."""
        # Basic initialization
        result = ValidationResultModel(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.validation_context, {})
        
        # Full initialization
        full_result = ValidationResultModel(
            is_valid=False,
            errors=["Invalid format"],
            warnings=["File is large"],
            validation_context={"format": "application/pdf", "size": 1024}
        )
        self.assertFalse(full_result.is_valid)
        self.assertEqual(full_result.errors, ["Invalid format"])
        self.assertEqual(full_result.warnings, ["File is large"])
        self.assertEqual(full_result.validation_context, {"format": "application/pdf", "size": 1024})
    
    def test_add_error(self):
        """Test adding errors to the validation result."""
        result = ValidationResultModel(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        
        # Add an error
        result.add_error("Error occurred")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, ["Error occurred"])
        
        # Add another error
        result.add_error("Another error")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, ["Error occurred", "Another error"])
    
    def test_add_warning(self):
        """Test adding warnings to the validation result."""
        result = ValidationResultModel(is_valid=True)
        self.assertEqual(result.warnings, [])
        
        # Add a warning
        result.add_warning("Warning message")
        self.assertTrue(result.is_valid)  # Warnings don't affect validity
        self.assertEqual(result.warnings, ["Warning message"])
        
        # Add another warning
        result.add_warning("Another warning")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.warnings, ["Warning message", "Another warning"])
    
    def test_serialization(self):
        """Test serialization of the validation result."""
        result = ValidationResultModel(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning"],
            validation_context={"file": "test.pdf"}
        )
        
        # Dictionary serialization
        result_dict = result.model_dump()
        self.assertFalse(result_dict["is_valid"])
        self.assertEqual(result_dict["errors"], ["Error 1", "Error 2"])
        self.assertEqual(result_dict["warnings"], ["Warning"])
        self.assertEqual(result_dict["validation_context"], {"file": "test.pdf"})
        
        # JSON serialization
        result_json = result.model_dump_json()
        parsed_json = json.loads(result_json)
        self.assertFalse(parsed_json["is_valid"])
        self.assertEqual(parsed_json["errors"], ["Error 1", "Error 2"])
        self.assertEqual(parsed_json["warnings"], ["Warning"])
        self.assertEqual(parsed_json["validation_context"], {"file": "test.pdf"})
    
    def test_schema(self):
        """Test schema generation for the validation result."""
        schema = ValidationResultModel.model_json_schema()
        
        # Check basic schema structure
        self.assertEqual(schema["title"], "ValidationResultModel")
        self.assertEqual(schema["type"], "object")
        
        # Check properties
        self.assertIn("is_valid", schema["properties"])
        self.assertIn("errors", schema["properties"])
        self.assertIn("warnings", schema["properties"])
        self.assertIn("validation_context", schema["properties"])
        
        # Check required fields
        self.assertIn("is_valid", schema["required"])
        
        # Check types
        self.assertEqual(schema["properties"]["is_valid"]["type"], "boolean")
        self.assertEqual(schema["properties"]["errors"]["type"], "array")
        self.assertEqual(schema["properties"]["warnings"]["type"], "array")
        self.assertEqual(schema["properties"]["validation_context"]["type"], "object")


if __name__ == "__main__":
    unittest.main()