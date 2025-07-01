# Test Results
Return Code: 1
## Standard Output
Configuration loaded from /home/kylerose1946/omni_converter_mk2/configs.yaml
✓ Dependency 'tqdm' loaded successfully.
✓ Dependency 'yaml' loaded successfully.
✓ Dependency 'psutil' loaded successfully.
✓ Dependency 'pydantic' loaded successfully.

## Standard Error
2025-06-30 19:29:19,543 - logger - WARNING - processor_factory.py:219 - Source processor 'docx_processor' does not have method 'extract_images'. Skipping...
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
GIVEN an OutputFormatter used by multiple threads ... ERROR
test_formatter_function_raises_exception (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_function_raises_exception)
GIVEN a formatter function that raises an exception ... ERROR
test_formatter_returns_non_string (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_returns_non_string)
GIVEN a formatter that returns non-string content ... ERROR
test_invalid_content_type_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_invalid_content_type_handling)
GIVEN various invalid content types (string, dict, list, etc.) ... ERROR
test_large_content_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_large_content_handling)
GIVEN extremely large content object ... ERROR
test_malformed_formatter_function (test_output_formatter.TestOutputFormatterErrorHandling.test_malformed_formatter_function)
GIVEN a formatter function with incorrect signature ... ERROR
test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes ... ERROR
test_resource_dependency_missing (test_output_formatter.TestOutputFormatterErrorHandling.test_resource_dependency_missing)
GIVEN OutputFormatter with missing resources ... ERROR
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
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163472'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163616'>)
GIVEN an OutputFormatter ... ERROR
  test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163568'>)
