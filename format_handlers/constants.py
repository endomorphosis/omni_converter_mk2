from typing import Any

from format_handlers.dependency_modules.dependencies import DEPENDENCIES
from format_handlers.dependency_modules.external_programs import EXTERNAL_PROGRAMS

libraries = {
    name: True if DEPENDENCIES.get(name) else False for name in DEPENDENCIES.keys()
}
external_programs = {
    name: True if EXTERNAL_PROGRAMS.get(name) else False for name in EXTERNAL_PROGRAMS.keys()
}

class _classproperty:
    """Helper decorator to turn class methods into properties."""
    def __init__(self, func):
        self.func = func
    
    def __get__(self, instance, owner):
        return self.func(owner)

class Constants:
    """
    Constants for format handlers including supported formats and capabilities.
    
    Table of Contents:
    - Dependency and External Programs Availability
        Boolean properties to check if external libraries and programs are available.
    - Combination Processors
        Boolean properties to check if a combination of libraries are available to enable certain processors.
        For example, if openpyxl *or* pandas is available, the xlsx processor can be used.
    - Format Handlers Constants
    - MIME Type to Format Mapping
    - Unimplemented Formats
    - All Formats from ROADMAP

    """
    #####################################################
    ### Dependency and External Programs Availability ###
    #####################################################

    @_classproperty
    def ANTHROPIC_AVAILABLE(cls) -> bool:
        """Check if anthropic is available."""
        return libraries['anthropic']

    @_classproperty
    def BS4_AVAILABLE(cls) -> bool:
        """Check if BeautifulSoup is available."""
        return libraries['bs4']

    @_classproperty
    def CV2_AVAILABLE(cls) -> bool:
        """Check if cv2 is available."""
        return libraries['cv2']

    @_classproperty
    def DUCKDB_AVAILABLE(cls) -> bool:
        """Check if duckdb is available."""
        return libraries['duckdb']

    @_classproperty
    def FFMPEG_AVAILABLE(cls) -> bool:
        """Check if ffmpeg is available."""
        return external_programs['ffmpeg']

    @_classproperty
    def FFPROBE_AVAILABLE(cls) -> bool:
        """Check if ffprobe is available."""
        return external_programs['ffprobe']

    @_classproperty
    def JINJA2_AVAILABLE(cls) -> bool:
        """Check if jinja2 is available."""
        return libraries['jinja2']

    @_classproperty
    def PYMEDIAINFO_AVAILABLE(cls) -> bool:
        """Check if pymediainfo is available."""
        return libraries['pymediainfo']

    @_classproperty
    def NLTK_AVAILABLE(cls) -> bool:
        """Check if nltk is available."""
        return libraries['nltk']

    @_classproperty
    def NUMPY_AVAILABLE(cls) -> bool:
        """Check if numpy is available."""
        return libraries['numpy']

    @_classproperty
    def OPENAI_AVAILABLE(cls) -> bool:
        """Check if openai is available."""
        return libraries['openai']

    @_classproperty
    def OPENPYXL_AVAILABLE(cls) -> bool:
        """Check if openpyxl is available."""
        return libraries['openpyxl']

    @_classproperty
    def PANDAS_AVAILABLE(cls) -> bool:
        """Check if pandas is available."""
        return libraries['pandas']

    @_classproperty
    def PYPDF2_AVAILABLE(cls) -> bool:
        """Check if PyPDF2 is available."""
        return libraries['PyPDF2']

    @_classproperty
    def PIL_AVAILABLE(cls) -> bool:
        return libraries['PIL']

    @_classproperty
    def PSUTIL_AVAILABLE(cls) -> bool:
        """Check if psutil is available."""
        return libraries['psutil']

    @_classproperty
    def PYDANTIC_AVAILABLE(cls) -> bool:
        """Check if pydantic is available."""
        return libraries['pydantic']

    @_classproperty
    def PYDUB_AVAILABLE(cls) -> bool:
        """Check if pydub is available."""
        return libraries['pydub']

    @_classproperty
    def PYPDF2_AVAILABLE(cls) -> bool:
        """Check if PDF processor is available."""
        return libraries['PyPDF2']

    @_classproperty
    def PYTESSERACT_AVAILABLE(cls) -> bool:
        """Check if pytesseract is available."""
        return libraries['pytesseract']

    @_classproperty
    def PYTHON_DOCX_PROCESSOR_AVAILABLE(cls) -> bool:
        """Check if DOCX processor is available."""
        return libraries['docx']

    @_classproperty
    def PYYAML_AVAILABLE(cls) -> bool:
        """Check if yaml is available."""
        return libraries['yaml']

    @_classproperty
    def REPORTLAB_AVAILABLE(cls) -> bool:
        """Check if reportlab is available."""
        return libraries['reportlab']

    @_classproperty
    def ROUGE_AVAILABLE(cls) -> bool:
        """Check if rouge is available."""
        return libraries['rouge']

    @_classproperty
    def TESSERACT_AVAILABLE(cls) -> bool:
        """Check if tesseract is available."""
        return external_programs['tesseract']

    @_classproperty
    def TIKTOKEN_AVAILABLE(cls) -> bool:
        """Check if tiktoken is available."""
        return libraries['tiktoken']

    @_classproperty
    def TORCH_AVAILABLE(cls) -> bool:
        """Check if torch is available."""
        return libraries['torch']

    @_classproperty
    def TQDM_AVAILABLE(cls) -> bool:
        """Check if tqdm is available."""
        return libraries['tqdm']

    @_classproperty
    def WHISPER_AVAILABLE(cls) -> bool:
        """Check if whisper is available."""
        return libraries['whisper']

    ##############################
    ### Combination Processors ###
    ##############################

    @_classproperty
    def IMAGE_PROCESSOR_AVAILABLE(cls) -> bool: # TODO Add more checks for other libraries. Should be along the lines of `x or y or z` to check for multiple libraries.
        """Check if image processing capabilities are available."""
        return cls.PIL_AVAILABLE or cls.OPENAI_AVAILABLE or cls.PYTESSERACT_AVAILABLE

    @_classproperty
    def VIDEO_PROCESSOR_AVAILABLE(cls) -> bool:
        """Check if video processing capabilities are available."""
        return cls.FFMPEG_AVAILABLE and cls.PYMEDIAINFO_AVAILABLE

    @_classproperty
    def XLSX_PROCESSOR_AVAILABLE(cls) -> bool:
        """Check if XLSX processing capabilities are available."""
        return cls.OPENPYXL_AVAILABLE or cls.PANDAS_AVAILABLE

    @_classproperty
    def PDF_PROCESSOR_AVAILABLE(cls) -> bool:
        """Check if PDF processor is available."""
        return cls.PYPDF2_AVAILABLE

    @_classproperty
    def HTML_PROCESSOR_AVAILABLE(cls) -> bool:
        """Check if HTML processor is available."""
        return cls.BS4_AVAILABLE or cls.JINJA2_AVAILABLE

    #################################
    ### Format Handlers Constants ###
    #################################

    # Audio formats and capabilities
    SUPPORTED_AUDIO_FORMATS_SET: set = {
        "mp3", "wav", "ogg", "flac", "aac"
    }
    AUDIO_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'audio',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_transcription': False  # Set to True if speech-to-text is implemented # TODO
    }

    #### Application formats and capabilities ####

    # Application formats and capabilities
    SUPPORTED_APPLICATION_FORMATS_SET: set = {
        "pdf", "json", "docx", "xlsx", "zip"
    } # TODO Add choice for presentational excel
    APPLICATION_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'application',
        'preserves_structure': True,
        'extracts_metadata': True,
        'supports_nested_files': True
    }
    SUPPORTED_XLSX_FORMATS_SET: set = {
        "xlsx", "xlsm", "xlsb", "xltx", "xltm" # TODO test these.
    }
    SUPPORTED_HTML_FORMATS_SET: set = {
        "html", "htm", "xhtml", "xml" # TODO test these.
    }

    # Video formats and capabilities
    SUPPORTED_VIDEO_FORMATS_SET: set = {
        "mp4", "webm", "avi", "mkv", "mov"
    }
    VIDEO_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'video',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_transcription': False,  # Set to True if speech-to-text is implemented
        'extracts_thumbnails': False  # Should be set dynamically based on video_processor_available
    }
    
    # Image formats and capabilities
    SUPPORTED_IMAGE_FORMATS_SET: set = {
        "jpeg", "jpg", "png", "gif", "webp", "svg+xml"
    }
    IMAGE_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'image',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_ocr': 'basic'  # Should be set dynamically based on ocr_processor
    }

    # Text formats and capabilities
    SUPPORTED_TEXT_FORMATS_SET: set = {
        "html", "xml", "plain", "calendar", "csv"
    }
    TEXT_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'text',
        'preserves_structure': True,
        'extracts_metadata': True,
        'supports_encoding_detection': True
    }

    # Unimplemented formats from ROADMAP (MIME types not yet supported)
    UNIMPLEMENTED_APPLICATION_FORMATS_SET: set = {
        # Archive/Compression formats
        "zip", "gzip", "x-gzip", "x-7z-compressed", "vnd.rar", "x-rar-compressed", 
        "x-bzip", "x-bzip2", "x-tar", "x-zip-compressed", "x-freearc",
        # Document formats - Microsoft Office
        "msword", "vnd.ms-excel", "vnd.ms-powerpoint", "vnd.ms-word",
        "vnd.openxmlformats-officedocument.presentationml.presentation",
        # Document formats - OpenDocument
        "vnd.oasis.opendocument.presentation", "vnd.oasis.opendocument.spreadsheet",
        "vnd.oasis.opendocument.text",
        # Document formats - Other
        "rtf", "postscript", "x-abiword", "x-tex", "x-troff-man",
        # eBook formats
        "epub+zip", "vnd.amazon.ebook", "x-mobipocket-ebook",
        # Web/Markup formats
        "xml", "xhtml+xml", "atom+xml", "rss+xml", "rdf+xml", "ld+json",
        "vnd.wap.xhtml+xml", "vnd.mozilla.xul+xml",
        # JavaScript/Programming formats
        "javascript", "x-javascript", "x-json", "x-httpd-php",
        # Geographic/Mapping formats
        "vnd.google-earth.kml+xml", "vnd.google-earth.kmz",
        # Calendar/Time formats
        "calendar", "ics",
        # Media/Multimedia formats
        "ogg", "x-shockwave-flash",
        # Security/Encryption formats
        "pgp-encrypted", "pgp-signature",
        # System/Binary formats
        "octet-stream", "octetstream", "x-msdownload", "vnd.android.package-archive",
        "vnd.apple.installer+xml", "x-debian-package",
        # Script/Shell formats
        "x-csh", "x-sh",
        # Scientific/Data formats
        "marc", "x-netcdf", "x-cdf", "x-endnote-refer", "x-research-info-systems",
        "x-bibtex",
        # Download/Transfer formats
        "download", "force-download", "save-to-disk", "x-download",
        # Application/Specialized formats
        "java-archive", "x-java-jnlp-file", "x-bittorrent", "vnd.visio", "text"
    }

    UNIMPLEMENTED_AUDIO_FORMATS_SET: set = {
        # Mobile/3GPP formats
        "3gpp", "3gpp2",
        # MIDI formats
        "midi", "x-midi",
        # Playlist/Streaming formats
        "x-mpegurl", "x-scpls",
        # Container formats
        "webm"
    }

    UNIMPLEMENTED_VIDEO_FORMATS_SET: set = {
        # Mobile/3GPP formats
        "3gpp", "3gpp2",
        # MPEG variants
        "mp2t", "mpeg", 
        # Container/Streaming formats
        "ogg", "x-ms-asf", "x-msvideo"
    }

    UNIMPLEMENTED_IMAGE_FORMATS_SET: set = {
        # Animated formats
        "apng",
        # Next-gen formats
        "avif",
        # Legacy/Common formats
        "bmp", "tiff",
        # JPEG variants
        "jp2", "pjpeg",
        # Specialized formats
        "vnd.djvu", "vnd.microsoft.icon"
    }

    UNIMPLEMENTED_TEXT_FORMATS_SET: set = {
        # Web/Styling formats
        "css", "javascript",
        # Programming/Source code formats
        "x-c", "x-csrc", "x-perl",
        # Data/Structured formats
        "tab-separated-values", "turtle", "x-bibtex",
        # Contact/Calendar formats
        "vcard", "x-vcalendar", "x-vcard",
        # Document/File formats
        "pdf", "directory", "enriched", "prs.lines.tag",
        # Development/Patch formats
        "x-diff", "x-patch"
    }

    # MIME type to format extension mapping (from ROADMAP)
    MIME_TYPE_TO_FORMAT_MAP: dict[str, str] = {
        # Application formats (implemented)
        "application/json": "json",
        "application/pdf": "pdf", 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/zip": "zip",
        
        # Audio formats (implemented)
        "audio/aac": "aac",
        "audio/flac": "flac", 
        "audio/mpeg": "mp3",
        "audio/ogg": "ogg",
        "audio/x-wav": "wav",
        
        # Image formats (implemented)
        "image/gif": "gif",
        "image/jpeg": "jpeg",
        "image/jpg": "jpg", 
        "image/png": "png",
        "image/svg+xml": "svg",
        "image/webp": "webp",
        
        # Text formats (implemented)
        "text/calendar": "calendar",
        "text/csv": "csv",
        "text/html": "html",
        "text/plain": "plain",
        "text/xml": "xml",
        
        # Video formats (implemented)
        "video/avi": "avi",
        "video/mkv": "mkv", 
        "video/mov": "mov",
        "video/mp4": "mp4",
        "video/webm": "webm"
    }

    # Additional unimplemented formats not in main MIME categories
    UNIMPLEMENTED_BINARY_FORMATS_SET: set = {
        "octet-stream"
    }

    UNIMPLEMENTED_MESSAGE_FORMATS_SET: set = {
        "rfc822"
    }

    # All formats from ROADMAP (implemented + unimplemented)
    ALL_ROADMAP_FORMATS: set = {
        # Get all unique format extensions from supported sets
        *SUPPORTED_APPLICATION_FORMATS_SET,
        *SUPPORTED_AUDIO_FORMATS_SET,
        *SUPPORTED_IMAGE_FORMATS_SET,
        *SUPPORTED_TEXT_FORMATS_SET,
        *SUPPORTED_VIDEO_FORMATS_SET,
        # Get all unimplemented formats
        *UNIMPLEMENTED_APPLICATION_FORMATS_SET,
        *UNIMPLEMENTED_AUDIO_FORMATS_SET,
        *UNIMPLEMENTED_IMAGE_FORMATS_SET,
        *UNIMPLEMENTED_TEXT_FORMATS_SET,
        *UNIMPLEMENTED_VIDEO_FORMATS_SET,
        *UNIMPLEMENTED_BINARY_FORMATS_SET,
        *UNIMPLEMENTED_MESSAGE_FORMATS_SET
    }

    PROCESSOR_MIME_TYPE_MAP: dict[str, list[str]] = {
        ""
    }
