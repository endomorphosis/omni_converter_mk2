from pathlib import Path
from typing import Optional, Any


from ._python_api import PythonAPI


class Convert(PythonAPI):
    """
    Public class for object-oriented access to the Omni-Converter.
    Similar to Pathlib's Path class, this class provides extensions to the API to make it
    certain operations more idiomatic and efficient.

    Methods:
        - walk_and_convert: Walk through a directory and convert all files.
        - estimate_file_count: Estimate the number of files in a directory that can potentially be converted.
        - convert: Convert a file or directory to text.
        - 
    """
    from configs import configs
    from batch_processor import make_batch_processor
    from monitors import make_resource_monitor

    def __init__(self, path=None, *args, **kwargs):
        """
        Initialize the Convert class.
        
        Args:
            args: Positional arguments for PythonAPI.
            kwargs: Keyword arguments for PythonAPI.
        """
        resources = {
            "batch_processor": self.make_batch_processor(),
            "resource_monitor": self.make_resource_monitor(),
        }
        super().__init__(resources=resources, configs=self.configs)
        
        self.target_file = None
        self.target_dir = None

        if path:
            path = Path(path)
            if path.is_file():
                self.target_file = path
            elif path.is_dir():
                self.target_dir = path
            else:
                raise ValueError(f"Invalid path: {path}. Must be a valid file or directory.")

    def walk_and_convert(self, path: str = None, recursive: bool = False) -> None:
        """
        Walk through a directory and convert all files.
        
        Args:
            path: The path to the directory to convert. If None, uses the current target directory.
            recursive: Whether to walk through subdirectories. Default is False.
        """
        # TODO Implement walk_and_convert method
        pass

    def estimate_file_count(self, path: str = None, recursive: bool = False) -> int:
        """
        Estimate the number of files in a directory that can potentially be converted.
        
        Args:
            path: The path to the directory to convert. If None, uses the current target directory.
            recursive: Whether to walk through subdirectories. Default is False.
        """
        # TODO Implement estimate_file_count method
        pass
    
    def convert(self, path: str = None, output_path: str = None, options: Optional[dict[str, Any]] = None) -> Any:
        """
        Convert a file or directory to text.
        
        Args:
        """
        file_path = path or self.target_file
        return super().convert_file(
            file_path=file_path,
            output_path=output_path,
            options=options
        )
