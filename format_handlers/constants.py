from typing import Any

from utils.logger import logger

# Import pymediainfo for metadata extraction (will be installed via requirements.txt)
try:
    import pymediainfo
    _MEDIAINFO_AVAILABLE = True
except ImportError:
    logger.warning("pymediainfo not available, video metadata extraction will be limited")
    _MEDIAINFO_AVAILABLE = False

# Import PIL for thumbnail extraction
try:
    import PIL
    _PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available, thumbnail extraction will be limited")
    _PIL_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.utils import mediainfo
    _PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("pydub not available, audio extraction will be limited")
    _PYDUB_AVAILABLE = False


class Constants:
    """Constants for format handlers including supported formats and capabilities."""

    @property
    def MEDIAINFO_AVAILABLE(self) -> bool:
        """Check if pymediainfo is available."""
        return _MEDIAINFO_AVAILABLE

    @property
    def PIL_AVAILABLE(self) -> bool:
        return _PIL_AVAILABLE

    @property
    def PYDUB_AVAILABLE(self) -> bool:
        """Check if pydub is available."""
        return _PYDUB_AVAILABLE

    # Audio formats and capabilities
    SUPPORTED_AUDIO_FORMATS_SET: set = {"mp3", "wav", "ogg", "flac", "aac"}
    AUDIO_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'audio',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_transcription': False  # Set to True if speech-to-text is implemented
    }

    # Application formats and capabilities
    SUPPORTED_APPLICATION_FORMATS_SET: set = {"pdf", "json", "docx", "xlsx", "zip"}
    APPLICATION_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'application',
        'preserves_structure': True,
        'extracts_metadata': True,
        'supports_nested_files': True
    }
    
    # Video formats and capabilities
    SUPPORTED_VIDEO_FORMATS_SET: set = {"mp4", "webm", "avi", "mkv", "mov"}
    VIDEO_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'video',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_transcription': False,  # Set to True if speech-to-text is implemented
        'extracts_thumbnails': False  # Should be set dynamically based on video_processor_available
    }
    
    # Image formats and capabilities
    SUPPORTED_IMAGE_FORMATS_SET: set = {"jpeg", "png", "gif", "webp", "svg"}
    IMAGE_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'image',
        'preserves_structure': False,
        'extracts_metadata': True,
        'supports_ocr': 'basic'  # Should be set dynamically based on ocr_processor
    }

    # Text formats and capabilities
    SUPPORTED_TEXT_FORMATS_SET: set = {"html", "xml", "plain", "calendar", "csv"}
    TEXT_HANDLER_CAPABILITIES: dict[str, Any] = {
        'category': 'text',
        'preserves_structure': True,
        'extracts_metadata': True,
        'supports_encoding_detection': True
    }