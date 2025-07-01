# Test Results
Return Code: 1
## Standard Output
Configuration loaded from /home/kylerose1946/omni_converter_mk2/configs.yaml
✓ Dependency 'tqdm' loaded successfully.
✓ Dependency 'yaml' loaded successfully.
✓ Dependency 'psutil' loaded successfully.
✓ Dependency 'pydantic' loaded successfully.
dict_keys(['txt', 'json', 'md'])
txt

## Standard Error
2025-06-30 20:12:44,447 - logger - WARNING - processor_factory.py:219 - Source processor 'docx_processor' does not have method 'extract_images'. Skipping...
test_available_formats_after_multiple_registrations (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_after_multiple_registrations)
GIVEN an OutputFormatter ... ok
test_available_formats_consistency_with_output_formats (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_consistency_with_output_formats)
GIVEN an OutputFormatter ... ok
test_available_formats_includes_defaults (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_includes_defaults)
GIVEN a newly initialized OutputFormatter ... ok
test_available_formats_is_immutable (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_is_immutable)
GIVEN an OutputFormatter ... ok
test_available_formats_returns_list (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_returns_list)
GIVEN an OutputFormatter ... ok
test_available_formats_updated_after_registration (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_updated_after_registration)
GIVEN an OutputFormatter ... ok
test_register_default_formatters_called_during_init (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_called_during_init)
GIVEN OutputFormatter class ... ok
test_register_default_formatters_creates_json_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_json_formatter)
GIVEN an OutputFormatter instance ... ok
test_register_default_formatters_creates_markdown_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_markdown_formatter)
GIVEN an OutputFormatter instance ... ok
test_register_default_formatters_creates_txt_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_txt_formatter)
GIVEN an OutputFormatter instance ... ok
test_format_output_with_all_parameters (test_output_formatter.TestFormatOutput.test_format_output_with_all_parameters)
GIVEN an OutputFormatter ... ERROR
test_format_output_with_default_format (test_output_formatter.TestFormatOutput.test_format_output_with_default_format)
GIVEN an OutputFormatter with default_format='txt' ... FAIL
test_format_output_with_invalid_format (test_output_formatter.TestFormatOutput.test_format_output_with_invalid_format)
GIVEN an OutputFormatter ... FAIL
test_format_output_with_none_content (test_output_formatter.TestFormatOutput.test_format_output_with_none_content)
GIVEN an OutputFormatter ... ok
test_format_output_with_options (test_output_formatter.TestFormatOutput.test_format_output_with_options)
GIVEN an OutputFormatter ... ERROR
test_format_output_with_output_path (test_output_formatter.TestFormatOutput.test_format_output_with_output_path)
GIVEN an OutputFormatter ... ERROR
test_format_output_with_specified_format (test_output_formatter.TestFormatOutput.test_format_output_with_specified_format)
GIVEN an OutputFormatter ... ERROR
test_format_as_json_encoding_special_characters (test_output_formatter.TestJsonFormatter.test_format_as_json_encoding_special_characters)
GIVEN a Content object with special characters (quotes, backslashes, unicode) ... ERROR
test_format_as_json_with_complex_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_complex_content)
GIVEN a Content object with nested data structures ... FAIL
test_format_as_json_with_datetime_attributes (test_output_formatter.TestJsonFormatter.test_format_as_json_with_datetime_attributes)
GIVEN a Content object containing datetime objects ... ERROR
test_format_as_json_with_non_serializable_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_non_serializable_content)
GIVEN a Content object with non-JSON-serializable attributes ... ERROR
test_format_as_json_with_simple_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_simple_content)
GIVEN a Content object with basic attributes ... FAIL
test_format_as_markdown_escaping_special_characters (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_escaping_special_characters)
GIVEN a Content object with Markdown special characters (*, _, #, etc.) ... ERROR
test_format_as_markdown_with_lists_and_formatting (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_lists_and_formatting)
GIVEN a Content object containing lists, bold, italic text ... ERROR
test_format_as_markdown_with_metadata (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_metadata)
GIVEN a Content object with metadata (title, author, date, etc.) ... ERROR
test_format_as_markdown_with_sections (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_sections)
GIVEN a Content object with multiple sections/chapters ... ERROR
test_format_as_markdown_with_simple_content (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_simple_content)
GIVEN a Content object with plain text ... FAIL
test_circular_reference_in_content (test_output_formatter.TestOutputFormatterErrorHandling.test_circular_reference_in_content)
GIVEN content with circular references ... ERROR
test_concurrent_format_registration (test_output_formatter.TestOutputFormatterErrorHandling.test_concurrent_format_registration)
GIVEN an OutputFormatter used by multiple threads ... ok
test_formatter_function_raises_exception (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_function_raises_exception)
GIVEN a formatter function that raises an exception ... ok
test_formatter_returns_non_string (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_returns_non_string)
GIVEN a formatter that returns non-string content ... ok
test_invalid_content_type_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_invalid_content_type_handling)
GIVEN various invalid content types (string, dict, list, etc.) ... ok
test_large_content_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_large_content_handling)
GIVEN extremely large content object ... ERROR
test_malformed_formatter_function (test_output_formatter.TestOutputFormatterErrorHandling.test_malformed_formatter_function)
GIVEN a formatter function with incorrect signature ... ok
test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes ... FAIL
test_resource_dependency_missing (test_output_formatter.TestOutputFormatterErrorHandling.test_resource_dependency_missing)
GIVEN OutputFormatter with missing resources ... ERROR
test_init_missing_logger_in_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_missing_logger_in_resources)
GIVEN resources dict missing 'logger' key ... ERROR
test_init_state_after_successful_initialization (test_output_formatter.TestOutputFormatterInitialization.test_init_state_after_successful_initialization)
GIVEN valid resources and configs ... ok
test_init_with_none_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_configs)
GIVEN configs=None ... ok
test_init_with_none_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_resources)
GIVEN resources=None ... ok
test_init_with_valid_resources_and_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_valid_resources_and_configs)
GIVEN valid resources dict containing: ... ok
test_end_to_end_formatting_workflow (test_output_formatter.TestOutputFormatterIntegration.test_end_to_end_formatting_workflow)
GIVEN complete setup with OutputFormatter, Content, and output path ... ERROR
test_formatted_output_creation (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_creation)
GIVEN an OutputFormatter with valid resources including FormattedOutput class ... FAIL
test_formatted_output_metadata_handling (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_metadata_handling)
GIVEN an OutputFormatter and Content with metadata ... FAIL
test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types)
GIVEN an OutputFormatter ... 
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513504'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513648'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513552'>)
GIVEN an OutputFormatter ... ERROR
test_integration_with_custom_formatter (test_output_formatter.TestOutputFormatterIntegration.test_integration_with_custom_formatter)
GIVEN an OutputFormatter with a custom registered format ... ERROR
test_register_format_case_sensitivity (test_output_formatter.TestRegisterFormat.test_register_format_case_sensitivity)
GIVEN an OutputFormatter ... ok
test_register_format_updates_available_formats (test_output_formatter.TestRegisterFormat.test_register_format_updates_available_formats)
GIVEN an OutputFormatter with default formats ... ok
test_register_format_with_duplicate_name (test_output_formatter.TestRegisterFormat.test_register_format_with_duplicate_name)
GIVEN an OutputFormatter with existing 'txt' format ... ok
test_register_format_with_invalid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_invalid_formatter)
GIVEN an OutputFormatter ... ok
test_register_format_with_lambda_function (test_output_formatter.TestRegisterFormat.test_register_format_with_lambda_function)
GIVEN an OutputFormatter ... ok
test_register_format_with_method_reference (test_output_formatter.TestRegisterFormat.test_register_format_with_method_reference)
GIVEN an OutputFormatter ... ok
test_register_format_with_valid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_valid_formatter)
GIVEN an OutputFormatter and a valid formatter function ... ok
test_format_as_txt_with_empty_content (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_empty_content)
GIVEN a Content object with empty text="" ... ok
test_format_as_txt_with_multiline_content (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_multiline_content)
GIVEN a Content object with text containing multiple lines ... ok
test_format_as_txt_with_none_text_attribute (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_none_text_attribute)
GIVEN a Content object with text=None ... ok
test_format_as_txt_with_simple_content (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_simple_content)
GIVEN a Content object with text="Hello World" ... ok
test_format_as_txt_with_special_characters (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_special_characters)
GIVEN a Content object with text containing special characters (tabs, unicode, etc.) ... ok

