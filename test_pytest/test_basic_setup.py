"""
Simple test to verify pytest setup is working.
"""
import pytest


@pytest.mark.unit
def test_pytest_setup():
    """Verify pytest is working correctly."""
    assert True


@pytest.mark.unit
def test_fixtures_work(temp_dir, mock_logger):
    """Verify fixtures are working."""
    assert temp_dir is not None
    assert mock_logger is not None
    
    # Test temp_dir fixture
    import os
    assert os.path.exists(temp_dir)
    assert os.path.isdir(temp_dir)
    
    # Test mock_logger fixture
    mock_logger.info("Test message")
    mock_logger.info.assert_called_once_with("Test message")


@pytest.mark.unit 
@pytest.mark.parametrize("input_value,expected", [
    (1, 2), 
    (2, 4), 
    (3, 6)
])
def test_parametrize_example(input_value, expected):
    """Test parametrize decorator works."""
    assert input_value * 2 == expected