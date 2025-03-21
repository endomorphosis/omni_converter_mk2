"""
Audio processor implementation using Whisper for speech-to-text.

This module provides a concrete implementation of audio processing with
speech-to-text capabilities using the OpenAI Whisper library.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Tuple, Optional, BinaryIO
from datetime import timedelta

from format_handlers.processors.base_processor import BaseProcessor
from utils.logger import logger

try:
    import whisper
    import numpy as np
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("Whisper not available, speech-to-text functionality will not be available")
    WHISPER_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.utils import mediainfo
    PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("pydub not available, audio extraction will be limited")
    PYDUB_AVAILABLE = False


class AudioProcessor(BaseProcessor):
    """
    Base interface for audio processors.
    
    This abstract class extends BaseProcessor with methods specific to audio processing.
    """
    
    def extract_metadata(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from an audio file.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            Metadata extracted from the audio file.
        """
        pass
    
    def extract_waveform(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract waveform data from an audio file.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            Waveform data extracted from the audio file.
        """
        pass
    
    def transcribe_audio(self, data: bytes, format_name: str, options: Dict[str, Any]) -> str:
        """
        Transcribe speech to text from an audio file.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            Transcribed text from the audio file.
        """
        pass
    
    def process_audio(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process an audio file completely, extracting metadata, waveform, and transcribing if available.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        pass


class WhisperAudioProcessor(AudioProcessor):
    """
    Audio processor implementation using Whisper for speech-to-text.
    
    This class provides functionality to extract metadata, waveform data, and
    transcribe speech to text from audio files using the Whisper library.
    """
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the Whisper audio processor.
        
        Args:
            model_name: The name of the Whisper model to use.
                Options include: "tiny", "base", "small", "medium", "large".
                Default is "base" which offers a good balance of accuracy and speed.
        """
        self.supported_formats = ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        self.model_name = model_name
        self.model = None
        
        # Initialize the Whisper model if available
        if WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Whisper model: {model_name}")
                self.model = whisper.load_model(model_name)
                logger.info(f"Whisper model {model_name} loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {str(e)}")
                self.model = None
    
    def can_process(self, format_name: str) -> bool:
        """
        Check if this processor can handle the given format.
        
        Args:
            format_name: The name of the format to check.
            
        Returns:
            True if this processor can handle the format and required libraries are available,
            False otherwise.
        """
        has_requirements = WHISPER_AVAILABLE and PYDUB_AVAILABLE
        return has_requirements and format_name.lower() in self.supported_formats
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the list of formats supported by this processor.
        
        Returns:
            A list of format names supported by this processor.
        """
        return self.supported_formats if WHISPER_AVAILABLE and PYDUB_AVAILABLE else []
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            A dictionary containing information about this processor.
        """
        info = {
            "name": "WhisperAudioProcessor",
            "supported_formats": self.get_supported_formats(),
            "whisper_available": WHISPER_AVAILABLE,
            "pydub_available": PYDUB_AVAILABLE,
            "model_name": self.model_name,
            "model_loaded": self.model is not None
        }
        
        if WHISPER_AVAILABLE:
            info["whisper_version"] = whisper.__version__
        
        return info
    
    def extract_metadata(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from an audio file.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            Metadata extracted from the audio file.
            
        Raises:
            ValueError: If pydub is not available or the data cannot be processed.
        """
        if not PYDUB_AVAILABLE:
            raise ValueError("pydub is not available for audio metadata extraction")
        
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{format_name}', delete=False) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name
            
            try:
                # Get media info
                info = mediainfo(temp_file_path)
                
                # Load audio file to get additional properties
                audio = AudioSegment.from_file(temp_file_path, format=format_name)
                
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
                    'file_size_bytes': len(data)
                }
                
                # Add additional metadata from mediainfo
                if info:
                    for key, value in info.items():
                        if key not in metadata and value:
                            metadata[key] = value
                
                # Extract tags if available
                if 'TAG' in info:
                    for tag_key, tag_value in info['TAG'].items():
                        if tag_value:
                            metadata[f'tag_{tag_key}'] = tag_value
                
                return metadata
                
            finally:
                # Remove temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"Error extracting metadata from audio: {str(e)}")
            raise ValueError(f"Error extracting metadata from audio: {str(e)}")
    
    def extract_waveform(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract waveform data from an audio file.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            Waveform data extracted from the audio file.
            
        Raises:
            ValueError: If pydub is not available or the data cannot be processed.
        """
        if not PYDUB_AVAILABLE:
            raise ValueError("pydub is not available for audio waveform extraction")
        
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{format_name}', delete=False) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                audio = AudioSegment.from_file(temp_file_path, format=format_name)
                
                # Extract a simplified waveform
                # For a full implementation, we'd analyze the waveform in detail
                # but for this version, we'll just extract some basic stats
                
                # Get a simplified waveform by sampling the audio
                # For a 30-second visualization, we'll extract 150 samples (1 sample per 0.2 seconds)
                duration_seconds = len(audio) / 1000.0
                max_samples = options.get("waveform_samples", 150)
                
                # Calculate sample interval based on duration
                sample_interval_ms = (len(audio) / max_samples) if duration_seconds > 0 else 200
                
                samples = []
                for i in range(0, len(audio), int(sample_interval_ms)):
                    if len(samples) >= max_samples:
                        break
                    segment = audio[i:i+10]  # Get a 10ms segment
                    if len(segment) > 0:
                        samples.append(segment.dBFS)
                
                return {
                    'waveform_type': 'dBFS',
                    'sample_count': len(samples),
                    'sample_interval_ms': sample_interval_ms,
                    'min_value': min(samples) if samples else None,
                    'max_value': max(samples) if samples else None,
                    'samples': samples
                }
                
            finally:
                # Remove temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"Error extracting waveform from audio: {str(e)}")
            raise ValueError(f"Error extracting waveform from audio: {str(e)}")
    
    def transcribe_audio(self, data: bytes, format_name: str, options: Dict[str, Any]) -> str:
        """
        Transcribe speech to text from an audio file using Whisper.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options including:
                language: The language code for transcription (e.g., "en")
                task: The task to perform ("transcribe" or "translate")
                
        Returns:
            Transcribed text from the audio file.
            
        Raises:
            ValueError: If Whisper is not available or the data cannot be processed.
        """
        if not WHISPER_AVAILABLE or self.model is None:
            raise ValueError("Whisper is not available for speech-to-text transcription")
        
        if not PYDUB_AVAILABLE:
            raise ValueError("pydub is not available for audio processing")
        
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{format_name}', delete=False) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name
            
            try:
                # Parse options
                language = options.get("language")
                task = options.get("task", "transcribe")  # Default to transcribe
                
                # Transcribe the audio
                result = self.model.transcribe(
                    temp_file_path,
                    language=language,
                    task=task
                )
                
                # Extract the transcribed text
                text = result.get("text", "")
                
                # Extract segments with timestamps if available
                segments = []
                if "segments" in result:
                    for segment in result["segments"]:
                        segments.append({
                            "start": segment.get("start"),
                            "end": segment.get("end"),
                            "text": segment.get("text")
                        })
                
                # Combine them into a nicely formatted transcript
                transcript = text.strip()
                
                # Add detailed transcript with timestamps if segments are available
                if segments:
                    detailed_transcript = []
                    for segment in segments:
                        start_time = segment.get("start")
                        if start_time is not None:
                            start_str = str(timedelta(seconds=int(start_time)))
                            detailed_transcript.append(f"[{start_str}] {segment.get('text', '')}")
                        else:
                            detailed_transcript.append(segment.get("text", ""))
                    
                    transcript += "\n\n--- Transcript with Timestamps ---\n\n"
                    transcript += "\n".join(detailed_transcript)
                
                return transcript
                
            finally:
                # Remove temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise ValueError(f"Error transcribing audio: {str(e)}")
    
    def process_audio(self, data: bytes, format_name: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process an audio file completely, extracting metadata, waveform, and transcribing if available.
        
        Args:
            data: The binary data of the audio file.
            format_name: The format of the audio file.
            options: Processing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
            
        Raises:
            ValueError: If required dependencies are not available or the data cannot be processed.
        """
        try:
            # Extract metadata
            metadata = self.extract_metadata(data, format_name, options)
            
            # Initialize sections
            sections = []
            
            # Extract waveform data if requested
            waveform_data = None
            if options.get("extract_waveform", True):
                try:
                    waveform_data = self.extract_waveform(data, format_name, options)
                    sections.append({
                        'type': 'waveform',
                        'content': waveform_data
                    })
                except Exception as e:
                    logger.warning(f"Error extracting waveform: {str(e)}")
            
            # Transcribe the audio if requested and Whisper is available
            transcript = ""
            transcribe_enabled = options.get("transcribe", True)
            
            if transcribe_enabled and WHISPER_AVAILABLE and self.model is not None:
                try:
                    transcript = self.transcribe_audio(data, format_name, options)
                    sections.append({
                        'type': 'transcript',
                        'content': transcript
                    })
                except Exception as e:
                    logger.warning(f"Error transcribing audio: {str(e)}")
                    transcript = f"[Error during transcription: {str(e)}]"
            elif transcribe_enabled and (not WHISPER_AVAILABLE or self.model is None):
                transcript = "[Speech-to-text transcription not available]"
                sections.append({
                    'type': 'transcript',
                    'content': transcript
                })
            
            # Generate human-readable description
            text_content = [f"Audio File: {metadata.get('tag_title', 'Untitled')}"]
            text_content.append(f"Format: {format_name.upper()}")
            text_content.append(f"Duration: {metadata.get('duration', '0:00:00')}")
            
            # Add artist and album if available
            if "tag_artist" in metadata:
                text_content.append(f"Artist: {metadata['tag_artist']}")
            
            if "tag_album" in metadata:
                text_content.append(f"Album: {metadata['tag_album']}")
            
            # Add technical info
            text_content.append(f"Channels: {metadata.get('channels', '?')} ({metadata.get('channel_mode', '?')})")
            text_content.append(f"Sample Rate: {metadata.get('frame_rate_hz', '?')} Hz")
            text_content.append(f"Bit Depth: {metadata.get('sample_width_bytes', '?') * 8} bits")
            
            if "bitrate" in metadata:
                text_content.append(f"Bitrate: {float(metadata['bitrate']) / 1000:.0f} kbps")
            
            # Add transcript if available
            if transcript:
                text_content.append("\n--- Transcript ---\n")
                text_content.append(transcript)
            
            # Add audio info section
            sections.append({
                'type': 'audio_info',
                'content': {
                    'format': format_name,
                    'duration': metadata.get('duration', '0:00:00'),
                    'channels': metadata.get('channels', 0),
                    'sample_rate': metadata.get('frame_rate_hz', 0),
                    'bit_depth': metadata.get('sample_width_bytes', 0) * 8
                }
            })
            
            # Add metadata section
            sections.append({
                'type': 'metadata',
                'content': metadata
            })
            
            return "\n".join(text_content), metadata, sections
            
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            raise ValueError(f"Error processing audio file: {str(e)}")


# Create a global instance for usage
whisper_processor = WhisperAudioProcessor()