import os
from typing import NamedTuple

try:
    import psutil
except ImportError:
    raise ImportError(
        "psutil is not installed. Please install it using 'pip install psutil'."
    )

_PID = os.getpid()

class PsUtil:
    """
    PsUtil is a utility class that provides static methods to monitor system and process resource usage.

    Methods:
        _get_cpu_usage() -> float:
            Returns the CPU usage percentage over a short interval.

        _get_virtual_memory_in_percent() -> float:
            Returns the percentage of virtual memory currently in use.

        _get_memory_info() -> NamedTuple:
            Returns detailed memory information of the current process.

        _get_memory_rss_usage_in_mb() -> float:
            Returns the Resident Set Size (RSS) memory usage of the current process in megabytes.

        _get_memory_vms_usage_in_mb() -> float:
            Returns the Virtual Memory Size (VMS) usage of the current process in megabytes.

        _get_disk_usage_in_percent() -> float:
            Returns the percentage of disk usage for the root directory.

        _get_num_open_files() -> int:
            Returns the number of open file descriptors for the current process.

        _get_shared_memory_usage_in_mb() -> float:
            Returns the shared memory usage of the current process in megabytes, if available.
    """

    @staticmethod
    def _get_cpu_usage() -> float:
        return psutil.cpu_percent(interval=0.1)

    @staticmethod
    def _get_virtual_memory_in_percent() -> float:
        return psutil.virtual_memory().percent

    @staticmethod
    def _get_memory_info() -> NamedTuple:
        return psutil.Process(_PID).memory_info()

    @staticmethod
    def _get_memory_rss_usage_in_mb() -> float:
        return psutil.Process(_PID).memory_info().rss / (1024 * 1024)

    @staticmethod
    def _get_memory_vms_usage_in_mb() -> float:
        return psutil.Process(_PID).memory_info().vms / (1024 * 1024)

    @staticmethod
    def _get_disk_usage_in_percent() -> float:
        return psutil.disk_usage('/').percent

    @staticmethod
    def _get_num_open_files() -> int:
        return len(psutil.Process(_PID).open_files())

    @staticmethod
    def _get_shared_memory_usage_in_mb() -> float:
        mem_info = psutil.Process(_PID).memory_info()
        return getattr(mem_info, 'shared', 0) / (1024 * 1024)

