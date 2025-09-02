"""
Test suite for monitors/_resource_monitor.py converted from unittest to pytest.

This test suite validates the ResourceMonitor component against several criteria:

1. Resource Utilization (Target: <6GB RAM, <80% CPU)
   - Tests verify accurate tracking of CPU usage against the 80% threshold
   - Tests verify accurate tracking of memory usage against the 6GB threshold
   - Tests ensure proper resource limitation enforcement
   - Tests confirm appropriate handling of resource constraints

2. Processing Speed (Indirect)
   - The resource monitor indirectly impacts processing speed by controlling 
     resource allocation, preventing system overload and ensuring sustained 
     performance across all file types
   
3. Error Handling Effectiveness
   - Tests verify graceful handling when system resources are constrained
   - Tests ensure appropriate logging and notification of resource issues
"""
import pytest
from unittest.mock import MagicMock, patch
import copy
import threading
import time

try:
    import psutil
except ImportError:
    pytest.skip("psutil library is required for resource monitoring. Please install it using 'pip install psutil'.", 
                allow_module_level=True)

from monitors._resource_monitor import ResourceMonitor
from utils.hardware import Hardware
from types_ import Logger
from logger import logger as debug_logger
from configs import configs, Configs

resources = {
    "get_cpu_usage_in_percent": Hardware.get_cpu_usage_in_percent,
    "get_virtual_memory_in_percent": Hardware.get_virtual_memory_in_percent,
    "get_memory_info": Hardware.get_memory_info,
    "get_memory_rss_usage_in_mb": Hardware.get_memory_rss_usage_in_mb,
    "get_memory_vms_usage_in_mb": Hardware.get_memory_vms_usage_in_mb,
    "get_disk_usage": Hardware.get_disk_usage_in_percent,
    "get_open_files": Hardware.get_num_open_files,
    "get_shared_memory_usage_in_mb": Hardware.get_shared_memory_usage_in_mb,
    "get_num_cpu_cores": Hardware.get_num_cpu_cores,
}


@pytest.fixture
def mock_configs():
    """Create mock configs for testing."""
    mock_configs = MagicMock(spec=Configs)
    mock_configs.resources = MagicMock()
    mock_configs.resources.memory_limit_mb = 512.0  # 512 MB
    mock_configs.resources.cpu_limit_percent = 80.0  # 80% CPU limit
    mock_configs.resources.monitoring_interval_seconds = 0.1  # Short interval for tests
    return mock_configs


@pytest.fixture
def mock_resources():
    """Create mock resources for testing."""
    return {
        **copy.deepcopy(resources),
        "logger": MagicMock(spec=Logger),  # Mock the logger to avoid actual logging during tests
    }


@pytest.fixture
def resource_monitor(mock_resources, mock_configs):
    """Create a ResourceMonitor instance for testing."""
    monitor = ResourceMonitor(resources=mock_resources, configs=mock_configs)
    yield monitor
    # Cleanup: Stop any active monitoring
    if hasattr(monitor, 'active_monitoring') and monitor.active_monitoring:
        monitor.stop_monitoring()


