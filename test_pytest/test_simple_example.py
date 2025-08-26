"""
Simple demonstration of pytest conversion patterns.
This file shows how unittest tests are converted to pytest format.
"""
import pytest


class TestSimpleExample:
    """Example class showing pytest test patterns."""

    def test_basic_assertion(self):
        """Test basic assertions using pytest."""
        # Pytest uses plain assert statements
        assert 1 + 1 == 2
        assert "hello" in "hello world"
        assert len([1, 2, 3]) == 3

    def test_exception_handling(self):
        """Test exception handling with pytest.raises."""
        # Using pytest.raises instead of unittest's assertRaises
        with pytest.raises(ValueError):
            int("not_a_number")
        
        with pytest.raises(ZeroDivisionError):
            1 / 0

    @pytest.mark.parametrize("input_val,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
        (-1, -2),
    ])
    def test_parametrized(self, input_val, expected):
        """Test parametrized tests using pytest.mark.parametrize."""
        # This replaces unittest's subTest pattern
        assert input_val * 2 == expected

    def test_approximate_equality(self):
        """Test approximate equality for floats."""
        # Pytest provides pytest.approx for float comparisons
        assert 0.1 + 0.2 == pytest.approx(0.3)
        assert 10 == pytest.approx(10.1, abs=0.2)


# Fixtures replace setUp/tearDown methods
@pytest.fixture
def sample_data():
    """Fixture providing sample data for tests."""
    # This replaces setUp method data creation
    data = {"name": "test", "values": [1, 2, 3]}
    yield data  # This is like the test execution point
    # Code after yield is like tearDown


def test_using_fixture(sample_data):
    """Test using a fixture (replaces setUp/tearDown pattern)."""
    assert sample_data["name"] == "test"
    assert len(sample_data["values"]) == 3


class TestWithClassFixture:
    """Example using class-scoped fixture."""
    
    @pytest.fixture(autouse=True)
    def setup_class_data(self):
        """Auto-use fixture that runs for all tests in this class."""
        self.class_data = "shared_data"
    
    def test_class_data_access(self):
        """Test accessing class-level fixture data."""
        assert self.class_data == "shared_data"


@pytest.mark.unit
def test_with_markers():
    """Test showing pytest markers (similar to unittest categories)."""
    assert True


@pytest.mark.slow
def test_slow_operation():
    """Test marked as slow (can be skipped with -m 'not slow')."""
    # Simulate slow operation
    import time
    time.sleep(0.1)
    assert True