"""
Batch result module for the Omni-Converter.

This module provides the BatchResult class for tracking the results of batch processing operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from core.processing_result import ProcessingResult


@dataclass
class BatchResult:
    """
    Result of batch processing multiple files.
    
    This class represents the result of processing a batch of files, including overall
    statistics and individual file results.
    
    Attributes:
        total_files (int): Total number of files in the batch.
        successful_files (int): Number of files processed successfully.
        failed_files (int): Number of files that failed processing.
        results (List[ProcessingResult]): List of individual file processing results.
        statistics (Dict[str, Any]): Additional statistics about the batch processing.
        start_time (datetime): Time when the batch processing started.
        end_time (datetime): Time when the batch processing ended.
    """
    results: List[ProcessingResult] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_files: int = field(init=False)
    successful_files: int = field(init=False)
    failed_files: int = field(init=False)
    
    def __post_init__(self):
        # Handle start_time if it's a timestamp
        if not isinstance(self.start_time, datetime):
            self.start_time = datetime.fromtimestamp(self.start_time)
        
        # Calculate counts
        self.total_files = len(self.results)
        self.successful_files = sum(1 for r in self.results if r.success)
        self.failed_files = sum(1 for r in self.results if not r.success)
    
    def add_result(self, result: ProcessingResult) -> None:
        """
        Add a file processing result to the batch.
        
        Args:
            result: The file processing result to add.
        """
        self.results.append(result)
        
        # Update counts
        self.total_files += 1
        if result.success:
            self.successful_files += 1
        else:
            self.failed_files += 1
    
    def complete(self) -> None:
        """Mark the batch processing as complete."""
        self.end_time = datetime.now()
        
        # Update statistics
        self.statistics['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
        self.statistics['success_rate'] = (
            (self.successful_files / self.total_files) * 100 if self.total_files > 0 else 0
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the batch processing.
        
        Returns:
            A dictionary with summary information.
        """
        return {
            'total_files': self.total_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'success_rate_percent': (
                (self.successful_files / self.total_files) * 100 if self.total_files > 0 else 0
            ),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': (
                (self.end_time - self.start_time).total_seconds() 
                if self.end_time and self.start_time else None
            ),
            'statistics': self.statistics
        }
    
    def get_failed_files(self) -> List[str]:
        """
        Get a list of files that failed processing.
        
        Returns:
            A list of paths to failed files.
        """
        return [r.file_path for r in self.results if not r.success]
    
    def get_successful_files(self) -> List[str]:
        """
        Get a list of files that were processed successfully.
        
        Returns:
            A list of paths to successfully processed files.
        """
        return [r.file_path for r in self.results if r.success]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the batch result.
        """
        return {
            'total_files': self.total_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'results': [r.to_dict() for r in self.results],
            'statistics': self.statistics,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def __str__(self) -> str:
        """
        Get a string representation of the batch result.
        
        Returns:
            A string representation of the batch result.
        """
        duration = (
            (self.end_time - self.start_time).total_seconds() 
            if self.end_time and self.start_time else None
        )
        
        success_rate = (
            f"{(self.successful_files / self.total_files) * 100:.1f}%" 
            if self.total_files > 0 else "N/A"
        )
        
        if duration is not None:
            duration_str = f"  Duration: {duration:.2f} seconds"
        else:
            duration_str = "  Status: In Progress"
        
        return (
            f"Batch Processing Result:\n"
            f"  Total Files: {self.total_files}\n"
            f"  Successful: {self.successful_files}\n"
            f"  Failed: {self.failed_files}\n"
            f"  Success Rate: {success_rate}\n"
            f"{duration_str}"
        )