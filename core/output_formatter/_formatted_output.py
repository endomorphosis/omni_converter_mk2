from dataclasses import dataclass, field
import os
from typing import Any, Optional


@dataclass
class FormattedOutput:
    """
    Formatted output for writing to a file or displaying.
    
    This class represents the formatted output from processing a file,
    ready to be written to a file or displayed.
    
    Attributes:
        content (str): The formatted content.
        format (str): The format of the output.
        metadata (dict[str, Any]): Metadata about the output.
        output_path (str): The path where the output will be written.
    """
    content: str
    format: str
    metadata: dict[str, Any] = field(default_factory=dict)
    output_path: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the formatted output.
        """
        return {
            'content': self.content,
            'format': self.format,
            'metadata': self.metadata,
            'output_path': self.output_path
        }
    
    def write_to_file(self, output_path: Optional[str] = None) -> str:
        """
        Write the formatted output to a file.
        
        Args:
            output_path: The path to write to. If None, the output_path attribute is used.
            
        Returns:
            The path where the output was written.
            
        Raises:
            ValueError: If no output path is specified.
            IOError: If the file cannot be written.
        """
        path = output_path or self.output_path
        if not path:
            raise ValueError("No output path specified")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        
        # Write the output
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        
        return path