"""
Tests for the base processor interfaces.

This module contains tests for the base processor interfaces, including
BaseProcessor and DocumentProcessor, focusing on the contract they define.
"""

import unittest
from abc import ABC

from format_handlers.processors.base_processor import BaseProcessor
from format_handlers.processors.document_processor import DocumentProcessor


class TestBaseProcessor(unittest.TestCase):
    """Test the BaseProcessor class."""
    
    def test_is_abstract(self):
        """Test that BaseProcessor is an abstract class."""
        self.assertTrue(issubclass(BaseProcessor, ABC))
        
        # Verify that we can't instantiate it directly
        with self.assertRaises(TypeError):
            BaseProcessor()
    
    def test_required_methods(self):
        """Test that BaseProcessor requires the correct methods."""
        # Define a method to check if a method is abstract
        def is_abstract_method(cls, method_name):
            method = getattr(cls, method_name, None)
            return hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__
        
        # Check that the required methods are abstract
        self.assertTrue(is_abstract_method(BaseProcessor, "can_process"))
        self.assertTrue(is_abstract_method(BaseProcessor, "get_supported_formats"))
        self.assertTrue(is_abstract_method(BaseProcessor, "get_processor_info"))
    
    def test_contract_compliance(self):
        """Test that a concrete subclass must implement the abstract methods."""
        # Create a subclass that doesn't implement all methods
        class IncompleteProcessor(BaseProcessor):
            def can_process(self, format_name):
                return True
        
        # Verify that we can't instantiate it
        with self.assertRaises(TypeError):
            IncompleteProcessor()
        
        # Create a complete subclass
        class CompleteProcessor(BaseProcessor):
            def can_process(self, format_name):
                return True
                
            def get_supported_formats(self):
                return ["test"]
                
            def get_processor_info(self):
                return {"name": "CompleteProcessor"}
        
        # Verify that we can instantiate it
        processor = CompleteProcessor()
        self.assertIsInstance(processor, BaseProcessor)
        
        # Verify that the methods work as expected
        self.assertTrue(processor.can_process("test"))
        self.assertEqual(processor.get_supported_formats(), ["test"])
        self.assertEqual(processor.get_processor_info()["name"], "CompleteProcessor")


class TestDocumentProcessor(unittest.TestCase):
    """Test the DocumentProcessor class."""
    
    def test_is_abstract(self):
        """Test that DocumentProcessor is an abstract class."""
        self.assertTrue(issubclass(DocumentProcessor, ABC))
        self.assertTrue(issubclass(DocumentProcessor, BaseProcessor))
        
        # Verify that we can't instantiate it directly
        with self.assertRaises(TypeError):
            DocumentProcessor()
    
    def test_required_methods(self):
        """Test that DocumentProcessor requires the correct methods."""
        # Define a method to check if a method is abstract
        def is_abstract_method(cls, method_name):
            method = getattr(cls, method_name, None)
            return hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__
        
        # Check that the required methods are abstract
        self.assertTrue(is_abstract_method(DocumentProcessor, "extract_text"))
        self.assertTrue(is_abstract_method(DocumentProcessor, "extract_metadata"))
        self.assertTrue(is_abstract_method(DocumentProcessor, "extract_structure"))
        self.assertTrue(is_abstract_method(DocumentProcessor, "process_document"))
        
        # Check that it still requires the BaseProcessor methods
        self.assertTrue(is_abstract_method(DocumentProcessor, "can_process"))
        self.assertTrue(is_abstract_method(DocumentProcessor, "get_supported_formats"))
        self.assertTrue(is_abstract_method(DocumentProcessor, "get_processor_info"))
    
    def test_contract_compliance(self):
        """Test that a concrete subclass must implement the abstract methods."""
        # Create an incomplete subclass
        class IncompleteDocProcessor(DocumentProcessor):
            def can_process(self, format_name):
                return True
                
            def get_supported_formats(self):
                return ["test"]
                
            def get_processor_info(self):
                return {"name": "IncompleteDocProcessor"}
        
        # Verify that we can't instantiate it
        with self.assertRaises(TypeError):
            IncompleteDocProcessor()
        
        # Create a complete subclass
        class CompleteDocProcessor(DocumentProcessor):
            def can_process(self, format_name):
                return True
                
            def get_supported_formats(self):
                return ["test"]
                
            def get_processor_info(self):
                return {"name": "CompleteDocProcessor"}
                
            def extract_text(self, data, options):
                return "Text"
                
            def extract_metadata(self, data, options):
                return {"title": "Test"}
                
            def extract_structure(self, data, options):
                return [{"type": "section"}]
                
            def process_document(self, data, options):
                return "Text", {"title": "Test"}, [{"type": "section"}]
        
        # Verify that we can instantiate it
        processor = CompleteDocProcessor()
        self.assertIsInstance(processor, DocumentProcessor)
        self.assertIsInstance(processor, BaseProcessor)
        
        # Verify that the methods work as expected
        self.assertTrue(processor.can_process("test"))
        self.assertEqual(processor.get_supported_formats(), ["test"])
        self.assertEqual(processor.extract_text(None, {}), "Text")
        self.assertEqual(processor.extract_metadata(None, {})["title"], "Test")
        self.assertEqual(processor.extract_structure(None, {})[0]["type"], "section")
        
        text, meta, struct = processor.process_document(None, {})
        self.assertEqual(text, "Text")
        self.assertEqual(meta["title"], "Test")
        self.assertEqual(struct[0]["type"], "section")


if __name__ == "__main__":
    unittest.main()