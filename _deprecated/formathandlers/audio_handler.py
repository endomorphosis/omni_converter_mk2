# """
# Audio format handlers for the Omni-Converter.

# This module provides handlers for audio formats like MP3, WAV, OGG, FLAC, and AAC.
# It extracts metadata and generates text descriptions of audio files.
# """

# import os
# import io
# from datetime import datetime, timedelta
# from typing import Any, Optional, Set, Union

# from utils.filesystem import FileSystem
# from logger import logger
# from core.file_format_detector import file_format_detector
# from format_handlers.base_handler import BaseFormatHandler, Content
# from format_handlers.processors.by_ability.audio_processor import whisper_processor
# from .constants import Constants


# # Import pydub for audio processing (will be installed via requirements.txt)
# try:
#     from pydub import AudioSegment
#     from pydub.utils import mediainfo
#     PYDUB_AVAILABLE = True
# except ImportError:
#     logger.warning("pydub not available, audio extraction will be limited")
#     PYDUB_AVAILABLE = False


# class AudioHandler(BaseFormatHandler):
#     """
#     Handler for audio-based formats.
    
#     Handles common audio formats like MP3, WAV, OGG, FLAC, and AAC.
#     Extracts metadata and generates basic descriptions for audio files.
#     """
    
#     def __init__(self):
#         """Initialize the audio handler."""
#         super().__init__(
#             handler_name="AudioHandler",
#             supported_formats={"mp3", "wav", "ogg", "flac", "aac"},
#             capabilities={
#                 'category': 'audio',
#                 'preserves_structure': False,
#                 'extracts_metadata': True,
#                 'supports_transcription': False  # Set to True if speech-to-text is implemented
#             }
#         )
        
#         # Format-specific file extensions
#         self.format_extensions = {
#             'mp3': ['.mp3'],
#             'wav': ['.wav', '.wave'],
#             'ogg': ['.ogg', '.oga'],
#             'flac': ['.flac'],
#             'aac': ['.aac', '.m4a']
#         }
    
#     def do_extraction(self, file_path: str, options: dict[str, Any]) -> Content:
#         """
#         Extract content from an audio file.
        
#         Args:
#             file_path: The path to the file.
#             options: Extraction options.
            
#         Returns:
#             The extracted content.
            
#         Raises:
#             ValueError: If the file format is not supported.
#             Exception: If an error occurs during extraction.
#         """
#         # Detect format if not provided in options
#         format_name = options.get('format')
#         if not format_name:
#             format_name, _ = file_format_detector.detect_format(file_path)
            
#             # Override format detection based on file extension if needed
#             _, ext = os.path.splitext(file_path)
#             ext = ext.lower()
            
#             # Map extension to format
#             for fmt, extensions in self.format_extensions.items():
#                 if ext in extensions:
#                     format_name = fmt
#                     break
        
#         if not format_name or format_name not in self.supported_formats:
#             raise ValueError(f"Unsupported format: {format_name}")
        
#         logger.debug(f"Extracting content from {format_name} audio file: {file_path}")
        
#         try:
#             # Read the file data
#             file_content = FileSystem.read_file(file_path, 'rb')
#             file_data = file_content.as_binary
            
#             # First try to use the Whisper processor if available
#             if whisper_processor.can_process(format_name):
#                 try:
#                     text, metadata, sections = whisper_processor.process_audio(file_data, format_name, options)
                    
#                     # Create content object
#                     content = Content(
#                         text=text,
#                         metadata=metadata,
#                         sections=sections,
#                         source_format=format_name,
#                         source_path=file_path
#                     )
                    
#                     return content
#                 except Exception as e:
#                     logger.warning(f"Whisper processor failed, falling back to basic extraction: {e}")
#                     # Fall back to the next method
            
#             # Extract metadata using mediainfo if pydub is available
#             if PYDUB_AVAILABLE:
#                 text, metadata, sections = self._extract_with_pydub(file_path, format_name)
#             else:
#                 # Fallback to basic extraction if pydub is not available
#                 text, metadata, sections = self._extract_basic(file_path, format_name)
            
#             # Create content object
#             content = Content(
#                 text=text,
#                 metadata=metadata,
#                 sections=sections,
#                 source_format=format_name,
#                 source_path=file_path
#             )
            
#             return content
            
#         except Exception as e:
#             logger.error(f"Error extracting content from {format_name} audio file: {file_path}", 
#                         {'error': e})
#             raise
    
#     def _extract_with_pydub(self, file_path: str, format_name: str) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
#         """
#         Extract audio information using pydub.
        
#         Args:
#             file_path: The path to the audio file.
#             format_name: The format of the audio file.
            
#         Returns:
#             A tuple of (text content, metadata, sections).
#         """
#         # Get media info
#         info = mediainfo(file_path)
        
#         # Load audio file to get additional properties
#         audio = AudioSegment.from_file(file_path, format=format_name)
        
