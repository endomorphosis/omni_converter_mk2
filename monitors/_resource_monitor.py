"""
Resource monitor module for the Omni-Converter.

This module provides the ResourceMonitor class for monitoring and managing system resources.
"""
import time
import threading
from typing import Any, Callable, Optional


from types_ import Configs, Logger
from utils.common.try_except_decorator import try_except


class ResourceMonitor:
    """
    Resource monitor for the Omni-Converter.

    This class monitors system resources such as CPU and memory usage, and
    provides methods to check if resources are available for processing.

    Attributes:
        cpu_limit_percent (float): Maximum CPU usage percentage (0-100).
        memory_limit (int): Maximum memory usage in MB.
        current_usage (dict[str, float]): Current resource usage.
        active_monitoring (bool): Whether active monitoring is enabled.
        monitoring_thread: Thread for active monitoring.
        monitoring_interval (float): Interval for active monitoring in seconds.
    """
    def __init__(
        self,
        configs: Configs = None,
        resources: dict[str, Callable] = None,
    ):
        """
        Initialize a resource monitor.

        Args:
            cpu_limit_percent: Maximum CPU usage percentage (0-100).
            memory_limit: Maximum memory usage in MB.
            monitoring_interval: Interval for active monitoring in seconds.
        """
        self.configs = configs
        self.resources = resources

        # Load resource limits from configs
        self.cpu_limit_percent: float = self.configs.resources.cpu_limit_percent
        self.memory_limit: float = self.configs.resources.memory_limit_mb
        self.monitoring_interval: float = self.configs.resources.monitoring_interval_seconds

        # Initialize resource usage methods
        self._get_cpu_usage:                 Callable = self.resources['get_cpu_usage']
        self._get_virtual_memory_in_percent: Callable = self.resources['get_virtual_memory_in_percent']
        self._get_memory_info:               Callable = self.resources['get_memory_info']
        self._get_memory_rss_usage_in_mb:    Callable = self.resources['get_memory_rss_usage_in_mb']
        self._get_memory_vms_usage_in_mb:    Callable = self.resources['get_memory_vms_usage_in_mb']
        self._get_disk_usage_in_percent:     Callable = self.resources['get_disk_usage']
        self._get_num_open_files:            Callable = self.resources['get_open_files']
        self._get_shared_memory_usage_in_mb: Callable = self.resources['get_shared_memory_usage_in_mb']
        self._get_memory_percent:            Callable = self.resources['get_virtual_memory_in_percent']

        self._logger: Logger = self.resources['logger']
        self.active_monitoring = False
        self.monitoring_thread = None
        self._current_usage: dict = {"cpu": 0.0, "memory": 0}

    def start_monitoring(self) -> bool:
        """Start active resource monitoring.

        Returns:
            True if monitoring started successfully, False otherwise.
        """
        if self.active_monitoring:
            return True  # Already monitoring

        self.active_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self._logger.info("Resource monitoring started")
        return True

    def stop_monitoring(self) -> None:
        """Stop active resource monitoring."""
        self.active_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
            self._logger.info("Resource monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Internal monitoring loop."""
        while self.active_monitoring:
            try:
                self.current_usage = self._get_resource_usage()
                # Log if approaching limits
                cpu_usage = self.current_usage.get("cpu", 0)
                memory_usage = self.current_usage.get("memory", 0)

                if cpu_usage > (self.cpu_limit_percent * 0.9): # TODO Verify why 0.9
                    self._logger.warning(f"High CPU usage: {cpu_usage:.1f}%")

                if memory_usage > (self.memory_limit * 0.9):
                    self._logger.warning(f"High memory usage: {memory_usage} MB")

                time.sleep(self.monitoring_interval)
            except Exception as e:
                self._logger.error(f"Error in resource monitoring: {e}")
                time.sleep(self.monitoring_interval * 2)  # Back off on error

    def _get_resource_usage(self) -> dict[str, float]:
        """
        Get current resource usage.

        Returns:
            A dictionary with current CPU and memory usage.
        """
        return {
            "cpu": self._get_cpu_usage(), 
            "memory": self._get_memory_rss_usage_in_mb(),
            "memory_percent": self._get_memory_percent(),
            "disk_usage": self._get_disk_usage_in_percent(),
            "open_files": self._get_num_open_files(),
            "shared_memory": self._get_shared_memory_usage_in_mb()
        }

    @property
    def current_usage(self) -> dict[str, float]:
        """
        Get current resource usage.

        Returns:
            A dictionary with current resource usage.
        """
        # If not actively monitoring, get current usage
        if not self.active_monitoring:
            self._current_usage = self._get_resource_usage()

        return self._current_usage

    @try_except(raise_=False,msg='Error getting detailed memory information')
    def _log_detailed_memory_information_for_debug_purposes(self):
        # Log detailed memory usage
        self._logger.debug(
            f"Memory usage details"
            f"RSS={self._get_memory_rss_usage_in_mb():.1f}MB, "
            f"VMS={self._get_memory_vms_usage_in_mb():.1f}MB, "
            f"Shared={self._get_shared_memory_usage_in_mb():.1f}MB, "
            f"System={self._get_memory_percent():.1f}%, "
            f"Limit={self.memory_limit}MB"
        )

        usage = self.current_usage
        # Check for memory leak indicators
        if usage.get("memory", 0) > (self.memory_limit * 0.8):
            self._logger.warning(
                f"Memory usage approaching limit: {usage.get('memory', 0):.1f}MB/{self.memory_limit}MB "
                f"({100 * usage.get('memory', 0)/self.memory_limit:.1f}%)"
            )

    @property # NOTE We purposefully don't cache this property, as we always want the latest usage
    def is_resource_available(self) -> tuple[bool, Optional[str]]:
        """
        Check if resources are available for processing.

        Returns:
            A tuple of (is_available, reason), where reason is None if resources are available.
        """
        # Get current usage
        usage = self.current_usage

        # Log detailed memory information for debugging purposes
        self._log_detailed_memory_information_for_debug_purposes()

        # Check CPU usage
        if usage.get("cpu", 0) > self.cpu_limit_percent:
            return False, f"CPU usage too high: {usage.get('cpu', 0):.1f}% > {self.cpu_limit_percent:.1f}%"

        # Check memory usage
        if usage.get("memory", 0) > self.memory_limit:
            return False, f"Memory usage too high: {usage.get('memory', 0):.1f}MB > {self.memory_limit}MB"
        
        return True, None

    def set_resource_limits(self, cpu_limit_percent: Optional[float] = None, memory_limit: Optional[int] = None) -> None:
        """
        Set resource limits.

        Args:
            cpu_limit_percent: Maximum CPU usage percentage (0-100).
            memory_limit: Maximum memory usage in MB.
        """
        if cpu_limit_percent is not None:
            self.cpu_limit_percent = max(0.0, min(100.0, cpu_limit_percent))

        if memory_limit is not None:
            self.memory_limit = max(0, memory_limit)

        self._logger.info(
            f"Resource limits updated: CPU {self.cpu_limit_percent:.1f}%, Memory {self.memory_limit} MB"
        )

    @property
    def resource_summary(self) -> dict[str, Any]:
        """
        Get a summary of resource usage and limits.

        Returns:
            A dictionary with resource usage summary.
        """
        usage = self.current_usage

        return {
            "current": {
                "cpu_percent": usage.get("cpu", 0),
                "memory_mb": usage.get("memory", 0),
                "memory_percent": usage.get("memory_percent", 0),
                "disk_usage_percent": usage.get("disk_usage", 0),
                "open_files": usage.get("open_files", 0)
            },
            "limits": {
                "cpu_percent": self.cpu_limit_percent,
                "memory_mb": self.memory_limit
            },
            "utilization": {
                "cpu_percent": (usage.get("cpu", 0) / self.cpu_limit_percent) * 100 if self.cpu_limit_percent > 0 else 0,
                "memory_percent": (usage.get("memory", 0) / self.memory_limit) * 100 if self.memory_limit > 0 else 0
            },
            "monitoring_active": self.active_monitoring
        }


