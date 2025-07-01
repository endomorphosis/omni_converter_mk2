# Test Results
Return Code: 1
## Standard Output
Configuration loaded from /home/kylerose1946/omni_converter_mk2/configs.yaml
✓ Dependency 'tqdm' loaded successfully.
✓ Dependency 'yaml' loaded successfully.
✓ Dependency 'psutil' loaded successfully.
✓ Dependency 'pydantic' loaded successfully.

## Standard Error
2025-06-30 18:16:19,123 - logger - WARNING - processor_factory.py:219 - Source processor 'docx_processor' does not have method 'extract_images'. Skipping...
test_available_formats_after_multiple_registrations (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_after_multiple_registrations)
GIVEN an OutputFormatter ... ok
test_available_formats_consistency_with_output_formats (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_consistency_with_output_formats)
GIVEN an OutputFormatter ... ok
test_available_formats_includes_defaults (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_includes_defaults)
GIVEN a newly initialized OutputFormatter ... FAIL
test_available_formats_is_immutable (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_is_immutable)
GIVEN an OutputFormatter ... ok
test_available_formats_returns_list (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_returns_list)
GIVEN an OutputFormatter ... ok
test_available_formats_updated_after_registration (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_updated_after_registration)
GIVEN an OutputFormatter ... ok
test_register_default_formatters_called_during_init (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_called_during_init)
GIVEN OutputFormatter class ... FAIL
test_register_default_formatters_creates_json_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_json_formatter)
GIVEN an OutputFormatter instance ... ok
test_register_default_formatters_creates_markdown_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_markdown_formatter)
GIVEN an OutputFormatter instance ... FAIL
test_register_default_formatters_creates_txt_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_txt_formatter)
GIVEN an OutputFormatter instance ... ok
test_format_output_with_all_parameters (test_output_formatter.TestFormatOutput.test_format_output_with_all_parameters)
GIVEN an OutputFormatter ... ERROR
test_format_output_with_default_format (test_output_formatter.TestFormatOutput.test_format_output_with_default_format)
GIVEN an OutputFormatter with default_format='txt' ... ERROR
test_format_output_with_invalid_format (test_output_formatter.TestFormatOutput.test_format_output_with_invalid_format)
GIVEN an OutputFormatter ... ERROR
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
GIVEN a Content object with nested data structures ... ERROR
test_format_as_json_with_datetime_attributes (test_output_formatter.TestJsonFormatter.test_format_as_json_with_datetime_attributes)
GIVEN a Content object containing datetime objects ... ERROR
test_format_as_json_with_non_serializable_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_non_serializable_content)
GIVEN a Content object with non-JSON-serializable attributes ... ERROR
test_format_as_json_with_simple_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_simple_content)
GIVEN a Content object with basic attributes ... ERROR
test_format_as_markdown_escaping_special_characters (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_escaping_special_characters)
GIVEN a Content object with Markdown special characters (*, _, #, etc.) ... ERROR
test_format_as_markdown_with_lists_and_formatting (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_lists_and_formatting)
GIVEN a Content object containing lists, bold, italic text ... ERROR
test_format_as_markdown_with_metadata (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_metadata)
GIVEN a Content object with metadata (title, author, date, etc.) ... ERROR
test_format_as_markdown_with_sections (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_sections)
GIVEN a Content object with multiple sections/chapters ... ERROR
test_format_as_markdown_with_simple_content (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_simple_content)
GIVEN a Content object with plain text ... ERROR
test_circular_reference_in_content (test_output_formatter.TestOutputFormatterErrorHandling.test_circular_reference_in_content)
GIVEN content with circular references ... ERROR
test_concurrent_format_registration (test_output_formatter.TestOutputFormatterErrorHandling.test_concurrent_format_registration)
GIVEN an OutputFormatter used by multiple threads ... ok
test_formatter_function_raises_exception (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_function_raises_exception)
GIVEN a formatter function that raises an exception ... ok
test_formatter_returns_non_string (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_returns_non_string)
GIVEN a formatter that returns non-string content ... ERROR
test_invalid_content_type_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_invalid_content_type_handling)
GIVEN various invalid content types (string, dict, list, etc.) ... ok
test_large_content_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_large_content_handling)
GIVEN extremely large content object ... ERROR
test_malformed_formatter_function (test_output_formatter.TestOutputFormatterErrorHandling.test_malformed_formatter_function)
GIVEN a formatter function with incorrect signature ... ERROR
test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes ... FAIL
test_resource_dependency_missing (test_output_formatter.TestOutputFormatterErrorHandling.test_resource_dependency_missing)
GIVEN OutputFormatter with missing resources ... ok
test_init_missing_logger_in_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_missing_logger_in_resources)
GIVEN resources dict missing 'logger' key ... ERROR
test_init_state_after_successful_initialization (test_output_formatter.TestOutputFormatterInitialization.test_init_state_after_successful_initialization)
GIVEN valid resources and configs ... FAIL
test_init_with_none_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_configs)
GIVEN configs=None ... ERROR
test_init_with_none_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_resources)
GIVEN resources=None ... ERROR
test_init_with_valid_resources_and_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_valid_resources_and_configs)
GIVEN valid resources dict containing: ... FAIL
test_configs_integration (test_output_formatter.TestOutputFormatterIntegration.test_configs_integration)
GIVEN an OutputFormatter with configuration object ... ERROR
test_end_to_end_formatting_workflow (test_output_formatter.TestOutputFormatterIntegration.test_end_to_end_formatting_workflow)
GIVEN complete setup with OutputFormatter, Content, and output path ... ERROR
test_formatted_output_creation (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_creation)
GIVEN an OutputFormatter with valid resources including FormattedOutput class ... ERROR
test_formatted_output_metadata_handling (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_metadata_handling)
GIVEN an OutputFormatter and Content with metadata ... ERROR
test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types)
GIVEN an OutputFormatter ... 
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121717932000'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121717931904'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121718358432'>)
GIVEN an OutputFormatter ... ERROR
test_integration_with_custom_formatter (test_output_formatter.TestOutputFormatterIntegration.test_integration_with_custom_formatter)
GIVEN an OutputFormatter with a custom registered format ... ERROR
test_resource_dependency_injection (test_output_formatter.TestOutputFormatterIntegration.test_resource_dependency_injection)
GIVEN an OutputFormatter with injected resources ... ERROR
test_register_format_case_sensitivity (test_output_formatter.TestRegisterFormat.test_register_format_case_sensitivity)
GIVEN an OutputFormatter ... ok
test_register_format_updates_available_formats (test_output_formatter.TestRegisterFormat.test_register_format_updates_available_formats)
GIVEN an OutputFormatter with default formats ... ok
test_register_format_with_duplicate_name (test_output_formatter.TestRegisterFormat.test_register_format_with_duplicate_name)
GIVEN an OutputFormatter with existing 'txt' format ... ok
test_register_format_with_invalid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_invalid_formatter)
GIVEN an OutputFormatter ... FAIL
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
GIVEN a Content object with text=None ... FAIL
test_format_as_txt_with_simple_content (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_simple_content)
GIVEN a Content object with text="Hello World" ... ok
test_format_as_txt_with_special_characters (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_special_characters)
GIVEN a Content object with text containing special characters (tabs, unicode, etc.) ... ok

