import subprocess
from typing import TypeVar


from logger import logger


class _classproperty:
    """Helper decorator to turn class methods into properties."""
    def __init__(self, func):
        self.func = func
    
    def __get__(self, instance, owner):
        return self.func(owner)

class ExternalPrograms:
    """
    Utility class to check the availability of external programs.
    
    NOTE Since the programs are entirely external, this class does not provide access to them.
    It only checks if they are available for use in the application.
    """

    _EXTERNAL_PROGRAMS = {
        "ffmpeg": False,  # ffmpeg for video processing
        "ffprobe": False,  # ffprobe for video metadata extraction
        "tesseract": False,  # tesseract for OCR (optional)
        "calibre": False,  # calibre for ebook processing (optional)
        "nvcc": False,  # nvcc for CUDA compilation (optional)
    }

    for program, bool_ in _EXTERNAL_PROGRAMS.items():
        try: # Every CLI program should have a --help option. 
            _ = subprocess.run([program, "--help"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _EXTERNAL_PROGRAMS[program] = True
            logger.info(f"{program} is available")
        except subprocess.CalledProcessError:
            logger.warning(f"{program} is not available, functionality will be limited")
            _EXTERNAL_PROGRAMS[program] = False
        except Exception as e:
            logger.warning(f"{type(e).__name__} checking {program} availability: {e}")
            _EXTERNAL_PROGRAMS[program] = False

    @_classproperty
    def ffmpeg(cls) -> bool:
        """Check if ffmpeg is available."""
        return cls._EXTERNAL_PROGRAMS["ffmpeg"]

    @_classproperty
    def ffprobe(cls) -> bool:
        """Check if ffprobe is available."""
        return cls._EXTERNAL_PROGRAMS["ffprobe"]

    @_classproperty
    def tesseract(cls) -> bool:
        """Check if tesseract is available."""
        return cls._EXTERNAL_PROGRAMS["tesseract"]

    @_classproperty
    def calibre(cls) -> bool:
        """Check if calibre is available."""
        return cls._EXTERNAL_PROGRAMS["calibre"]

    @_classproperty
    def cuda(cls) -> bool:
        """Check if nvcc (NVIDIA CUDA Compiler) is available."""
        return cls._EXTERNAL_PROGRAMS["nvcc"]

    def __getitem__(self, name: str) -> bool:
        """Get a external program by name."""
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError(f"External program '{name}' not found ExternalPrograms.") from e

    @classmethod
    def get(cls, name: str, default: bool = False) -> bool:
        """Get a external program by name with a default value.
        
        Args:
            name (str): The name of the external program.
            default (bool): The default value to return if the external program is not found.
                Defaults to False.
        
        Returns:
            The external program if found, otherwise the default value.
        """
        return getattr(cls, name, default)

    @classmethod
    def keys(cls) -> list[str]:
        """Get a list of all external program names.
        
        Returns:
            A list of external program names.
        """
        return [
            name for name in dir(cls) 
            if not name.startswith('_') # Check if it's not a private attribute
            and hasattr(_classproperty, name) # Check for class properties decorator
        ]

    @classmethod
    def items(cls) -> list[tuple[str, bool]]:
        """
        Get a list of all dependencies as (name, dependency) tuples.
        
        Returns:
            A list of tuples containing dependency names and their corresponding objects.
        """
        return [
            (name, getattr(cls, name)) # Check if the attribute exists. The second part of each tuple must be a boolean
            for name in cls.keys()
        ]
