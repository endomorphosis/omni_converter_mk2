import importlib
from typing import TypeVar


from logger import logger


Dependency = TypeVar('Dependency')


class _dependency_wrapper:
    def __init__(self, module, module_name):
        self._module = module
        self._module_name = module_name
    
    def __getattr__(self, name):
        if self._module is None:
            raise ImportError(f"Module '{self._module_name}' not available")
        return getattr(self._module, name)
    
    def __bool__(self):
        return self._module is not None
    
    @property
    def available(self):
        return self._module is not None


class _classproperty:
    def __init__(self, func):
        self.func = func
        self._cached = None
        self._checked = False
    
    def __get__(self, instance, owner):
        if not self._checked:
            try:
                module = self.func(owner)
                self._cached = _dependency_wrapper(module, self.func.__name__)
            except ImportError:
                self._cached = _dependency_wrapper(None, self.func.__name__)
            self._checked = True
        return self._cached


class Dependencies:
    """
    Comprehensive dependency management system for the omni-converter application.
    
    This class provides centralized access to 20+ optional Python libraries spanning multiple
    domains including AI APIs (anthropic, openai), document processing (docx, PyPDF2, openpyxl),
    computer vision (cv2, PIL), audio/video processing (pydub, whisper, pymediainfo), data science
    (pandas, numpy, torch), web scraping (bs4), OCR (pytesseract), templating (jinja2), and more.
    
    Architecture:
        - Uses a global cls._DEPENDENCIES dict that's populated at module import time
        - Each dependency is checked via importlib.import_module() with graceful error handling
        - Class properties provide type-safe access to imported modules or None if unavailable
        - Custom _classproperty decorator enables accessing dependencies as class attributes
        - Dictionary-like interface (__getitem__, get, keys, items) for dynamic access
        
    Dependency Categories:
        AI/ML APIs: anthropic (Claude), openai (ChatGPT), tiktoken (tokenization)
        Document Processing: docx (Word), PyPDF2 (PDF), openpyxl (Excel), reportlab (PDF generation)
        Computer Vision: cv2 (OpenCV), PIL (Pillow for images), pytesseract (OCR)
        Audio/Video: pydub (audio processing), whisper (speech-to-text), pymediainfo (metadata)
        Data Science: pandas (data manipulation), numpy (numerical), torch (deep learning)
        Web/Text: bs4 (BeautifulSoup), jinja2 (templating), nltk (NLP), rouge (text evaluation)
        Infrastructure: psutil (system monitoring), pydantic (validation), tqdm (progress bars)
        Formats: yaml (YAML parsing), duckdb (database operations)
        
    Usage Patterns:
        # Property access (preferred for known dependencies)
        if Dependencies.pandas:
            df = Dependencies.pandas.DataFrame(data)
            
        # Dictionary access (useful for dynamic dependency resolution)
        pdf_processor = Dependencies.get('PyPDF2')
        if pdf_processor:
            reader = pdf_processor.PdfReader(file)
            
        # Checking availability before feature enablement
        features = []
        if Dependencies.torch:
            features.append('deep_learning')
        if Dependencies.whisper:
            features.append('audio_transcription')
            
        # Iterating over all dependencies
        missing_deps = [name for name, dep in Dependencies.items() if dep is None]
        
    Error Handling:
        - Missing dependencies return None instead of raising ImportError
        - All import attempts are logged with appropriate warning/info levels
        - Application can gracefully degrade functionality based on available dependencies
        - Unknown dependency names raise KeyError in dictionary interface
        
    Performance Notes:
        - Dependencies are imported once at module load time (not on each access)
        - Class properties have minimal overhead via _classproperty descriptor
        - Failed imports are cached as None to avoid repeated import attempts
        
    Future Improvements:
        - TODO: Load dependency list from external JSON/YAML configuration
        - Potential for dependency version checking and compatibility validation
        - Runtime dependency installation hooks for development environments
    """
    # Check for external dependencies and programs
    # Default to None (e.g. the library/program is not available)
    # TODO These should be loaded from a JSON or YAML file in the top-level directory to allow for easier updates and management
    _DEPENDENCIES = {
        "anthropic": None,  # anthropic for Claude API (optional)
        "bs4": None,  # BeautifulSoup for HTML processing
        "cv2": None, # cv2 for computer vision (opencv-contrib-python-headless in requirements.txt)
        "docx": None, # python-docx for DOCX processing
        "duckdb": None, # duckdb for database operations
        "jinja2": None, # jinja2 for templating
        "nltk": None, # nltk for natural language processing
        "numpy": None, # numpy for numerical operations
        "markitdown": None, # Other multi-format-to-text conversion program. (optional)
        "openai": None, # openai for ChatGPT API (optional)
        "openpyxl": None, # openpyxl for XLSX processing
        "pandas": None, # pandas for data manipulation
        "PIL": None, # PIL for thumbnail extraction (Pillow in requirements.txt)
        "psutil": None, # psutil for system monitoring
        "pydantic": None, # pydantic for data validation
        "pydub": None, # pydub for audio processing
        "pymediainfo": None, # pymediainfo for metadata extraction (will be installed via requirements.txt)
        "PyPDF2": None, # PyPDF2 for PDF processing
        "pytesseract": None, # pytesseract for OCR (optional)
        "reportlab": None, # reportlab for PDF generation
        "rouge": None, # rouge for text evaluation (rouge-score in requirements.txt)
        "tiktoken": None, # tiktoken for token counting
        "torch": None, # torch for deep learning models
        "tqdm": None, # tqdm for progress bars
        "whisper": None, # whisper for audio processing (openai-whisper in requirements.txt)
        "yaml": None, # yaml for YAML parsing (pyyaml in requirements.txt)
    }

    # List of critical dependencies that MUST be available for the application to run at all.
    _CRITICAL_DEPENDENCIES = [
        "tqdm",  "yaml", "psutil", "pydantic"
    ]

    for library, bool_ in _DEPENDENCIES.items():
        try:
            _DEPENDENCIES[library] = importlib.import_module(library)
            logger.info(f"{library} is available")
        except (ImportError, ModuleNotFoundError):
            if library in _CRITICAL_DEPENDENCIES:
                raise ImportError(f"Critical dependency '{library}' is not available. Please install it to run the application.")
            else:
                logger.warning(f"{library} is not available.")
                _DEPENDENCIES[library] = None
        except Exception as e:
            logger.warning(f"{type(e).__name__} checking {library} availability: {e}")
            _DEPENDENCIES[library] = None

    @_classproperty
    def anthropic(cls) -> Dependency | None:
        """Dependency for anthropic. Equivalent to 'import anthropic'."""
        return cls._DEPENDENCIES["anthropic"]

    @_classproperty
    def bs4(cls) -> Dependency | None:
        """Dependency for bs4. Equivalent to 'import bs4'."""
        return cls._DEPENDENCIES["bs4"]

    @_classproperty
    def cv2(cls) -> Dependency | None:
        """Dependency for cv2. Equivalent to 'import cv2'."""
        return cls._DEPENDENCIES["cv2"]

    @_classproperty
    def docx(cls) -> Dependency | None:
        """Dependency for python-docx. Equivalent to 'import docx'."""
        return cls._DEPENDENCIES["docx"]

    @_classproperty
    def duckdb(cls) -> Dependency | None:
        """Dependency for duckdb. Equivalent to 'import duckdb'."""
        return cls._DEPENDENCIES["duckdb"]

    @_classproperty
    def jinja2(cls) -> Dependency | None:
        """Dependency for jinja2. Equivalent to 'import jinja2'."""
        return cls._DEPENDENCIES["jinja2"]

    @_classproperty
    def nltk(cls) -> Dependency | None:
        """Dependency for nltk. Equivalent to 'import nltk'."""
        return cls._DEPENDENCIES["nltk"]

    @_classproperty
    def numpy(cls) -> Dependency | None:
        """Dependency for numpy. Equivalent to 'import numpy'."""
        return cls._DEPENDENCIES["numpy"]

    @_classproperty
    def openai(cls) -> Dependency | None:
        """Dependency for openai. Equivalent to 'import openai'."""
        return cls._DEPENDENCIES["openai"]

    @_classproperty
    def openpyxl(cls) -> Dependency | None:
        """Dependency for openpyxl. Equivalent to 'import openpyxl'."""
        return cls._DEPENDENCIES["openpyxl"]

    @_classproperty
    def pandas(cls) -> Dependency | None:
        """Dependency for pandas. Equivalent to 'import pandas'."""
        return cls._DEPENDENCIES["pandas"]

    @_classproperty
    def PIL(cls) -> Dependency | None:
        """Dependency for PIL. Equivalent to 'import PIL'."""
        return cls._DEPENDENCIES["PIL"]

    @_classproperty
    def psutil(cls) -> Dependency | None:
        """Dependency for psutil. Equivalent to 'import psutil'."""
        return cls._DEPENDENCIES["psutil"]

    @_classproperty
    def pydantic(cls) -> Dependency | None:
        """Dependency for pydantic. Equivalent to 'import pydantic'."""
        return cls._DEPENDENCIES["pydantic"]

    @_classproperty
    def pydub(cls) -> Dependency | None:
        """Dependency for pydub. Equivalent to 'import pydub'."""
        return cls._DEPENDENCIES["pydub"]

    @_classproperty
    def pymediainfo(cls) -> Dependency | None:
        """Dependency for pymediainfo. Equivalent to 'import pymediainfo'."""
        return cls._DEPENDENCIES["pymediainfo"]

    @_classproperty
    def PyPDF2(cls) -> Dependency | None:
        """Dependency for PyPDF2. Equivalent to 'import PyPDF2'."""
        return cls._DEPENDENCIES["PyPDF2"]

    @_classproperty
    def pytesseract(cls) -> Dependency | None:
        """Dependency for pytesseract. Equivalent to 'import pytesseract'."""
        return cls._DEPENDENCIES["pytesseract"]

    @_classproperty
    def reportlab(cls) -> Dependency | None:
        """Dependency for reportlab. Equivalent to 'import reportlab'."""
        return cls._DEPENDENCIES["reportlab"]

    @_classproperty
    def rouge(cls) -> Dependency | None:
        """Dependency for rouge. Equivalent to 'import rouge'."""
        return cls._DEPENDENCIES["rouge"]

    @_classproperty
    def tiktoken(cls) -> Dependency | None:
        """Dependency for tiktoken. Equivalent to 'import tiktoken'."""
        return cls._DEPENDENCIES["tiktoken"]

    @_classproperty
    def torch(cls) -> Dependency | None:
        """Dependency for torch. Equivalent to 'import torch'."""
        return cls._DEPENDENCIES["torch"]

    @_classproperty
    def tqdm(cls) -> Dependency | None:
        """Dependency for tqdm. Equivalent to 'import tqdm'."""
        return cls._DEPENDENCIES["tqdm"]

    @_classproperty
    def whisper(cls) -> Dependency | None:
        """Dependency for whisper. Equivalent to 'import whisper'."""
        return cls._DEPENDENCIES["whisper"]

    @_classproperty
    def yaml(cls) -> Dependency | None:
        """Dependency for yaml. Equivalent to 'import yaml'."""
        return cls._DEPENDENCIES["yaml"]

    ####################################################
    #### Dictionary-like interface for dependencies ####
    ####################################################

    @classmethod
    def __getitem__(cls, name: str) -> Dependency | None:
        """Get a dependency by name."""
        if hasattr(cls, name):
            return getattr(cls, name)
        else:
            raise KeyError(f"Dependency '{name}' not found in dependencies.")

    @classmethod
    def get(cls, name: str, default: Dependency | None = None) -> Dependency | None:
        """
        Get a dependency by name with a default value.
        
        Args:
            name: The name of the dependency.
            default: The default value to return if the dependency is not found.
        
        Returns:
            The dependency if found, otherwise the default value.
        """
        return getattr(cls, name, default)

    @classmethod
    def keys(cls) -> list[str]:
        """
        Get a list of all dependency names.
        
        Returns:
            A list of dependency names.
        """
        return [
            name for name in dir(cls) 
            if not name.startswith('_') 
            and isinstance(getattr(cls, name), Dependency)
        ]

    @classmethod
    def values(cls) -> list[Dependency | None]:
        """
        Get a list of all dependencies.
        
        Returns:
            A list of dependency objects or None if not available.
        """
        return [getattr(cls, name) for name in cls.keys()]

    @classmethod
    def items(cls) -> list[tuple[str, Dependency | None]]:
        """
        Get a list of all dependencies as (name, dependency) tuples.
        
        Returns:
            A list of tuples containing dependency names and their corresponding objects.
        """
        return [(name, getattr(cls, name)) for name in cls.keys()]

