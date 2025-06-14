# """
# Video format handlers for the Omni-Converter.

# This module provides handlers for video formats like MP4, WebM, AVI, MKV, and MOV.
# It extracts metadata and generates text descriptions of video files.
# """

# import os
# import io
# from datetime import datetime, timedelta
# from typing import Any, Callable, Optional, Set, TypeAlias, TypeVar, Union
# import tempfile
# import shutil

# from utils.filesystem import FileSystem
# from logger import logger
# from core.file_format_detector import file_format_detector
# from core.content_extractor.base_handler import BaseFormatHandler, Content

# # Import pymediainfo for metadata extraction (will be installed via requirements.txt)
# try:
#     import pymediainfo
#     MEDIAINFO_AVAILABLE = True
# except ImportError:
#     logger.warning("pymediainfo not available, video metadata extraction will be limited")
#     MEDIAINFO_AVAILABLE = False

# # Import PIL for thumbnail extraction
# try:
#     import PIL
#     PIL_AVAILABLE = True
# except ImportError:
#     logger.warning("PIL not available, thumbnail extraction will be limited")
#     PIL_AVAILABLE = False

# if MEDIAINFO_AVAILABLE:
#     # Define custom type for pymediainfo Track
#     Track: TypeAlias = pymediainfo.Track
# else:
#     # Fallback to Any if pymediainfo is not available
#     Track: TypeAlias = Any

# def _format_text_content(text_content: list[str], track: 'Track', attribute_list: list[tuple[str, Any, Any]]) -> str:
#     """
#     Format text content for a specific track.
#     """
#     for attr, default, func in attribute_list:
#         if hasattr(track, attr):
#             value = getattr(track, attr, default)
#             if value:
#                 name = attr.replace('_', ' ').capitalize()
#                 value = func(value) if isinstance(func, Callable) else value
#                 text_content.append(
#                     f"  {name}: {value}".rstrip()
#                 )

# class VideoHandler(BaseFormatHandler):
#     """
#     Handler for video-based formats.
    
#     Handles common video formats like MP4, WebM, AVI, MKV, and MOV.
#     Extracts metadata and generates basic descriptions for video files.
#     Can extract thumbnails and frames using the video processor.
#     """
    
#     def __init__(self):
#         """Initialize the video handler."""
#         # Try to import the video processor
#         try:
#             from core.content_extractor.processors.by_ability.video_processor import video_processor
#             self.video_processor_available = True
#         except ImportError:
#             self.video_processor_available = False
            
#         super().__init__(
#             handler_name="VideoHandler",
#             supported_formats={"mp4", "webm", "avi", "mkv", "mov"},
#             capabilities={
#                 'category': 'video',
#                 'preserves_structure': False,
#                 'extracts_metadata': True,
#                 'supports_transcription': False,  # Set to True if speech-to-text is implemented # TODO
#                 'extracts_thumbnails': self.video_processor_available  # True if video processor is available
#             }
#         )
        
#         # Format-specific file extensions
#         self.format_extensions = {
#             'mp4': ['.mp4', '.m4v'],
#             'webm': ['.webm'],
#             'avi': ['.avi'],
#             'mkv': ['.mkv'],
#             'mov': ['.mov', '.qt']
#         }
    
#     def do_extraction(self, file_path: str, options: dict[str, Any]) -> Content:
#         """
#         Extract content from a video file.
        
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
        
#         logger.debug(f"Extracting content from {format_name} video file: {file_path}")
        
#         try:
#             # Extract metadata using mediainfo if available
#             if MEDIAINFO_AVAILABLE:
#                 text, metadata, sections = self._extract_with_mediainfo(file_path, format_name, options)
#             else:
#                 # Fallback to basic extraction
#                 text, metadata, sections = self._extract_basic(file_path, format_name, options)
            
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
#             logger.exception(f"Error extracting content from {format_name} video file: '{file_path}'\n{e}")
#             raise e

#     def _extract_with_mediainfo(self, file_path: str, format_name: str, options: Optional[dict[str, Any]] = None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
#         """
#         Extract video information using pymediainfo.
        