GIVEN an OutputFormatter ... ERROR
test_integration_with_custom_formatter (test_output_formatter.TestOutputFormatterIntegration.test_integration_with_custom_formatter)
GIVEN an OutputFormatter with a custom registered format ... ERROR
test_resource_dependency_injection (test_output_formatter.TestOutputFormatterIntegration.test_resource_dependency_injection)
GIVEN an OutputFormatter with injected resources ... ERROR
test_register_format_case_sensitivity (test_output_formatter.TestRegisterFormat.test_register_format_case_sensitivity)
GIVEN an OutputFormatter ... ERROR
test_register_format_updates_available_formats (test_output_formatter.TestRegisterFormat.test_register_format_updates_available_formats)
GIVEN an OutputFormatter with default formats ... ERROR
test_register_format_with_duplicate_name (test_output_formatter.TestRegisterFormat.test_register_format_with_duplicate_name)
GIVEN an OutputFormatter with existing 'txt' format ... ERROR
test_register_format_with_invalid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_invalid_formatter)
GIVEN an OutputFormatter ... ERROR
test_register_format_with_lambda_function (test_output_formatter.TestRegisterFormat.test_register_format_with_lambda_function)
GIVEN an OutputFormatter ... ERROR
test_register_format_with_method_reference (test_output_formatter.TestRegisterFormat.test_register_format_with_method_reference)
GIVEN an OutputFormatter ... ERROR
test_register_format_with_valid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_valid_formatter)
GIVEN an OutputFormatter and a valid formatter function ... ERROR
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1023, in test_format_output_with_all_parameters
    result = self.formatter.format_output(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 200, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <MagicMock name='mock.__deepcopy__().output.default_format' id='140508392713888'>

======================================================================
ERROR: test_format_output_with_default_format (test_output_formatter.TestFormatOutput.test_format_output_with_default_format)
GIVEN an OutputFormatter with default_format='txt'
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 926, in test_format_output_with_default_format
    result = self.formatter.format_output(self.mock_content, format=None)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 200, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <MagicMock name='mock.__deepcopy__().output.default_format' id='140508394415136'>

======================================================================
ERROR: test_format_output_with_invalid_format (test_output_formatter.TestFormatOutput.test_format_output_with_invalid_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 964, in test_format_output_with_invalid_format
    self.formatter.format_output(self.mock_content, format='invalid_format')
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 200, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <MagicMock name='mock.__deepcopy__().output.default_format' id='140508393413168'>

======================================================================
ERROR: test_format_output_with_options (test_output_formatter.TestFormatOutput.test_format_output_with_options)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 982, in test_format_output_with_options
    result = self.formatter.format_output(self.mock_content, format='json', options=options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 201, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
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
TypeError: Object of type MagicMock is not JSON serializable

======================================================================
ERROR: test_format_output_with_output_path (test_output_formatter.TestFormatOutput.test_format_output_with_output_path)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1000, in test_format_output_with_output_path
    result = self.formatter.format_output(self.mock_content, output_path=output_path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 200, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <MagicMock name='mock.__deepcopy__().output.default_format' id='140508391685584'>

======================================================================
ERROR: test_format_output_with_specified_format (test_output_formatter.TestFormatOutput.test_format_output_with_specified_format)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 947, in test_format_output_with_specified_format
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 201, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
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
TypeError: Object of type MagicMock is not JSON serializable

======================================================================
ERROR: test_format_as_json_encoding_special_characters (test_output_formatter.TestJsonFormatter.test_format_as_json_encoding_special_characters)
GIVEN a Content object with special characters (quotes, backslashes, unicode)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 730, in test_format_as_json_encoding_special_characters
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
ERROR: test_format_as_json_with_complex_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_complex_content)
GIVEN a Content object with nested data structures
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 646, in test_format_as_json_with_complex_content
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 676, in test_format_as_json_with_datetime_attributes
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 703, in test_format_as_json_with_non_serializable_content
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
ERROR: test_format_as_json_with_simple_content (test_output_formatter.TestJsonFormatter.test_format_as_json_with_simple_content)
GIVEN a Content object with basic attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 610, in test_format_as_json_with_simple_content
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 886, in test_format_as_markdown_escaping_special_characters
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 861, in test_format_as_markdown_with_lists_and_formatting
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 803, in test_format_as_markdown_with_metadata
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 836, in test_format_as_markdown_with_sections
    result = self.formatter._format_as_markdown(mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 130, in _format_as_markdown
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 774, in test_format_as_markdown_with_simple_content
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_concurrent_format_registration (test_output_formatter.TestOutputFormatterErrorHandling.test_concurrent_format_registration)
GIVEN an OutputFormatter used by multiple threads
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_formatter_function_raises_exception (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_function_raises_exception)
GIVEN a formatter function that raises an exception
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_formatter_returns_non_string (test_output_formatter.TestOutputFormatterErrorHandling.test_formatter_returns_non_string)
GIVEN a formatter that returns non-string content
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_invalid_content_type_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_invalid_content_type_handling)
GIVEN various invalid content types (string, dict, list, etc.)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_large_content_handling (test_output_formatter.TestOutputFormatterErrorHandling.test_large_content_handling)
GIVEN extremely large content object
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_malformed_formatter_function (test_output_formatter.TestOutputFormatterErrorHandling.test_malformed_formatter_function)
GIVEN a formatter function with incorrect signature
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_missing_content_attributes (test_output_formatter.TestOutputFormatterErrorHandling.test_missing_content_attributes)
GIVEN content object missing expected attributes
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_resource_dependency_missing (test_output_formatter.TestOutputFormatterErrorHandling.test_resource_dependency_missing)
GIVEN OutputFormatter with missing resources
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1542, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_init_missing_logger_in_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_missing_logger_in_resources)
GIVEN resources dict missing 'logger' key
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 337, in test_init_missing_logger_in_resources
    formatter = OutputFormatter(resources=resources_without_logger, configs=self.mock_configs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 68, in __init__
    self._logger: Logger = self.resources["logger"]
                           ~~~~~~~~~~~~~~^^^^^^^^^^
KeyError: 'logger'

======================================================================
ERROR: test_init_with_none_configs (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_configs)
GIVEN configs=None
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 314, in test_init_with_none_configs
    formatter = OutputFormatter(resources=self.mock_resources, configs=None)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'output'

======================================================================
ERROR: test_init_with_none_resources (test_output_formatter.TestOutputFormatterInitialization.test_init_with_none_resources)
GIVEN resources=None
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 297, in test_init_with_none_resources
    formatter = OutputFormatter(resources=None, configs=self.mock_configs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 66, in __init__
    self._normalized_content = self.resources["normalized_content"]
                               ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable

======================================================================
ERROR: test_configs_integration (test_output_formatter.TestOutputFormatterIntegration.test_configs_integration)
GIVEN an OutputFormatter with configuration object
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1519, in test_configs_integration
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 201, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
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
TypeError: Object of type MagicMock is not JSON serializable

======================================================================
ERROR: test_end_to_end_formatting_workflow (test_output_formatter.TestOutputFormatterIntegration.test_end_to_end_formatting_workflow)
GIVEN complete setup with OutputFormatter, Content, and output path
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1421, in test_end_to_end_formatting_workflow
    self.mock_formatted_output_instance.write_to_file = Mock(return_value=True)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_formatted_output_creation (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_creation)
GIVEN an OutputFormatter with valid resources including FormattedOutput class
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1381, in test_formatted_output_creation
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_formatted_output_metadata_handling (test_output_formatter.TestOutputFormatterIntegration.test_formatted_output_metadata_handling)
GIVEN an OutputFormatter and Content with metadata
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1397, in test_formatted_output_metadata_handling
    result = self.formatter.format_output(self.mock_content, format='json')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 201, in format_output
    formatted_content = formatter(content)
                        ^^^^^^^^^^^^^^^^^^
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
TypeError: Object of type MagicMock is not JSON serializable

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163472'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1461, in test_formatting_with_different_content_types
    self.mock_formatted_output_class.reset_mock()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_class'. Did you mean: 'test_formatted_output_creation'?

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163616'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1461, in test_formatting_with_different_content_types
    self.mock_formatted_output_class.reset_mock()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_class'. Did you mean: 'test_formatted_output_creation'?

======================================================================
ERROR: test_formatting_with_different_content_types (test_output_formatter.TestOutputFormatterIntegration.test_formatting_with_different_content_types) (content=<Mock spec='Content' id='140508390163568'>)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1461, in test_formatting_with_different_content_types
    self.mock_formatted_output_class.reset_mock()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_class'. Did you mean: 'test_formatted_output_creation'?

======================================================================
ERROR: test_integration_with_custom_formatter (test_output_formatter.TestOutputFormatterIntegration.test_integration_with_custom_formatter)
GIVEN an OutputFormatter with a custom registered format
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1489, in test_integration_with_custom_formatter
    self.assertEqual(result, self.mock_formatted_output_instance)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'TestOutputFormatterIntegration' object has no attribute 'mock_formatted_output_instance'

======================================================================
ERROR: test_resource_dependency_injection (test_output_formatter.TestOutputFormatterIntegration.test_resource_dependency_injection)
GIVEN an OutputFormatter with injected resources
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1502, in test_resource_dependency_injection
    result = self.formatter.format_output(self.mock_content)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 200, in format_output
    formatter = self.output_formats[output_format]
                ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
KeyError: <MagicMock name='mock.__deepcopy__().output.default_format' id='140508388380640'>

======================================================================
ERROR: test_register_format_case_sensitivity (test_output_formatter.TestRegisterFormat.test_register_format_case_sensitivity)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_updates_available_formats (test_output_formatter.TestRegisterFormat.test_register_format_updates_available_formats)
GIVEN an OutputFormatter with default formats
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_with_duplicate_name (test_output_formatter.TestRegisterFormat.test_register_format_with_duplicate_name)
GIVEN an OutputFormatter with existing 'txt' format
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_with_invalid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_invalid_formatter)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_with_lambda_function (test_output_formatter.TestRegisterFormat.test_register_format_with_lambda_function)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_with_method_reference (test_output_formatter.TestRegisterFormat.test_register_format_with_method_reference)
GIVEN an OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
ERROR: test_register_format_with_valid_formatter (test_output_formatter.TestRegisterFormat.test_register_format_with_valid_formatter)
GIVEN an OutputFormatter and a valid formatter function
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1062, in setUp
    self.formatter = OutputFormatter(resources=self.mock_resources, configs=self.mock_configs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/omni_converter_mk2/core/output_formatter/_output_formatter.py", line 70, in __init__
    self.default_format = self.configs.output.default_format
                          ^^^^^^^^^^^^^^^^^^^
  File "/home/kylerose1946/.pyenv/versions/3.12.2/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'output'

======================================================================
FAIL: test_available_formats_includes_defaults (test_output_formatter.TestAvailableFormatsProperty.test_available_formats_includes_defaults)
GIVEN a newly initialized OutputFormatter
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 1256, in test_available_formats_includes_defaults
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 460, in test_register_default_formatters_called_during_init
    self.assertEqual(set(formatter_real.output_formats.keys()), expected_formats)
AssertionError: Items in the second set but not the first:
'json'
'markdown'
'txt'

======================================================================
FAIL: test_register_default_formatters_creates_markdown_formatter (test_output_formatter.TestDefaultFormattersRegistration.test_register_default_formatters_creates_markdown_formatter)
GIVEN an OutputFormatter instance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 435, in test_register_default_formatters_creates_markdown_formatter
    self.assertIn('markdown', formatter.output_formats)
AssertionError: 'markdown' not found in {'txt': <bound method OutputFormatter._format_as_txt of <core.output_formatter._output_formatter.OutputFormatter object at 0x7fcaa8d8b6b0>>, 'json': <bound method OutputFormatter._format_as_json of <core.output_formatter._output_formatter.OutputFormatter object at 0x7fcaa8d8b6b0>>, 'md': <bound method OutputFormatter._format_as_markdown of <core.output_formatter._output_formatter.OutputFormatter object at 0x7fcaa8d8b6b0>>}

======================================================================
FAIL: test_init_state_after_successful_initialization (test_output_formatter.TestOutputFormatterInitialization.test_init_state_after_successful_initialization)
GIVEN valid resources and configs
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 360, in test_init_state_after_successful_initialization
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
  File "/home/kylerose1946/omni_converter_mk2/tests/unit_tests/core_/output_formatter_/test_output_formatter.py", line 277, in test_init_with_valid_resources_and_configs
    self.assertEqual(formatter.default_format, 'txt')
AssertionError: <MagicMock name='mock.__deepcopy__().outp[35 chars]960'> != 'txt'

----------------------------------------------------------------------
Ran 60 tests in 0.414s

FAILED (failures=5, errors=44)
