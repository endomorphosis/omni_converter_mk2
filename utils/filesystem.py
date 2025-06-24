"""
Filesystem utility functions for the Omni-Converter.

This module provides filesystem utility functions for the Omni-Converter,
including file reading, writing, and information retrieval.
"""
from dataclasses import dataclass
import glob
import magic
import mimetypes
import os
from datetime import datetime
from typing import Any, Optional


from pydantic import BaseModel, Field, BeforeValidator, FilePath, PositiveInt


def _determine_mime_type(path_or_bytes: str | bytes | None) -> Optional[str]:
    """Determine the MIME type of a file.
    
    Args:
        file_path: The path to the file.
        
    Returns:
        The MIME type of the file.
    """
    match path_or_bytes:
        case str():
            try:
                return magic.from_file(path_or_bytes, mime=True)
            except Exception:
                return mimetypes.guess_type(path_or_bytes)[0] or 'application/octet-stream'
        case bytes():
            try:
                return magic.from_buffer(path_or_bytes, mime=True)
            except (ImportError, Exception):
                return 'application/octet-stream'
        case _:
            return None


class FileInfo(BaseModel):
    """
    Information about a file.
    
    Attributes:
        path (str): The path to the file.
        size (int): The size of the file in bytes.
        modified_time (datetime): The time the file was last modified.
        mime_type (str): The MIME type of the file.
        extension (str): The file extension.
        is_readable (bool): Whether the file is readable.
        is_writable (bool): Whether the file is writable.
    """
    path: FilePath = Field(description="The absolute path to the file")
    size: PositiveInt = Field(description="The size of the file in bytes")
    modified_time: datetime = Field(description="The time the file was last modified")
    mime_type: Optional[str] = Field(None, description="The MIME type of the file")
    extension: str = Field(description="The file extension")
    is_readable: bool = Field(description="Whether the file is readable")
    is_writable: bool = Field(description="Whether the file is writable")


    @classmethod
    def from_path(cls, path: str) -> 'FileInfo':
        """
        Create FileInfo from a file path.
        
        Args:
            path: The path to the file.
            
        Returns:
            FileInfo instance with populated data.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        abs_path = os.path.abspath(path)
        size = os.path.getsize(path)
        modified_time = datetime.fromtimestamp(os.path.getmtime(path))
        mime_type = _determine_mime_type(path)
        extension = os.path.splitext(path)[1].lstrip('.')
        is_readable = os.access(path, os.R_OK)
        is_writable = os.access(path, os.W_OK)
        
        return cls(
            path=abs_path,
            size=size,
            modified_time=modified_time,
            mime_type=mime_type,
            extension=extension,
            is_readable=is_readable,
            is_writable=is_writable
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary containing the file information.
        """
        return {
            'path': self.path,
            'size': self.size,
            'modified_time': self.modified_time.isoformat(),
            'mime_type': self.mime_type,
            'extension': self.extension,
            'is_readable': self.is_readable,
            'is_writable': self.is_writable
        }



class FileContent:
    """
    Content of a file.
    
    Attributes:
        raw_content (bytes): The raw binary content of the file.
        text_content (str): The text content of the file, if applicable.
        encoding (str): The encoding of the text content.
        size (int): The size of the content in bytes.
        mime_type (str): The MIME type of the content.
    """
    def __init__(
        self, 
        raw_content: bytes, 
        encoding: str = 'utf-8', 
        mime_type: Optional[str] = None
    ):
        """
        Initialize file content.
        
        Args:
            raw_content: The raw binary content of the file.
            encoding: The encoding to use for text conversion.
            mime_type: The MIME type of the content. If None, will be guessed from content.
        """
        self.raw_content = raw_content
        self.encoding = encoding
        self.size = len(raw_content)
        
        # Determine MIME type if not provided
        if mime_type is None:
            try:
                import magic
                self.mime_type = magic.from_buffer(raw_content, mime=True)
            except (ImportError, Exception):
                self.mime_type = 'application/octet-stream'
        else:
            self.mime_type = mime_type
        
        # Convert to text if possible
        try:
            self.text_content = raw_content.decode(encoding)
        except UnicodeDecodeError:
            self.text_content = ''
    
    def get_as_text(self, encoding: Optional[str] = None) -> str:
        """
        Get the content as text.
        
        Args:
            encoding: The encoding to use. If None, uses the current encoding.
            
        Returns:
            The content as text.
        """
        if encoding and encoding != self.encoding:
            try:
                return self.raw_content.decode(encoding)
            except UnicodeDecodeError:
                return self.text_content
        return self.text_content
    
    @property
    def as_binary(self) -> bytes:
        """
        Get the content as binary.
        
        Returns:
            The raw binary content.
        """
        return self.raw_content


