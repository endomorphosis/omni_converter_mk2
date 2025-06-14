"""
Python API usage examples for the Omni-Converter.

This module demonstrates how to use the Omni-Converter Python API
for various common tasks such as converting files and managing configuration.
"""

import os
import sys
from pprint import pprint

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Omni-Converter Python API
from interfaces._python_api import api
from interfaces.factory import interface_factory


def basic_usage():
    """Demonstrate basic API usage for converting a single file."""
    print("\n=== Basic Usage ===")
    
    # Get the example test file path
    test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_files/test.svg'))
    
    # Check if the file exists
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    print(f"Converting file: {test_file}")
    
    try:
        # Convert the file without writing output to disk
        # Use txt format since it's always supported
        result = api.convert_file(test_file, options={"format": "txt"})
        
        # Display the result
        print(f"Conversion {'succeeded' if result.success else 'failed'}")
        print(f"Format detected: {result.format}")
        print(f"Errors: {result.errors}")
        print("Metadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")
        
        # Access the extracted text
        if hasattr(result, 'content') and result.success:
            print(f"Extracted text (first 100 chars): {result.content[:100]}...")
    except Exception as e:
        print(f"Error occurred during conversion: {e}")


def batch_processing():
    """Demonstrate batch processing of multiple files."""
    print("\n=== Batch Processing ===")
    
    # Get the example test directory path
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_files'))
    
    # Check if the directory exists
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return
    
    print(f"Processing directory: {test_dir}")
    
    try:
        # Configure batch options
        options = {
            "format": "txt",
            "parallel": False,  # Use sequential mode for simplicity
            "continue_on_error": True
        }
        
        # Process the directory
        batch_result = api.convert_batch(test_dir, options=options)
        
        # Display the results
        print("Batch Processing Results:")
        print(f"Total files: {batch_result.total_files}")
        print(f"Successful: {batch_result.successful_files}")
        print(f"Failed: {batch_result.failed_files}")
        
        if batch_result.successful_files > 0:
            print("\nSuccessful Files:")
            for file_path in batch_result.get_successful_files()[:5]:  # Show up to 5 files
                print(f"  - {os.path.basename(file_path)}")
        
        if batch_result.failed_files > 0:
            print("\nFailed Files:")
            for file_path in batch_result.get_failed_files()[:5]:  # Show up to 5 files
                print(f"  - {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error occurred during batch processing: {e}")


def working_with_config():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management ===")
    
    # Get supported formats
    supported_formats = api.supported_formats
    print("Supported Formats:")
    for category, formats in supported_formats.items():
        print(f"  {category.capitalize()}: {', '.join(formats)}")
    
    # Get current configuration
    current_config = api.get_config()
    print("\nCurrent Configuration (excerpt):")
    print("  Output Format:", current_config['output']['format'])
    print("  Normalize Text:", current_config['processing']['normalize_text'])
    print("  Resource Limits:")
    print(f"    Memory: {current_config['resources']['memory_limit_gb']} GB")
    print(f"    CPU: {current_config['resources']['cpu_limit_percent']}%")
    
    # Modify configuration
    print("\nModifying configuration...")
    api.set_config({
        'output.format': 'json',
        'processing.normalize_text': False,
        'resources.memory_limit_gb': 4
    })
    
    # Verify changes
    updated_config = api.get_config()
    print("\nUpdated Configuration:")
    print("  Output Format:", updated_config['output']['format'])
    print("  Normalize Text:", updated_config['processing']['normalize_text'])
    print("  Memory Limit:", updated_config['resources']['memory_limit_gb'], "GB")
    
    # Reset changes (optional in a real application)
    api.set_config({
        'output.format': 'txt',
        'processing.normalize_text': True,
        'resources.memory_limit_gb': 6
    })


def using_interface_factory():
    """Demonstrate using the InterfaceFactory."""
    print("\n=== Using Interface Factory ===")
    
    # Create a new API instance with custom configuration
    custom_api = interface_factory.create_api()
    
    # Get the configuration manager
    configs = interface_factory.configs
    
    # Set a custom configuration value
    configs.set_config_value('processing.quality_threshold', 0.8)
    
    # Use the custom API
    formats = custom_api.supported_formats
    print(f"API from factory supports {sum(len(f) for f in formats.values())} formats")
    
    # Try to create a CLI (will raise NotImplementedError, but handle it gracefully)
    try:
        interface_factory.create_cli()
    except NotImplementedError as e:
        print(f"CLI creation via factory: {e}")


def main():
    """Run all example functions."""
    print("Omni-Converter Python API Examples")
    print("==================================")
    
    try:
        basic_usage()
    except Exception as e:
        print(f"Error in basic_usage: {e}")
    
    try:
        batch_processing()
    except Exception as e:
        print(f"Error in batch_processing: {e}")
    
    try:
        working_with_config()
    except Exception as e:
        print(f"Error in working_with_config: {e}")
    
    try:
        using_interface_factory()
    except Exception as e:
        print(f"Error in using_interface_factory: {e}")


if __name__ == "__main__":
    main()