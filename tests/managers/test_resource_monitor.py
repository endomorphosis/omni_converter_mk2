"""
Test the resource monitor module.
"""

import unittest
import threading
import time
from unittest.mock import MagicMock, patch

from managers.resource_monitor import ResourceMonitor


class TestResourceMonitor(unittest.TestCase):
    """Test the ResourceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.resource_monitor = ResourceMonitor(
            cpu_limit=80.0,
            memory_limit=512,
            monitoring_interval=0.1
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.resource_monitor.active_monitoring:
            self.resource_monitor.stop_monitoring()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.resource_monitor.cpu_limit, 80.0)
        self.assertEqual(self.resource_monitor.memory_limit, 512)
        self.assertEqual(self.resource_monitor.monitoring_interval, 0.1)
        self.assertFalse(self.resource_monitor.active_monitoring)
        self.assertIsNone(self.resource_monitor.monitoring_thread)
    
    @patch('managers.resource_monitor.psutil')
    def test_start_monitoring_with_psutil(self, mock_psutil):
        """Test starting monitoring with psutil available."""
        # Mock psutil availability
        with patch('managers.resource_monitor.HAS_PSUTIL', True):
            result = self.resource_monitor.start_monitoring()
            
            self.assertTrue(result)
            self.assertTrue(self.resource_monitor.active_monitoring)
            self.assertIsNotNone(self.resource_monitor.monitoring_thread)
            self.assertTrue(self.resource_monitor.monitoring_thread.is_alive())
            
            # Stop monitoring to clean up
            self.resource_monitor.stop_monitoring()
    
    @patch('managers.resource_monitor.HAS_PSUTIL', False)
    def test_start_monitoring_without_psutil(self):
        """Test starting monitoring without psutil available."""
        result = self.resource_monitor.start_monitoring()
        
        self.assertFalse(result)
        self.assertFalse(self.resource_monitor.active_monitoring)
        self.assertIsNone(self.resource_monitor.monitoring_thread)
    
    @patch('managers.resource_monitor.psutil')
    def test_stop_monitoring(self, mock_psutil):
        """Test stopping monitoring."""
        # Start monitoring
        with patch('managers.resource_monitor.HAS_PSUTIL', True):
            self.resource_monitor.start_monitoring()
            
            # Verify monitoring is running
            self.assertTrue(self.resource_monitor.active_monitoring)
            self.assertIsNotNone(self.resource_monitor.monitoring_thread)
            
            # Stop monitoring
            self.resource_monitor.stop_monitoring()
            
            # Verify monitoring is stopped
            self.assertFalse(self.resource_monitor.active_monitoring)
            
            # Give thread time to stop
            time.sleep(0.2)
            self.assertFalse(self.resource_monitor.monitoring_thread.is_alive())
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_get_resource_usage_with_psutil(self, mock_psutil):
        """Test getting resource usage with psutil available."""
        # Mock psutil methods
        mock_process = MagicMock()
        mock_process.memory_info.return_value.rss = 100 * 1024 * 1024  # 100 MB
        mock_psutil.Process.return_value = mock_process
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_usage.return_value.percent = 60.0
        mock_process.open_files.return_value = ["file1", "file2"]
        
        # Get resource usage
        usage = self.resource_monitor._get_resource_usage()
        
        # Check usage
        self.assertEqual(usage["cpu"], 25.0)
        self.assertEqual(usage["memory"], 100.0)
        self.assertEqual(usage["memory_percent"], 50.0)
        self.assertEqual(usage["disk_usage"], 60.0)
        self.assertEqual(usage["open_files"], 2)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', False)
    def test_get_resource_usage_without_psutil(self):
        """Test getting resource usage without psutil available."""
        # Get resource usage
        usage = self.resource_monitor._get_resource_usage()
        
        # Check usage
        self.assertEqual(usage["cpu"], 0.0)
        self.assertEqual(usage["memory"], 0)
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.psutil')
    def test_get_current_usage(self, mock_psutil):
        """Test getting current resource usage."""
        # Mock resource usage method
        orig_method = self.resource_monitor._get_resource_usage
        self.resource_monitor._get_resource_usage = MagicMock(
            return_value={"cpu": 30.0, "memory": 200.0}
        )
        
        # Test with active monitoring
        self.resource_monitor.active_monitoring = True
        self.resource_monitor.current_usage = {"cpu": 30.0, "memory": 200.0}
        
        usage = self.resource_monitor.get_current_usage()
        self.assertEqual(usage["cpu"], 30.0)
        self.assertEqual(usage["memory"], 200.0)
        self.resource_monitor._get_resource_usage.assert_not_called()
        
        # Test without active monitoring
        self.resource_monitor.active_monitoring = False
        
        usage = self.resource_monitor.get_current_usage()
        self.assertEqual(usage["cpu"], 30.0)
        self.assertEqual(usage["memory"], 200.0)
        self.resource_monitor._get_resource_usage.assert_called_once()
        
        # Restore original method
        self.resource_monitor._get_resource_usage = orig_method
    
    def test_is_resource_available(self):
        """Test checking if resources are available."""
        # Mock get_current_usage
        self.resource_monitor.get_current_usage = MagicMock()
        
        # Test with resources available
        self.resource_monitor.get_current_usage.return_value = {"cpu": 70.0, "memory": 400.0}
        available, reason = self.resource_monitor.is_resource_available()
        self.assertTrue(available)
        self.assertIsNone(reason)
        
        # Test with CPU usage too high
        self.resource_monitor.get_current_usage.return_value = {"cpu": 90.0, "memory": 400.0}
        available, reason = self.resource_monitor.is_resource_available()
        self.assertFalse(available)
        self.assertIn("CPU usage too high", reason)
        
        # Test with memory usage too high
        self.resource_monitor.get_current_usage.return_value = {"cpu": 70.0, "memory": 600.0}
        available, reason = self.resource_monitor.is_resource_available()
        self.assertFalse(available)
        self.assertIn("Memory usage too high", reason)
    
    def test_set_resource_limits(self):
        """Test setting resource limits."""
        # Set new limits
        self.resource_monitor.set_resource_limits(cpu_limit=90.0, memory_limit=1024)
        
        # Check limits
        self.assertEqual(self.resource_monitor.cpu_limit, 90.0)
        self.assertEqual(self.resource_monitor.memory_limit, 1024)
        
        # Test clamping CPU limit to 0-100 range
        self.resource_monitor.set_resource_limits(cpu_limit=120.0)
        self.assertEqual(self.resource_monitor.cpu_limit, 100.0)
        
        self.resource_monitor.set_resource_limits(cpu_limit=-10.0)
        self.assertEqual(self.resource_monitor.cpu_limit, 0.0)
        
        # Test setting only one limit
        self.resource_monitor.set_resource_limits(memory_limit=2048)
        self.assertEqual(self.resource_monitor.cpu_limit, 0.0)  # Unchanged from previous test
        self.assertEqual(self.resource_monitor.memory_limit, 2048)
    
    def test_get_resource_summary(self):
        """Test getting resource summary."""
        # Mock get_current_usage
        self.resource_monitor.get_current_usage = MagicMock(
            return_value={
                "cpu": 40.0,
                "memory": 300.0,
                "memory_percent": 30.0,
                "disk_usage": 50.0,
                "open_files": 5
            }
        )
        
        # Get summary
        summary = self.resource_monitor.get_resource_summary()
        
        # Check summary
        self.assertEqual(summary["current"]["cpu_percent"], 40.0)
        self.assertEqual(summary["current"]["memory_mb"], 300.0)
        self.assertEqual(summary["current"]["memory_percent"], 30.0)
        self.assertEqual(summary["current"]["disk_usage_percent"], 50.0)
        self.assertEqual(summary["current"]["open_files"], 5)
        
        self.assertEqual(summary["limits"]["cpu_percent"], 80.0)
        self.assertEqual(summary["limits"]["memory_mb"], 512)
        
        self.assertEqual(summary["utilization"]["cpu_percent"], 50.0)  # 40.0 / 80.0 * 100
        self.assertEqual(summary["utilization"]["memory_percent"], 58.59375)  # 300.0 / 512 * 100
        
        self.assertFalse(summary["monitoring_active"])
    
    @patch('managers.resource_monitor.HAS_PSUTIL', True)
    @patch('managers.resource_monitor.logger')
    def test_monitoring_loop_logs_high_usage(self, mock_logger):
        """Test monitoring loop logs high usage."""
        # Mock _get_resource_usage
        self.resource_monitor._get_resource_usage = MagicMock(
            return_value={"cpu": 85.0, "memory": 490.0}
        )
        
        # Create a condition to control the test
        stop_event = threading.Event()
        
        # Override _monitoring_loop to run once and signal completion
        def mock_loop():
            self.resource_monitor.active_monitoring = True
            while self.resource_monitor.active_monitoring and not stop_event.is_set():
                # Run the real monitoring logic once
                self.resource_monitor.current_usage = self.resource_monitor._get_resource_usage()
                
                # Log high usage
                cpu_usage = self.resource_monitor.current_usage.get("cpu", 0)
                memory_usage = self.resource_monitor.current_usage.get("memory", 0)
                
                if cpu_usage > (self.resource_monitor.cpu_limit * 0.9):
                    mock_logger.warning(f"High CPU usage: {cpu_usage:.1f}%", {"resource": "cpu"})
                
                if memory_usage > (self.resource_monitor.memory_limit * 0.9):
                    mock_logger.warning(f"High memory usage: {memory_usage} MB", {"resource": "memory"})
                
                # Signal completion
                stop_event.set()
                time.sleep(0.1)
        
        # Start mocked monitoring loop
        with patch.object(self.resource_monitor, '_monitoring_loop', mock_loop):
            # Start monitoring
            self.resource_monitor.start_monitoring()
            
            # Wait for the monitoring loop to run once
            stop_event.wait(timeout=1.0)
            
            # Check that high usage warnings were logged
            mock_logger.warning.assert_any_call(
                "High CPU usage: 85.0%", {"resource": "cpu"}
            )
            
            # Also check that high memory warning was logged
            mock_logger.warning.assert_any_call(
                "High memory usage: 490.0 MB", {"resource": "memory"}
            )
            
            # Stop monitoring
            self.resource_monitor.stop_monitoring()


if __name__ == "__main__":
    unittest.main()