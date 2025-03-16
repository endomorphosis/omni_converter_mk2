# Omni-Converter Test Suite

This directory contains the test suite for the Omni-Converter project. The tests are designed to verify that the converter meets the requirements specified in the [TESTING.md](TESTING.md) document.

## Test Categories

1. **Format Support Coverage** - Tests if the required number of formats are supported in each category
2. **Processing Success Rate** - Tests the success rate of processing valid files
3. **Resource Utilization** - Tests memory and CPU usage during file processing
4. **Processing Speed** - Tests processing speed for different file types
5. **Error Handling** - Tests how well the system handles errors during processing
6. **Security Effectiveness** - Tests how well the system prevents code execution from malicious inputs
7. **Text Quality** - Tests the quality of text extraction across different file types

## Running the Tests

You can run individual tests with:

```bash
python -m unittest tests.test_module_name
```

Or run all tests with:

```bash
python tests/run_all_tests.py
```

This will execute all tests and generate a summary report. The test results are saved to JSON files in the `tests/collected_results` directory.

## Test Results

Test results are stored in the `collected_results` directory as JSON files. Each test generates its own JSON file with detailed results, and a summary file is also generated.

## Test Documentation

Comprehensive documentation for the test suite is available in the `docs/tests` directory. You can view the documentation starting from the [index.md](../docs/tests/index.md) file.

## Dependencies

The test suite requires the following dependencies:
- Python 3.12+
- psutil (for resource monitoring)
- pandas, numpy, pydantic, duckdb (for various test utilities)

These dependencies are installed by the [install.sh](../install.sh) script in the project root.