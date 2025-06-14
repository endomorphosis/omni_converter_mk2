"""
Tests for ValidationResult pydantic model.

This module contains tests for the ValidationResult class.
"""

import unittest
from typing import Any

from core.file_validator._validation_result import ValidationResult


class TestValidationResult(unittest.TestCase):
    """Test suite for ValidationResult class."""
    
    def setUp(self):
        """Set up test cases."""
        self.valid_result = ValidationResult()
        self.invalid_result = ValidationResult(
            is_valid=False,
            errors=["Invalid format", "Missing required field"],
            warnings=["File size is too large"],
            validation_context={"source": "test", "severity": "high"}
        )
    
    def test_initialization(self):
        """Test initialization with various parameter combinations."""
        # Test with default parameters
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.validation_context, {})
        
        # Test with explicit parameters
        custom_result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            validation_context={"test": True}
        )
        self.assertFalse(custom_result.is_valid)
        self.assertEqual(custom_result.errors, ["Error 1", "Error 2"])
        self.assertEqual(custom_result.warnings, ["Warning 1"])
        self.assertEqual(custom_result.validation_context, {"test": True})
    
    def test_add_error(self):
        """Test adding errors and its effect on validity status."""
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        result.add_error("Test error")
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")
        
        result.add_error("Another error")
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.errors[1], "Another error")
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult()
        self.assertEqual(len(result.warnings), 0)
        
        result.add_warning("Test warning")
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0], "Test warning")
        
        # Warnings should not affect validity
        self.assertTrue(result.is_valid)
    
    def test_add_context(self):
        """Test adding validation context."""
        result = ValidationResult()
        self.assertEqual(result.validation_context, {})
        
        result.add_context("source", "test")
        self.assertEqual(result.validation_context, {"source": "test"})
        
        result.add_context("severity", "high")
        self.assertEqual(result.validation_context, {"source": "test", "severity": "high"})
        
        # Overwrite existing context
        result.add_context("source", "updated")
        self.assertEqual(result.validation_context, {"source": "updated", "severity": "high"})
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result_dict = self.invalid_result.to_dict()
        
        self.assertFalse(result_dict["is_valid"])
        self.assertEqual(result_dict["errors"], ["Invalid format", "Missing required field"])
        self.assertEqual(result_dict["warnings"], ["File size is too large"])
        self.assertEqual(result_dict["validation_context"], {"source": "test", "severity": "high"})
    
    def test_model_validation(self):
        """Test Pydantic validation when creating instances."""
        # Test with invalid types (should raise validation error)
        with self.assertRaises(Exception):
            ValidationResult(is_valid="not_a_bool")
        
        with self.assertRaises(Exception):
            ValidationResult(errors="not_a_list")
        
        with self.assertRaises(Exception):
            ValidationResult(warnings=123)
        
        with self.assertRaises(Exception):
            ValidationResult(validation_context="not_a_dict")


if __name__ == "__main__":
    unittest.main()