from types_ import Any, Callable, Configs, Logger


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
