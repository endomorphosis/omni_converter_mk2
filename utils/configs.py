"""
Configuration manager for the Omni-Converter.

This module provides a configuration manager that handles loading, saving, and validating
configuration settings for the Omni-Converter.
"""
from pathlib import Path
from typing import Any, Union


from pydantic import BaseModel, DirectoryPath, FilePath, Field, ValidationError
import yaml


from utils.logger import logger


class Paths(BaseModel):
    """
    Paths for important files and directories.

    Attributes:
        THIS_FILE: DirectoryPath: The path to this file (configs.py)
        THIS_DIR: DirectoryPath: The directory containing this file (utils).
        ROOT_DIR: DirectoryPath: The root directory of the project.
        CONFIG_PATH: DirectoryPath: The path to the configuration file (configs.yaml).
    """
    THIS_FILE: DirectoryPath = Path(__file__).resolve()
    THIS_DIR: DirectoryPath = THIS_FILE.parent
    ROOT_DIR: DirectoryPath = THIS_DIR.parent
    CONFIG_PATH: FilePath = ROOT_DIR / 'configs.yaml'


def name(e: Exception) -> str:
    """
    Get the name of the error.

    Returns:
        The name of the error.
    """
    return type(e).__name__

def getitem(cls: BaseModel, key: str) -> Union[str, int, float]:
    try:
        return getattr(cls, key)
    except AttributeError as e:
        raise KeyError(f"Key '{key}' not found in configuration") from e

def setitem(cls: BaseModel, key: str, value: Any) -> None:
    try:
        setattr(cls, key, value)
        cls.model_validate()
    except ValidationError as e:
        raise ValueError(f"Invalid value for key '{key}': {value}") from e
    except TypeError as e:
        raise TypeError(f"Invalid type for key '{key}': {type(value)}") from e
    except AttributeError as e:
        raise KeyError(f"Key '{key}' not found in configuration") from e

class _Resources(BaseModel):
    memory_limit_gb: float = Field(default=6, description="RAM limit in GB")
    cpu_limit_percent: float = Field(default=80, description="CPU utilization limit percentage")
    timeout_seconds: float = Field(default=3600, description="Timeout in seconds")
    batch_size: int = Field(default=100, description="Maximum number of files to process in one batch")

class _Formats(BaseModel):
    text: list[str] = Field(default=["html", "xml", "plain", "calendar", "csv"])
    image: list[str] = Field(default=["jpeg", "png", "gif", "webp", "svg"])
    audio: list[str] = Field(default=["mp3", "wav", "ogg", "flac", "aac"])
    video: list[str] = Field(default=["mp4", "webm", "avi", "mkv", "mov"])
    application: list[str] = Field(default=["pdf", "json", "zip", "docx", "xlsx"])

class _Security(BaseModel):
    max_file_size_mb: float = Field(default=100, description="Maximum file size in MB")
    sandbox_enabled: bool = Field(default=True, description="Enable sandbox for file processing")
    allowed_formats: list[str] = Field(default=[], description="Empty list means all formats are allowed")
    sanitize_output: bool = Field(default=True, description="Sanitize output to remove potential security risks")

class _Processing(BaseModel):
    continue_on_error: bool = Field(default=True, description="Continue processing batch even if some files fail")
    extract_metadata: bool = Field(default=True, description="Extract metadata from files")
    normalize_text: bool = Field(default=True, description="Normalize extracted text")
    quality_threshold: float = Field(default=0.9, description="Minimum quality score for text extraction")
    # TODO Add custom validators for whisper and tesseract models
    whisper_model: str = Field(default="base", description="Whisper model to use for audio processing")
    whisper_language: str = Field(default="en", description="Language for Whisper model")
    tesseract_language: str = Field(default="eng", description="Tesseract model for OCR")

class _Output(BaseModel):
    format: str = Field(default="txt", description="Default output format")
    include_metadata: bool = Field(default=True, description="Include metadata in output")
    preserve_structure: bool = Field(default=True, description="Attempt to preserve document structure")
    encoding: str = Field(default="utf-8", description="Output file encoding")

class Configs(BaseModel):
    resources: _Resources = Field(default_factory=_Resources)
    formats: _Formats = Field(default_factory=_Formats)
    security: _Security = Field(default_factory=_Security)
    processing: _Processing = Field(default_factory=_Processing)
    output: _Output = Field(default_factory=_Output)


class Configs(BaseModel):
    resources: _Resources = Field(default_factory=_Resources)
    formats: _Formats = Field(default_factory=_Formats)
    security: _Security = Field(default_factory=_Security)
    processing: _Processing = Field(default_factory=_Processing)
    output: _Output = Field(default_factory=_Output)

    def get_config_value(self, key: str, default: Any) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The key to get the value for, using dot notation for nested keys.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value, or the default if the key is not found.
        """
        keys = key.split('.')
        value = self
        try:
            for k in keys:
                value = getattr(value, k)
            return value.model_dump() if isinstance(value, BaseModel) else value
        except AttributeError as e:
            logger.debug(f"Key '{key}' not found in configuration: {e}")
            return default


PATHS = Paths()

try:
    with open(PATHS.CONFIG_PATH.resolve(), 'r') as file:
        config_dict = yaml.safe_load(file)
    configs = Configs().model_validate(config_dict)
    print(f"Configuration loaded from {PATHS.CONFIG_PATH}")
except (FileNotFoundError, yaml.YAMLError, ValidationError) as e:
    print(f"{name(e)}: {e}\nUsing default configuration.")
    configs = Configs().model_validate()

# Function injections for dictionary-like access.
for cls in [Configs, _Resources, _Formats, _Security, _Processing, _Output]:
    cls.__getitem__ = classmethod(getitem)
    cls.__setitem__ = classmethod(setitem)
    cls.items = classmethod(lambda cls: cls.__dict__.items())
