# Function stubs from '/home/kylerose1946/omni_converter_mk2/interfaces/options.py'

## _validate_format

```python
def _validate_format(format: str) -> str:
    """
    Validate the output format option.

Args:
    format: The output format string.

Returns:
    The validated output format string.

Raises:
    ValueError: If the format is not supported.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## _validate_max_workers

```python
def _validate_max_workers(max_workers: PositiveInt) -> PositiveInt:
    """
    Validate the maximum number of worker threads.

Returns:
    The validated maximum number of worker threads.

Raises:
    ValueError: If the maximum number of workers is less than 1.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## _validate_max_memory

```python
def _validate_max_memory(max_memory: PositiveInt) -> PositiveInt:
    """
    Validate the maximum memory usage in MB.

Args:
    max_memory: The maximum memory usage in MB.

Returns:
    The validated maximum memory usage in MB.

Raises:
    ValueError: If the maximum memory is less than 1MB.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## _validate_max_vram

```python
def _validate_max_vram(max_vram: PositiveInt) -> PositiveInt:
    """
    Validate the maximum VRAM usage in MB.)

Args:
    max_vram: The maximum VRAM usage in MB.

Returns:
    The validated maximum VRAM usage in MB.

Raises:
    ValueError: If the maximum VRAM is less than 1MB.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A


## Options

```python
import argparse
from enum import StrEnum
from pathlib import Path
from typing import Optional, Any, Annotated as Ann
try:
    from pydantic import (
        BaseModel, 
        Field, 
        PositiveInt, 
        AfterValidator as AV, 
        ValidationError, 
        DirectoryPath,
        FilePath,
        PositiveFloat,
        NonNegativeFloat,
    )
except ImportError:
    raise ImportError("Pydantic is required for the Python API.")