======================================================================
ERROR: test_format_output_with_all_parameters (test_output_formatter.TestFormatOutput.test_format_output_with_all_parameters)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1021, in test_format_output_with_all_parameters
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestFormatOutput' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_format_output_with_options (test_output_formatter.TestFormatOutput.test_format_output_with_options)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 975, in test_format_output_with_options
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestFormatOutput' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_format_output_with_output_path (test_output_formatter.TestFormatOutput.test_format_output_with_output_path)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 993, in test_format_output_with_output_path
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestFormatOutput' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_format_output_with_specified_format (test_output_formatter.TestFormatOutput.test_format_output_with_specified_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 940, in test_format_output_with_specified_format
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestFormatOutput' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_format_as_json_encoding_special_characters (test_output_formatter.TestJsonFormatter.test_format_as_json_encoding_special_characters)
GIVEN a Content object with special characters (quotes, backslashes, unicode)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 724, in test_format_as_json_encoding_special_characters
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 117, in _format_as_json
    return json.dumps(content.to_dict(), indent=2)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
          ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 202, in encode
    chunks = list(chunks)
             ^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 439, in _iterencode
    o = _default(o)
        ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type Mock is not JSON serializable

======================================================================
ERROR: test_format_as_json_with_datetime_attributes (test_output_formatter.TestJsonFormatter.test_format_as_json_with_datetime_attributes)
GIVEN a Content object containing datetime objects
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 670, in test_format_as_json_with_datetime_attributes
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 117, in _format_as_json
    return json.dumps(content.to_dict(), indent=2)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
          ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 202, in encode
    chunks = list(chunks)
             ^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 439, in _iterencode
    o = _default(o)
        ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type Mock is not JSON serializable

