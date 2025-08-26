"""
Integration test for a simple vertical slice: TXT file processing.
This test represents the DESIRED behavior, not current behavior.

This is a pytest conversion of the original unittest file.
"""
import tempfile
import os
import pytest
from pathlib import Path


@pytest.fixture
def test_txt_file():
    """Fixture that creates a temporary test file and cleans it up."""
    test_content = "Hello, this is a test file."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
        tf.write(test_content)
        test_file_path = tf.name
    
    yield test_file_path, test_content
    
    # Cleanup
    if os.path.exists(test_file_path):
        os.unlink(test_file_path)


@pytest.fixture
def pipeline_test_file():
    """Fixture for pipeline testing with different content."""
    test_content = "Direct pipeline test."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
        tf.write(test_content)
        test_file_path = tf.name
    
    yield test_file_path, test_content
    
    # Cleanup
    if os.path.exists(test_file_path):
        os.unlink(test_file_path)


@pytest.mark.integration
def test_txt_file_processing_vertical_slice(test_txt_file):
    """Test that a simple TXT file can be processed end-to-end."""
    test_file_path, test_content = test_txt_file
    
    # Act - This is what SHOULD work
    from interfaces import make_cli
    cli = make_cli()
    
    # Simulate CLI processing a single file
    result: bool = cli.process_file(test_file_path)
    
    # Assert
    assert result is not None
    assert result is True


@pytest.mark.integration
def test_processing_pipeline_directly(pipeline_test_file):
    """Test the core processing pipeline without CLI."""
    test_file_path, test_content = pipeline_test_file
    
    # Act
    from core import make_processing_pipeline
    from core._processing_result import ProcessingResult
    pipeline = make_processing_pipeline()
    
    result: ProcessingResult = pipeline.process_file(test_file_path)
    print(f"Processing result: {result}")
    
    # Assert
    assert result.success is True
    print(f"Processing result: {result}")

    # Check if the output file was created
    output_file_path = result.output_path
    print(f"Output file path: {output_file_path}")
    assert Path(output_file_path).exists()

    # Check if the content matches
    with open(output_file_path, 'r') as output_file:
        output_content = output_file.read()
        print(f"Test Content: {test_content}\nOutput content: {output_content}")
        assert test_content in output_content

    # Cleanup output file if it exists
    if os.path.exists(output_file_path):
        os.unlink(output_file_path)