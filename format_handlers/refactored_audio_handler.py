"""
Audio format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for audio formats like MP3, WAV, OGG, FLAC, and AAC
using dependency injection for better modularity and testability, without inheritance.
"""

import os
import io
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from utils.configs import Configs
from utils.logger import logger
from format_handlers.unified_handler import BaseFormatHandler, Content, create_handler, map_extension_to_format
from format_handlers.constants import Constants
from utils.format_detector import format_detector


# Audio format handler implementation using composition instead of inheritance
def create_audio_handler(resources: Dict[str, Any], configs: Optional[Configs] = None) -> BaseFormatHandler:
    """
    Create an audio handler instance with injected dependencies.
    
    Args:
        resources: Resources dictionary with dependencies.
        configs: Configuration settings.
        
    Returns:
        BaseFormatHandler instance configured for audio formats.
    """
    # Format-specific file extensions
    format_extensions = {
        'mp3': ['.mp3'],
        'wav': ['.wav', '.wave'],
        'ogg': ['.ogg', '.oga'],
        'flac': ['.flac'],
        'aac': ['.aac', '.m4a']
    }
    
    # Prepare parsers with the appropriate functions
    parsers = {
        "audio": {
            "mp3": process_audio_file,
            "wav": process_audio_file,
            "ogg": process_audio_file,
            "flac": process_audio_file,
            "aac": process_audio_file
        }
    }
    
    # Get constants and processors
    pydub_available = resources.get("pydub_available", Constants.PYDUB_AVAILABLE)
    whisper_processor = resources.get("whisper_processor")
    
    # Additional resources specific to audio handling
    audio_resources = {
        "pydub_available": pydub_available,
        "whisper_processor": whisper_processor,
        "format_extensions": format_extensions
    }
    
    # Create and return the handler
    return create_handler(
        handler_name="AudioHandler",
        format_detector=format_detector,
        ext_to_format=map_extension_to_format,
        supported_formats=Constants.SUPPORTED_AUDIO_FORMATS_SET,
        capabilities=Constants.AUDIO_HANDLER_CAPABILITIES,
        parsers=parsers,
        resources_extra=audio_resources,
        configs=configs
    )
    
