import unittest


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pydantic import ValidationError

# Import the class under test
from core.file_validator._validation_result import ValidationResult

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import copy

# Import the class under test
from core.file_validator._validation_result import ValidationResult



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

# Import the class under test
from core.file_validator._validation_result import ValidationResult











class TestValidationResultInitialization(unittest.TestCase):
    """Test ValidationResult initialization and BaseModel behavior."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_init_with_all_valid_parameters(self):
        """
        GIVEN valid parameters:
            - is_valid: True
            - errors: ['error1', 'error2']
            - warnings: ['warning1']
            - validation_context: {'key': 'value'}
        WHEN ValidationResult is initialized
        THEN expect:
            - Instance created successfully
            - is_valid is True
            - errors list contains provided errors
            - warnings list contains provided warnings
            - validation_context dict contains provided context
        """
        # GIVEN
        is_valid = True
        errors = ['error1', 'error2']
        warnings = ['warning1']
        validation_context = {'key': 'value'}
        
        # WHEN
        result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            validation_context=validation_context
        )
        
        # THEN
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.is_valid, True)
        self.assertEqual(result.errors, ['error1', 'error2'])
        self.assertEqual(result.warnings, ['warning1'])
        self.assertEqual(result.validation_context, {'key': 'value'})

    def test_init_with_minimal_parameters(self):
        """
        GIVEN only required parameters (if any)
        WHEN ValidationResult is initialized
        THEN expect:
            - Instance created successfully
            - is_valid has default value (likely False)
            - errors is empty list
            - warnings is empty list
            - validation_context is empty dict
        """
        # WHEN
        result = ValidationResult()
        
        # THEN
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.is_valid, True)  # Based on your specification
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.validation_context, {})

    def test_init_with_invalid_is_valid_type(self):
        """
        GIVEN is_valid parameter with non-boolean type (e.g., string)
        WHEN ValidationResult is initialized
        THEN expect:
            - Pydantic ValidationError raised
            - Error indicates type mismatch for is_valid
        """
        # WHEN & THEN
        with self.assertRaises(ValidationError) as context:
            ValidationResult(is_valid="not a boolean")
        
        # Verify the error is related to is_valid field
        error_details = str(context.exception)
        self.assertIn('is_valid', error_details.lower())

    def test_init_with_invalid_errors_type(self):
        """
        GIVEN errors parameter as non-list type (e.g., string)
        WHEN ValidationResult is initialized
        THEN expect:
            - Pydantic ValidationError raised
            - Error indicates type mismatch for errors
        """
        # WHEN & THEN
        with self.assertRaises(ValidationError) as context:
            ValidationResult(errors="not a list")
        
        # Verify the error is related to errors field
        error_details = str(context.exception)
        self.assertIn('errors', error_details.lower())

    def test_init_with_invalid_warnings_type(self):
        """
        GIVEN warnings parameter as non-list type (e.g., dict)
        WHEN ValidationResult is initialized
        THEN expect:
            - Pydantic ValidationError raised
            - Error indicates type mismatch for warnings
        """
        # WHEN & THEN
        with self.assertRaises(ValidationError) as context:
            ValidationResult(warnings={'not': 'a list'})
        
        # Verify the error is related to warnings field
        error_details = str(context.exception)
        self.assertIn('warnings', error_details.lower())

    def test_init_with_invalid_validation_context_type(self):
        """
        GIVEN validation_context parameter as non-dict type (e.g., list)
        WHEN ValidationResult is initialized
        THEN expect:
            - Pydantic ValidationError raised
            - Error indicates type mismatch for validation_context
        """
        # WHEN & THEN
        with self.assertRaises(ValidationError) as context:
            ValidationResult(validation_context=['not', 'a', 'dict'])
        
        # Verify the error is related to validation_context field
        error_details = str(context.exception)
        self.assertIn('validation_context', error_details.lower())

    def test_init_with_none_values(self):
        """
        GIVEN None values for optional parameters
        WHEN ValidationResult is initialized
        THEN expect:
            - Instance created successfully
            - None values converted to appropriate defaults
            - errors becomes empty list
            - warnings becomes empty list
            - validation_context becomes empty dict
        """
        # WHEN
        result = ValidationResult(
            errors=None,
            warnings=None,
            validation_context=None
        )
        
        # THEN
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.validation_context, {})



class TestAddError(unittest.TestCase):
    """Test ValidationResult.add_error method."""

    def setUp(self):
        """Set up test fixtures."""
        self.result = ValidationResult()

    def test_add_error_to_empty_list(self):
        """
        GIVEN a ValidationResult instance with empty errors list
        AND an error message string
        WHEN add_error is called
        THEN expect:
            - Error is added to errors list
            - errors list contains exactly one item
            - The item equals the provided error message
        """
        # GIVEN
        error_message = "Test error message"
        
        # WHEN
        self.result.add_error(error_message)
        
        # THEN
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.errors[0], error_message)

    def test_add_error_to_existing_list_preserves_count(self):
        """
        GIVEN a ValidationResult instance with existing errors
        AND a new error message string
        WHEN add_error is called
        THEN expect:
            - Error is appended to errors list
            - Total count equals previous count plus one
        """
        # GIVEN
        existing_error = "Existing error"
        new_error = "New error"
        self.result.add_error(existing_error)
        
        # WHEN
        self.result.add_error(new_error)
        
        # THEN
        self.assertEqual(len(self.result.errors), 2)

    def test_add_error_to_existing_list_preserves_previous_errors(self):
        """
        GIVEN a ValidationResult instance with existing errors
        AND a new error message string
        WHEN add_error is called
        THEN expect:
            - Previous errors are preserved
        """
        # GIVEN
        existing_error = "Existing error"
        new_error = "New error"
        self.result.add_error(existing_error)
        
        # WHEN
        self.result.add_error(new_error)
        
        # THEN
        self.assertEqual(self.result.errors[0], existing_error)

    def test_add_error_to_existing_list_appends_new_error(self):
        """
        GIVEN a ValidationResult instance with existing errors
        AND a new error message string
        WHEN add_error is called
        THEN expect:
            - New error is at the end of the list
        """
        # GIVEN
        existing_error = "Existing error"
        new_error = "New error"
        self.result.add_error(existing_error)
        
        # WHEN
        self.result.add_error(new_error)
        
        # THEN
        self.assertEqual(self.result.errors[1], new_error)

    def test_add_multiple_errors_sequentially_correct_length(self):
        """
        GIVEN a ValidationResult instance
        WHEN add_error is called multiple times with different messages
        THEN expect:
            - errors list length equals number of calls
        """
        # GIVEN
        errors = ["Error 1", "Error 2", "Error 3"]

        # WHEN
        for error in errors:
            self.result.add_error(error)

        # THEN
        self.assertEqual(len(self.result.errors), 3)

    def test_add_multiple_errors_sequentially_preserves_order(self):
        """
        GIVEN a ValidationResult instance
        WHEN add_error is called multiple times with different messages
        THEN expect:
            - Order is preserved
        """
        # GIVEN
        errors = ["Error 1", "Error 2", "Error 3"]

        # WHEN
        for error in errors:
            self.result.add_error(error)

        # THEN
        self.assertEqual(self.result.errors, errors)

    def test_add_empty_string_error(self):
        """
        GIVEN a ValidationResult instance
        AND an empty string error message
        WHEN add_error is called
        THEN expect:
            - Empty string is not added to the errors list
        """
        # GIVEN
        empty_error = ""
        
        # WHEN
        self.result.add_error(empty_error)

        # THEN
        self.assertEqual(len(self.result.errors), 0)

    def test_add_none_error(self):
        """
        GIVEN a ValidationResult instance
        AND None as error message
        WHEN add_error is called
        THEN expect:
            - TypeError is raised
        """
        # GIVEN
        error_is_none = None

        # WHEN & THEN
        with self.assertRaises(TypeError):
            self.result.add_error(error_is_none)

    def test_add_duplicate_error(self):
        """
        GIVEN a ValidationResult instance with an existing error
        AND the same error message
        WHEN add_error is called
        THEN expect:
            - Duplicate error is added (no deduplication)
            - errors list contains both instances
        """
        # GIVEN
        error_message = "Duplicate error"
        self.result.add_error(error_message)
        
        # WHEN
        self.result.add_error(error_message)
        
        # THEN
        self.assertEqual(len(self.result.errors), 2)
        self.assertEqual(self.result.errors[0], error_message)
        self.assertEqual(self.result.errors[1], error_message)

    def test_add_error_affects_is_valid(self):
        """
        GIVEN a ValidationResult instance with is_valid=True
        WHEN add_error is called
        THEN expect:
            - is_valid automatically becomes False
        """
        # GIVEN
        self.assertTrue(self.result.is_valid)  # Default is True
        
        # WHEN
        self.result.add_error("Test error")
        
        # THEN - is_valid automatically becomes False when errors are added
        self.assertFalse(self.result.is_valid)



class TestAddWarning(unittest.TestCase):
    """Test ValidationResult.add_warning method."""

    def setUp(self):
        """Set up test fixtures."""
        self.result = ValidationResult()

    def test_add_warning_to_empty_list(self):
        """
        GIVEN a ValidationResult instance with empty warnings list
        AND a warning message string
        WHEN add_warning is called
        THEN expect:
            - Warning is added to warnings list
            - warnings list contains exactly one item
            - The item equals the provided warning message
        """
        # GIVEN
        warning_message = "Test warning message"
        
        # WHEN
        self.result.add_warning(warning_message)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 1)
        self.assertEqual(self.result.warnings[0], warning_message)

    def test_add_warning_to_existing_list(self):
        """
        GIVEN a ValidationResult instance with existing warnings
        AND a new warning message string
        WHEN add_warning is called
        THEN expect:
            - Warning is appended to warnings list
            - Previous warnings are preserved
            - New warning is at the end of the list
        """
        # GIVEN
        existing_warning = "Existing warning"
        new_warning = "New warning"
        self.result.add_warning(existing_warning)
        
        # WHEN
        self.result.add_warning(new_warning)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 2)
        self.assertEqual(self.result.warnings[0], existing_warning)
        self.assertEqual(self.result.warnings[1], new_warning)

    def test_add_multiple_warnings_sequentially(self):
        """
        GIVEN a ValidationResult instance
        WHEN add_warning is called multiple times with different messages
        THEN expect:
            - All warnings are added in order
            - warnings list length equals number of calls
            - Order is preserved
        """
        # GIVEN
        warnings = ["Warning 1", "Warning 2", "Warning 3"]
        
        # WHEN
        for warning in warnings:
            self.result.add_warning(warning)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 3)
        self.assertEqual(self.result.warnings, warnings)

    def test_add_empty_string_warning(self):
        """
        GIVEN a ValidationResult instance
        AND an empty string warning message
        WHEN add_warning is called
        THEN expect:
            - Empty string is added to warnings list
            - No exception raised
        """
        # GIVEN
        empty_warning = ""
        
        # WHEN
        self.result.add_warning(empty_warning)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 1)
        self.assertEqual(self.result.warnings[0], "")

    def test_add_none_warning(self):
        """
        GIVEN a ValidationResult instance
        AND None as warning message
        WHEN add_warning is called
        THEN expect:
            - None is added to warnings list OR
            - TypeError is raised OR
            - None is converted to string 'None'
        """
        # WHEN & THEN
        try:
            self.result.add_warning(None)
            # If no exception, check what was actually added
            self.assertEqual(len(self.result.warnings), 1)
            # Could be None or string 'None' depending on implementation
            self.assertIn(self.result.warnings[0], [None, 'None'])
        except TypeError:
            # This is also acceptable behavior
            pass

    def test_add_duplicate_warning(self):
        """
        GIVEN a ValidationResult instance with an existing warning
        AND the same warning message
        WHEN add_warning is called
        THEN expect:
            - Duplicate warning is added (no deduplication)
            - warnings list contains both instances
        """
        # GIVEN
        warning_message = "Duplicate warning"
        self.result.add_warning(warning_message)
        
        # WHEN
        self.result.add_warning(warning_message)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 2)
        self.assertEqual(self.result.warnings[0], warning_message)
        self.assertEqual(self.result.warnings[1], warning_message)

    def test_add_warning_does_not_affect_is_valid(self):
        """
        GIVEN a ValidationResult instance with is_valid=True
        WHEN add_warning is called
        THEN expect:
            - is_valid remains True
            - Warnings don't affect validation status
        """
        # GIVEN
        self.assertTrue(self.result.is_valid)  # Default is True
        
        # WHEN
        self.result.add_warning("Test warning")
        
        # THEN
        self.assertTrue(self.result.is_valid)

    def test_add_warning_with_errors_present(self):
        """
        GIVEN a ValidationResult instance with existing errors
        WHEN add_warning is called
        THEN expect:
            - Warning is added successfully
            - Errors list is not affected
            - warnings and errors lists remain separate
        """
        # GIVEN
        error_message = "Existing error"
        warning_message = "New warning"
        self.result.add_error(error_message)
        original_errors = self.result.errors.copy()
        
        # WHEN
        self.result.add_warning(warning_message)
        
        # THEN
        self.assertEqual(len(self.result.warnings), 1)
        self.assertEqual(self.result.warnings[0], warning_message)
        self.assertEqual(self.result.errors, original_errors)
        self.assertEqual(len(self.result.errors), 1)




class TestAddContext(unittest.TestCase):
    """Test ValidationResult.add_context method."""

    def setUp(self):
        """Set up test fixtures."""
        self.result = ValidationResult()

    def test_add_context_to_empty_dict(self):
        """
        GIVEN a ValidationResult instance with empty validation_context
        AND a key-value pair (string key, any value)
        WHEN add_context is called
        THEN expect:
            - Key-value pair is added to validation_context
            - validation_context contains exactly one entry
            - The entry matches provided key and value
        """
        # GIVEN
        key = "test_key"
        value = "test_value"
        
        # WHEN
        self.result.add_context(key, value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 1)
        self.assertEqual(self.result.validation_context[key], value)

    def test_add_context_to_existing_dict(self):
        """
        GIVEN a ValidationResult instance with existing context entries
        AND a new key-value pair
        WHEN add_context is called
        THEN expect:
            - New key-value pair is added
            - Previous entries are preserved
            - validation_context contains all entries
        """
        # GIVEN
        existing_key = "existing_key"
        existing_value = "existing_value"
        new_key = "new_key"
        new_value = "new_value"
        self.result.add_context(existing_key, existing_value)
        
        # WHEN
        self.result.add_context(new_key, new_value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 2)
        self.assertEqual(self.result.validation_context[existing_key], existing_value)
        self.assertEqual(self.result.validation_context[new_key], new_value)

    def test_add_context_with_duplicate_key(self):
        """
        GIVEN a ValidationResult instance with existing context entry
        AND a key-value pair with same key but different value
        WHEN add_context is called
        THEN expect:
            - Existing value is overwritten
            - New value replaces old value
            - Other entries remain unchanged
        """
        # GIVEN
        key = "duplicate_key"
        original_value = "original_value"
        new_value = "new_value"
        other_key = "other_key"
        other_value = "other_value"
        
        self.result.add_context(key, original_value)
        self.result.add_context(other_key, other_value)
        
        # WHEN
        self.result.add_context(key, new_value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 2)
        self.assertEqual(self.result.validation_context[key], new_value)
        self.assertEqual(self.result.validation_context[other_key], other_value)

    def test_add_context_with_various_value_types(self):
        """
        GIVEN a ValidationResult instance
        WHEN add_context is called with various value types:
            - String value
            - Integer value
            - List value
            - Dict value
            - None value
            - Boolean value
        THEN expect:
            - All values are stored correctly
            - Type integrity is maintained
            - No type conversion occurs
        """
        # GIVEN
        test_cases = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("list_key", [1, 2, 3]),
            ("dict_key", {"nested": "dict"}),
            ("none_key", None),
            ("bool_key", True)
        ]
        
        # WHEN
        for key, value in test_cases:
            self.result.add_context(key, value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 6)
        for key, expected_value in test_cases:
            self.assertEqual(self.result.validation_context[key], expected_value)
            self.assertEqual(type(self.result.validation_context[key]), type(expected_value))

    def test_add_context_with_empty_string_key(self):
        """
        GIVEN a ValidationResult instance
        AND an empty string as key
        WHEN add_context is called
        THEN expect:
            - Empty string key is accepted
            - Value is stored under empty string key
            - No exception raised
        """
        # GIVEN
        empty_key = ""
        value = "value_for_empty_key"
        
        # WHEN
        self.result.add_context(empty_key, value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 1)
        self.assertEqual(self.result.validation_context[empty_key], value)

    def test_add_context_with_none_key(self):
        """
        GIVEN a ValidationResult instance
        AND None as key
        WHEN add_context is called
        THEN expect:
            - TypeError is raised OR
            - None key is accepted (dict allows None keys)
        """
        # GIVEN
        none_key = None
        value = "value_for_none_key"
        
        # WHEN & THEN
        try:
            self.result.add_context(none_key, value)
            # If no exception, check that None key was accepted
            self.assertEqual(len(self.result.validation_context), 1)
            self.assertEqual(self.result.validation_context[none_key], value)
        except TypeError:
            # This is also acceptable behavior
            pass

    def test_add_context_with_complex_nested_value(self):
        """
        GIVEN a ValidationResult instance
        AND a complex nested structure as value (e.g., dict of lists of dicts)
        WHEN add_context is called
        THEN expect:
            - Complex structure is stored correctly
            - Structure is preserved without modification
            - Can retrieve exact same structure
        """
        # GIVEN
        key = "complex_key"
        complex_value = {
            "level1": {
                "level2": [
                    {"item1": "value1"},
                    {"item2": [1, 2, {"nested": True}]}
                ]
            },
            "other_level1": ["a", "b", {"c": "d"}]
        }
        
        # WHEN
        self.result.add_context(key, complex_value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 1)
        retrieved_value = self.result.validation_context[key]
        self.assertEqual(retrieved_value, complex_value)
        
        # Verify deep structure is preserved
        self.assertEqual(retrieved_value["level1"]["level2"][1]["item2"][2]["nested"], True)
        self.assertEqual(retrieved_value["other_level1"][2]["c"], "d")

    def test_add_multiple_contexts_sequentially(self):
        """
        GIVEN a ValidationResult instance
        WHEN add_context is called multiple times with different keys
        THEN expect:
            - All key-value pairs are added
            - validation_context size equals number of unique keys
            - All values are accessible by their keys
        """
        # GIVEN
        contexts = [
            ("key1", "value1"),
            ("key2", "value2"),
            ("key3", "value3"),
            ("key4", "value4")
        ]
        
        # WHEN
        for key, value in contexts:
            self.result.add_context(key, value)
        
        # THEN
        self.assertEqual(len(self.result.validation_context), 4)
        for key, expected_value in contexts:
            self.assertEqual(self.result.validation_context[key], expected_value)


class TestToDict(unittest.TestCase):
    """Test ValidationResult.to_dict method."""

    def setUp(self):
        """Set up test fixtures."""
        self.result = ValidationResult()

    def test_to_dict_with_all_fields_populated(self):
        """
        GIVEN a ValidationResult instance with:
            - is_valid: True
            - errors: ['error1', 'error2']
            - warnings: ['warning1']
            - validation_context: {'key': 'value', 'count': 42}
        WHEN to_dict is called
        THEN expect:
            - Returns dict with all fields
            - dict['is_valid'] == True
            - dict['errors'] == ['error1', 'error2']
            - dict['warnings'] == ['warning1']
            - dict['validation_context'] == {'key': 'value', 'count': 42}
        """
        # GIVEN
        self.result.is_valid = True
        self.result.add_error('error1')
        self.result.add_error('error2')
        self.result.add_warning('warning1')
        self.result.add_context('key', 'value')
        self.result.add_context('count', 42)
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['is_valid'], True)
        self.assertEqual(result_dict['errors'], ['error1', 'error2'])
        self.assertEqual(result_dict['warnings'], ['warning1'])
        self.assertEqual(result_dict['validation_context'], {'key': 'value', 'count': 42})

    def test_to_dict_with_empty_collections(self):
        """
        GIVEN a ValidationResult instance with:
            - is_valid: False
            - errors: []
            - warnings: []
            - validation_context: {}
        WHEN to_dict is called
        THEN expect:
            - Returns dict with all fields
            - dict['errors'] is empty list
            - dict['warnings'] is empty list
            - dict['validation_context'] is empty dict
        """
        # GIVEN
        self.result.is_valid = False
        # Default initialization should have empty collections
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['is_valid'], False)
        self.assertEqual(result_dict['errors'], [])
        self.assertEqual(result_dict['warnings'], [])
        self.assertEqual(result_dict['validation_context'], {})

    def test_to_dict_preserves_data_types(self):
        """
        GIVEN a ValidationResult instance with various data types in context:
            - String values
            - Integer values
            - Float values
            - Boolean values
            - List values
            - Nested dict values
        WHEN to_dict is called
        THEN expect:
            - All data types are preserved
            - No unwanted type conversions
            - Nested structures remain intact
        """
        # GIVEN
        self.result.add_context('string_val', "test string")
        self.result.add_context('int_val', 123)
        self.result.add_context('float_val', 45.67)
        self.result.add_context('bool_val', True)
        self.result.add_context('list_val', [1, 2, 3])
        self.result.add_context('nested_dict', {'inner': {'value': 'nested'}})
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN
        context = result_dict['validation_context']
        self.assertEqual(type(context['string_val']), str)
        self.assertEqual(type(context['int_val']), int)
        self.assertEqual(type(context['float_val']), float)
        self.assertEqual(type(context['bool_val']), bool)
        self.assertEqual(type(context['list_val']), list)
        self.assertEqual(type(context['nested_dict']), dict)
        
        # Verify values are correct
        self.assertEqual(context['string_val'], "test string")
        self.assertEqual(context['int_val'], 123)
        self.assertEqual(context['float_val'], 45.67)
        self.assertEqual(context['bool_val'], True)
        self.assertEqual(context['list_val'], [1, 2, 3])
        self.assertEqual(context['nested_dict'], {'inner': {'value': 'nested'}})

    def test_to_dict_returns_new_dict_instance(self):
        """
        GIVEN a ValidationResult instance
        WHEN to_dict is called multiple times
        THEN expect:
            - Each call returns a new dict instance
            - Modifying returned dict doesn't affect original
            - Modifying original doesn't affect returned dicts
        """
        # GIVEN
        self.result.add_error('test error')
        self.result.add_context('test_key', 'test_value')
        
        # WHEN
        dict1 = self.result.to_dict()
        dict2 = self.result.to_dict()
        
        # THEN
        self.assertIsNot(dict1, dict2)  # Different instances
        
        # Modify dict1 and verify dict2 and original are unaffected
        dict1['errors'].append('modified error')
        dict1['validation_context']['new_key'] = 'new_value'
        
        self.assertNotEqual(dict1['errors'], dict2['errors'])
        self.assertNotIn('new_key', dict2['validation_context'])
        self.assertEqual(len(self.result.errors), 1)  # Original unchanged

    def test_to_dict_handles_modified_instance(self):
        """
        GIVEN a ValidationResult instance
        AND instance is modified after creation using:
            - add_error()
            - add_warning()
            - add_context()
        WHEN to_dict is called
        THEN expect:
            - Returns dict with all modifications included
            - All added errors present
            - All added warnings present
            - All added context entries present
        """
        # GIVEN - Initial state
        initial_dict = self.result.to_dict()
        
        # WHEN - Modify the instance
        self.result.add_error('error after creation')
        self.result.add_warning('warning after creation')
        self.result.add_context('context_after', 'creation')
        
        modified_dict = self.result.to_dict()
        
        # THEN
        self.assertNotEqual(initial_dict['errors'], modified_dict['errors'])
        self.assertNotEqual(initial_dict['warnings'], modified_dict['warnings'])
        self.assertNotEqual(initial_dict['validation_context'], modified_dict['validation_context'])
        
        self.assertIn('error after creation', modified_dict['errors'])
        self.assertIn('warning after creation', modified_dict['warnings'])
        self.assertEqual(modified_dict['validation_context']['context_after'], 'creation')

    def test_to_dict_deep_copy_behavior(self):
        """
        GIVEN a ValidationResult instance with nested mutable objects
        WHEN to_dict is called
        THEN expect:
            - Nested lists are copied (not referenced)
            - Nested dicts are copied (not referenced)
            - Modifying returned nested structures doesn't affect original
        """
        # GIVEN
        nested_list = [1, 2, [3, 4]]
        nested_dict = {'outer': {'inner': 'value'}}
        
        self.result.add_context('nested_list', nested_list)
        self.result.add_context('nested_dict', nested_dict)
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN - Modify nested structures in returned dict
        result_dict['validation_context']['nested_list'][2].append(5)
        result_dict['validation_context']['nested_dict']['outer']['inner'] = 'modified'
        
        # Original should be unchanged
        original_nested_list = self.result.validation_context['nested_list']
        original_nested_dict = self.result.validation_context['nested_dict']
        
        self.assertEqual(len(original_nested_list[2]), 2)  # Should still be [3, 4]
        self.assertEqual(original_nested_dict['outer']['inner'], 'value')  # Unchanged

    def test_to_dict_with_pydantic_model_features(self):
        """
        GIVEN a ValidationResult instance (Pydantic BaseModel)
        WHEN to_dict is called
        THEN expect:
            - Only includes defined fields
            - No Pydantic internal attributes
            - No private attributes included
            - Result is JSON-serializable
        """
        # GIVEN
        self.result.add_error('test error')
        self.result.add_warning('test warning')
        self.result.add_context('test_key', 'test_value')
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN
        expected_keys = {'is_valid', 'errors', 'warnings', 'validation_context'}
        self.assertEqual(set(result_dict.keys()), expected_keys)
        
        # Should not include Pydantic internals
        for key in result_dict.keys():
            self.assertFalse(key.startswith('_'))
        
        # Should be JSON-serializable
        import json
        json.dumps(result_dict)


    def test_to_dict_field_order(self):
        """
        GIVEN a ValidationResult instance
        WHEN to_dict is called
        THEN expect:
            - Fields appear in consistent order
            - Likely order: is_valid, errors, warnings, validation_context
            - Order matches model field definition order
        """
        # GIVEN
        self.result.add_error('test error')
        self.result.add_warning('test warning')
        self.result.add_context('test_key', 'test_value')
        
        # WHEN
        result_dict = self.result.to_dict()
        
        # THEN
        keys_list = list(result_dict.keys())
        expected_order = ['is_valid', 'errors', 'warnings', 'validation_context']
        
        # Check that all expected keys are present
        self.assertEqual(set(keys_list), set(expected_order))

        # Check order
        self.assertEqual(keys_list, expected_order)


if __name__ == "__main__":
    unittest.main()