#         # Extract common properties
#         duration_seconds = len(audio) / 1000.0
#         duration = str(timedelta(seconds=duration_seconds))
#         channels = audio.channels
#         sample_width = audio.sample_width
#         frame_rate = audio.frame_rate
#         frame_width = audio.frame_width
        
#         # Calculate average loudness (dBFS)
#         loudness = audio.dBFS
        
#         # Build metadata dictionary
#         metadata = {
#             'format': format_name,
#             'duration_seconds': duration_seconds,
#             'duration': duration,
#             'channels': channels,
#             'sample_width_bytes': sample_width,
#             'frame_rate_hz': frame_rate,
#             'frame_width_bytes': frame_width,
#             'loudness_dbfs': loudness,
#             'file_size_bytes': os.path.getsize(file_path)
#         }
        
#         # Add additional metadata from mediainfo
#         if info:
#             for key, value in info.items():
#                 if key not in metadata and value:
#                     metadata[key] = value
        
#         # Generate human-readable description
#         text_content = [f"Audio File: {os.path.basename(file_path)}"]
#         text_content.append(f"Format: {format_name.upper()}")
#         text_content.append(f"Duration: {duration}")
#         text_content.append(f"Channels: {channels} ({'Mono' if channels == 1 else 'Stereo' if channels == 2 else 'Multi-channel'})")
#         text_content.append(f"Sample Rate: {frame_rate} Hz")
#         text_content.append(f"Bit Depth: {sample_width * 8} bits")
        
#         # Add bitrate if available
#         if 'bit_rate' in info and info['bit_rate']:
#             try:
#                 bitrate_kbps = int(info['bit_rate']) / 1000
#                 text_content.append(f"Bitrate: {bitrate_kbps:.0f} kbps")
#                 metadata['bitrate_kbps'] = bitrate_kbps
#             except (ValueError, TypeError):
#                 pass
        
#         # Add title, artist, album if available
#         if 'TAG' in info:
#             tag_info = info['TAG']
#             if 'title' in tag_info and tag_info['title']:
#                 text_content.append(f"Title: {tag_info['title']}")
#                 metadata['title'] = tag_info['title']
            
#             if 'artist' in tag_info and tag_info['artist']:
#                 text_content.append(f"Artist: {tag_info['artist']}")
#                 metadata['artist'] = tag_info['artist']
            
#             if 'album' in tag_info and tag_info['album']:
#                 text_content.append(f"Album: {tag_info['album']}")
#                 metadata['album'] = tag_info['album']
            
#             if 'genre' in tag_info and tag_info['genre']:
#                 text_content.append(f"Genre: {tag_info['genre']}")
#                 metadata['genre'] = tag_info['genre']
            
#             if 'date' in tag_info and tag_info['date']:
#                 text_content.append(f"Year: {tag_info['date']}")
#                 metadata['year'] = tag_info['date']
        
#         # Create sections
#         sections = [
#             {
#                 'type': 'audio_info',
#                 'content': {
#                     'format': format_name,
#                     'duration': duration,
#                     'channels': channels,
#                     'sample_rate': frame_rate,
#                     'bit_depth': sample_width * 8
#                 }
#             }
#         ]
        
#         # Add metadata section if tags exist
#         if 'TAG' in info and info['TAG']:
#             sections.append({
#                 'type': 'metadata',
#                 'content': info['TAG']
#             })
        
#         # Add waveform description (placeholder for actual visualization)
#         sections.append({
#             'type': 'waveform',
#             'content': f"Audio loudness: {loudness:.2f} dBFS"
#         })
        
#         return "\n".join(text_content), metadata, sections
    
#     def _extract_basic(self, file_path: str, format_name: str) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
#         """
#         Basic extraction when pydub is not available.
        
#         Args:
#             file_path: The path to the audio file.
#             format_name: The format of the audio file.
            
#         Returns:
#             A tuple of (text content, metadata, sections).
#         """
#         # Get basic file information
#         file_size = os.path.getsize(file_path)
#         file_name = os.path.basename(file_path)
        
#         # Build basic metadata
#         metadata = {
#             'format': format_name,
#             'file_size_bytes': file_size,
#             'file_name': file_name
#         }
        
#         # Generate basic description
#         text_content = [f"Audio File: {file_name}"]
#         text_content.append(f"Format: {format_name.upper()}")
#         text_content.append(f"File Size: {file_size} bytes")
#         text_content.append("")
#         text_content.append("Note: Detailed audio information not available.")
#         text_content.append("Install pydub for enhanced audio metadata extraction.")
        
#         # Create basic sections
#         sections = [
#             {
#                 'type': 'audio_info',
#                 'content': {
#                     'format': format_name,
#                     'file_size': file_size
#                 }
#             }
#         ]
        
#         return "\n".join(text_content), metadata, sections


# # Global audio handler instance
# audio_handler = AudioHandler()