"""
Test suite for monitors/_error_monitor.py converted from unittest to pytest.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
from pathlib import Path
from logging import Logger
from typing import Optional, Any, Type
import threading
import time
import tempfile
import shutil
import os
import pathlib

# Skip tests if modules can't be imported
pytest_plugins = []
try:
    from configs import Configs
    from monitors._error_monitor import ErrorMonitor
    from monitors import make_error_monitor
except ImportError:
    pytest.skip("monitors module not available", allow_module_level=True)


@pytest.fixture
def mock_resources():
    """Mock resources for testing."""
    return {
        'logger': MagicMock(spec=Logger),
        'traceback': MagicMock(),
        'datetime': MagicMock(),
    }


@pytest.fixture
def mock_configs():
    """Mock configs for testing."""
    mock_configs = MagicMock(spec=Configs)
    mock_configs.processing = MagicMock()
    mock_configs.paths = MagicMock()
    mock_configs.processing.suppress_errors = False
    root_dir_return_value = Path("/test/root")
    if os.name == "nt":
        root_dir_spec = pathlib.WindowsPath
    else:
        root_dir_spec = pathlib.PosixPath
    mock_configs.paths.ROOT_DIR = MagicMock(spec=root_dir_spec, return_value=root_dir_return_value)
    return mock_configs


@pytest.mark.unit
class TestErrorMonitorInitialization:
    """Test ErrorMonitor initialization and configuration."""

    def test_init_with_valid_resources_and_configs(self, mock_resources, mock_configs):
        """
        GIVEN valid resources dict containing:
            - logger: A logger instance
            - traceback: The traceback module
            - datetime: The datetime module
        AND valid configs object with:
            - processing.suppress_errors attribute
            - paths.ROOT_DIR attribute
        WHEN ErrorMonitor is initialized
        THEN expect:
            - Instance created successfully
            - _logger is set from resources['logger']
            - _suppress_errors is set from configs.processing.suppress_errors
            - _root_dir is set from configs.paths.ROOT_DIR
            - _error_counters initialized as empty dict
            - _error_types initialized as empty set
            - traceback and datetime attributes are set from resources
        """
        monitor = ErrorMonitor(mock_resources, mock_configs)

        assert isinstance(monitor, ErrorMonitor)
        assert monitor._logger == mock_resources['logger']
        assert monitor._suppress_errors is False
        assert monitor._root_dir == Path("/test/root")
        assert monitor._error_counters == {}
        assert monitor._error_types == set()
        assert monitor.traceback == mock_resources['traceback']
        assert monitor.datetime == mock_resources['datetime']

    def test_init_missing_logger_in_resources(self, mock_configs):
        """
        GIVEN resources dict missing 'logger' key
        WHEN ErrorMonitor is initialized
        THEN expect KeyError to be raised
        """
        invalid_resources = {
            'traceback': MagicMock(),
            'datetime': MagicMock()
        }
        
        with pytest.raises(KeyError):
            ErrorMonitor(invalid_resources, mock_configs)

    def test_init_missing_traceback_in_resources(self, mock_configs):
        """
        GIVEN resources dict missing 'traceback' key
        WHEN ErrorMonitor is initialized
        THEN expect KeyError to be raised
        """
        invalid_resources = {
            'logger': MagicMock(spec=Logger),
            'datetime': MagicMock()
        }
        
        with pytest.raises(KeyError):
            ErrorMonitor(invalid_resources, mock_configs)

    def test_init_missing_datetime_in_resources(self, mock_configs):
        """
        GIVEN resources dict missing 'datetime' key
        WHEN ErrorMonitor is initialized
        THEN expect KeyError to be raised
        """
        invalid_resources = {
            'logger': MagicMock(spec=Logger),
            'traceback': MagicMock()
        }
        
        with pytest.raises(KeyError):
            ErrorMonitor(invalid_resources, mock_configs)

    def test_init_with_none_resources(self, mock_configs):
        """
        GIVEN resources=None
        WHEN ErrorMonitor is initialized
        THEN expect TypeError or AttributeError when trying to access resources dict
        """
        with pytest.raises((TypeError, AttributeError)):
            ErrorMonitor(None, mock_configs)

    def test_init_with_none_configs(self, mock_resources):
        """
        GIVEN configs=None
        WHEN ErrorMonitor is initialized
        THEN expect AttributeError when trying to access configs attributes
        """
        with pytest.raises(AttributeError):
            ErrorMonitor(mock_resources, None)


@pytest.mark.unit
class TestErrorMonitorErrorHandling:
    """Test ErrorMonitor error handling and tracking."""

    @pytest.fixture
    def error_monitor(self, mock_resources, mock_configs):
        """Create an ErrorMonitor instance for testing."""
        return ErrorMonitor(mock_resources, mock_configs)

    def test_track_error_adds_to_counters(self, error_monitor):
        """
        GIVEN an ErrorMonitor instance
        WHEN track_error is called with a specific error type
        THEN expect error counter to increment for that type
        """
        error_type = "FileNotFoundError"
        
        error_monitor.track_error(error_type)
        
        assert error_type in error_monitor._error_counters
        assert error_monitor._error_counters[error_type] == 1
        assert error_type in error_monitor._error_types

    def test_track_multiple_same_errors(self, error_monitor):
        """
        GIVEN an ErrorMonitor instance
        WHEN track_error is called multiple times with same error type
        THEN expect counter to increment each time
        """
        error_type = "ValueError"
        
        error_monitor.track_error(error_type)
        error_monitor.track_error(error_type)
        error_monitor.track_error(error_type)
        
        assert error_monitor._error_counters[error_type] == 3

    @pytest.mark.parametrize("error_types", [
        ["FileNotFoundError", "ValueError", "IOError"],
        ["CustomError", "AnotherError"],
        ["SingleError"]
    ])
    def test_track_different_error_types(self, error_monitor, error_types):
        """
        GIVEN an ErrorMonitor instance
        WHEN track_error is called with different error types
        THEN expect separate counters for each type
        """
        for error_type in error_types:
            error_monitor.track_error(error_type)
        
        for error_type in error_types:
            assert error_type in error_monitor._error_counters
            assert error_monitor._error_counters[error_type] == 1
            assert error_type in error_monitor._error_types


@pytest.mark.unit
class TestErrorMonitorReporting:
    """Test ErrorMonitor reporting functionality."""

    @pytest.fixture
    def error_monitor_with_errors(self, mock_resources, mock_configs):
        """Create an ErrorMonitor with some tracked errors."""
        monitor = ErrorMonitor(mock_resources, mock_configs)
        monitor.track_error("FileNotFoundError")
        monitor.track_error("FileNotFoundError")
        monitor.track_error("ValueError")
        return monitor

    def test_get_error_summary(self, error_monitor_with_errors):
        """
        GIVEN an ErrorMonitor with tracked errors
        WHEN get_error_summary is called
        THEN expect summary dict with error counts
        """
        summary = error_monitor_with_errors.get_error_summary()
        
        assert isinstance(summary, dict)
        assert "FileNotFoundError" in summary
        assert "ValueError" in summary
        assert summary["FileNotFoundError"] == 2
        assert summary["ValueError"] == 1

    def test_get_total_errors(self, error_monitor_with_errors):
        """
        GIVEN an ErrorMonitor with tracked errors
        WHEN get_total_errors is called
        THEN expect total count of all errors
        """
        total = error_monitor_with_errors.get_total_errors()
        
        assert total == 3  # 2 FileNotFoundError + 1 ValueError

    def test_has_errors_returns_true_when_errors_exist(self, error_monitor_with_errors):
        """
        GIVEN an ErrorMonitor with tracked errors
        WHEN has_errors is called
        THEN expect True
        """
        assert error_monitor_with_errors.has_errors() is True

    def test_has_errors_returns_false_when_no_errors(self, mock_resources, mock_configs):
        """
        GIVEN an ErrorMonitor with no tracked errors
        WHEN has_errors is called
        THEN expect False
        """
        monitor = ErrorMonitor(mock_resources, mock_configs)
        assert monitor.has_errors() is False


@pytest.mark.integration
class TestMakeErrorMonitor:
    """Test the make_error_monitor factory function."""

    def test_make_error_monitor_creates_instance(self):
        """
        GIVEN valid resources and configs
        WHEN make_error_monitor is called
        THEN expect ErrorMonitor instance to be created
        """
        mock_resources = {
            'logger': MagicMock(spec=Logger),
            'traceback': MagicMock(),
            'datetime': MagicMock(),
        }
        mock_configs = MagicMock(spec=Configs)
        mock_configs.processing = MagicMock()
        mock_configs.processing.suppress_errors = False
        mock_configs.paths = MagicMock()
        mock_configs.paths.ROOT_DIR = Path("/test/root")

        monitor = make_error_monitor(mock_resources, mock_configs)
        
        assert isinstance(monitor, ErrorMonitor)


@pytest.mark.slow  
class TestErrorMonitorPerformance:
    """Test ErrorMonitor performance characteristics."""

    def test_track_many_errors_performance(self, mock_resources, mock_configs):
        """
        GIVEN an ErrorMonitor instance
        WHEN tracking many errors rapidly
        THEN expect reasonable performance
        """
        monitor = ErrorMonitor(mock_resources, mock_configs)
        
        start_time = time.time()
        for i in range(1000):
            monitor.track_error(f"Error{i % 10}")  # 10 different error types
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 1.0  # Should complete in less than 1 second
        assert monitor.get_total_errors() == 1000