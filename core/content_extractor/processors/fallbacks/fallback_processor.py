from types_ import Any, Callable, Configs, Logger, Protocol



class Processor(Protocol):

    def __init__(self, resources: dict[str, Callable] = None, configs: Configs = None) -> None:
        """
        Initialize the processor with resources and configurations.
        """
        self.resources = resources
        self.configs = configs

        self._supported_formats: set[str] = self.resources["supported_formats"]
        self._processor_available: bool = self.resources["processor_available"]
        self._processor_name: str = self.resources["processor_name"]

        self._get_version: Callable = self.resources["get_version"]
        self._extract_structure: Callable = self.resources["extract_structure"]
        self._extract_text: Callable = self.resources["extract_text"]
        self._extract_metadata: Callable = self.resources["extract_metadata"]
        self._open_file: Callable = self.resources["open_file"]
        self._process: Callable = self.resources["process"]

        self._logger: Logger = self.resources["logger"]


    def __call__(self, data: bytes | str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """
        Process the given data and return a tuple of (text content, metadata, sections).
        """
        ...
    
    def process(self, data: bytes | str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """
        Process the content and return it unchanged.
        """
        ...

    def extract_text(self, data: bytes | str, options: dict[str, Any]) -> str:
        """
        Extract text from the given data.
        """
        ...

    def extract_metadata(self, data: bytes | str, options: dict[str, Any]) -> dict[str, Any]:
        """
        Extract metadata from the given data.
        """
        ...

    def extract_structure(self, data: bytes | str, options: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract structure from the given data.
        """
        ...

    def get_version(self) -> str:
        """
        Get the version of the processor.
        
        Returns:
            The version of the processor.
        """
        ...




class FallbackProcessor:
    """
    Fallback processor that uses python's builtins to process data.
    This is used when no other processor is available.
    """

    def __init__(self, resources: dict[str, Callable] = None, configs: Configs = None):
        self.resources=resources
        self.configs = configs

    def __call__(self, data: bytes | str, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        return self.process(data, options)

    def process(self, content: str) -> str:
        """
        Process the content and return it unchanged.
        """
        return content