======================================================================
ERROR: test_format_as_json_with_non_serializable_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_non_serializable_content)
GIVEN a Content object with non-JSON-serializable attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 697, in test_format_as_json_with_non_serializable_content
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 117, in _format_as_json
    return json.dumps(content.to_dict(), indent=2)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
          ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 202, in encode
    chunks = list(chunks)
             ^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 439, in _iterencode
    o = _default(o)
        ^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type Mock is not JSON serializable

======================================================================
ERROR: test_format_as_markdown_escaping_special_characters (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_escaping_special_characters)
GIVEN a Content object with Markdown special characters (*, _, #, etc.)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 876, in test_format_as_markdown_escaping_special_characters
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 130, in _format_as_markdown
    md = f"# Content from {os.path.basename(content.source_path)}\n\n"
                                            ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_format_as_markdown_with_lists_and_formatting (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_lists_and_formatting)
GIVEN a Content object containing lists, bold, italic text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 851, in test_format_as_markdown_with_lists_and_formatting
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 130, in _format_as_markdown
    md = f"# Content from {os.path.basename(content.source_path)}\n\n"
                                            ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_format_as_markdown_with_metadata (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_metadata)
GIVEN a Content object with metadata (title, author, date, etc.)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 793, in test_format_as_markdown_with_metadata
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 130, in _format_as_markdown
    md = f"# Content from {os.path.basename(content.source_path)}\n\n"
                                            ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_format_as_markdown_with_sections (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_sections)
GIVEN a Content object with multiple sections/chapters
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 826, in test_format_as_markdown_with_sections
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 130, in _format_as_markdown
    md = f"# Content from {os.path.basename(content.source_path)}\n\n"
                                            ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_circular_reference_in_content (test_output_formatter.TestOutputFormatterErrorHandling.test_circular_reference_in_content)
GIVEN content with circular references
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1670, in test_circular_reference_in_content
    result = self.formatter.format_output(circular_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 188, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_large_content_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_large_content_handling)
GIVEN extremely large content object
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1692, in test_large_content_handling
    result = self.formatter.format_output(large_content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 188, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_resource_dependency_missing (test_output_formatter.TestOutputFormatterErrorHandling.test_resource_dependency_missing)
GIVEN OutputFormatter with missing resources
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1642, in test_resource_dependency_missing
    "logger": self.mock_logger,
              ^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterErrorHandling' object has no attribute 'mock_logger'

======================================================================
ERROR: test_init_missing_logger_in_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_missing_logger_in_resources)
GIVEN resources dict missing 'logger' key
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 336, in test_init_missing_logger_in_resources
    formatter = OutputFormatter(resources=resources_without_logger, configs=self.mock_configs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 68, in __init__
    self._logger: Logger = self.resources["logger"]
                           ~~~~~~~~~~~~~~^^^^^^^^^^
KeyError: 'logger'

======================================================================
ERROR: test_end_to_end_formatting_workflow (test_output_formatter.TestOutputFormatterIntegration.test_end_to_end_formatting_workflow)
GIVEN complete setup with OutputFormatter, Content, and output path
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1407, in test_end_to_end_formatting_workflow
    self.mock_formatted_output_instance.write_to_file = Mock(return_value=True)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513504'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1450, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 188, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513648'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1450, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 188, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='139777554513552'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1450, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 188, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_integration_with_custom_formatter (test_output_formatter.TestOutputFormatterIntegration.test_integration_with_custom_formatter)
GIVEN an OutputFormatter with a custom registered format
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1475, in test_integration_with_custom_formatter
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_instance'

======================================================================
FAIL: test_format_output_with_default_format (test_output_formatter.TestFormatOutput.test_format_output_with_default_format)
GIVEN an OutputFormatter with default_format='txt'
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 919, in test_format_output_with_default_format
    self.assertEqual(result, self.formatter._formatted_output)
AssertionError: <MagicMock name='mock()' id='139777557758272'> != <MagicMock spec='FormattedOutput' id='139777558003680'>

======================================================================
FAIL: test_format_output_with_invalid_format (test_output_formatter.TestFormatOutput.test_format_output_with_invalid_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 953, in test_format_output_with_invalid_format
    with self.assertRaises(ValueError) as context:
AssertionError: ValueError not raised

======================================================================
FAIL: test_format_as_json_with_complex_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_complex_content)
GIVEN a Content object with nested data structures
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 651, in test_format_as_json_with_complex_content
    self.assertIn("nested", parsed["metadata"])
AssertionError: 'nested' not found in {'title': 'Test Document', 'author': 'Test Author', 'created_at': '2023-01-01T12:00:00', 'tags': ['test', 'sample'], 'word_count': 6}

======================================================================
FAIL: test_format_as_json_with_simple_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_simple_content)
GIVEN a Content object with basic attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 615, in test_format_as_json_with_simple_content
    self.assertEqual(parsed["text"], "Hello World")
AssertionError: 'Sample content text for testing' != 'Hello World'
- Sample content text for testing
+ Hello World


======================================================================
FAIL: test_format_as_markdown_with_simple_content (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_simple_content)
GIVEN a Content object with plain text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 768, in test_format_as_markdown_with_simple_content
    self.assertIn("This is plain text content.", result)
AssertionError: 'This is plain text content.' not found in "# Content from test_document.txt\n\n## Metadata\n\n- **title**: Test Document\n- **author**: Test Author\n- **created_at**: 2023-01-01T12:00:00\n- **tags**: ['test', 'sample']\n- **word_count**: 6\n\n## Sections\n\n### Introduction\n\nIntro content\n\n### Body\n\nMain body content\n\n## Content\n\nSample content text for testing"

======================================================================
FAIL: test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1629, in test_missing_content_attributes
    with self.assertRaises((AttributeError, TypeError)):
AssertionError: (<class 'AttributeError'>, <class 'TypeError'>) not raised

======================================================================
FAIL: test_formatted_output_creation (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_creation)
GIVEN an OutputFormatter with valid resources including FormattedOutput class
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1367, in test_formatted_output_creation
    self.assertEqual(result, self.mock_resources['formatted_output'])
AssertionError: <MagicMock name='mock()' id='139777554373360'> != <MagicMock spec='FormattedOutput' id='139777554424000'>

======================================================================
FAIL: test_formatted_output_metadata_handling (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_metadata_handling)
GIVEN an OutputFormatter and Content with metadata
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1386, in test_formatted_output_metadata_handling
    self.assertEqual(result, self.mock_resources['formatted_output'])
AssertionError: <MagicMock name='mock()' id='139777554092048'> != <MagicMock spec='FormattedOutput' id='139777554375376'>

----------------------------------------------------------------------
Ran 58 tests in 0.364s

FAILED (failures=8, errors=20)
