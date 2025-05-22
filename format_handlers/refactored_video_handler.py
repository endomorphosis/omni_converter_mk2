"""
Video format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for video formats like MP4, WebM, AVI, MKV, and MOV
using dependency injection for better modularity and testability, without inheritance.
"""

import os
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.configs import Configs
from utils.logger import logger
from utils.format_detector import format_detector
from format_handlers.unified_handler import BaseFormatHandler, Content, create_handler, map_extension_to_format
from format_handlers.constants import Constants


def create_video_handler(resources: Dict[str, Any], configs: Optional[Configs] = None) -> BaseFormatHandler:
    """
    Create a video handler instance with injected dependencies.
    
    Args:
        resources: Resources dictionary with dependencies.
        configs: Configuration settings.
        
    Returns:
        BaseFormatHandler instance configured for video formats.
    """
    # Format-specific file extensions
    format_extensions = {
        'mp4': ['.mp4', '.m4v'],
        'webm': ['.webm'],
        'avi': ['.avi'],
        'mkv': ['.mkv'],
        'mov': ['.mov', '.qt']
    }
    
    # Prepare parsers with the appropriate functions
    parsers = {
        "video": {
            "mp4": process_video_file,
            "webm": process_video_file,
            "avi": process_video_file,
            "mkv": process_video_file,
            "mov": process_video_file
        }
    }
    
    # Extract required processors from resources - fail fast if missing
    pymediainfo_processor = resources["pymediainfo_processor"]
    cv2_processor = resources.get("cv2_processor")
    ffmpeg_processor = resources.get("ffmpeg_processor")
    
    # Determine capabilities based on available processors
    capabilities = dict(Constants.VIDEO_HANDLER_CAPABILITIES)
    capabilities['extracts_thumbnails'] = ffmpeg_processor is not None or cv2_processor is not None
    
    # Additional resources specific to video handling
    video_resources = {
        "pymediainfo_processor": pymediainfo_processor,
        "cv2_processor": cv2_processor,
        "ffmpeg_processor": ffmpeg_processor,
        "format_extensions": format_extensions
    }
    
    # Create and return the handler
    return create_handler(
        handler_name="VideoHandler",
        format_detector=format_detector,
        ext_to_format=map_extension_to_format,
        supported_formats=Constants.SUPPORTED_VIDEO_FORMATS_SET,
        capabilities=capabilities,
        parsers=parsers,
        resources_extra=video_resources,
        configs=configs
    )


def process_video_file(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a video file and extract content.
    
    Args:
        file_content: The file content to process (typically binary).
        options: Processing options including format information.
        
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Get key information from the options
    file_path = options.get("file_path", "")
    format_name = options.get("format", "")
    
    # Get processors from options
    pymediainfo_processor = options.get("pymediainfo_processor")
    cv2_processor = options.get("cv2_processor")
    ffmpeg_processor = options.get("ffmpeg_processor")
    
    # Extract metadata using pymediainfo if available
    if pymediainfo_processor and pymediainfo_processor.is_available():
        text, metadata, sections = pymediainfo_processor.process_video_metadata(file_path, format_name)
    else:
        # Basic extraction if pymediainfo is not available
        text, metadata, sections = extract_basic(file_path, format_name)
    
    # Extract thumbnail and frames if requested
    extract_thumbnails = options.get('extract_thumbnails', True)
    extract_frames = options.get('extract_frames', False)
    
    if extract_thumbnails or extract_frames:
        # Try using FFmpeg first
        if ffmpeg_processor and ffmpeg_processor.is_available():
            try:
                # Get video info if not already present in metadata
                if not metadata.get('video_info') and 'duration' not in metadata:
                    video_info = ffmpeg_processor.get_video_info(file_path)
                    metadata['video_info'] = video_info
                
                # Extract thumbnail
                if extract_thumbnails:
                    # Use 25% of duration for better representation
                    if 'video_info' in metadata and metadata['video_info'].get('duration', 0) > 0:
                        time_offset = metadata['video_info']['duration'] * 0.25
                    else:
                        time_offset = 5.0  # Default to 5 seconds
                    
                    thumbnail_data = ffmpeg_processor.extract_thumbnail(
                        file_path, 
                        time_offset=time_offset,
                        max_size=320
                    )
                    
                    if thumbnail_data:
                        sections.append({
                            'type': 'thumbnail',
                            'content': thumbnail_data,
                            'format': 'png',
                            'time_offset': time_offset
                        })
                        text += "\nThumbnail extracted successfully."
                
                # Extract frames
                if extract_frames:
                    frames = ffmpeg_processor.extract_multiple_frames(
                        file_path,
                        frame_count=5,
                        max_size=320
                    )
                    
                    if frames:
                        sections.append({
                            'type': 'key_frames',
                            'content': frames
                        })
                        text += f"\n{len(frames)} key frames extracted."
            
            except Exception as e:
                logger.warning(f"Error using FFmpeg for video processing: {e}")
                # Continue to try OpenCV as fallback
        
        # Fallback to OpenCV if FFmpeg failed or is not available
        if (not ffmpeg_processor or not any(s.get('type') == 'thumbnail' for s in sections)) and cv2_processor and cv2_processor.is_available():
            try:
                # Get video properties
                video_props = cv2_processor.get_video_properties(file_path)
                
                # Add to metadata if not already present
                if 'video_info' not in metadata:
                    metadata['video_info'] = video_props
                
                # Extract thumbnail
                if extract_thumbnails and not any(s.get('type') == 'thumbnail' for s in sections):
                    # Use 25% of duration for better representation
                    if video_props.get('duration', 0) > 0:
                        time_offset = video_props['duration'] * 0.25
                    else:
                        time_offset = 5.0  # Default to 5 seconds
                    
                    thumbnail_data = cv2_processor.extract_frame(
                        file_path,
                        time_offset=time_offset,
                        max_size=320
                    )
                    
                    if thumbnail_data:
                        sections.append({
                            'type': 'thumbnail',
                            'content': thumbnail_data,
                            'format': 'png',
                            'time_offset': time_offset
                        })
                        text += "\nThumbnail extracted successfully."
                
                # Extract frames
                if extract_frames and not any(s.get('type') == 'key_frames' for s in sections):
                    frames = cv2_processor.extract_multiple_frames(
                        file_path,
                        frame_count=5,
                        max_size=320
                    )
                    
                    if frames:
                        sections.append({
                            'type': 'key_frames',
                            'content': frames
                        })
                        text += f"\n{len(frames)} key frames extracted."
                
            except Exception as e:
                logger.warning(f"Error using OpenCV for video processing: {e}")
    
    # If thumbnails or frames were requested but not extracted, add a placeholder
    if extract_thumbnails and not any(s.get('type') == 'thumbnail' for s in sections):
        sections.append({
            'type': 'thumbnail',
            'content': "Thumbnail extraction not available - video processor not found."
        })
    
    return text, metadata, sections


def extract_basic(file_path: str, format_name: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Basic extraction when pymediainfo is not available.
    
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
    text_content.append(f"File Size: {format_file_size(file_size)}")
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


def format_file_size(size_in_bytes: int) -> str:
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