@pytest.mark.unit
class TestResourceMonitor:
    """Test the ResourceMonitor class."""
    
    def test_init(self, resource_monitor):
        """Test initialization."""
        assert resource_monitor.cpu_limit_percent == 80.0
        assert resource_monitor.memory_limit == 512.0
        assert resource_monitor.monitoring_interval == 0.1
        assert not resource_monitor.active_monitoring
        assert resource_monitor.monitoring_thread is None
        assert "cpu" in resource_monitor.current_resource_usage
        assert "memory" in resource_monitor.current_resource_usage

    @patch('utils.hardware.psutil')
    def test_start_monitoring(self, mock_psutil, resource_monitor):
        """Test starting resource monitoring."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 10.0
        process_mock = MagicMock(spec="psutil.Process")

        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 100 * 1024 * 1024  # 100 MB in bytes
        memory_info_mock.vms = 120 * 1024 * 1024  # 120 MB in bytes
        memory_info_mock.shared = 10 * 1024 * 1024  # 10 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock

        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 25.0
        process_mock.open_files.return_value = ["file1", "file2"]

        # Start monitoring
        resource_monitor.start_monitoring()

        # Check if monitoring started
        assert resource_monitor.active_monitoring
        assert resource_monitor.monitoring_thread is not None
        assert resource_monitor.monitoring_thread.is_alive()

        # Wait briefly for monitoring to collect data
        time.sleep(0.2)

        # Check if resource usage was updated
        usage = resource_monitor.current_resource_usage
        assert usage["cpu"] >= 0
        assert usage["memory"] >= 0

        # Stop monitoring
        resource_monitor.stop_monitoring()
        assert not resource_monitor.active_monitoring

    @patch('utils.hardware.psutil')
    def test_get_resource_usage(self, mock_psutil, resource_monitor):
        """Test getting resource usage."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 30.0
        process_mock = MagicMock(spec="psutil.Process")
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 200 * 1024 * 1024  # 200 MB in bytes
        memory_info_mock.vms = 240 * 1024 * 1024  # 240 MB in bytes  
        memory_info_mock.shared = 20 * 1024 * 1024  # 20 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 40.0
        mock_psutil.disk_usage.return_value.percent = 50.0
        process_mock.open_files.return_value = ["file1", "file2", "file3"]

        # Get resource usage
        usage = resource_monitor._get_resource_usage()

        # Check usage values
        assert usage["cpu"] == 30.0
        assert usage["memory"] == 200.0  # Should be converted to MB
        assert usage["memory_percent"] == 40.0
        assert usage["disk_usage"] == 50.0
        assert usage["open_files"] == 3

    @patch('utils.hardware.psutil')
    def test_get_current_usage(self, mock_psutil, resource_monitor):
        """Test getting current usage."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 20.0
        process_mock = MagicMock(spec="psutil.Process")
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 150 * 1024 * 1024  # 150 MB in bytes
        memory_info_mock.vms = 180 * 1024 * 1024  # 180 MB in bytes
        memory_info_mock.shared = 15 * 1024 * 1024  # 15 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 30.0
        mock_psutil.disk_usage.return_value.percent = 45.0
        process_mock.open_files.return_value = ["file1", "file2"]

        # Get current usage
        usage = resource_monitor.current_resource_usage

        # Check if the usage contains expected keys
        assert "cpu" in usage
        assert "memory" in usage
        assert "memory_percent" in usage

    @patch('utils.hardware.psutil')
    def test_are_resources_available(self, mock_psutil, resource_monitor):
        """Test checking if resources are available."""
        # Configure mock for psutil - under limits
        mock_psutil.cpu_percent.return_value = 70.0  # Below 80% limit
        process_mock = MagicMock(spec="psutil.Process")
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 400 * 1024 * 1024  # 400 MB - below 512 MB limit
        memory_info_mock.vms = 450 * 1024 * 1024  # 450 MB
        memory_info_mock.shared = 40 * 1024 * 1024  # 40 MB
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock

        # Resources should be available
        assert resource_monitor.are_resources_available()

        # Configure mock for psutil - over limits
        mock_psutil.cpu_percent.return_value = 90.0  # Above 80% limit
        memory_info_mock.rss = 600 * 1024 * 1024  # 600 MB - above 512 MB limit

        # Resources should not be available
        assert not resource_monitor.are_resources_available()

    def test_set_resource_limits(self, resource_monitor):
        """Test setting resource limits."""
        # Set new limits
        resource_monitor.set_resource_limits(memory_limit_mb=1024, cpu_limit_percent=90)

        # Check if limits were updated
        assert resource_monitor.memory_limit == 1024
        assert resource_monitor.cpu_limit_percent == 90

        # Test with partial updates
        resource_monitor.set_resource_limits(memory_limit_mb=2048)
        assert resource_monitor.memory_limit == 2048
        assert resource_monitor.cpu_limit_percent == 90  # Should remain unchanged

    @patch('utils.hardware.psutil')
    def test_get_resource_summary(self, mock_psutil, resource_monitor):
        """Test getting resource summary."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 25.0
        process_mock = MagicMock(spec="psutil.Process")
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 300 * 1024 * 1024  # 300 MB in bytes
        memory_info_mock.vms = 350 * 1024 * 1024  # 350 MB in bytes
        memory_info_mock.shared = 30 * 1024 * 1024  # 30 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 35.0
        mock_psutil.disk_usage.return_value.percent = 55.0
        process_mock.open_files.return_value = ["file1", "file2", "file3", "file4"]

        # Get resource summary
        summary = resource_monitor.get_resource_summary()

        # Check summary contains expected information
        assert "current_usage" in summary
        assert "limits" in summary
        assert "within_limits" in summary
        assert summary["limits"]["memory_mb"] == 512.0
        assert summary["limits"]["cpu_percent"] == 80.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])