#         Args:
#             file_path: The path to the video file.
#             format_name: The format of the video file.
#             options: Optional processing options.
            
#         Returns:
#             A tuple of (text content, metadata, sections).
#         """
#         options = options or {}
#         # Use chunk-based analysis to prevent loading entire file in memory
#         # Create a temporary file pointer to read the file in chunks for mediainfo
#         # This prevents loading large video files entirely into memory
#         try:
#             # Create metadata dictionary
#             metadata = {
#                 'format': format_name,
#                 'file_size_bytes': os.path.getsize(file_path),
#                 'tracks': []
#             }
            
#             # Get media info using streaming mode if possible
#             if hasattr(pymediainfo.MediaInfo, 'parse_with_options'):
#                 # Use streaming mode if available (newer pymediainfo versions)
#                 media_info = pymediainfo.MediaInfo.parse_with_options(
#                     filename=file_path,
#                     options={"File_FileNameFormat": "CSV", "File_ExpandFileNames": "1"}
#                 )
#             else:
#                 # Fall back to standard parser
#                 media_info = pymediainfo.MediaInfo.parse(file_path)
#         except Exception as e:
#             logger.warning(f"Error during mediainfo parsing: {e}")
#             # Fall back to basic extraction if mediainfo fails
#             return self._extract_basic(file_path, format_name)
        
#         # Generate human-readable description
#         text_content = [f"Video File: {os.path.basename(file_path)}"]
#         text_content.append(f"Format: {format_name.upper()}")
        
#         # Process tracks
#         general_info = None
#         video_tracks = []
#         audio_tracks = []
#         text_tracks = []
#         other_tracks = []
        
#         for track in media_info.tracks:
#             track_data = {'track_type': track.track_type}
            
#             # Add all attributes from the track to track_data
#             for attr in dir(track):
#                 if not attr.startswith('__') and not callable(getattr(track, attr)):
#                     value = getattr(track, attr)
#                     if value is not None and value != "":
#                         track_data[attr] = value
            
#             # Categorize tracks by type
#             match track.track_type:
#                 case 'General':
#                     general_info = track_data
#                     metadata['general'] = track_data
                    
#                     # Add duration and other general information
#                     if hasattr(track, 'duration'):
#                         duration_ms = getattr(track, 'duration', 0)
#                         if duration_ms:
#                             duration = str(timedelta(milliseconds=int(duration_ms)))
#                             text_content.append(f"Duration: {duration}")
#                             metadata['duration_ms'] = duration_ms
#                             metadata['duration'] = duration
                    
#                     # Add file size
#                     if hasattr(track, 'file_size'):
#                         file_size = getattr(track, 'file_size', 0)
#                         if file_size:
#                             text_content.append(f"File Size: {self._format_file_size(file_size)}")
#                             metadata['file_size_bytes'] = file_size
                    
#                     # Add overall bitrate
#                     if hasattr(track, 'overall_bit_rate'):
#                         overall_bit_rate = getattr(track, 'overall_bit_rate', 0)
#                         if overall_bit_rate:
#                             text_content.append(f"Overall Bitrate: {int(overall_bit_rate)/1000:.0f} kbps")
#                             metadata['overall_bitrate_kbps'] = int(overall_bit_rate)/1000
                
#                 case 'Video':
#                     video_tracks.append(track_data)
                    
#                     # Add video track details to text content
#                     text_content.append("\nVideo:")
                    
#                     # Add resolution
#                     if hasattr(track, 'width') and hasattr(track, 'height'):
#                         width, height = getattr(track, 'width', 0), getattr(track, 'height', 0)
#                         if width and height:
#                             text_content.append(f"  Resolution: {width}x{height}")

#                     # Add frame rate, code, bit depth, and bit rate
#                     for attr, default, func in [('frame_rate', 0, lambda x: f"{x:.2f} fps"),
#                                                 ('codec', '', ''),
#                                                 ('bit_depth', '', lambda x: f"{x} bits"),
#                                                 ('bit_rate', 0, lambda x: f"{int(x)/1000:.0f} kbps")]:
#                         if hasattr(track, attr):
#                             value = getattr(track, attr, default)
#                             if value:
#                                 name = attr.replace('_', ' ').capitalize()
#                                 value = func(value) if isinstance(func, Callable) else value
#                                 text_content.append(
#                                     f"  {name}: {value}".rstrip()
#                                 )

