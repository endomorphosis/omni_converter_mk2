"""
Logging utility for the Omni-Converter.

This module provides logging functionality for the Omni-Converter.
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


from pydantic import BaseModel, Field


def get_logger(name: str,
                log_file_name: str = 'app.log',
                level: int = logging.INFO,
                max_size: int = 5*1024*1024,
                backup_count: int = 3
                ) -> logging.Logger:
    """Sets up a logger with both file and console handlers.

    Args:
        name: Name of the logger.
        log_file_name: Name of the log file. Defaults to 'app.log'.
        level: Logging level. Defaults to logging.INFO.
        max_size: Maximum size of the log file before it rotates. Defaults to 5MB.
        backup_count: Number of backup files to keep. Defaults to 3.

    Returns:
        Configured logger.

    Example:
        # Usage
        logger = get_logger(__name__)
    """
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    console_handler = logging.StreamHandler()

    # Create 'logs' directory in the current working directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, log_file_name)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=max_size, backupCount=backup_count)

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


class LogRecord(BaseModel):
    """
    A record of a log message.
    
    Attributes:
        level (str): The log level.
        message (str): The log message.
        context (dict): Additional context for the log.
        timestamp (datetime): The time the log was created.
        source (str): The source of the log.
    """
    level: str
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=datetime.now().isoformat)
    source: Optional[str] = Field(default='unknown')

    @property 
    def string(self) -> str:
        """
        Convert to a string.
        
        Returns:
            A string representation of the log record.
        """
        # Format the context as a string
        context_str = ''
        if self.context:
            try:
                context_str = ' ' + json.dumps(self.context)
            except (TypeError, ValueError):
                # Fall back to simple string representation
                context_str = ' ' + str(self.context)
        
        return f"{self.timestamp} [{self.level}] {self.source}: {self.message}{context_str}"
    
    @property
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the log record.
        """
        return {
            'level': self.level,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp,
            'source': self.source
        }


class Logger:
    """
    Logger for the Omni-Converter.
    
    Handles logging messages to file and console.
    
    Attributes:
        log_level (str): The minimum log level to record.
        log_file (str): The path to the log file.
        console_output (bool): Whether to output logs to the console.
        log_formatters (dict): Custom formatters for different log levels.
    """
    
    # Log levels in order of severity
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(
        self, 
        log_level: str = 'INFO', 
        log_file: Optional[str] = None, 
        console_output: bool = True
    ):
        """
        Initialize the logger.
        
        Args:
            log_level: The minimum log level to record.
            log_file: The path to the log file. If None, logs are not written to a file.
            console_output: Whether to output logs to the console.
        """
        self.log_level = log_level.upper()
        self.log_file = log_file
        self.console_output = console_output
        
        # Custom formatters for different log levels
        self.log_formatters: Dict[str, Optional[callable]] = {
            'DEBUG': None,
            'INFO': None,
            'WARNING': None,
            'ERROR': None,
            'CRITICAL': None
        }
        
        # Create the log file directory if it doesn't exist
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Set up Python's built-in logging
        self._setup_python_logging()
    
    def _setup_python_logging(self) -> None:
        """Set up Python's built-in logging."""
        # Map our log level to Python's log level
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        # Configure root logger
        logging.basicConfig(
            level=level_map.get(self.log_level, logging.INFO),
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
            filename=self.log_file,
            filemode='a'
        )
        
        # Add console handler if needed
        if self.console_output and self.log_file:
            console = logging.StreamHandler()
            console.setLevel(level_map.get(self.log_level, logging.INFO))
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
    
    def _should_log(self, level: str) -> bool:
        """
        Check if a message with the given level should be logged.
        
        Args:
            level: The log level to check.
            
        Returns:
            Whether the message should be logged.
        """
        return self.LOG_LEVELS.index(level) >= self.LOG_LEVELS.index(self.log_level)
    
    def _write_to_file(self, record: LogRecord) -> None:
        """
        Write a log record to the log file.
        
        Args:
            record: The log record to write.
        """
        if not self.log_file:
            return
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(record.string() + '\n')
        except Exception:
            # Fall back to Python's built-in logging
            logging.error(f"Failed to write to log file: {self.log_file}")
            logging.log(
                getattr(logging, record.level, logging.INFO),
                record.message,
                extra={'source': record.source, 'context': record.context}
            )
    
    def _write_to_console(self, record: LogRecord) -> None:
        """
        Write a log record to the console.
        
        Args:
            record: The log record to write.
        """
        if not self.console_output:
            return
        
        # Use Python's built-in logging for console output
        logging.log(
            getattr(logging, record.level, logging.INFO),
            record.message,
            extra={'source': record.source, 'context': record.context}
        )
    
    def log(self, 
            level: str, 
            message: str, 
            context: Optional[Dict[str, Any]] = None, 
            source: Optional[str] = None
            ) -> None:
        """
        Log a message.
        
        Args:
            level: The log level.
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        level = level.upper()
        if not self._should_log(level):
            return
        
        # Create the log record
        record = LogRecord(level=level, message=message, context=context, source=source)

        # Apply custom formatter if one exists
        formatter = self.log_formatters.get(level)
        if formatter:
            record = formatter(record)
        
        # Write to file and console
        self._write_to_file(record)
        self._write_to_console(record)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        self.log('DEBUG', message, context, source)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Log an info message.
        
        Args:
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        self.log('INFO', message, context, source)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Log a warning message.
        
        Args:
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        self.log('WARNING', message, context, source)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        self.log('ERROR', message, context, source)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Log a critical message.
        
        Args:
            message: The log message.
            context: Additional context for the log.
            source: The source of the log.
        """
        self.log('CRITICAL', message, context, source)
    
    def set_log_level(self, level: str) -> None:
        """
        Set the minimum log level to record.
        
        Args:
            level: The log level.
        """
        self.log_level = level.upper()
    
    def set_log_file(self, file_path: Optional[str]) -> None:
        """
        Set the log file path.
        
        Args:
            file_path: The path to the log file. If None, logs are not written to a file.
        """
        self.log_file = file_path
        
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Reconfigure Python's built-in logging
        self._setup_python_logging()
    
    def enable_console_output(self, flag: bool) -> None:
        """
        Enable or disable console output.
        
        Args:
            flag: Whether to output logs to the console.
        """
        self.console_output = flag
        
        # Reconfigure Python's built-in logging
        self._setup_python_logging()


# Global logger instance
#logger = Logger()

logger = get_logger(__name__, log_file_name='app.log', level=logging.DEBUG)

test_logger = get_logger('tests', log_file_name='test.log', level=logging.DEBUG)