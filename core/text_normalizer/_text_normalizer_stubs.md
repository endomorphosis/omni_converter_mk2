# Function stubs from '/home/kylerose1946/omni_converter_mk2/core/text_normalizer/_text_normalizer.py'

## __init__

```python
def __init__(self, resources: dict[str, Any] = None, configs: "Configs" = None):
    """
    Initialize a text normalizer.

Args:
    resources: A dictionary of callable objects and dependencies.
    configs: A pydantic model containing configuration settings.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## _register_default_normalizers

```python
def _register_default_normalizers(self) -> None:
    """
    Register the default text normalizers.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## _normalize_whitespace

```python
@staticmethod
def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

Args:
    text: The text to normalize.
    
Returns:
    The normalized text.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## _normalize_line_endings

```python
@staticmethod
def _normalize_line_endings(text: str) -> str:
    """
    Normalize line endings in text.

Args:
    text: The text to normalize.
    
Returns:
    The normalized text.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## _normalize_empty_lines

```python
@staticmethod
def _normalize_empty_lines(text: str) -> str:
    """
    Normalize empty lines in text.

Args:
    text: The text to normalize.
    
Returns:
    The normalized text.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## _normalize_unicode

```python
@staticmethod
def _normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters in text.

Args:
    text: The text to normalize.
    
Returns:
    The normalized text.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## normalize_text

```python
def normalize_text(self, content: "Content", normalizers: Optional[list[str]] = None) -> "NormalizedContent":
    """
    Normalize text content.

Args:
    content: The content to normalize.
    normalizers: list of normalizer names to apply. If None, all normalizers are applied.
    
Returns:
    The normalized content.
    
Raises:
    ValueError: If an unknown normalizer is specified.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## register_normalizer

```python
def register_normalizer(self, name: str, normalizer: NormalizerFunc) -> None:
    """
    Register a normalizer.

Args:
    name: The name of the normalizer.
    normalizer: The normalizer function.
    
Raises:
    ValueError: If a normalizer with the same name already exists.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer

## applied_normalizers

```python
@property
def applied_normalizers(self) -> list[str]:
    """
    Get the names of all registered normalizers.

Returns:
    list of normalizer names.
    """
```
* **Async:** False
* **Method:** True
* **Class:** TextNormalizer