#                 case 'Audio':
#                     audio_tracks.append(track_data)
                    
#                     # Add audio track details to text content
#                     if len(audio_tracks) == 1:
#                         text_content.append("\nAudio:")
                    
#                     # Label track if multiple audio tracks
#                     if len(audio_tracks) > 1:
#                         text_content.append(f"\nAudio Track {len(audio_tracks)}:")
                    
#                     # Add channels, sample rate, codec, language, and bit rate
#                     for attr, default, func in [('channel_s', 0, lambda x: '(Mono)' if x == 1 else '(Stereo)' if x == 2 else '(Multi-channel)'),
#                                             ('sampling_rate', 0, lambda x: f"{int(x)/1000:.1f} kHz"),
#                                             ('codec', '', ''),
#                                             ('language', '', ''),
#                                             ('bit_rate', 0, lambda x: f"{int(x)/1000:.0f} kbps")]:
#                         if hasattr(track, attr):
#                             value = getattr(track, attr, default)
#                             if value:
#                                 name = attr.replace('_', ' ').capitalize()
#                                 value = func(value) if isinstance(func, Callable) else value
#                                 text_content.append(
#                                     f"  {name}: {value}".rstrip()
#                                 )

#                 case 'Text':
#                     text_tracks.append(track_data)
                    
#                     # Add subtitle track details if this is the first track
#                     if len(text_tracks) == 1:
#                         text_content.append("\nSubtitles:")

#                     # Add language and format
#                     for attr in ['language', 'format']:
#                         if hasattr(track, attr):
#                             value = getattr(track, attr, '')
#                             if value:
#                                 text_content.append(f"  {attr.capitalize()}: {value}")
#                 case _:
#                     other_tracks.append(track_data)

#         # Add track data to metadata
#         for key, value in [("video_tracks", video_tracks),
#                            ("audio_tracks", audio_tracks),
#                            ("text_tracks", text_tracks),
#                            ("other_tracks", other_tracks)]:
#             metadata[key] = value
#             metadata[key.rstrip('s') + "_count"] = len(value) # Add track count to metadata

#         # Create sections
#         sections = []

#         # Add general info section
#         for type_, content in [('general_info', general_info),
#                                ('video_tracks', video_tracks), # Add video tracks section
#                                ('audio_tracks', audio_tracks), # Add audio tracks section
#                                ('text_tracks', text_tracks),  # Add text tracks section
#                                ('other_tracks', other_tracks)]: # Add other tracks section
#             if content:
#                 sections.append({
#                     'type': type_,
#                     'content': content,
#                 })

#         # Add thumbnail section - use the video processor if available
#         if self.video_processor_available and hasattr(self, 'video_processor_available'):
#             try:
#                 from core.content_extractor.processors.by_ability.video_processor import video_processor
                
#                 # Extract video info
#                 video_info = video_processor.extract_video_info(file_path)
                
#                 # Add video info to metadata
#                 metadata.update({
#                     'video_info': video_info
#                 })
                
#                 # Extract thumbnail if processor is available and options allow it
#                 extract_thumbnails = options.get('extract_thumbnails', True)
#                 if extract_thumbnails:
#                     # Get one thumbnail from a quarter way through the video for better representation
#                     time_offset = video_info.get('duration', 0) * 0.25
#                     if time_offset <= 0:
#                         time_offset = 5  # Default to 5 seconds if duration is unknown
                        
#                     thumbnail_data = video_processor.extract_thumbnail(
#                         file_path, 
#                         {'time_offset': time_offset, 'max_size': 320}
#                     )
                    
