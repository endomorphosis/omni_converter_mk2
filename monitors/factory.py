import atexit
from configs import configs
from logger import logger
from utils.resource_monitor.dependencies.psutil import PsUtil


from ._resource_monitor import ResourceMonitor
from .security_monitor import SecurityMonitor, SecurityResult, SanitizedContent
from ._error_monitor import ErrorMonitor

from ._monitor_constants import Constants

import datetime
import traceback


def make_resource_monitor() -> ResourceMonitor:
    resources = {
        "get_cpu_usage": PsUtil._get_cpu_usage,
        "get_virtual_memory_in_percent": PsUtil._get_virtual_memory_in_percent,
        "get_memory_info": PsUtil._get_memory_info,
        "get_memory_rss_usage_in_mb": PsUtil._get_memory_rss_usage_in_mb,
        "get_memory_vms_usage_in_mb": PsUtil._get_memory_vms_usage_in_mb,
        "get_disk_usage": PsUtil._get_disk_usage_in_percent,
        "get_open_files": PsUtil._get_num_open_files,
        "get_shared_memory_usage_in_mb": PsUtil._get_shared_memory_usage_in_mb,
        "logger": logger,
    }
    return ResourceMonitor(resources=resources,configs=configs)

def make_error_monitor() -> ErrorMonitor:
    resources = {
        "logger": logger,
        "traceback": traceback,
        "datetime": datetime,
    }
    error_monitor = ErrorMonitor(resources=resources, configs=configs)
    # Register core_dump function to run on an unexpected exit.
    atexit.register(error_monitor.core_dump)
    return error_monitor

def make_security_monitor() -> SecurityMonitor:
    """
    Create a security monitor instance.
    
    Args:
        resources: Optional dictionary of resources for the security monitor.
        configs: Optional configuration object.
        
    Returns:
        An instance of SecurityMonitor.
    """
    resources = {
        "dangerous_patterns": Constants.SecurityMonitor.DANGEROUS_PATTERNS_REGEX,
        "executable_extensions": Constants.SecurityMonitor.EXECUTABLE_EXTENSIONS,
        "file_size_limits_in_bytes": Constants.SecurityMonitor.FILE_SIZE_LIMITS_IN_BYTES,
        "format_names": Constants.SecurityMonitor.FORMAT_NAMES,
        "pii_detection_regex": Constants.SecurityMonitor.PII_DETECTION_REGEX,
        "remove_active_content_regex": Constants.SecurityMonitor.REMOVE_ACTIVE_CONTENT_REGEX,
        "remove_scripts_regex": Constants.SecurityMonitor.REMOVE_SCRIPTS_REGEX,
        "security_rules": Constants.SecurityMonitor.SECURITY_RULES,
        "sensitive_keys": Constants.SecurityMonitor.SENSITIVE_KEYS,
        "security_result": SecurityResult,
        "sanitized_content": SanitizedContent,
        "logger": logger,
    }

    return SecurityMonitor(resources=resources, configs=configs)
