from types_ import Any, Callable, Configs, Content, Logger

class PlainTextProcessor:

    def __init__(self, 
                 resources: dict[str, Callable] = None, 
                 configs: 'Configs' = None
                ) -> None:
        """Initialize the plaintext processor."""
        self.configs = configs
        self.resources = resources

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
        """Process plaintext content.
        
        Args:
            file_content: The file content to process.
            options: Processing options.
            
        Returns:
            tuple of (text content, metadata, sections).
        """
        # Get text content
        text = self._extract_text(data, options)

        # Get metadata
        metadata = self._extract_metadata(data, options)

        # Create sections
        sections = self._extract_structure(data, options)
        
        return text, metadata, sections

    def get_version(self) -> str:
        """
        Get the version of the processor.
        
        Returns:
            The version of the processor.
        """
        return self._get_version()