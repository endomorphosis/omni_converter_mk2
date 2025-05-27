import importlib
from typing import TypeVar


from logger import logger


Dependency = TypeVar('Dependency')


# Check for external dependencies and programs
# Default to None (e.g. the library/program is not available)
# TODO These should be loaded from a JSON or YAML file in the top-level directory to allow for easier updates and management
DEPENDENCIES = {
    "anthropic": None,  # anthropic for Claude API (optional)
    "bs4": None,  # BeautifulSoup for HTML processing
    "cv2": None, # cv2 for computer vision (opencv-contrib-python-headless in requirements.txt)
    "docx": None, # python-docx for DOCX processing
    "duckdb": None, # duckdb for database operations
    "jinja2": None, # jinja2 for templating
    "nltk": None, # nltk for natural language processing
    "numpy": None, # numpy for numerical operations
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

for library, bool_ in DEPENDENCIES.items():
    try:
        DEPENDENCIES[library] = importlib.import_module(library)
        logger.info(f"{library} is available")
    except (ImportError, ModuleNotFoundError):
        logger.warning(f"{library} is not available, functionality will be limited")
        DEPENDENCIES[library] = None
    except Exception as e:
        logger.warning(f"{type(e).__name__} checking {library} availability: {e}")
        DEPENDENCIES[library] = None

class Dependencies:
    """Class to manage dependencies and their availability."""

    @property
    def anthropic(self) -> Dependency | None:
        """Dependency for anthropic. Equivalent to 'import anthropic'."""
        return DEPENDENCIES["anthropic"]

    @property
    def bs4(self) -> Dependency | None:
        """Dependency for bs4. Equivalent to 'import bs4'."""
        return DEPENDENCIES["bs4"]

    @property
    def cv2(self) -> Dependency | None:
        """Dependency for cv2. Equivalent to 'import cv2'."""
        return DEPENDENCIES["cv2"]

    @property
    def docx(self) -> Dependency | None:
        """Dependency for docx. Equivalent to 'import docx'."""
        return DEPENDENCIES["docx"]

    @property
    def duckdb(self) -> Dependency | None:
        """Dependency for duckdb. Equivalent to 'import duckdb'."""
        return DEPENDENCIES["duckdb"]

    @property
    def jinja2(self) -> Dependency | None:
        """Dependency for jinja2. Equivalent to 'import jinja2'."""
        return DEPENDENCIES["jinja2"]

    @property
    def nltk(self) -> Dependency | None:
        """Dependency for nltk. Equivalent to 'import nltk'."""
        return DEPENDENCIES["nltk"]

    @property
    def numpy(self) -> Dependency | None:
        """Dependency for numpy. Equivalent to 'import numpy'."""
        return DEPENDENCIES["numpy"]

    @property
    def openai(self) -> Dependency | None:
        """Dependency for openai. Equivalent to 'import openai'."""
        return DEPENDENCIES["openai"]

    @property
    def openpyxl(self) -> Dependency | None:
        """Dependency for openpyxl. Equivalent to 'import openpyxl'."""
        return DEPENDENCIES["openpyxl"]

    @property
    def pandas(self) -> Dependency | None:
        """Dependency for pandas. Equivalent to 'import pandas'."""
        return DEPENDENCIES["pandas"]

    @property
    def PIL(self) -> Dependency | None:
        """Dependency for PIL. Equivalent to 'import PIL'."""
        return DEPENDENCIES["PIL"]

    @property
    def psutil(self) -> Dependency | None:
        """Dependency for psutil. Equivalent to 'import psutil'."""
        return DEPENDENCIES["psutil"]

    @property
    def pydantic(self) -> Dependency | None:
        """Dependency for pydantic. Equivalent to 'import pydantic'."""
        return DEPENDENCIES["pydantic"]

    @property
    def pydub(self) -> Dependency | None:
        """Dependency for pydub. Equivalent to 'import pydub'."""
        return DEPENDENCIES["pydub"]

    @property
    def pymediainfo(self) -> Dependency | None:
        """Dependency for pymediainfo. Equivalent to 'import pymediainfo'."""
        return DEPENDENCIES["pymediainfo"]

    @property
    def PyPDF2(self) -> Dependency | None:
        """Dependency for PyPDF2. Equivalent to 'import PyPDF2'."""
        return DEPENDENCIES["PyPDF2"]

    @property
    def pytesseract(self) -> Dependency | None:
        """Dependency for pytesseract. Equivalent to 'import pytesseract'."""
        return DEPENDENCIES["pytesseract"]

    @property
    def reportlab(self) -> Dependency | None:
        """Dependency for reportlab. Equivalent to 'import reportlab'."""
        return DEPENDENCIES["reportlab"]

    @property
    def rouge(self) -> Dependency | None:
        """Dependency for rouge. Equivalent to 'import rouge'."""
        return DEPENDENCIES["rouge"]

    @property
    def tiktoken(self) -> Dependency | None:
        """Dependency for tiktoken. Equivalent to 'import tiktoken'."""
        return DEPENDENCIES["tiktoken"]

    @property
    def torch(self) -> Dependency | None:
        """Dependency for torch. Equivalent to 'import torch'."""
        return DEPENDENCIES["torch"]

    @property
    def tqdm(self) -> Dependency | None:
        """Dependency for tqdm. Equivalent to 'import tqdm'."""
        return DEPENDENCIES["tqdm"]

    @property
    def whisper(self) -> Dependency | None:
        """Dependency for whisper. Equivalent to 'import whisper'."""
        return DEPENDENCIES["whisper"]

    @property
    def yaml(self) -> Dependency | None:
        """Dependency for yaml. Equivalent to 'import yaml'."""
        return DEPENDENCIES["yaml"]

    def __getitem__(self, name: str) -> Dependency | None:
        """Get a dependency by name."""
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise KeyError(f"Dependency '{name}' not found in dependencies.")
