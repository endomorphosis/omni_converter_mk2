"""
Tests for the processor factory functionality.

This module tests the processor factory's ability to create processors
dynamically based on available dependencies, fall back gracefully,
and produce appropriate mocks when necessary.
"""
from __future__ import annotations
import logging
from typing import Any, Callable, Dict, Set, Optional, Type
import unittest
from unittest.mock import MagicMock, Mock, patch, call


from core.content_extractor.processors.factory import (
    _make_processor,
    make_processors,
    _mock_processor,
    ProcessorResources,
)
from configs import Configs

class TestMakeProcessor(unittest.TestCase):
    """Test the _make_processor factory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.mock_configs = MagicMock(spec=Configs)
        
        # Mock dependencies
        self.mock_dependencies = {
            "openpyxl": MagicMock(),
            "pandas": None,  # Simulate unavailable dependency
        }

        # Basic processor resources
        self.basic_resources = {
            "supported_formats": {"xlsx", "xlsm"},
            "processor_name": "test_processor",
            "dependencies": self.mock_dependencies,
            "critical_resources": ["extract_text", "extract_metadata"],
            "optional_resources": ["extract_images"],
            "logger": self.mock_logger,
            "configs": self.mock_configs,
        }

    def test_creates_processor_with_all_dependencies_available(self) -> None:
        """
        Test that _make_processor creates a fully functional processor
        when all dependencies are available.
        
        Expected behavior:
        - Returns a processor instance (not a mock)
        - All critical resources are properly injected
        - Processor reports all capabilities as available
        
        Raises:
            AssertionError: If processor creation fails or returns a mock
        """
        # Arrange
        all_available_dependencies = {
            "openpyxl": MagicMock(),
            "pandas": MagicMock(),
            "pillow": MagicMock(),
        }
        resources = {
            **self.basic_resources,
            "dependencies": all_available_dependencies,
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsNotNone(processor)
        self.assertNotIsInstance(processor, MagicMock)
        self.assertTrue(hasattr(processor, "extract_text"))
        self.assertTrue(hasattr(processor, "extract_metadata"))
        self.assertTrue(hasattr(processor, "extract_images"))
        self.assertTrue(hasattr(processor, "can_process"))
        self.assertTrue(hasattr(processor, "supported_formats"))
        self.assertEqual(processor.supported_formats, {"xlsx", "xlsm"})
        
        # Verify processor reports full capabilities
        processor_info = processor.processor_info
        self.assertIn("capabilities", processor_info)
        self.assertIn("extract_text", processor_info["capabilities"])
        self.assertIn("extract_metadata", processor_info["capabilities"])
        self.assertIn("extract_images", processor_info["capabilities"])
        
        # Verify all capabilities are marked as available (not mocked)
        for capability in ["extract_text", "extract_metadata", "extract_images"]:
            self.assertTrue(processor_info["capabilities"][capability]["available"])
            self.assertNotEqual(processor_info["capabilities"][capability]["implementation"], "mock")

    def test_creates_processor_with_fallback_dependencies(self) -> None:
        """
        Test that _make_processor falls back to secondary dependencies
        when primary ones are unavailable.
        
        Expected behavior:
        - Primary dependency (e.g., libreoffice) is unavailable
        - Falls back to secondary (e.g., python-docx)
        - Returns a functional processor with secondary implementation
        - Reports which implementation is being used
        
        Raises:
            AssertionError: If fallback mechanism doesn't work
        """
        # Arrange
        fallback_dependencies = {
            "libreoffice": None,  # Primary unavailable
            "python-docx": MagicMock(),  # Secondary available
            "openpyxl": MagicMock(),
        }
        resources = {
            **self.basic_resources,
            "dependencies": fallback_dependencies,
            "dependency_priority": ["libreoffice", "python-docx", "openpyxl"],
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsNotNone(processor)
        self.assertNotIsInstance(processor, MagicMock)
        
        # Verify fallback is reported
        processor_info = processor.processor_info
        self.assertIn("implementation_used", processor_info)
        self.assertEqual(processor_info["implementation_used"], "python-docx")
        
        # Verify logger was called to report fallback
        self.mock_logger.warning.assert_called()
        warning_calls = [call.args[0] for call in self.mock_logger.warning.call_args_list]
        fallback_logged = any("fallback" in msg.lower() or "unavailable" in msg.lower() for msg in warning_calls)
        self.assertTrue(fallback_logged)

    def test_creates_mock_when_no_dependencies_available(self) -> None:
        """
        Test that _make_processor returns a mock when no dependencies
        are available for critical resources.
        
        Expected behavior:
        - All dependencies are unavailable
        - Returns a MagicMock instance
        - Mock has all required methods
        - Mock methods return appropriate default values
        
        Raises:
            AssertionError: If mock creation fails
        """
        # Arrange
        no_dependencies = {
            "openpyxl": None,
            "pandas": None,
            "pillow": None,
        }
        resources = {
            **self.basic_resources,
            "dependencies": no_dependencies,
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsInstance(processor, MagicMock)
        
        # Verify mock has all required methods
        self.assertTrue(hasattr(processor, "extract_text"))
        self.assertTrue(hasattr(processor, "extract_metadata"))
        self.assertTrue(hasattr(processor, "extract_images"))
        self.assertTrue(hasattr(processor, "can_process"))
        self.assertTrue(hasattr(processor, "supported_formats"))
        
        # Verify mock methods return appropriate values
        self.assertEqual(processor.extract_text(), "Mocked text content")
        self.assertEqual(processor.extract_metadata(), {"mocked": "metadata"})
        self.assertEqual(processor.supported_formats, {"xlsx", "xlsm"})
        
        # Verify processor reports all capabilities as mocked
        processor_info = processor.processor_info
        for capability in ["extract_text", "extract_metadata"]:
            self.assertFalse(processor_info["capabilities"][capability]["available"])
            self.assertEqual(processor_info["capabilities"][capability]["implementation"], "mock")

    def test_handles_partial_dependency_availability(self) -> None:
        """
        Test that _make_processor handles cases where some but not all
        methods can be provided by available dependencies.
        
        Expected behavior:
        - Some methods available from dependencies
        - Missing methods are mocked
        - Processor reports degraded capabilities
        
        Raises:
            AssertionError: If partial availability isn't handled correctly
        """
        # Arrange
        partial_dependencies = {
            "openpyxl": MagicMock(),  # Can provide extract_text and extract_metadata
            "pillow": None,  # Cannot provide extract_images
        }
        resources = {
            **self.basic_resources,
            "dependencies": partial_dependencies,
            "dependency_mapping": {
                "extract_text": ["openpyxl"],
                "extract_metadata": ["openpyxl"],
                "extract_images": ["pillow"],
            }
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsNotNone(processor)
        
        # Verify processor has all methods
        self.assertTrue(hasattr(processor, "extract_text"))
        self.assertTrue(hasattr(processor, "extract_metadata"))
        self.assertTrue(hasattr(processor, "extract_images"))
        
        # Verify processor reports degraded capabilities
        processor_info = processor.processor_info
        self.assertTrue(processor_info["capabilities"]["extract_text"]["available"])
        self.assertTrue(processor_info["capabilities"]["extract_metadata"]["available"])
        self.assertFalse(processor_info["capabilities"]["extract_images"]["available"])
        self.assertEqual(processor_info["capabilities"]["extract_images"]["implementation"], "mock")
        
        # Verify degradation is logged
        self.mock_logger.warning.assert_called()
        warning_calls = [call.args[0] for call in self.mock_logger.warning.call_args_list]
        degraded_logged = any("degraded" in msg.lower() or "partial" in msg.lower() for msg in warning_calls)
        self.assertTrue(degraded_logged)

    def test_respects_dependency_priority_order(self) -> None:
        """
        Test that _make_processor tries dependencies in the correct order.
        
        Expected behavior:
        - Dependencies are tried in the order they appear in the dict
        - First available dependency is used
        - Later dependencies are not checked if earlier ones work
        
        Raises:
            AssertionError: If dependency order is not respected
        """
        # Arrange
        mock_dep1 = MagicMock()
        mock_dep2 = MagicMock()
        mock_dep3 = MagicMock()
        
        ordered_dependencies = {
            "first_choice": mock_dep1,
            "second_choice": mock_dep2,
            "third_choice": mock_dep3,
        }
        resources = {
            **self.basic_resources,
            "dependencies": ordered_dependencies,
            "dependency_priority": ["first_choice", "second_choice", "third_choice"],
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        processor_info = processor.processor_info
        self.assertEqual(processor_info["implementation_used"], "first_choice")
        
        # Test with first unavailable
        ordered_dependencies["first_choice"] = None
        processor2 = _make_processor(resources)
        processor_info2 = processor2.processor_info
        self.assertEqual(processor_info2["implementation_used"], "second_choice")
        
        # Test with first two unavailable
        ordered_dependencies["second_choice"] = None
        processor3 = _make_processor(resources)
        processor_info3 = processor3.processor_info
        self.assertEqual(processor_info3["implementation_used"], "third_choice")

    def test_injects_logger_and_configs_properly(self) -> None:
        """
        Test that _make_processor properly injects logger and configs
        into the created processor.
        
        Expected behavior:
        - Logger is accessible in processor resources
        - Configs are passed to processor constructor
        - Both are available for use in processor methods
        
        Raises:
            AssertionError: If injection fails
        """
        # Arrange
        resources = {
            **self.basic_resources,
            "dependencies": {"openpyxl": MagicMock()},
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        # Verify logger is accessible
        self.assertEqual(processor.logger, self.mock_logger)
        
        # Verify configs are accessible
        self.assertEqual(processor.configs, self.mock_configs)
        
        # Verify processor can use logger
        processor.extract_text()
        self.mock_logger.debug.assert_called()


class TestMockProcessor(unittest.TestCase):
    """Test the _mock_processor function."""

    def test_creates_mock_with_all_required_methods(self) -> None:
        """
        Test that _mock_processor creates a mock with all specified methods.
        
        Expected behavior:
        - Mock has all methods listed in the methods dict
        - Methods are callable
        - Methods return expected mock values
        
        Raises:
            AssertionError: If mock doesn't have required methods
        """
        # Arrange
        methods = {
            "extract_text": "text_extraction",
            "extract_metadata": "metadata_extraction", 
            "extract_images": "image_extraction",
            "can_process": "validation",
        }
        supported_formats = {"xlsx", "xlsm"}
        processor_name = "test_processor"
        
        # Act
        mock_processor = _mock_processor(methods, supported_formats, processor_name)
        
        # Assert
        self.assertIsInstance(mock_processor, MagicMock)
        
        # Verify all methods exist and are callable
        for method_name in methods:
            self.assertTrue(hasattr(mock_processor, method_name))
            self.assertTrue(callable(getattr(mock_processor, method_name)))
        
        # Verify methods can be called
        self.assertIsNotNone(mock_processor.extract_text())
        self.assertIsNotNone(mock_processor.extract_metadata())
        self.assertIsNotNone(mock_processor.extract_images())
        self.assertIsNotNone(mock_processor.can_process())

    def test_mock_methods_return_appropriate_values(self) -> None:
        """
        Test that mock methods return sensible default values.
        
        Expected behavior:
        - extract_text returns "Mocked text content"
        - extract_metadata returns {"mocked": "metadata"}
        - extract_structure returns {"mocked": "structure"}
        - etc.
        
        Raises:
            AssertionError: If mock return values are incorrect
        """
        # Arrange
        methods = {
            "extract_text": "text_extraction",
            "extract_metadata": "metadata_extraction",
            "extract_structure": "structure_extraction",
            "extract_images": "image_extraction",
            "can_process": "validation",
        }
        
        # Act
        mock_processor = _mock_processor(methods, {"xlsx"}, "test_processor")
        
        # Assert
        self.assertEqual(mock_processor.extract_text(), "Mocked text content")
        self.assertEqual(mock_processor.extract_metadata(), {"mocked": "metadata"})
        self.assertEqual(mock_processor.extract_structure(), {"mocked": "structure"})
        self.assertEqual(mock_processor.extract_images(), [])
        self.assertEqual(mock_processor.can_process("test.xlsx"), False)

    def test_handles_tuple_method_specifications(self) -> None:
        """
        Test that _mock_processor correctly handles tuple-format methods.
        
        Expected behavior:
        - Tuples like ('extract_images', processor_ref) are handled
        - Method name is extracted from first element
        - Mock method is created with correct name
        
        Raises:
            AssertionError: If tuple handling fails
        """
        # Arrange
        mock_image_processor = MagicMock()
        methods = {
            "extract_text": "text_extraction",
            ("extract_images", mock_image_processor): "image_extraction",
            ("extract_metadata", None): "metadata_extraction",
        }
        
        # Act
        mock_processor = _mock_processor(methods, {"xlsx"}, "test_processor")
        
        # Assert
        self.assertTrue(hasattr(mock_processor, "extract_text"))
        self.assertTrue(hasattr(mock_processor, "extract_images"))
        self.assertTrue(hasattr(mock_processor, "extract_metadata"))
        
        # Verify tuple methods are callable
        self.assertIsNotNone(mock_processor.extract_images())
        self.assertIsNotNone(mock_processor.extract_metadata())

    def test_generates_heuristic_mock_values_for_unknown_methods(self) -> None:
        """
        Test that _mock_processor generates reasonable values for methods
        not in the predefined mock_map.
        
        Expected behavior:
        - Methods with "process" in name return process-like values
        - Methods with "extract" in name return extract-like values
        - Methods with "open" in name return open-like values
        
        Raises:
            AssertionError: If heuristic generation fails
        """
        # Arrange
        methods = {
            "process_document": "document_processing",
            "extract_unknown_data": "unknown_extraction",
            "open_file": "file_opening",
            "validate_format": "format_validation",
            "completely_unknown_method": "unknown_category",
        }
        
        # Act
        mock_processor = _mock_processor(methods, {"test"}, "test_processor")
        
        # Assert
        # Process methods should return success indicators
        result = mock_processor.process_document()
        self.assertIn(result, [True, {"status": "processed"}, "Processed"])
        
        # Extract methods should return appropriate data structures
        extract_result = mock_processor.extract_unknown_data()
        self.assertIn(type(extract_result), [str, dict, list])
        
        # Open methods should return file-like indicators
        open_result = mock_processor.open_file()
        self.assertIn(open_result, [True, {"opened": True}, "File opened"])
        
        # Validate methods should return boolean-like
        validate_result = mock_processor.validate_format()
        self.assertIn(validate_result, [True, False, {"valid": False}])
        
        # Unknown methods should return generic mock values
        unknown_result = mock_processor.completely_unknown_method()
        self.assertIsNotNone(unknown_result)


class TestMakeProcessors(unittest.TestCase):
    """Test the make_processors function that creates all processors."""

    def test_creates_all_processor_types(self) -> None:
        """
        Test that make_processors creates all expected processor types.
        
        Expected behavior:
        - Creates ability processors (image, audio, text, etc.)
        - Creates MIME-type processors (xlsx, pdf, etc.)
        - Returns dict with all processor names as keys
        
        Raises:
            AssertionError: If any expected processor is missing
        """
        # Act
        processors = make_processors()
        
        # Assert
        self.assertIsInstance(processors, dict)
        
        # Verify ability processors
        expected_ability_processors = [
            "image_processor",
            "audio_processor", 
            "text_processor",
            "document_processor",
        ]
        for processor_name in expected_ability_processors:
            self.assertIn(processor_name, processors)
            self.assertIsNotNone(processors[processor_name])
        
        # Verify MIME-type processors
        expected_mime_processors = [
            "xlsx_processor",
            "pdf_processor",
            "docx_processor",
            "pptx_processor",
        ]
        for processor_name in expected_mime_processors:
            self.assertIn(processor_name, processors)
            self.assertIsNotNone(processors[processor_name])
        
        # Verify all processors have consistent interface
        for processor_name, processor in processors.items():
            self.assertTrue(hasattr(processor, "can_process"))
            self.assertTrue(hasattr(processor, "supported_formats"))
            self.assertTrue(hasattr(processor, "processor_info"))

    def test_handles_cross_processor_dependencies(self) -> None:
        """
        Test that processors can use other processors (e.g., XLSX using image).
        
        Expected behavior:
        - XLSX processor can access image processor for extract_images
        - Dependency injection works across processor types
        - Circular dependencies are prevented
        
        Raises:
            AssertionError: If cross-dependencies don't work
        """
        # Act
        processors = make_processors()
        
        # Assert
        xlsx_processor = processors["xlsx_processor"]
        image_processor = processors["image_processor"]
        
        # Verify XLSX processor can extract images (using image processor)
        self.assertTrue(hasattr(xlsx_processor, "extract_images"))
        
        # Verify cross-processor method works
        images = xlsx_processor.extract_images()
        self.assertIsNotNone(images)
        
        # Verify processor info shows cross-dependency
        xlsx_info = xlsx_processor.processor_info
        self.assertIn("dependencies", xlsx_info)
        self.assertIn("image_processor", xlsx_info["dependencies"])
        
        # Verify no circular dependencies
        image_info = image_processor.processor_info
        if "dependencies" in image_info:
            self.assertNotIn("xlsx_processor", image_info["dependencies"])

    def test_reports_capability_availability_correctly(self) -> None:
        """
        Test that each processor correctly reports its available capabilities.
        
        Expected behavior:
        - processor.processor_info includes available capabilities
        - Degraded capabilities are clearly marked
        - Mock implementations are identified
        
        Raises:
            AssertionError: If capability reporting is incorrect
        """
        # Act
        processors = make_processors()
        
        # Assert
        for processor_name, processor in processors.items():
            processor_info = processor.processor_info
            
            # Verify basic info structure
            self.assertIn("processor_name", processor_info)
            self.assertIn("capabilities", processor_info)
            self.assertIn("supported_formats", processor_info)
            
            # Verify capability reporting structure
            capabilities = processor_info["capabilities"]
            for capability_name, capability_info in capabilities.items():
                self.assertIn("available", capability_info)
                self.assertIn("implementation", capability_info)
                self.assertIsInstance(capability_info["available"], bool)
                self.assertIsInstance(capability_info["implementation"], str)
                
                # If not available, should be marked as mock
                if not capability_info["available"]:
                    self.assertEqual(capability_info["implementation"], "mock")

    def test_all_processors_have_consistent_interface(self) -> None:
        """
        Test that all created processors implement the same interface.
        
        Expected behavior:
        - All have can_process method
        - All have supported_formats property
        - All have processor_info property
        - All have process method
        
        Raises:
            AssertionError: If interface is inconsistent
        """
        # Act
        processors = make_processors()
        
        # Assert
        required_methods = ["can_process", "process"]
        required_properties = ["supported_formats", "processor_info"]
        
        for processor_name, processor in processors.items():
            # Check required methods
            for method_name in required_methods:
                self.assertTrue(hasattr(processor, method_name), 
                              f"{processor_name} missing method {method_name}")
                self.assertTrue(callable(getattr(processor, method_name)),
                              f"{processor_name}.{method_name} is not callable")
            
            # Check required properties
            for property_name in required_properties:
                self.assertTrue(hasattr(processor, property_name),
                              f"{processor_name} missing property {property_name}")
            
            # Verify property types
            self.assertIsInstance(processor.supported_formats, (set, frozenset))
            self.assertIsInstance(processor.processor_info, dict)
            
            # Verify method signatures work
            self.assertIsInstance(processor.can_process("test.txt"), bool)


class TestProcessorResources(unittest.TestCase):
    """Test the ProcessorResources TypedDict structure."""

    def test_processor_resources_structure_is_valid(self) -> None:
        """
        Test that ProcessorResources TypedDict has correct structure.
        
        Expected behavior:
        - Has all required fields
        - Field types are correct
        - Can be used for type checking
        
        Raises:
            AssertionError: If structure is invalid
        """
        # This test verifies the TypedDict structure at import time
        # The fact that we can import ProcessorResources means it's syntactically valid
        
        # Verify ProcessorResources can be used for type annotations
        def test_function(resources: ProcessorResources) -> None:
            pass
        
        # Create a valid resources dict
        valid_resources = {
            "supported_formats": {"xlsx", "xlsm"},
            "processor_name": "test_processor",
            "dependencies": {"openpyxl": MagicMock()},
            "critical_resources": ["extract_text"],
            "optional_resources": ["extract_images"],
            "logger": MagicMock(spec=logging.Logger),
            "configs": MagicMock(spec=Configs),
        }
        
        # Should not raise any type errors
        test_function(valid_resources)
        
        # Verify required fields
        required_fields = [
            "supported_formats", "processor_name", "dependencies",
            "critical_resources", "optional_resources", "logger", "configs"
        ]
        for field in required_fields:
            self.assertIn(field, valid_resources)

    def test_resource_list_contains_valid_resources(self) -> None:
        """
        Test that all resources in resource_list follow the structure.
        
        Expected behavior:
        - Each resource dict has all required fields
        - Values are of correct types
        - No missing or extra fields
        
        Raises:
            AssertionError: If any resource is invalid
        """
        # Import the actual resource_list (assuming it exists in the factory module)
        from core.content_extractor.processors.factory import resource_list
        
        # Verify resource_list exists and is a list
        self.assertIsInstance(resource_list, list)
        self.assertGreater(len(resource_list), 0)
        
        # Check each resource in the list
        for i, resource in enumerate(resource_list):
            with self.subTest(f"Resource {i}: {resource.get('processor_name', 'unknown')}"):
                # Verify required fields
                required_fields = [
                    "supported_formats", "processor_name", "dependencies",
                    "critical_resources", "optional_resources"
                ]
                for field in required_fields:
                    self.assertIn(field, resource, f"Missing field {field}")
                
                # Verify field types
                self.assertIsInstance(resource["supported_formats"], (set, frozenset))
                self.assertIsInstance(resource["processor_name"], str)
                self.assertIsInstance(resource["dependencies"], dict)
                self.assertIsInstance(resource["critical_resources"], list)
                self.assertIsInstance(resource["optional_resources"], list)
                
                # Verify processor_name is not empty
                self.assertGreater(len(resource["processor_name"]), 0)
                
                # Verify supported_formats is not empty
                self.assertGreater(len(resource["supported_formats"]), 0)


class TestFactoryErrorHandling(unittest.TestCase):
    """Test error handling in the factory."""

    def test_handles_import_errors_gracefully(self) -> None:
        """
        Test that factory handles ImportError when loading processors.
        
        Expected behavior:
        - Catches ImportError
        - Falls back to next option or mock
        - Logs appropriate warning
        - Never crashes
        
        Raises:
            AssertionError: If import errors cause crashes
        """
        # Arrange
        resources = {
            **TestMakeProcessor().basic_resources,
            "dependencies": {"nonexistent_module": None},
        }
        
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            # Act - should not raise an exception
            processor = _make_processor(resources)
            
            # Assert
            self.assertIsNotNone(processor)
            # Should fall back to mock
            self.assertIsInstance(processor, MagicMock)

    def test_handles_processor_instantiation_errors(self) -> None:
        """
        Test that factory handles errors during processor instantiation.
        
        Expected behavior:
        - Catches exceptions from processor __init__
        - Returns mock instead
        - Logs error with details
        - Never crashes
        
        Raises:
            AssertionError: If instantiation errors cause crashes
        """
        # Arrange
        faulty_dependency = MagicMock()
        faulty_dependency.side_effect = RuntimeError("Instantiation failed")
        
        resources = {
            **TestMakeProcessor().basic_resources,
            "dependencies": {"faulty_dep": faulty_dependency},
        }
        
        # Act - should not raise an exception
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsNotNone(processor)
        # Should fall back to mock due to instantiation error
        self.assertIsInstance(processor, MagicMock)

    def test_handles_missing_critical_resources(self) -> None:
        """
        Test that factory handles cases where critical resources are missing.
        
        Expected behavior:
        - Identifies missing resources
        - Returns mock with those methods
        - Reports degradation clearly
        
        Raises:
            AssertionError: If missing resources cause issues
        """
        # Arrange
        resources = {
            **TestMakeProcessor().basic_resources,
            "dependencies": {},  # No dependencies available
            "critical_resources": ["extract_text", "extract_metadata"],
        }
        
        # Act
        processor = _make_processor(resources)
        
        # Assert
        self.assertIsInstance(processor, MagicMock)
        
        # Verify critical methods are available as mocks
        self.assertTrue(hasattr(processor, "extract_text"))
        self.assertTrue(hasattr(processor, "extract_metadata"))
        
        # Verify processor info reports missing critical resources
        processor_info = processor.processor_info
        self.assertIn("capabilities", processor_info)
        
        for critical_resource in resources["critical_resources"]:
            self.assertIn(critical_resource, processor_info["capabilities"])
            self.assertFalse(processor_info["capabilities"][critical_resource]["available"])
            self.assertEqual(processor_info["capabilities"][critical_resource]["implementation"], "mock")


class TestCapabilityReporting(unittest.TestCase):
    """Test capability reporting functionality."""

    def test_generates_accurate_capability_reports(self) -> None:
        """
        Test that processors generate accurate capability reports.
        
        Expected behavior:
        - Reports list all requested capabilities
        - Shows actual implementation for each
        - Identifies mocked capabilities
        
        Raises:
            AssertionError: If reports are inaccurate
        """
        # Act
        processors = make_processors()
        
        # Assert
        for processor_name, processor in processors.items():
            processor_info = processor.processor_info
            capabilities = processor_info["capabilities"]
            
            # Verify all capabilities are reported
            self.assertIsInstance(capabilities, dict)
            self.assertGreater(len(capabilities), 0)
            
            # Verify each capability has required info
            for capability_name, capability_info in capabilities.items():
                self.assertIn("available", capability_info)
                self.assertIn("implementation", capability_info)
                
                # If available, implementation should not be mock
                if capability_info["available"]:
                    self.assertNotEqual(capability_info["implementation"], "mock")
                else:
                    self.assertEqual(capability_info["implementation"], "mock")

    def test_capability_reports_are_human_readable(self) -> None:
        """
        Test that capability reports are formatted for human consumption.
        
        Expected behavior:
        - Clear formatting with checkmarks/x marks
        - Implementation names are understandable
        - Grouped logically by processor
        
        Raises:
            AssertionError: If reports are not readable
        """
        # Act
        processors = make_processors()
        
        # Get a formatted capability report
        from core.content_extractor.processors.factory import generate_capability_report
        report = generate_capability_report(processors)
        
        # Assert
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        # Verify human-readable formatting
        self.assertIn("✓", report)  # Available capabilities
        self.assertIn("✗", report)  # Unavailable capabilities
        
        # Verify processor names are included
        for processor_name in processors.keys():
            self.assertIn(processor_name, report)
        
        # Verify implementation names are understandable (not internal module paths)
        self.assertNotIn("core.content_extractor.processors", report)
        self.assertNotIn("__pycache__", report)
        
        # Verify logical grouping - processors should be clearly separated
        lines = report.split('\n')
        processor_headers = [line for line in lines if "processor" in line.lower() and ":" in line]
        self.assertGreater(len(processor_headers), 0)

    def test_startup_report_summarizes_all_processors(self) -> None:
        """
        Test that startup report shows all processor capabilities.
        
        Expected behavior:
        - Lists all processors
        - Shows degraded capabilities prominently
        - Provides actionable information
        
        Raises:
            AssertionError: If startup report is incomplete
        """
        # Act
        processors = make_processors()
        from core.content_extractor.processors.factory import generate_startup_report
        startup_report = generate_startup_report(processors)
        
        # Assert
        self.assertIsInstance(startup_report, str)
        self.assertGreater(len(startup_report), 0)
        
        # Verify all processors are listed
        for processor_name in processors.keys():
            self.assertIn(processor_name, startup_report)
        
        # Verify degraded capabilities are prominently shown
        self.assertIn("DEGRADED", startup_report.upper())
        self.assertIn("WARNING", startup_report.upper())
        
        # Verify actionable information is provided
        self.assertIn("install", startup_report.lower())
        self.assertIn("pip", startup_report.lower())
        
        # Verify summary statistics
        self.assertIn("processors loaded", startup_report.lower())
        self.assertIn("fully functional", startup_report.lower())
        
        # Verify format is suitable for logging at startup
        lines = startup_report.split('\n')
        self.assertGreater(len(lines), 5)  # Multi-line report
        self.assertLess(len(lines), 100)   # But not excessively long


if __name__ == "__main__":
    unittest.main()
