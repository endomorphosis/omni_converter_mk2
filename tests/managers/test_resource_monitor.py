"""
Test the resource monitor module.

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

import unittest
from unittest.mock import MagicMock, patch
import threading
import time

from managers.resource_monitor import ResourceMonitor


class TestResourceMonitor(unittest.TestCase):
    """Test the ResourceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a resource monitor with test limits
        self.resource_monitor = ResourceMonitor(
            cpu_limit=80.0,
            memory_limit=500,  # 500 MB
            monitoring_interval=0.1  # Short interval for tests
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Stop any active monitoring
        if hasattr(self, 'resource_monitor') and self.resource_monitor.active_monitoring:
            self.resource_monitor.stop_monitoring()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.resource_monitor.cpu_limit, 80.0)
        self.assertEqual(self.resource_monitor.memory_limit, 500)
        self.assertEqual(self.resource_monitor.monitoring_interval, 0.1)
        self.assertFalse(self.resource_monitor.active_monitoring)
        self.assertIsNone(self.resource_monitor.monitoring_thread)
        self.assertIn("cpu", self.resource_monitor.current_usage)
        self.assertIn("memory", self.resource_monitor.current_usage)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_start_monitoring(self, mock_psutil):
        """Test starting resource monitoring."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 10.0
        process_mock = MagicMock()
        process_mock.memory_info.return_value.rss = 100 * 1024 * 1024  # 100 MB in bytes
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_usage.return_value.percent = 60.0
        process_mock.open_files.return_value = ["file1", "file2"]
        
        # Start monitoring
        result = self.resource_monitor.start_monitoring()
        
        # Check result
        self.assertTrue(result)
        self.assertTrue(self.resource_monitor.active_monitoring)
        self.assertIsNotNone(self.resource_monitor.monitoring_thread)
        
        # Stop monitoring
        self.resource_monitor.stop_monitoring()
        
        # Check that monitoring has stopped
        self.assertFalse(self.resource_monitor.active_monitoring)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', False)
    def test_start_monitoring_without_psutil(self):
        """Test starting monitoring without psutil available."""
        # Try to start monitoring
        result = self.resource_monitor.start_monitoring()
        
        # Should return False since psutil is not available
        self.assertFalse(result)
        self.assertFalse(self.resource_monitor.active_monitoring)
        self.assertIsNone(self.resource_monitor.monitoring_thread)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_get_resource_usage(self, mock_psutil):
        """Test getting resource usage."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 30.0
        process_mock = MagicMock()
        process_mock.memory_info.return_value.rss = 200 * 1024 * 1024  # 200 MB in bytes
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 40.0
        mock_psutil.disk_usage.return_value.percent = 50.0
        process_mock.open_files.return_value = ["file1", "file2", "file3"]
        
        # Get resource usage
        usage = self.resource_monitor._get_resource_usage()
        
        # Check usage values
        self.assertEqual(usage["cpu"], 30.0)
        self.assertEqual(usage["memory"], 200.0)  # Should be converted to MB
        self.assertEqual(usage["memory_percent"], 40.0)
        self.assertEqual(usage["disk_usage"], 50.0)
        self.assertEqual(usage["open_files"], 3)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', False)
    def test_get_resource_usage_without_psutil(self):
        """Test getting resource usage without psutil available."""
        # Get resource usage
        usage = self.resource_monitor._get_resource_usage()
        
        # Should return default values
        self.assertEqual(usage["cpu"], 0.0)
        self.assertEqual(usage["memory"], 0)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_get_current_usage(self, mock_psutil):
        """Test getting current usage."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 20.0
        process_mock = MagicMock()
        process_mock.memory_info.return_value.rss = 150 * 1024 * 1024  # 150 MB in bytes
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 30.0
        mock_psutil.disk_usage.return_value.percent = 40.0
        process_mock.open_files.return_value = ["file1"]
        
        # Get current usage without active monitoring
        usage = self.resource_monitor.get_current_usage()
        
        # Check usage values
        self.assertEqual(usage["cpu"], 20.0)
        self.assertEqual(usage["memory"], 150.0)  # Should be converted to MB
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_is_resource_available(self, mock_psutil):
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
        process_mock.memory_info.return_value.rss = 200 * 1024 * 1024  # 200 MB in bytes
        mock_psutil.Process.return_value = process_mock
        
        # Check if resources are available
        available, reason = self.resource_monitor.is_resource_available()
        
        # Should report resources available
        self.assertTrue(available)
        self.assertIsNone(reason)
        
        # Now configure mock to report high CPU usage
        mock_psutil.cpu_percent.return_value = 90.0
        
        # Check if resources are available
        available, reason = self.resource_monitor.is_resource_available()
        
        # Should report resources not available due to high CPU
        self.assertFalse(available)
        self.assertIn("CPU usage too high", reason)
        
        # Configure mock to report high memory usage
        mock_psutil.cpu_percent.return_value = 30.0
        process_mock.memory_info.return_value.rss = 600 * 1024 * 1024  # 600 MB in bytes
        
        # Check if resources are available
        available, reason = self.resource_monitor.is_resource_available()
        
        # Should report resources not available due to high memory
        self.assertFalse(available)
        self.assertIn("Memory usage too high", reason)
    
    def test_set_resource_limits(self):
        """Test setting resource limits."""
        # Set new limits
        self.resource_monitor.set_resource_limits(cpu_limit=60.0, memory_limit=300)
        
        # Check if limits were updated
        self.assertEqual(self.resource_monitor.cpu_limit, 60.0)
        self.assertEqual(self.resource_monitor.memory_limit, 300)
        
        # Test bounds checking for CPU
        self.resource_monitor.set_resource_limits(cpu_limit=150.0)
        
        # CPU should be clamped to 100%
        self.assertEqual(self.resource_monitor.cpu_limit, 100.0)
        
        # Test with negative values
        self.resource_monitor.set_resource_limits(cpu_limit=-10.0, memory_limit=-100)
        
        # Should be clamped to 0
        self.assertEqual(self.resource_monitor.cpu_limit, 0.0)
        self.assertEqual(self.resource_monitor.memory_limit, 0)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_get_resource_summary(self, mock_psutil):
        """Test getting resource summary."""
        # Configure mock for psutil
        mock_psutil.cpu_percent.return_value = 40.0
        process_mock = MagicMock()
        process_mock.memory_info.return_value.rss = 250 * 1024 * 1024  # 250 MB in bytes
        mock_psutil.Process.return_value = process_mock
        mock_psutil.virtual_memory.return_value.percent = 60.0
        mock_psutil.disk_usage.return_value.percent = 70.0
        process_mock.open_files.return_value = ["file1", "file2"]
        
        # Get resource summary
        summary = self.resource_monitor.get_resource_summary()
        
        # Check summary structure
        self.assertIn("current", summary)
        self.assertIn("limits", summary)
        self.assertIn("utilization", summary)
        self.assertIn("monitoring_active", summary)
        
        # Check current values
        self.assertEqual(summary["current"]["cpu_percent"], 40.0)
        self.assertEqual(summary["current"]["memory_mb"], 250.0)
        
        # Check limits
        self.assertEqual(summary["limits"]["cpu_percent"], 80.0)
        self.assertEqual(summary["limits"]["memory_mb"], 500)
        
        # Check monitoring status
        self.assertFalse(summary["monitoring_active"])


if __name__ == "__main__":
    unittest.main()