# Function stubs from '/home/kylerose1946/omni_converter_mk2/batch_processor/_batch_processor.py'

## BatchProcessor

```python
class BatchProcessor:
    """
    Batch processor for the Omni-Converter.
    
    This class orchestrates the processing of multiple files in batches, handling
    resource management, error handling, and security validation.
    
    Attributes:
        pipeline: The processing pipeline to use.
        error_monitor: The error handler to use.
        resource_monitor: The resource monitor to use.
        security_monitor: The security manager to use.
        max_batch_size (int): Maximum number of files to process in a single batch.
        continue_on_error (bool): Whether to continue processing if errors occur.
        max_threads (int): Maximum number of worker threads for parallel processing.
        cancellation_requested (bool): Whether processing cancellation has been requested.
    """
    
    def __init__(
        self,
        configs: Configs = None,
        resources: dict[str, Callable] = None,
    ):
        """
        Initialize a batch processor.
        
        Args:
            pipeline: The processing pipeline to use. If None, the global pipeline will be used.
            error_monitor: The error handler to use. If None, the global error handler will be used.
        """
        self.configs = configs
        self.resources = resources

        self.pipeline = self.resources['processing_pipeline']
        self.error_monitor = self.resources['error_monitor']
        self.resource_monitor = self.resources['resource_monitor']
        self.security_monitor = self.resources['security_monitor']
        self._logger: Logger = self.resources['logger']
        self._processing_result: 'ProcessingResult' = self.resources['processing_result']

        self.max_batch_size = self.configs.resources.max_batch_size
        self.max_threads = self.configs.resources.max_threads
        self.continue_on_error = self.configs.processing.continue_on_error

        self.cancellation_requested = False
        self._lock = threading.RLock()  # For thread safety
```

## __init__

```python
def __init__(self, configs: Configs = None, resources: dict[str, Callable] = None):
    """
    Initialize a batch processor.

Args:
    pipeline: The processing pipeline to use. If None, the global pipeline will be used.
    error_monitor: The error handler to use. If None, the global error handler will be used.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## process_batch

```python
def process_batch(self, file_paths: Union[list[str], str], output_dir: Optional[str] = None, options: Optional[dict[str, Any]] = None, progress_callback: Optional[ProgressCallback] = None) -> BatchResult:
    """
    Process a batch of files.

Args:
    file_paths: list of file paths to process, or a directory path to
        recursively process all files within.
    output_dir: Directory to write output files to. If None, files will
        be processed but output will not be written to disk.
    options: Processing options to pass to the pipeline.
    progress_callback: Optional callback function for reporting progress.
        The function should accept current_count, total_count, and current_file.
        
Returns:
    A BatchResult object with the results of the batch processing.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _process_chunk

```python
def _process_chunk(self, file_paths: list[str], output_dir: Optional[str], options: Optional[dict[str, Any]], progress_callback: Optional[ProgressCallback], total_count: int, current_index: int) -> list['ProcessingResult']:
    """
    Process a chunk of files.

Args:
    file_paths: list of file paths to process.
    output_dir: Directory to write output files to.
    options: Processing options.
    progress_callback: Progress callback function.
    total_count: Total number of files in the full batch.
    current_index: Current index in the full batch.
    
Returns:
    List of ProcessingResult objects for the processed files.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _process_files_parallel

```python
def _process_files_parallel(self, file_paths: list[str], output_dir: Optional[str], options: dict[str, Any], progress_callback: Optional[ProgressCallback], total_count: int, current_index: int) -> list['ProcessingResult']:
    """
    Process files in parallel using a thread pool.

Args:
    file_paths: list of file paths to process.
    output_dir: Directory to write output files to.
    options: Processing options.
    progress_callback: Progress callback function.
    total_count: Total number of files in the full batch.
    current_index: Current index in the full batch.
    
Returns:
    List of ProcessingResult objects for the processed files.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _process_files_sequential

```python
def _process_files_sequential(self, file_paths: list[str], output_dir: Optional[str], options: dict[str, Any], progress_callback: Optional[ProgressCallback], total_count: int, current_index: int) -> list[ProcessingResult]:
    """
    Process files sequentially.

Args:
    file_paths: list of file paths to process.
    output_dir: Directory to write output files to.
    options: Processing options.
    progress_callback: Progress callback function.
    total_count: Total number of files in the full batch.
    current_index: Current index in the full batch.
    
Returns:
    List of ProcessingResult objects for the processed files.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _process_single_file

```python
def _process_single_file(self, file_path: str, output_path: Optional[str], options: dict[str, Any]) -> ProcessingResult:
    """
    Process a single file.

Args:
    file_path: Path to the file to process.
    output_path: Path to write output to.
    options: Processing options.
    
Returns:
    ProcessingResult object for the processed file.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _resolve_paths

```python
def _resolve_paths(self, file_paths: Union[list[str], str]) -> list[str]:
    """
    Resolve file paths, expanding directories if necessary.

Args:
    file_paths: list of file paths or a directory path.
    
Returns:
    List of resolved file paths.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## _get_output_path

```python
def _get_output_path(self, input_path: str, output_dir: Optional[str], options: dict[str, Any]) -> Optional[str]:
    """
    Get the output path for a file.

Args:
    input_path: Path to the input file.
    output_dir: Directory to write output to.
    options: Processing options.
    
Returns:
    Path to write output to, or None if output should not be written.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## cancel_processing

```python
def cancel_processing(self) -> None:
    """
    Cancel ongoing batch processing.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## processing_status

```python
@property
def processing_status(self) -> dict[str, Any]:
    """
    Get the current status of batch processing.

Returns:
    A dictionary with the current status.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## set_max_batch_size

```python
def set_max_batch_size(self, size: int) -> None:
    """
    Set the maximum batch size.

Args:
    size: Maximum number of files to process in a single batch.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## set_continue_on_error

```python
def set_continue_on_error(self, flag: bool) -> None:
    """
    Set whether to continue processing if errors occur.

Args:
    flag: Whether to continue processing if errors occur.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor

## set_max_threads

```python
def set_max_threads(self, count: int) -> None:
    """
    Set the maximum number of worker threads for parallel processing.

Args:
    count: Maximum number of worker threads.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchProcessor
