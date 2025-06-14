from typing import Any


try:
    from pydantic import BaseModel, PositiveInt, FilePath
except ImportError:
    raise ImportError("Pydantic is required for this module. Please install it using 'pip install pydantic'.")


class PipelineStatus(BaseModel):
    """
    Status of the processing pipeline.
    
    This class represents the current status of the processing pipeline,
    including statistics and the current state.
    
    Attributes:
        total_files (int): Total number of files processed.
        successful_files (int): Number of files processed successfully.
        failed_files (int): Number of files that failed processing.
        current_file (str): Path to the file currently being processed.
        is_processing (bool): Whether the pipeline is currently processing a file.
    """
    total_files: PositiveInt = 0
    successful_files: PositiveInt = 0
    failed_files: PositiveInt = 0
    current_file: FilePath = ""
    is_processing: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the pipeline status.
        """
        return self.model_dump()