#                     if thumbnail_data:
#                         sections.append({
#                             'type': 'thumbnail',
#                             'content': thumbnail_data,
#                             'format': 'png',
#                             'time_offset': time_offset
#                         })
#                         text_content.append("\nThumbnail extracted successfully.")
#                     else:
#                         sections.append({
#                             'type': 'thumbnail',
#                             'content': "Thumbnail extraction failed."
#                         })
#                         text_content.append("\nThumbnail extraction failed.")
                
#                 # Extract key frames if requested
#                 extract_frames = options.get('extract_frames', False)
#                 if extract_frames:
#                     # Get 5 evenly spaced frames
#                     frames = video_processor.extract_key_frames(
#                         file_path, 
#                         {'frame_count': 5, 'max_size': 320}
#                     )
                    
#                     if frames:
#                         sections.append({
#                             'type': 'key_frames',
#                             'content': frames
#                         })
#                         text_content.append(f"\n{len(frames)} key frames extracted.")
#                     else:
#                         sections.append({
#                             'type': 'key_frames',
#                             'content': "Key frame extraction failed."
#                         })
                
#             except Exception as e:
#                 logger.warning(f"Error using video processor: {e}")
#                 sections.append({
#                     'type': 'thumbnail',
#                     'content': f"Thumbnail extraction failed: {str(e)}"
#                 })
#         else:
#             # Add thumbnail placeholder section if video processor is not available
#             sections.append({
#                 'type': 'thumbnail',
#                 'content': "Thumbnail extraction not available - video processor not found."
#             })
        
#         return "\n".join(text_content), metadata, sections
    
#     def _extract_basic(self, file_path: str, format_name: str, options: Optional[dict[str, Any]] = None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
#         """
#         Basic extraction when mediainfo is not available.
        
#         Args:
#             file_path: The path to the video file.
#             format_name: The format of the video file.
#             options: Optional processing options.
            
#         Returns:
#             A tuple of (text content, metadata, sections).
#         """
#         options = options or {}
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
#         text_content = [f"Video File: {file_name}"]
#         text_content.append(f"Format: {format_name.upper()}")
#         text_content.append(f"File Size: {self._format_file_size(file_size)}")
#         text_content.append("")
#         text_content.append("Note: Detailed video information not available.")
#         text_content.append("Install pymediainfo for enhanced video metadata extraction.")
        
#         # Create basic sections
#         sections = [
#             {
#                 'type': 'video_info',
#                 'content': {
#                     'format': format_name,
#                     'file_size': file_size
#                 }
#             }
#         ]
        
#         # Try to extract thumbnail using the video processor if available
#         if self.video_processor_available and hasattr(self, 'video_processor_available'):
#             try:
#                 from core.content_extractor.processors.by_ability.video_processor import video_processor
                
#                 # Extract thumbnail
#                 extract_thumbnails = options.get('extract_thumbnails', True)
#                 if extract_thumbnails:
#                     thumbnail_data = video_processor.extract_thumbnail(
#                         file_path, 
#                         {'time_offset': 5, 'max_size': 320}  # Default values
#                     )
                    
#                     if thumbnail_data:
#                         sections.append({
#                             'type': 'thumbnail',
#                             'content': thumbnail_data,
#                             'format': 'png',
#                             'time_offset': 5
#                         })
#                         text_content.append("\nThumbnail extracted successfully.")
#                     else:
#                         sections.append({
#                             'type': 'thumbnail',
#                             'content': "Thumbnail extraction failed."
#                         })
#             except Exception as e:
#                 logger.warning(f"Error using video processor for basic extraction: {e}")
#                 sections.append({
#                     'type': 'thumbnail',
#                     'content': "Thumbnail extraction not available."
#                 })
        
#         return "\n".join(text_content), metadata, sections
    
#     def _format_file_size(self, size_in_bytes: int) -> str:
#         """
#         Format file size in human-readable format.
        
#         Args:
#             size_in_bytes: Size in bytes.
            
#         Returns:
#             Formatted file size string.
#         """
#         for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
#             if size_in_bytes < 1024.0 or unit == 'TB':
#                 break
#             size_in_bytes /= 1024.0
#         return f"{size_in_bytes:.2f} {unit}"


# # Global video handler instance
# video_handler = VideoHandler()
