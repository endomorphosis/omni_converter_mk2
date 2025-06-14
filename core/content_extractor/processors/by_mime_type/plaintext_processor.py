
from types_ import Callable, Configs, Content, Logger

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