======================================================================
ERROR: test_format_output_with_all_parameters (test_output_formatter.TestFormatOutput.test_format_output_with_all_parameters)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1053, in test_format_output_with_all_parameters
    result = self.formatter.format_output(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 194, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <Mock name='mock.get_config_value()' id='140121718837504'>

======================================================================
ERROR: test_format_output_with_default_format (test_output_formatter.TestFormatOutput.test_format_output_with_default_format)
GIVEN an OutputFormatter with default_format='txt'
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 956, in test_format_output_with_default_format
    result = self.formatter.format_output(self.mock_content, format=None)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 194, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <Mock name='mock.get_config_value()' id='140121718839856'>

======================================================================
ERROR: test_format_output_with_invalid_format (test_output_formatter.TestFormatOutput.test_format_output_with_invalid_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 994, in test_format_output_with_invalid_format
    self.formatter.format_output(self.mock_content, format='invalid_format')
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 194, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <Mock name='mock.get_config_value()' id='140121718843360'>

======================================================================
ERROR: test_format_output_with_options (test_output_formatter.TestFormatOutput.test_format_output_with_options)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1012, in test_format_output_with_options
    result = self.formatter.format_output(self.mock_content, format='json', options=options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 195, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
ERROR: test_format_output_with_output_path (test_output_formatter.TestFormatOutput.test_format_output_with_output_path)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1030, in test_format_output_with_output_path
    result = self.formatter.format_output(self.mock_content, output_path=output_path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 194, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <Mock name='mock.get_config_value()' id='140121720031424'>

======================================================================
ERROR: test_format_output_with_specified_format (test_output_formatter.TestFormatOutput.test_format_output_with_specified_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 977, in test_format_output_with_specified_format
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 195, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
ERROR: test_format_as_json_encoding_special_characters (test_output_formatter.TestJsonFormatter.test_format_as_json_encoding_special_characters)
GIVEN a Content object with special characters (quotes, backslashes, unicode)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 746, in test_format_as_json_encoding_special_characters
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
ERROR: test_format_as_json_with_complex_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_complex_content)
GIVEN a Content object with nested data structures
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 662, in test_format_as_json_with_complex_content
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 692, in test_format_as_json_with_datetime_attributes
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 719, in test_format_as_json_with_non_serializable_content
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
ERROR: test_format_as_json_with_simple_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_simple_content)
GIVEN a Content object with basic attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 626, in test_format_as_json_with_simple_content
    result = self.formatter._format_as_json(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 111, in _format_as_json
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 903, in test_format_as_markdown_escaping_special_characters
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 124, in _format_as_markdown
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 878, in test_format_as_markdown_with_lists_and_formatting
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 124, in _format_as_markdown
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 820, in test_format_as_markdown_with_metadata
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 124, in _format_as_markdown
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 853, in test_format_as_markdown_with_sections
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 124, in _format_as_markdown
    md = f"# Content from {os.path.basename(content.source_path)}\n\n"
                                            ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_format_as_markdown_with_simple_content (test_output_formatter.TestMarkdownFormatter.test_format_as_markdown_with_simple_content)
GIVEN a Content object with plain text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 791, in test_format_as_markdown_with_simple_content
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 124, in _format_as_markdown
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1775, in test_circular_reference_in_content
    result = self.formatter.format_output(circular_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatter_returns_non_string (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_returns_non_string)
GIVEN a formatter that returns non-string content
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1714, in test_formatter_returns_non_string
    result = self.formatter.format_output(self.mock_content, format='non_string')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1797, in test_large_content_handling
    result = self.formatter.format_output(large_content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_malformed_formatter_function (test_output_formatter.TestOutputFormatterErrorHandling.test_malformed_formatter_function)
GIVEN a formatter function with incorrect signature
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1695, in test_malformed_formatter_function
    self.formatter.format_output(self.mock_content, format='bad_signature')
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_init_missing_logger_in_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_missing_logger_in_resources)
GIVEN resources dict missing 'logger' key
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 352, in test_init_missing_logger_in_resources
    formatter = OutputFormatter(resources=resources_without_logger, configs=self.mock_configs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 64, in __init__
    self._logger: Logger = self.resources["logger"]
                           ~~~~~~~~~~~~~~^^^^^^^^^^
KeyError: 'logger'

======================================================================
ERROR: test_init_with_none_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_configs)
GIVEN configs=None
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 329, in test_init_with_none_configs
    formatter = OutputFormatter(resources=self.valid_resources, configs=None)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 67, in __init__
    self.default_format = self.configs.get_config_value('output.default_format', 'txt')
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'get_config_value'

======================================================================
ERROR: test_init_with_none_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_resources)
GIVEN resources=None
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 312, in test_init_with_none_resources
    formatter = OutputFormatter(resources=None, configs=self.mock_configs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 62, in __init__
    self._normalized_content = self.resources["normalized_content"]
                               ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable

======================================================================
ERROR: test_configs_integration (test_output_formatter.TestOutputFormatterIntegration.test_configs_integration)
GIVEN an OutputFormatter with configuration object
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1567, in test_configs_integration
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_end_to_end_formatting_workflow (test_output_formatter.TestOutputFormatterIntegration.test_end_to_end_formatting_workflow)
GIVEN complete setup with OutputFormatter, Content, and output path
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1472, in test_end_to_end_formatting_workflow
    result = self.formatter.format_output(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatted_output_creation (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_creation)
GIVEN an OutputFormatter with valid resources including FormattedOutput class
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1426, in test_formatted_output_creation
    result = self.formatter.format_output(self.mock_content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatted_output_metadata_handling (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_metadata_handling)
GIVEN an OutputFormatter and Content with metadata
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1445, in test_formatted_output_metadata_handling
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121717932000'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1512, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121717931904'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1512, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140121718358432'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1512, in test_formatting_with_different_content_types
    result = self.formatter.format_output(content, format='txt')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1534, in test_integration_with_custom_formatter
    result = self.formatter.format_output(self.mock_content, format='custom_test')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
ERROR: test_resource_dependency_injection (test_output_formatter.TestOutputFormatterIntegration.test_resource_dependency_injection)
GIVEN an OutputFormatter with injected resources
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1550, in test_resource_dependency_injection
    result = self.formatter.format_output(self.mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 182, in format_output
    self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
                                                ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'source_path'

======================================================================
FAIL: test_available_formats_includes_defaults (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_includes_defaults)
GIVEN a newly initialized OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1289, in test_available_formats_includes_defaults
    self.assertTrue(expected_defaults.issubset(result_set))
AssertionError: False is not true

======================================================================
FAIL: test_register_default_formatters_called_during_init (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_called_during_init)
GIVEN OutputFormatter class
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 1387, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 475, in test_register_default_formatters_called_during_init
    self.assertEqual(set(formatter_real.output_formats.keys()), expected_formats)
AssertionError: Items in the second set but not the first:
'json'
'txt'
'markdown'

======================================================================
FAIL: test_register_default_formatters_creates_markdown_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_markdown_formatter)
GIVEN an OutputFormatter instance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 450, in test_register_default_formatters_creates_markdown_formatter
    self.assertIn('markdown', formatter.output_formats)
AssertionError: 'markdown' not found in {'txt': <bound method OutputFormatter._format_as_txt of <core.output_formatter._output_formatter.OutputFormatter object at 0x7f70a15bf2f0>>, 'json': <bound method OutputFormatter._format_as_json of <core.output_formatter._output_formatter.OutputFormatter object at 0x7f70a15bf2f0>>, 'md': <bound method OutputFormatter._format_as_markdown of <core.output_formatter._output_formatter.OutputFormatter object at 0x7f70a15bf2f0>>}

======================================================================
FAIL: test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1734, in test_missing_content_attributes
    with self.assertRaises((AttributeError, TypeError)):
AssertionError: (<class 'AttributeError'>, <class 'TypeError'>) not raised

======================================================================
FAIL: test_init_state_after_successful_initialization (test_output_formatter.TestOutputFormatterInitialization.test_init_state_after_successful_initialization)
GIVEN valid resources and configs
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 375, in test_init_state_after_successful_initialization
    self.assertEqual(set(formatter.output_formats.keys()), expected_formats)
AssertionError: Items in the first set but not the second:
'md'
Items in the second set but not the first:
'markdown'

======================================================================
FAIL: test_init_with_valid_resources_and_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_valid_resources_and_configs)
GIVEN valid resources dict containing:
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 292, in test_init_with_valid_resources_and_configs
    self.assertEqual(formatter.default_format, 'txt')
AssertionError: <Mock name='mock.get_config_value()' id='140121717924416'> != 'txt'

======================================================================
FAIL: test_register_format_with_invalid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_invalid_formatter)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1153, in test_register_format_with_invalid_formatter
    with self.assertRaises((TypeError, ValueError)) as context:
AssertionError: (<class 'TypeError'>, <class 'ValueError'>) not raised

======================================================================
FAIL: test_format_as_txt_with_none_text_attribute (test_output_formatter.TestTxtFormatter.test_format_as_txt_with_none_text_attribute)
GIVEN a Content object with text=None
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 565, in test_format_as_txt_with_none_text_attribute
    self.assertIn(result, ["", "None", str(None)])
AssertionError: None not found in ['', 'None', 'None']

----------------------------------------------------------------------
Ran 60 tests in 0.257s

FAILED (failures=8, errors=32)
