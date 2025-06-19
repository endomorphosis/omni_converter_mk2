"""
Lazy loading of dependencies to optimize performance and reduce initial load time.

Modules can access these dependencies via the `dependencies` object.
"""
# NOTE Make imports private to enforce singleton pattern.
from types import ModuleType as _ModuleType
from importlib import import_module as _import_module # NOTE We import this outside the class to avoid circular imports.

class _Dependencies:
    """
    Class to enable the lazy-loading of dependencies and third-party libraries.
    This optimizes performance, allows for dynamic error checking, and reduce initial load time.
    """

    _CRITICAL_DEPENDENCIES: list[str] = [
        "tqdm",  "yaml", "psutil", "pydantic"
    ]

    def __init__(self):
        self._cache: dict[str, _ModuleType | None] = {
            "anthropic": None,
            "bs4": None,  # BeautifulSoup for HTML processing
            "chardet": None,  # Character encoding detection
            "cv2": None,
            "docx": None,
            "duckdb": None,
            "llama_cpp": None, # TODO Confirm library name.
            "jinja2": None,
            "markitdown": None,  # Other multi-format-to-text conversion program. (optional)
            "multiformats": None,
            "numpy": None,
            "openai": None,
            "openpyxl": None,
            "pandas": None,
            "PIL": None,  # Pillow for image processing
            "playsound3": None,  # Playsound for audio playback
            "psutil": None,
            "pydantic": None, # TODO FIgure out how to get types from pydantic without importing it.
            "pydub": None,
            "pymediainfo": None,
            "PyPDF2": None,
            "pytesseract": None,
            "pydocx": None, # TODO Confirm libraries existence.
            "pymediainfo": None,
            "rouge": None,
            "tiktoken": None,
            "torch": None,  # PyTorch for deep learning
            "tqdm": None,
            "whisper": None,
            "yaml": None,
        }
        self.check_critical_dependencies()

    def check_critical_dependencies(self) -> None:
        """
        Check if all critical dependencies are available.
        
        Raises:
            ImportError: If any critical dependency is not available.
        """
        for dep in self._CRITICAL_DEPENDENCIES:
            try:
                self._load_module(dep)
            except ImportError as e:
                raise ImportError(f"Critical dependency '{dep}' is not available. Please install it to run the application.") from e

    def load_all_modules(self) -> None:
        """
        Load all modules and cache them.
        
        This is called at the start of the program to check which dependencies are available.
        """
        for module_name in self._cache.keys():
            self._load_module(module_name)

    def _load_module(self, module_name: str) -> _ModuleType | None:
        if self._cache[module_name] is None:
            try:
                self._cache[module_name] = _import_module(module_name)
            except ModuleNotFoundError as e:
                print(f"Could not find third-party dependency '{module_name}'.")
            except Exception as e:
                raise ImportError(f"Could not import third-party dependency '{module_name}': {e}") from e
        return self._cache[module_name]

    def __str__(self) -> str:
        return "_Dependencies"

    def startswith(self, prefix: str) -> bool: # TODO Remove this debug code later.
        import traceback
        print(f"startswith called with prefix: {prefix}")
        print("Call stack:")
        traceback.print_stack()
        return str(self).startswith(prefix)

    def __repr__(self) -> str:
        loaded_modules = [name for name, module in self._cache.items() if module is not None]
        return f"<_Dependencies loaded: {loaded_modules}>"

    def clear_cache(self) -> None:
        """
        Clear the cache of loaded modules.

        Used to save memory when large dependencies are no longer needed.
        """
        self._cache = {key: None for key in self._cache.keys()}

    def clear_module(self, module_name: str) -> None:
        """
        Clear a specific module from the cache.

        Args:
            module_name (str): The name of the module to clear.
        """
        if module_name in self._cache:
            self._cache[module_name] = None
        else:
            raise KeyError(f"Module '{module_name}' not found in dependencies.")

    def is_available(self, module_name: str) -> bool: # TODO Test this method.
        """
        Check if a specific module is available.

        Args:
            module_name (str): The name of the module to check.

        Returns:
            bool: True if the module is available, False otherwise.
        """
        return self._load_module(module_name) is not None

    @property
    def anthropic(self) -> _ModuleType | None:
        return self._load_module('anthropic')

    @property
    def bs4(self) -> _ModuleType | None:
        return self._load_module('bs4')

    @property
    def duckdb(self) -> _ModuleType | None:
        return self._load_module('duckdb')

    @property
    def multiformats(self) -> _ModuleType | None:
        return self._load_module('multiformats')

    @property
    def numpy(self) -> _ModuleType | None:
        return self._load_module('numpy')

    @property
    def openai(self) -> _ModuleType | None:
        return self._load_module('openai')
    
    @property
    def pandas(self) -> _ModuleType | None:
        return self._load_module('pandas')

    @property
    def pil(self) -> _ModuleType | None:
        return self._load_module('PIL')

    @property
    def playsound(self) -> _ModuleType | None:
        return self._load_module('playsound3')
    
    @property
    def python_docx(self) -> _ModuleType | None:
        return self._load_module('docx')

    @property
    def pydantic(self) -> _ModuleType | None:
        return self._load_module('pydantic')

    @property
    def tiktoken(self) -> _ModuleType | None:
        return self._load_module('tiktoken')

    @property
    def torch(self) -> _ModuleType | None:
        return self._load_module('torch')

    @property
    def tqdm(self) -> _ModuleType | None:
        return self._load_module('tqdm')

    @property
    def pytesseract(self) -> _ModuleType | None:
        return self._load_module('pytesseract')

    @property
    def pymediainfo(self) -> _ModuleType | None:
        return self._load_module('pymediainfo')

    @property
    def cv2(self) -> _ModuleType | None:
        """Load the cv2 module."""
        return self._load_module('cv2')

    @property
    def pydub(self) -> _ModuleType | None:
        """Load the pydub module."""
        return self._load_module('pydub')
    
    @property
    def openpyxl(self) -> _ModuleType | None:
        """Load the openpyxl module."""
        return self._load_module('openpyxl')

    @property
    def whisper(self) -> _ModuleType | None:
        """Load the whisper module."""
        return self._load_module('whisper')

    @property
    def chardet(self) -> _ModuleType | None:
        """Load the chardet module."""
        return self._load_module('chardet')

    def keys(self) -> list[str]:
        """Get a list of all dependency names.
        
        Returns:
            A list of dependency names.
        """
        return [name for name in self._cache.keys()]
    
    def __iter__(self):
        """Iterate over the loaded modules."""
        for name, module in self._cache.items():
            if module is not None:
                yield name, module

    def __contains__(self, item: str) -> bool:
        """Check if a specific module is loaded."""
        return item in self._cache and self._cache[item] is not None

    def __getitem__(self, item: str) -> _ModuleType | None:
        """Get a specific module by name."""
        return self._load_module(item)

dependencies = _Dependencies()
