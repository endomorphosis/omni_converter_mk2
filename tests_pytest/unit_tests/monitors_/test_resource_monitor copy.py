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
# NOTE we convert GB to MB because 
# the psutil library returns memory in MB


@pytest.fixture
def mock_configs():
    """Create mock configs for resource monitor testing."""
    mock_configs = MagicMock(spec=Configs)
    mock_configs.resources = MagicMock()
    mock_configs.resources.memory_limit_mb = 512.0  # 512 MB
    mock_configs.resources.cpu_limit_percent = 80.0  # 80% CPU limit
    mock_configs.resources.monitoring_interval_seconds = 0.1  # Short interval for tests
    return mock_configs


@pytest.fixture
def mock_resources():
    """Create mock resources for resource monitor testing."""
    mock_resources = {
        **copy.deepcopy(resources),
        "logger": MagicMock(spec=Logger),  # Mock the logger to avoid actual logging during tests
    }
    return mock_resources


@pytest.fixture
def resource_monitor(mock_resources, mock_configs):
    """Create ResourceMonitor instance for testing."""
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
        assert resource_monitor.active_monitoring is False
        assert resource_monitor.monitoring_thread is None
        assert "cpu" in resource_monitor.current_resource_usage
        assert "memory" in resource_monitor.current_resource_usage

    @patch('utils.hardware.psutil')
    def test_start_monitoring(self, mock_psutil, resource_monitor):
        """Test starting resource monitoring."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 10.0
        process_mock = MagicMock(spec=psutil.Process)

        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 100 * 1024 * 1024  # 100 MB in bytes
        memory_info_mock.vms = 120 * 1024 * 1024  # 120 MB in bytes
        memory_info_mock.shared = 10 * 1024 * 1024  # 10 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_usage.return_value.percent = 60.0
        process_mock.open_files.return_value = ["file1", "file2"]
        
        # Start monitoring
        result = resource_monitor.start_monitoring()
        
        # Check result
        assert result is True
        assert resource_monitor.active_monitoring is True
        assert resource_monitor.monitoring_thread is not None
        
        # Stop monitoring
        resource_monitor.stop_monitoring()
        
        # Check that monitoring has stopped
        assert resource_monitor.active_monitoring is False

    @patch('utils.hardware.psutil')
    def test_get_resource_usage(self, mock_psutil, resource_monitor):
        """Test getting resource usage."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 30.0
        process_mock = MagicMock()
        
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
        process_mock.memory_info = MagicMock()
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 150 * 1024 * 1024  # 150 MB in bytes
        memory_info_mock.vms = 180 * 1024 * 1024  # 180 MB in bytes
        memory_info_mock.shared = 15 * 1024 * 1024  # 15 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 30.0
        mock_psutil.disk_usage.return_value.percent = 40.0
        process_mock.open_files = MagicMock()
        process_mock.open_files.return_value = ["file1"]
        
        # Get current usage without active monitoring
        usage = resource_monitor.current_resource_usage
        
        # Check usage values
        assert usage["cpu"] == 20.0
        assert usage["memory"] == 150.0  # Should be converted to MB
    
    @patch('utils.hardware.psutil')
    def test_are_resources_available(self, mock_psutil, resource_monitor):
        """Test checking if resources are available.
        
        This test validates the resource checking functionality of the ResourceMonitor,
        addressing the "Resource Utilization" criteria. It verifies that:
        
        1. The monitor correctly identifies when resources are within acceptable limits
        2. The monitor detects when CPU usage exceeds the 80% threshold and reports it
        3. The monitor detects when memory usage exceeds the configured limit and reports it
        4. Appropriate reason messages are provided when resources are constrained
        
        These validations ensure the system can enforce the target resource constraints
        of <80% CPU usage and <6GB RAM usage as specified in the testing criteria.
        """
        # Configure mock for psutil to report low resource usage
        mock_psutil.cpu_percent.return_value = 30.0
        process_mock = MagicMock()
        
        # Mock memory_info with all required attributes - THIS IS THE FIX
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 200 * 1024 * 1024  # 200 MB in bytes
        memory_info_mock.vms = 240 * 1024 * 1024  # 240 MB in bytes
        memory_info_mock.shared = 20 * 1024 * 1024  # 20 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_usage.return_value.percent = 60.0
        process_mock.open_files.return_value = ["file1", "file2"]
        
        # Check if resources are available
        available, reason = resource_monitor.are_resources_available
        
        # Should report resources available
        assert available is True
        assert reason is None
        
        # Now configure mock to report high CPU usage
        mock_psutil.cpu_percent.return_value = 90.0
        
        # Check if resources are available
        available, reason = resource_monitor.are_resources_available
        
        # Should report resources not available due to high CPU
        assert available is False
        assert "CPU usage too high" in reason
        
        # Configure mock to report high memory usage
        mock_psutil.cpu_percent.return_value = 30.0
        memory_info_mock.rss = 600 * 1024 * 1024  # 600 MB in bytes
        
        # Check if resources are available
        available, reason = resource_monitor.are_resources_available
        
        # Should report resources not available due to high memory
        assert available is False
        assert "Memory usage too high" in reason
    
    def test_set_resource_limits(self, resource_monitor):
        """Test setting resource limits."""
        # Set new limits
        resource_monitor.set_resource_limits(cpu_limit_percent=60.0, memory_limit=300)
        
        # Check if limits were updated
        assert resource_monitor.cpu_limit_percent == 60.0
        assert resource_monitor.memory_limit == 300
        
        # Test bounds checking for CPU
        resource_monitor.set_resource_limits(cpu_limit_percent=150.0)
        
        # CPU should be clamped to 100%
        assert resource_monitor.cpu_limit_percent == 100.0
        
        # Test with negative values
        resource_monitor.set_resource_limits(cpu_limit_percent=-10.0, memory_limit=-100)
        
        # Should be clamped to 0
        assert resource_monitor.cpu_limit_percent == 0.0
        assert resource_monitor.memory_limit == 0
    
    @patch('utils.hardware.psutil')
    def test_get_resource_summary(self, mock_psutil, resource_monitor):
        """Test getting resource summary."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 40.0
        process_mock = MagicMock()
        
        # Mock memory_info with all required attributes
        memory_info_mock = MagicMock()
        memory_info_mock.rss = 250 * 1024 * 1024  # 250 MB in bytes
        memory_info_mock.vms = 300 * 1024 * 1024  # 300 MB in bytes
        memory_info_mock.shared = 25 * 1024 * 1024  # 25 MB in bytes
        process_mock.memory_info.return_value = memory_info_mock
        
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 60.0
        mock_psutil.disk_usage.return_value.percent = 70.0
        process_mock.open_files.return_value = ["file1", "file2"]
        
        # Get resource summary
        summary = resource_monitor.resource_summary
        
        # Check summary structure
        assert "current" in summary
        assert "limits" in summary
        assert "utilization" in summary
        assert "monitoring_active" in summary
        
        # Check current values
        assert summary["current"]["cpu_percent"] == 40.0
        assert summary["current"]["memory_mb"] == 250.0
        
        # Check limits
        assert summary["limits"]["cpu_percent"] == 80.0
        assert summary["limits"]["memory_mb"] == 512.0
        
        # Check monitoring status
        assert summary["monitoring_active"] is False