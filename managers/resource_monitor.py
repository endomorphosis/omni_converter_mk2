"""
Resource monitor module for the Omni-Converter.

This module provides the ResourceMonitor class for monitoring and managing system resources.
"""

import os
import time
import threading
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from utils.logger import logger


class ResourceMonitor:
    """
    Resource monitor for the Omni-Converter.
    
    This class monitors system resources such as CPU and memory usage, and
    provides methods to check if resources are available for processing.
    
    Attributes:
        cpu_limit (float): Maximum CPU usage percentage (0-100).
        memory_limit (int): Maximum memory usage in MB.
        current_usage (Dict[str, float]): Current resource usage.
        active_monitoring (bool): Whether active monitoring is enabled.
        monitoring_thread: Thread for active monitoring.
        monitoring_interval (float): Interval for active monitoring in seconds.
    """
    
    def __init__(
        self,
        cpu_limit: float = 90.0,
        memory_limit: int = 1024,  # in MB
        monitoring_interval: float = 1.0
    ):
        """
        Initialize a resource monitor.
        
        Args:
            cpu_limit: Maximum CPU usage percentage (0-100).
            memory_limit: Maximum memory usage in MB.
            monitoring_interval: Interval for active monitoring in seconds.
        """
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.current_usage = {"cpu": 0.0, "memory": 0}
        self.active_monitoring = False
        self.monitoring_thread = None
        self.monitoring_interval = monitoring_interval
        
        # Check if psutil is available
        if not HAS_PSUTIL:
            logger.warning("psutil not available, resource monitoring will be limited")
    
    def start_monitoring(self) -> bool:
        """
        Start active resource monitoring.
        
        Returns:
            True if monitoring started successfully, False otherwise.
        """
        if not HAS_PSUTIL:
            logger.warning("psutil not available, cannot start active monitoring")
            return False
        
        if self.active_monitoring:
            return True  # Already monitoring
        
        self.active_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Resource monitoring started")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop active resource monitoring."""
        self.active_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
            logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Internal monitoring loop."""
        while self.active_monitoring:
            try:
                self.current_usage = self._get_resource_usage()
                # Log if approaching limits
                cpu_usage = self.current_usage.get("cpu", 0)
                memory_usage = self.current_usage.get("memory", 0)
                
                if cpu_usage > (self.cpu_limit * 0.9):
                    logger.warning(f"High CPU usage: {cpu_usage:.1f}%", {"resource": "cpu"})
                
                if memory_usage > (self.memory_limit * 0.9):
                    logger.warning(f"High memory usage: {memory_usage} MB", {"resource": "memory"})
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {str(e)}")
                time.sleep(self.monitoring_interval * 2)  # Back off on error
    
    def _get_resource_usage(self) -> Dict[str, float]:
        """
        Get current resource usage.
        
        Returns:
            A dictionary with current CPU and memory usage.
        """
        usage = {"cpu": 0.0, "memory": 0}
        
        if HAS_PSUTIL:
            # Get CPU usage
            usage["cpu"] = psutil.cpu_percent(interval=0.1)
            
            # Get memory usage (in MB)
            memory_info = psutil.Process(os.getpid()).memory_info()
            usage["memory"] = memory_info.rss / (1024 * 1024)  # Convert to MB
            
            # Get additional metrics
            usage["memory_percent"] = psutil.virtual_memory().percent
            usage["disk_usage"] = psutil.disk_usage('/').percent
            usage["open_files"] = len(psutil.Process(os.getpid()).open_files())
        else:
            # Fallback to basic metrics
            usage["cpu"] = 0.0  # Can't measure without psutil
            usage["memory"] = 0  # Can't measure without psutil
        
        return usage
    
    def get_current_usage(self) -> Dict[str, float]:
        """
        Get current resource usage.
        
        Returns:
            A dictionary with current resource usage.
        """
        # If not actively monitoring, get current usage
        if not self.active_monitoring:
            self.current_usage = self._get_resource_usage()
        
        return self.current_usage
    
    def is_resource_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if resources are available for processing.
        
        Returns:
            A tuple of (is_available, reason), where reason is None if resources are available.
        """
        # Get current usage
        usage = self.get_current_usage()
        
        # Check CPU usage
        if usage.get("cpu", 0) > self.cpu_limit:
            return False, f"CPU usage too high: {usage.get('cpu', 0):.1f}% > {self.cpu_limit:.1f}%"
        
        # Check memory usage
        if usage.get("memory", 0) > self.memory_limit:
            return False, f"Memory usage too high: {usage.get('memory', 0):.1f} MB > {self.memory_limit} MB"
        
        return True, None
    
    def set_resource_limits(self, cpu_limit: Optional[float] = None, memory_limit: Optional[int] = None) -> None:
        """
        Set resource limits.
        
        Args:
            cpu_limit: Maximum CPU usage percentage (0-100).
            memory_limit: Maximum memory usage in MB.
        """
        if cpu_limit is not None:
            self.cpu_limit = max(0.0, min(100.0, cpu_limit))
        
        if memory_limit is not None:
            self.memory_limit = max(0, memory_limit)
        
        logger.info(
            f"Resource limits updated: CPU {self.cpu_limit:.1f}%, Memory {self.memory_limit} MB"
        )
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """
        Get a summary of resource usage and limits.
        
        Returns:
            A dictionary with resource usage summary.
        """
        usage = self.get_current_usage()
        
        return {
            "current": {
                "cpu_percent": usage.get("cpu", 0),
                "memory_mb": usage.get("memory", 0),
                "memory_percent": usage.get("memory_percent", 0),
                "disk_usage_percent": usage.get("disk_usage", 0),
                "open_files": usage.get("open_files", 0)
            },
            "limits": {
                "cpu_percent": self.cpu_limit,
                "memory_mb": self.memory_limit
            },
            "utilization": {
                "cpu_percent": (usage.get("cpu", 0) / self.cpu_limit) * 100 if self.cpu_limit > 0 else 0,
                "memory_percent": (usage.get("memory", 0) / self.memory_limit) * 100 if self.memory_limit > 0 else 0
            },
            "monitoring_active": self.active_monitoring
        }


# Global resource monitor instance
resource_monitor = ResourceMonitor()