class FileSystem:
    """
    File system utility functions.
    
    Provides functions for file reading, writing, and information retrieval.
    """
    
    @staticmethod
    def read_file(file_path: str, mode: str = 'rb') -> FileContent:
        """
        Read a file.
        
        Args:
            file_path: The path to the file.
            mode: The mode to open the file in. Default is binary mode.
            
        Returns:
            The file content.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read.
        """
        # Ensure the path is absolute
        file_path = os.path.abspath(file_path)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if the file is readable
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied for file: {file_path}")
        
        # Determine the MIME type
        try:
            mime_type = magic.from_file(file_path, mime=True)
        except Exception:
            mime_type = None
        
        # Read the file
        with open(file_path, mode) as f:
            content = f.read()
        
        # If the mode is text mode, convert the content to bytes
        if 'b' not in mode and isinstance(content, str):
            encoding = 'utf-8'  # Default encoding
            content = content.encode(encoding)
            return FileContent(content, encoding, mime_type)
        
        return FileContent(content, 'utf-8', mime_type)
    
    @staticmethod
    def write_file(file_path: str, content: str | bytes, mode: str = 'wb') -> bool:
        """
        Write to a file.
        
        Args:
            file_path: The path to the file.
            content: The content to write.
            mode: The mode to open the file in. Default is binary mode.
            
        Returns:
            True if the file was written successfully, False otherwise.
            
        Raises:
            PermissionError: If the file cannot be written.
        """
        # Ensure the path is absolute
        file_path = os.path.abspath(file_path)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert string content to bytes if in binary mode
        if 'b' in mode and isinstance(content, str):
            content = content.encode('utf-8')
        
        # Convert bytes content to string if in text mode
        if 'b' not in mode and isinstance(content, bytes):
            content = content.decode('utf-8')
        
        try:
            with open(file_path, mode) as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def list_files(directory: str, pattern: str = '*.*') -> list[str]:
        """
        list files in a directory.
        
        Args:
            directory: The directory to list files in.
            pattern: The pattern to match files against.
            
        Returns:
            A list of file paths matching the pattern.
            
        Raises:
            FileNotFoundError: If the directory does not exist.
            PermissionError: If the directory cannot be read.
        """
        # Ensure the path is absolute
        directory = os.path.abspath(directory)
        
        # Check if the directory exists
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Check if the directory is readable
        if not os.access(directory, os.R_OK):
            raise PermissionError(f"Cannot read directory: {directory}")
        
        # list files matching the pattern
        return sorted(glob.glob(os.path.join(directory, pattern)))
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file exists, False otherwise.
        """
        # Ensure the path is absolute
        file_path = os.path.abspath(file_path)
        
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod
    def get_file_info(path: str) -> FileInfo:
        """
        Get information about a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            File information.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        # Ensure the path is absolute
        path = os.path.abspath(path)
        
        return FileInfo.from_path(path)
    
    @staticmethod
    def create_directory(directory_path: str) -> bool:
        """
        Create a directory.
        
        Args:
            directory_path: The path to the directory.
            
        Returns:
            True if the directory was created successfully, False otherwise.
        """
        # Ensure the path is absolute
        directory_path = os.path.abspath(directory_path)
        
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False