class Options(BaseModel):
    """Options for the Omni-Converter.

    These options are intended to validate argparse arguments 
    and provide a structured way to manage conversion settings.

    Attributes:
        input: The input file(s) or directory to convert.
        output: Output directory for the converted content.
        walk: Process directories recursively, including all subdirectories.
        normalize: Normalize text before saving.
        security_checks: Check input files for malicious aspects.
        metadata: Extract metadata from input files.
        structure: Extract structural elements from input files.
        format: Output format for the converted text.
        max_threads: Maximum number of threads for parallel processing.
        max_memory: Maximum memory usage (GB).
        max_vram: Maximum VRAM usage (GB).
        budget_in_usd: Budget in USD for priced API calls.
        normalizers: Text normalizers to apply (comma-separated).
        max_cpu: Maximum CPU usage percentage.
        quality_threshold: Quality filtering threshold (0-1).
        continue_on_error: Continue processing files even if some fail.
        parallel: Enable parallel document processing.
        follow_symlinks: Follow symbolic links when processing directories.
        include_metadata: Include file metadata in output.
        lossy: Relax quality threshold for large/complex files.
        normalize_text: Normalize text output.
        sanitize: Sanitize output files.
        show_options: Show current options and exit.
        show_progress: Show progress bar during batch operations.
        verbose: Log detailed information during processing.
        list_formats: List supported input formats and exit.
        version: Show version information and exit.
        batch_size: Number of files to process in a single batch.
        retries: Number of retries for failed conversions.
    """
    input:             DirectoryPath | FilePath | list[FilePath] = Field(..., description="The input file(s) or directory to convert")
    output:            DirectoryPath = Field(default_factory=Path.home(), description="Output directory for the converted content. Defaults to home directory", alias="o")
    walk:              bool = Field(default=False, description="If input is a directory, process it recursively, including all subdirectories", alias="w")
    normalize:         bool = Field(default=True, description="Normalize text before saving (e.g., remove extra whitespace, convert to lowercase, etc.)")
    security_checks:   bool = Field(default=True, description="Check the input files for malicious aspects. Ex: malware, zip bombs, etc. Disable at your own risk")
    metadata:          bool = Field(default=True, description="Extract metadata from input files and append it to the converted text. Ex: author, title, etc.")
    structure:         bool = Field(default=True, description="Extract structural elements from the input files and append it to the converted text. Ex: headings, lists, etc.")
    format:            OutputFormat = Field(default=OutputFormat.TXT, description="Output format for the converted text. Options are: 'txt', 'md', 'json'", alias="f")
    max_threads:       Ann[PositiveInt, AV(_validate_max_workers)] = Field(default=4, description="Maximum number of threads to use during parallel processing")  # At least one worker thread
    max_memory:        Ann[PositiveInt, AV(_validate_max_memory)]  = Field(default=6, description="Maximum memory usage (GB). Cannot exceed the system's total physical RAM.") # 6GB in MB
    max_vram:          Ann[PositiveInt, AV(_validate_max_vram)]    = Field(default=6, description="Maximum VRAM usage (GB). Cannot exceed your graphics card's total VRAM.")  # 6GB in MB
    budget_in_usd:     NonNegativeFloat = Field(default=0.00, description="Budget in USD for priced API calls and cloud processing. NOTE: Setting this to 0 will disable certain dependencies (e.g. OpenAI, Anthropic, etc.).")  # Budget for cloud processing
    normalizers:       Optional[str] = Field(default=None, description="Specifies which text normalizers to apply (comma-separated)")
    max_cpu:           PositiveInt = Field(default=80, le=100, description="Maximum CPU usage allowed during processing (percentage)")
    quality_threshold: NonNegativeFloat = Field(default=0.9, le=1.0, description="Arbitrary threshold for quality filtering. Range is a float from 0 to 1, where 0 is no filtering and 1 is strict filtering. Default is 0.9.")
    continue_on_error: bool = Field(default=True, description="Whether to continue processing files even if some fail")
    parallel:          bool = Field(default=False, description="Enables parallel document processing", alias="p")  # TODO Implement parallel processing.
    follow_symlinks:   bool = Field(default=False, description="Whether to follow symbolic links when processing directories")
    include_metadata:  bool = Field(default=True, description="Whether to include file metadata in the output")
    lossy:             bool = Field(default=False, description="Relax the quality threshold for large/complex files and formats")
    normalize_text:    bool = Field(default=True, description="Whether to normalize text (e.g., remove extra whitespace, convert to lowercase, etc.)")
    sanitize:          bool = Field(default=True, description="Whether to sanitize output files (e.g. remove executable code, personal information, etc.)")
    show_options:      bool = Field(default=False, description="Show current options and exit")
    show_progress:     bool = Field(default=False, description="Show a progress bar during batch operations")  # TODO Unused argument. Implement.
    verbose:           bool = Field(default=False, description="Log detailed information during processing")
    list_formats:      bool = Field(default=False, description="List supported input formats and exit")
    version:           bool = Field(default=False, description="Show version information and exit")
    batch_size:        PositiveInt = Field(default=100, description="Number of files to process in a single batch.")  # TODO Make this dynamic somehow?
    retries:           PositiveInt = Field(default=0, description="Number of retries for failed conversions")
```

## to_dict

```python
def to_dict(self) -> dict[str, Any]:
    """
    Convert to a dictionary.

Returns:
    A dictionary representation of the options.
    """
```
* **Async:** False
* **Method:** True
* **Class:** Options

## print_options

```python
def print_options(self, type_: str = "defaults") -> None:
    """
    Pretty-print the options in a human-readable format.

Args:
    type_: Type of options to print ('defaults' or 'current').
    Defaults will show the default values for each option.
    Current will show the current values set in the instance.

Raises:
    ValueError: If an invalid type is specified.
    """
```
* **Async:** False
* **Method:** True
* **Class:** Options

## make_argparse

```python
def make_argparse(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Assign the options to an argparse parser.

Args:
    parser: The argparse parser to assign the options to.
    """
```
* **Async:** False
* **Method:** True
* **Class:** Options
