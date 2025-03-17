"""
Video format handlers for the Omni-Converter.

This module provides handlers for video formats like MP4, WebM, AVI, MKV, and MOV.
It extracts metadata and generates text descriptions of video files.
"""

import os
import io
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import tempfile
import shutil

from utils.filesystem import FileSystem
from utils.logger import logger
from utils.format_detector import format_detector
from format_handlers.base_handler import BaseFormatHandler, Content

# Import pymediainfo for metadata extraction (will be installed via requirements.txt)
try:
    import pymediainfo
    MEDIAINFO_AVAILABLE = True
except ImportError:
    logger.warning("pymediainfo not available, video metadata extraction will be limited")
    MEDIAINFO_AVAILABLE = False

# Import PIL for thumbnail extraction
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available, thumbnail extraction will be limited")
    PIL_AVAILABLE = False


class VideoHandler(BaseFormatHandler):
    """
    Handler for video-based formats.
    
    Handles common video formats like MP4, WebM, AVI, MKV, and MOV.
    Extracts metadata and generates basic descriptions for video files.
    """
    
    def __init__(self):
        """Initialize the video handler."""
        super().__init__(
            handler_name="VideoHandler",
            supported_formats={"mp4", "webm", "avi", "mkv", "mov"},
            capabilities={
                'category': 'video',
                'preserves_structure': False,
                'extracts_metadata': True,
                'supports_transcription': False,  # Set to True if speech-to-text is implemented
                'extracts_thumbnails': False      # Set to True if thumbnail extraction is implemented
            }
        )
        
        # Format-specific file extensions
        self.format_extensions = {
            'mp4': ['.mp4', '.m4v'],
            'webm': ['.webm'],
            'avi': ['.avi'],
            'mkv': ['.mkv'],
            'mov': ['.mov', '.qt']
        }
    
    def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
        """
        Extract content from a video file.
        
        Args:
            file_path: The path to the file.
            options: Extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            ValueError: If the file format is not supported.
            Exception: If an error occurs during extraction.
        """
        # Detect format if not provided in options
        format_name = options.get('format')
        if not format_name:
            format_name, _ = format_detector.detect_format(file_path)
            
            # Override format detection based on file extension if needed
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            # Map extension to format
            for fmt, extensions in self.format_extensions.items():
                if ext in extensions:
                    format_name = fmt
                    break
        
        if not format_name or format_name not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")
        
        logger.debug(f"Extracting content from {format_name} video file: {file_path}")
        
        try:
            # Extract metadata using mediainfo if available
            if MEDIAINFO_AVAILABLE:
                text, metadata, sections = self._extract_with_mediainfo(file_path, format_name)
            else:
                # Fallback to basic extraction
                text, metadata, sections = self._extract_basic(file_path, format_name)
            
            # Create content object
            content = Content(
                text=text,
                metadata=metadata,
                sections=sections,
                source_format=format_name,
                source_path=file_path
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {format_name} video file: {file_path}", 
                        {'error': str(e)})
            raise
    
    def _extract_with_mediainfo(self, file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extract video information using pymediainfo.
        
        Args:
            file_path: The path to the video file.
            format_name: The format of the video file.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Get media info
        media_info = pymediainfo.MediaInfo.parse(file_path)
        
        # Create metadata dictionary
        metadata = {
            'format': format_name,
            'file_size_bytes': os.path.getsize(file_path),
            'tracks': []
        }
        
        # Generate human-readable description
        text_content = [f"Video File: {os.path.basename(file_path)}"]
        text_content.append(f"Format: {format_name.upper()}")
        
        # Process tracks
        general_info = None
        video_tracks = []
        audio_tracks = []
        text_tracks = []
        other_tracks = []
        
        for track in media_info.tracks:
            track_data = {'track_type': track.track_type}
            
            # Add all attributes from the track to track_data
            for attr in dir(track):
                if not attr.startswith('__') and not callable(getattr(track, attr)):
                    value = getattr(track, attr)
                    if value is not None and value != "":
                        track_data[attr] = value
            
            # Categorize tracks by type
            if track.track_type == 'General':
                general_info = track_data
                metadata['general'] = track_data
                
                # Add duration and other general information
                if hasattr(track, 'duration'):
                    duration_ms = getattr(track, 'duration', 0)
                    if duration_ms:
                        duration = str(timedelta(milliseconds=int(duration_ms)))
                        text_content.append(f"Duration: {duration}")
                        metadata['duration_ms'] = duration_ms
                        metadata['duration'] = duration
                
                # Add file size
                if hasattr(track, 'file_size'):
                    file_size = getattr(track, 'file_size', 0)
                    if file_size:
                        text_content.append(f"File Size: {self._format_file_size(file_size)}")
                        metadata['file_size_bytes'] = file_size
                
                # Add overall bitrate
                if hasattr(track, 'overall_bit_rate'):
                    overall_bit_rate = getattr(track, 'overall_bit_rate', 0)
                    if overall_bit_rate:
                        text_content.append(f"Overall Bitrate: {int(overall_bit_rate)/1000:.0f} kbps")
                        metadata['overall_bitrate_kbps'] = int(overall_bit_rate)/1000
                
            elif track.track_type == 'Video':
                video_tracks.append(track_data)
                
                # Add video track details to text content
                text_content.append("\nVideo:")
                
                # Add resolution
                if hasattr(track, 'width') and hasattr(track, 'height'):
                    width = getattr(track, 'width', 0)
                    height = getattr(track, 'height', 0)
                    if width and height:
                        text_content.append(f"  Resolution: {width}x{height}")
                
                # Add frame rate
                if hasattr(track, 'frame_rate'):
                    frame_rate = getattr(track, 'frame_rate', 0)
                    if frame_rate:
                        text_content.append(f"  Frame Rate: {frame_rate} fps")
                
                # Add codec
                if hasattr(track, 'codec'):
                    codec = getattr(track, 'codec', '')
                    if codec:
                        text_content.append(f"  Codec: {codec}")
                
                # Add bit depth
                if hasattr(track, 'bit_depth'):
                    bit_depth = getattr(track, 'bit_depth', 0)
                    if bit_depth:
                        text_content.append(f"  Bit Depth: {bit_depth} bits")
                
                # Add bit rate
                if hasattr(track, 'bit_rate'):
                    bit_rate = getattr(track, 'bit_rate', 0)
                    if bit_rate:
                        text_content.append(f"  Bitrate: {int(bit_rate)/1000:.0f} kbps")
                
            elif track.track_type == 'Audio':
                audio_tracks.append(track_data)
                
                # Add audio track details to text content
                if len(audio_tracks) == 1:
                    text_content.append("\nAudio:")
                
                # Label track if multiple audio tracks
                if len(audio_tracks) > 1:
                    text_content.append(f"\nAudio Track {len(audio_tracks)}:")
                
                # Add channels
                if hasattr(track, 'channel_s'):
                    channels = getattr(track, 'channel_s', 0)
                    if channels:
                        text_content.append(f"  Channels: {channels} ({'Mono' if channels == 1 else 'Stereo' if channels == 2 else 'Multi-channel'})")
                
                # Add sample rate
                if hasattr(track, 'sampling_rate'):
                    sampling_rate = getattr(track, 'sampling_rate', 0)
                    if sampling_rate:
                        text_content.append(f"  Sample Rate: {int(sampling_rate)/1000:.1f} kHz")
                
                # Add codec
                if hasattr(track, 'codec'):
                    codec = getattr(track, 'codec', '')
                    if codec:
                        text_content.append(f"  Codec: {codec}")
                
                # Add language
                if hasattr(track, 'language'):
                    language = getattr(track, 'language', '')
                    if language:
                        text_content.append(f"  Language: {language}")
                
                # Add bit rate
                if hasattr(track, 'bit_rate'):
                    bit_rate = getattr(track, 'bit_rate', 0)
                    if bit_rate:
                        text_content.append(f"  Bitrate: {int(bit_rate)/1000:.0f} kbps")
                
            elif track.track_type == 'Text':
                text_tracks.append(track_data)
                
                # Add subtitle track details if this is the first track
                if len(text_tracks) == 1:
                    text_content.append("\nSubtitles:")
                
                # Add language
                if hasattr(track, 'language'):
                    language = getattr(track, 'language', '')
                    if language:
                        text_content.append(f"  Language: {language}")
                
                # Add format
                if hasattr(track, 'format'):
                    subtitle_format = getattr(track, 'format', '')
                    if subtitle_format:
                        text_content.append(f"  Format: {subtitle_format}")
            
            else:
                other_tracks.append(track_data)
        
        # Add track data to metadata
        metadata['video_tracks'] = video_tracks
        metadata['audio_tracks'] = audio_tracks
        metadata['text_tracks'] = text_tracks
        metadata['other_tracks'] = other_tracks
        
        # Add track counts to metadata
        metadata['video_track_count'] = len(video_tracks)
        metadata['audio_track_count'] = len(audio_tracks)
        metadata['text_track_count'] = len(text_tracks)
        metadata['other_track_count'] = len(other_tracks)
        
        # Create sections
        sections = []
        
        # Add general info section
        if general_info:
            sections.append({
                'type': 'general_info',
                'content': general_info
            })
        
        # Add video tracks section
        if video_tracks:
            sections.append({
                'type': 'video_tracks',
                'content': video_tracks
            })
        
        # Add audio tracks section
        if audio_tracks:
            sections.append({
                'type': 'audio_tracks',
                'content': audio_tracks
            })
        
        # Add text tracks section
        if text_tracks:
            sections.append({
                'type': 'text_tracks',
                'content': text_tracks
            })
        
        # Add other tracks section
        if other_tracks:
            sections.append({
                'type': 'other_tracks',
                'content': other_tracks
            })
        
        # Add thumbnail placeholder section
        sections.append({
            'type': 'thumbnail',
            'content': "Thumbnail extraction not implemented in this version."
        })
        
        return "\n".join(text_content), metadata, sections
    
    def _extract_basic(self, file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Basic extraction when mediainfo is not available.
        
        Args:
            file_path: The path to the video file.
            format_name: The format of the video file.
            
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
        text_content = [f"Video File: {file_name}"]
        text_content.append(f"Format: {format_name.upper()}")
        text_content.append(f"File Size: {self._format_file_size(file_size)}")
        text_content.append("")
        text_content.append("Note: Detailed video information not available.")
        text_content.append("Install pymediainfo for enhanced video metadata extraction.")
        
        # Create basic sections
        sections = [
            {
                'type': 'video_info',
                'content': {
                    'format': format_name,
                    'file_size': file_size
                }
            }
        ]
        
        return "\n".join(text_content), metadata, sections
    
    def _format_file_size(self, size_in_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_in_bytes: Size in bytes.
            
        Returns:
            Formatted file size string.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0 or unit == 'TB':
                break
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} {unit}"


# Global video handler instance
video_handler = VideoHandler()