def process_audio_file(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an audio file and extract content.
    
    Args:
        file_content: The file content to process (typically binary).
        options: Processing options including format information.
        
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # This function is called by the BaseFormatHandler's do_extraction method
    # It receives the file content and options from that method
    
    # Get key information from the options
    file_path = options.get("file_path", "")
    format_name = options.get("format", "")
    
    # Check if whisper processor is available and should be used
    whisper_processor = options.get("whisper_processor")
    if whisper_processor and whisper_processor.can_process(format_name):
        try:
            text, metadata, sections = whisper_processor.process_audio(file_content.as_binary, format_name, options)
            return text, metadata, sections
        except Exception as e:
            logger.warning(f"Whisper processor failed, falling back to basic extraction: {e}")
    
    # Check if pydub is available
    pydub_available = options.get("pydub_available", Constants.PYDUB_AVAILABLE)
    
    # Choose the appropriate extraction method
    if pydub_available:
        return extract_with_pydub(file_path, format_name)
    else:
        return extract_basic(file_path, format_name)


def extract_with_pydub(file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extract audio information using pydub.
    
    Args:
        file_path: The path to the audio file.
        format_name: The format of the audio file.
        
    Returns:
        A tuple of (text content, metadata, sections).
    """
    # Import pydub here to ensure it's only used when available
    from pydub import AudioSegment
    from pydub.utils import mediainfo
    
    # Get media info
    info = mediainfo(file_path)
    
    # Load audio file to get additional properties
    audio = AudioSegment.from_file(file_path, format=format_name)
    
    # Extract common properties
    duration_seconds = len(audio) / 1000.0
    duration = str(timedelta(seconds=duration_seconds))
    channels = audio.channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate
    frame_width = audio.frame_width
    
    # Calculate average loudness (dBFS)
    loudness = audio.dBFS
    
    # Build metadata dictionary
    metadata = {
        'format': format_name,
        'duration_seconds': duration_seconds,
        'duration': duration,
        'channels': channels,
        'sample_width_bytes': sample_width,
        'frame_rate_hz': frame_rate,
        'frame_width_bytes': frame_width,
        'loudness_dbfs': loudness,
        'file_size_bytes': os.path.getsize(file_path)
    }
    
    # Add additional metadata from mediainfo
    if info:
        for key, value in info.items():
            if key not in metadata and value:
                metadata[key] = value
    
    # Generate human-readable description
    text_content = [f"Audio File: {os.path.basename(file_path)}"]
    text_content.append(f"Format: {format_name.upper()}")
    text_content.append(f"Duration: {duration}")
    text_content.append(f"Channels: {channels} ({'Mono' if channels == 1 else 'Stereo' if channels == 2 else 'Multi-channel'})")
    text_content.append(f"Sample Rate: {frame_rate} Hz")
    text_content.append(f"Bit Depth: {sample_width * 8} bits")
    
    # Add bitrate if available
    if 'bit_rate' in info and info['bit_rate']:
        try:
            bitrate_kbps = int(info['bit_rate']) / 1000
            text_content.append(f"Bitrate: {bitrate_kbps:.0f} kbps")
            metadata['bitrate_kbps'] = bitrate_kbps
        except (ValueError, TypeError):
            pass
    
    # Add title, artist, album if available
    if 'TAG' in info:
        tag_info = info['TAG']
        if 'title' in tag_info and tag_info['title']:
            text_content.append(f"Title: {tag_info['title']}")
            metadata['title'] = tag_info['title']
        
        if 'artist' in tag_info and tag_info['artist']:
            text_content.append(f"Artist: {tag_info['artist']}")
            metadata['artist'] = tag_info['artist']
        
        if 'album' in tag_info and tag_info['album']:
            text_content.append(f"Album: {tag_info['album']}")
            metadata['album'] = tag_info['album']
        
        if 'genre' in tag_info and tag_info['genre']:
            text_content.append(f"Genre: {tag_info['genre']}")
            metadata['genre'] = tag_info['genre']
        
        if 'date' in tag_info and tag_info['date']:
            text_content.append(f"Year: {tag_info['date']}")
            metadata['year'] = tag_info['date']
    
    # Create sections
    sections = [
        {
            'type': 'audio_info',
            'content': {
                'format': format_name,
                'duration': duration,
                'channels': channels,
                'sample_rate': frame_rate,
                'bit_depth': sample_width * 8
            }
        }
    ]
    
    # Add metadata section if tags exist
    if 'TAG' in info and info['TAG']:
        sections.append({
            'type': 'metadata',
            'content': info['TAG']
        })
    
    # Add waveform description (placeholder for actual visualization)
    sections.append({
        'type': 'waveform',
        'content': f"Audio loudness: {loudness:.2f} dBFS"
    })
    
    return "\n".join(text_content), metadata, sections


def extract_basic(file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Basic extraction when pydub is not available.
    
    Args:
        file_path: The path to the audio file.
        format_name: The format of the audio file.
        
    Returns:
        A tuple of (text content, metadata, sections).
    """
    # Get basic file information
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    # Build basic metadata
    metadata = {
        'format': format_name,
        'file_size_bytes': file_size,
        'file_name': file_name
    }
    
    # Generate basic description
    text_content = [f"Audio File: {file_name}"]
    text_content.append(f"Format: {format_name.upper()}")
    text_content.append(f"File Size: {file_size} bytes")
    text_content.append("")
    text_content.append("Note: Detailed audio information not available.")
    text_content.append("Install pydub for enhanced audio metadata extraction.")
    
    # Create basic sections
    sections = [
        {
            'type': 'audio_info',
            'content': {
                'format': format_name,
                'file_size': file_size
            }
        }
    ]
    
    return "\n".join(text_content), metadata, sections