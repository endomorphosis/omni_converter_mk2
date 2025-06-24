from typing import Optional, Any

try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Pydantic is required for the Python API.")


class Options(BaseModel):
    """Options for the Omni-Converter Python API.

    Attributes:
        output_dir: Directory to write output files to.
        format: Output format for the converted text (default: "txt").
        include_metadata: Whether to include file metadata in the output (default: True).
        extract_metadata: Whether to extract metadata from the data in the input files (default: True).
        normalize_text: Whether to normalize text (e.g., remove extra whitespace, convert to lowercase, etc.) (default: True).
        quality_threshold: Arbitrary threshold for quality filtering (default: 0.9).
        continue_on_error: Whether to continue processing files even if some fail (default: True).
        max_batch_size: Maximum number of files to process in a single batch (default: 100).
        parallel: Whether to process files in parallel (default: False).
        max_workers: Maximum number of worker threads to use for parallel processing (default: 4).
        sanitize: Whether to sanitize output files (e.g. remove executable code, etc.) (default: True).
        max_cpu: Maximum CPU usage percentage allowed (default: 80).
        max_memory: Maximum memory usage in MB (default: 6144 i.e. 6GB).
        show_progress: Whether to show a progress bar (default: False, TODO: Unused argument. Implement).
        lossy: Relax the quality threshold for large/complex files and formats (default: False).
        retries: Number of retries for failed conversions (default: None, meaning no retries).
        follow_symlinks: Whether to follow symbolic links when processing directories (default: False).
    """
    output_dir: Optional[str] = Field(default=None)
    format: str = Field(default="txt")
    include_metadata: bool = Field(default=True)
    extract_metadata: bool = Field(default=True)
    normalize_text: bool = Field(default=True)
    quality_threshold: float = Field(default=0.9)
    continue_on_error: bool = Field(default=True)
    max_batch_size: int = Field(default=100)
    parallel: bool = Field(default=False)
    max_workers: int = Field(default=4)
    sanitize: bool = Field(default=True)
    max_cpu: int = Field(default=80)
    max_memory: int = Field(default=6144)  # 6GB in MB
    show_progress: bool = Field(default=False)  # TODO Unused argument. Implement.
    lossy: bool = Field(default=False)
    retries: int = Field(default=None)
    follow_symlinks: bool = Field(default=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary.

        Returns:
            A dictionary representation of the options.
        """
        return self.model_dump()
