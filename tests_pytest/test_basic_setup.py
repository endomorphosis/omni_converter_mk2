"""
Simple test to verify pytest setup is working.
"""
import pytest
import os


# Test Constants  
EXPECTED_MULTIPLICATION_FACTOR = 2


@pytest.mark.unit
class TestPytestSetup:
    """
    Tests for pytest framework setup verification.
    Function under test: pytest framework functionality
    """

    def test_when_pytest_runs_then_assertions_work(self):
        """
        GIVEN pytest test framework
        WHEN test assertion is executed
        THEN expect assertion passes without error
        """
        assert True, "Expected assertion to pass"


@pytest.mark.unit
class TestFixturesConfiguration:
    """
    Tests for pytest fixtures configuration verification.
    Functions under test: temp_dir and mock_logger fixtures
    """

    def test_when_temp_dir_fixture_used_then_returns_directory_path(self, temp_dir):
        """
        GIVEN temp_dir fixture
        WHEN fixture is injected into test
        THEN expect temp_dir is not None
        """
        assert temp_dir is not None, f"Expected temp_dir to be not None, got {temp_dir}"

    def test_when_temp_dir_fixture_used_then_directory_exists(self, temp_dir):
        """
        GIVEN temp_dir fixture
        WHEN fixture is injected into test
        THEN expect temp_dir path exists on filesystem
        """
        assert os.path.exists(temp_dir), f"Expected temp_dir {temp_dir} to exist"

    def test_when_temp_dir_fixture_used_then_path_is_directory(self, temp_dir):
        """
        GIVEN temp_dir fixture
        WHEN fixture is injected into test
        THEN expect temp_dir path is a directory
        """
        assert os.path.isdir(temp_dir), f"Expected {temp_dir} to be a directory"

    def test_when_mock_logger_fixture_used_then_returns_logger_instance(self, mock_logger):
        """
        GIVEN mock_logger fixture
        WHEN fixture is injected into test
        THEN expect mock_logger is not None
        """
        assert mock_logger is not None, f"Expected mock_logger to be not None, got {mock_logger}"

    def test_when_mock_logger_info_called_then_method_is_tracked(self, mock_logger):
        """
        GIVEN mock_logger fixture
        WHEN info method is called with test message
        THEN expect method call is tracked by mock
        """
        test_message = "Test message"
        mock_logger.info(test_message)
        
        mock_logger.info.assert_called_once_with(test_message)


@pytest.mark.unit 
@pytest.mark.parametrize("input_value,expected", [
    (1, 2), 
    (2, 4), 
    (3, 6)
])
def test_when_parametrize_used_then_multiplication_works(input_value, expected):
    """
    GIVEN parametrized input value and expected result
    WHEN input value is multiplied by expected factor
    THEN expect result equals expected value
    """
    result = input_value * EXPECTED_MULTIPLICATION_FACTOR
    
    assert result == expected, f"Expected {expected}, got {result}"