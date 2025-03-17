# Omni-Converter Examples

This directory contains examples demonstrating how to use the Omni-Converter.

## Python API Examples

The [python_api_example.py](python_api_example.py) script demonstrates how to use the Omni-Converter Python API for:

1. **Basic Usage**: Converting a single file to text
2. **Batch Processing**: Converting multiple files or directories
3. **Configuration Management**: Getting and setting configuration options
4. **Interface Factory**: Using the InterfaceFactory to create API instances

To run the example:

```bash
# From the project root directory
python examples/python_api_example.py
```

## Programmatic Usage

### Single File Conversion

```python
from interfaces.python_api import api

# Convert a file to text
result = api.convert_file("/path/to/file.pdf")

# Check if conversion was successful
if result.success:
    print(f"Text content: {result.content}")
    print(f"Metadata: {result.metadata}")
else:
    print(f"Conversion failed: {result.errors}")
```

### Batch Processing

```python
from interfaces.python_api import api

# Process a directory of files
result = api.convert_batch(
    "/path/to/directory", 
    output_dir="/path/to/output",
    options={
        "format": "txt",
        "parallel": True,
        "max_workers": 4
    }
)

# Print summary
print(f"Total files: {result.total_files}")
print(f"Successful: {result.successful_files}")
print(f"Failed: {result.failed_files}")

# Get list of successful and failed files
successful_files = result.get_successful_files()
failed_files = result.get_failed_files()
```

### Configuration Management

```python
from interfaces.python_api import api

# Get supported formats
formats = api.get_supported_formats()
print(formats)

# Get current configuration
config = api.get_config()
print(config)

# Update configuration
api.set_config({
    'output.format': 'json',
    'processing.normalize_text': False,
    'resources.memory_limit_gb': 4
})
```

### Using the Interface Factory

```python
from interfaces.interface_factory import interface_factory

# Create a new API instance
api = interface_factory.create_api()

# Get the configuration manager
config_manager = interface_factory.get_config_manager()

# Set configuration
config_manager.set_config_value('output.format', 'json')

# Use the API
result = api.convert_file("/path/to/file.pdf")
```