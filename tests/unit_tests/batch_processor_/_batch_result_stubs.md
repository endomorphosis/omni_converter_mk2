# Function stubs from '/home/kylerose1946/omni_converter_mk2/batch_processor/_batch_result.py'

## BatchResult

```python
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
        results (list[ProcessingResult]): list of individual file processing results.
        statistics (dict[str, Any]): Additional statistics about the batch processing.
        start_time (datetime): Time when the batch processing started.
        end_time (datetime): Time when the batch processing ended.
    """
    results: list[ProcessingResult] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_files: int = field(init=False)
    successful_files: int = field(init=False)
    failed_files: int = field(init=False)
```

## __post_init__

```python
def __post_init__(self):
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## add_result

```python
def add_result(self, result: ProcessingResult) -> None:
    """
    Add a file processing result to the batch.

Args:
    result: The file processing result to add.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## complete

```python
def complete(self) -> None:
    """
    Mark the batch processing as complete.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## get_summary

```python
def get_summary(self) -> dict[str, Any]:
    """
    Get a summary of the batch processing.

Returns:
    A dictionary with summary information.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## get_failed_files

```python
def get_failed_files(self) -> list[str]:
    """
    Get a list of files that failed processing.

Returns:
    A list of paths to failed files.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## get_successful_files

```python
def get_successful_files(self) -> list[str]:
    """
    Get a list of files that were processed successfully.

Returns:
    A list of paths to successfully processed files.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## to_dict

```python
def to_dict(self) -> dict[str, Any]:
    """
    Convert to a dictionary.

Returns:
    A dictionary representation of the batch result.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult

## __str__

```python
def __str__(self) -> str:
    """
    Get a string representation of the batch result.

Returns:
    A string representation of the batch result.
    """
```
* **Async:** False
* **Method:** True
* **Class:** BatchResult
