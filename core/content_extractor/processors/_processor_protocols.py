

from types_ import Any, BaseModel, Callable, Protocol


class ExtractionFunc(Protocol):
    """Protocol for processor functions."""

    def __call__(self, data: bytes | str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """Process data and return (text, metadata, sections)."""
        ...

class ExtractTextFunc(Protocol):
    """Protocol for text extraction functions."""

    def __call__(self, data: bytes | str, options: dict[str, Any]) -> str:
        """Extract text from data."""
        ...

class ExtractMetadataFunc(Protocol):
    """Protocol for metadata extraction functions."""

    def __call__(self, data: bytes | str, options: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from data."""
        ...

class ExtractSectionsFunc(Protocol):
    """Protocol for section extraction functions."""

    def __call__(self, data: bytes | str, options: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract sections from data."""
        ...

class ProcessorByAbility(Protocol):
    """Protocol for validator functions."""

    def __call__(self, data: Any) -> None:
        """Validate data, raise exception if invalid."""
        ...

class ProcessorByFormat(Protocol):
    """Protocol for processor functions."""

    def __init__(self, resources: dict[str, Callable], configs: BaseModel) -> None:
        """Process data and return (text, metadata, sections)."""
        ...

