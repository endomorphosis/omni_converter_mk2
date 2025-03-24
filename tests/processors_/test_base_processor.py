"""
Tests for the base processor interfaces.

This module contains comprehensive tests for the base processor abstract interfaces,
including BaseProcessor and DocumentProcessor. These tests focus on verifying the
contract these interfaces define, ensuring proper inheritance hierarchies, abstract
method declarations, and implementation requirements for concrete subclasses.

These tests are crucial for maintaining the processor architecture's integrity,
as they verify that all processor implementations will adhere to the expected
interface contracts.
"""

import unittest
from abc import ABC

from format_handlers.processors.base_processor import BaseProcessor
from format_handlers.processors.document_processor import DocumentProcessor


class TestBaseProcessor(unittest.TestCase):
    """
    Test suite for the BaseProcessor abstract class.
    
    This test class verifies that the BaseProcessor properly defines the base contract
    for all processor implementations. It ensures the class is properly marked as
    abstract, defines the required abstract methods, and enforces implementation
    of these methods in concrete subclasses.
    """
    
    def test_is_abstract(self):
        """
        Test that BaseProcessor is correctly defined as an abstract class.
        
        Verifies that the BaseProcessor class inherits from ABC (Abstract Base Class)
        and cannot be instantiated directly. This ensures that the processor architecture
        maintains its contract-based design where concrete implementations must fulfill
        the defined interface.
        """
        self.assertTrue(issubclass(BaseProcessor, ABC))
        
        # Verify that we can't instantiate it directly
        with self.assertRaises(TypeError):
            BaseProcessor()
    
    def test_required_methods(self):
        """
        Test that BaseProcessor defines the required abstract methods.
        
        Verifies that the BaseProcessor class correctly declares the essential methods
        as abstract, which includes:
        - can_process: For determining if a specific format is supported
        - get_supported_formats: For listing all formats the processor can handle
        - get_processor_info: For providing metadata about the processor
        
        This ensures that all concrete implementations must provide these core capabilities.
        """
        # Define a method to check if a method is abstract
        def is_abstract_method(cls, method_name):
            method = getattr(cls, method_name, None)
            return hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__
        
        # Check that the required methods are abstract
        self.assertTrue(is_abstract_method(BaseProcessor, "can_process"))
        self.assertTrue(is_abstract_method(BaseProcessor, "get_supported_formats"))
        self.assertTrue(is_abstract_method(BaseProcessor, "get_processor_info"))
    
    def test_contract_compliance(self):
        """
        Test that concrete subclasses must implement all abstract methods.
        
        Verifies the contract enforcement mechanism of the BaseProcessor class by:
        1. Creating an incomplete subclass that doesn't implement all required methods
           and confirming it cannot be instantiated
        2. Creating a complete subclass that implements all required methods and
           confirming it can be instantiated successfully
        3. Verifying that the implemented methods function correctly
        
        This ensures that the abstract class pattern effectively enforces the
        implementation contract on concrete subclasses.
        """
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
    """
    Test suite for the DocumentProcessor abstract class.
    
    This test class verifies that the DocumentProcessor properly extends the BaseProcessor
    class and defines the additional contract required for document processing functionality.
    It ensures the class maintains the proper inheritance hierarchy, defines document-specific
    abstract methods, and enforces implementation of these methods in concrete subclasses.
    """
    
    def test_is_abstract(self):
        """
        Test that DocumentProcessor is correctly defined as an abstract class.
        
        Verifies that the DocumentProcessor class inherits from both ABC (Abstract Base Class)
        and BaseProcessor, establishing the proper inheritance hierarchy. Also confirms
        that the class cannot be instantiated directly, maintaining the contract-based
        design where concrete implementations must fulfill the defined interface.
        """
        self.assertTrue(issubclass(DocumentProcessor, ABC))
        self.assertTrue(issubclass(DocumentProcessor, BaseProcessor))
        
        # Verify that we can't instantiate it directly
        with self.assertRaises(TypeError):
            DocumentProcessor()
    
    def test_required_methods(self):
        """
        Test that DocumentProcessor defines the required document-specific abstract methods.
        
        Verifies that the DocumentProcessor class correctly declares essential document
        processing methods as abstract, which includes:
        - extract_text: For extracting plain text from documents
        - extract_metadata: For extracting document metadata
        - extract_structure: For extracting document structure information
        - process_document: For performing a complete document processing operation
        
        Also confirms that the DocumentProcessor inherits and maintains the abstract method
        requirements from the BaseProcessor parent class. This ensures that concrete
        implementations must provide all required functionality for the processor architecture.
        """
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
        """
        Test that concrete DocumentProcessor subclasses must implement all abstract methods.
        
        Verifies the contract enforcement mechanism of the DocumentProcessor class by:
        1. Creating an incomplete subclass that implements BaseProcessor methods but not
           all DocumentProcessor-specific methods, and confirming it cannot be instantiated
        2. Creating a complete subclass that implements all required methods from both
           BaseProcessor and DocumentProcessor, and confirming it can be instantiated successfully
        3. Verifying that all implemented methods function correctly with representative inputs
           and outputs
        
        This ensures that the abstract class pattern effectively enforces the full
        implementation contract on concrete document processor subclasses, maintaining
        the integrity of the document processing architecture.
        """
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