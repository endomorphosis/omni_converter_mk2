#!/usr/bin/env python3
"""
Tests for the AudioHandler class.

This module provides comprehensive tests for the AudioHandler class, which is responsible
for processing various audio file formats (MP3, WAV, OGG, FLAC, AAC). The tests verify
that the handler can correctly identify supported formats, extract metadata, and process
audio content both with and without the optional pydub library for enhanced audio analysis.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from format_handlers.audio_handler import AudioHandler, PYDUB_AVAILABLE
from format_handlers.base_handler import Content


class TestAudioHandler(unittest.TestCase):
    """
    Test suite for the AudioHandler class.
    
    This test class verifies that the AudioHandler correctly processes audio files,
    extracts metadata (such as duration, bitrate, artist, title), and provides appropriate
    textual representation of audio content. The tests are designed to work with both the
    enhanced functionality when pydub is available and the basic functionality when it's not.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        
        Creates an AudioHandler instance and ensures the test directory exists.
        Also creates a mock audio file for testing if it doesn't already exist.
        This ensures each test has access to necessary resources without requiring
        actual audio files to be committed to the repository.
        """
        self.handler = AudioHandler()
        
        # Create test directory if it doesn't exist
        os.makedirs("test_files", exist_ok=True)
        
        # Create mock audio file if needed
        self.test_audio_path = "test_files/test.mp3"
        if not os.path.exists(self.test_audio_path):
            # Create a simple mock file
            with open(self.test_audio_path, "wb") as f:
                f.write(b"MOCK AUDIO FILE")
    
    def test_init(self):
        """
        Test proper initialization of the AudioHandler.
        
        Verifies that the AudioHandler correctly initializes with the expected
        handler name, supported formats (MP3, WAV, OGG, FLAC, AAC), and capabilities
        (category = audio, preserves_structure = False, extracts_metadata = True,
        supports_transcription = False).
        """
        self.assertEqual(self.handler.handler_name, "AudioHandler")
        self.assertEqual(self.handler.supported_formats, {"mp3", "wav", "ogg", "flac", "aac"})
        self.assertEqual(self.handler.capabilities['category'], "audio")
        self.assertFalse(self.handler.capabilities['preserves_structure'])
        self.assertTrue(self.handler.capabilities['extracts_metadata'])
        self.assertFalse(self.handler.capabilities['supports_transcription'])
    
    def test_can_handle(self):
        """
        Test the can_handle method for format detection.
        
        Verifies that the AudioHandler correctly identifies files of supported formats
        (MP3, WAV, OGG, FLAC, AAC) and rejects unsupported formats. Tests both the
        explicit format specification and format detection from file extension.
        """
        # Test with format name
        self.assertTrue(self.handler.can_handle("dummy_path.mp3", "mp3"))
        self.assertTrue(self.handler.can_handle("dummy_path.wav", "wav"))
        self.assertTrue(self.handler.can_handle("dummy_path.ogg", "ogg"))
        self.assertTrue(self.handler.can_handle("dummy_path.flac", "flac"))
        self.assertTrue(self.handler.can_handle("dummy_path.aac", "aac"))
        
        # Test with unsupported format
        self.assertFalse(self.handler.can_handle("dummy_path.txt", "txt"))
    
    @patch('format_handlers.audio_handler.PYDUB_AVAILABLE', False)
    @patch('format_handlers.audio_handler.format_detector')
    @patch('os.path.getsize')
    def test_extract_basic(self, mock_getsize, mock_detector):
        """
        Test basic audio content extraction without the pydub library.
        
        Verifies that the AudioHandler can extract basic information from audio files
        even when the pydub library is not available. Tests the fallback mechanism that
        provides limited metadata (format, file size) and basic content structure.
        Uses mocking to simulate file properties and format detection.
        """
        # Setup mocks
        mock_detector.detect_format.return_value = ("mp3", "audio/mpeg")
        mock_getsize.return_value = 12345
        
        # Mock validate_input to return True
        with patch.object(self.handler, 'validate_input', return_value=True):
            # Test basic extraction
            content = self.handler.extract_content(self.test_audio_path)
            
            # Verify the content
            self.assertIsInstance(content, Content)
            self.assertEqual(content.source_format, "mp3")
            self.assertEqual(content.source_path, self.test_audio_path)
            
            # Verify metadata
            self.assertEqual(content.metadata['format'], "mp3")
            self.assertEqual(content.metadata['file_size_bytes'], 12345)
            
            # Verify sections
            self.assertEqual(len(content.sections), 1)
            self.assertEqual(content.sections[0]['type'], "audio_info")
    
    @unittest.skipIf(not PYDUB_AVAILABLE, "pydub not available")
    @patch('format_handlers.audio_handler.mediainfo')
    @patch('format_handlers.audio_handler.AudioSegment')
    def test_extract_with_pydub(self, mock_AudioSegment, mock_mediainfo):
        """
        Test enhanced audio content extraction with the pydub library.
        
        Verifies that the AudioHandler can extract comprehensive information from audio files
        when the pydub library is available. Tests the extraction of detailed audio properties
        (channels, sample width, frame rate, loudness) and metadata tags (title, artist, album).
        Also checks that content is properly structured into audio_info, metadata, and waveform
        sections. Uses mocking to simulate audio segment properties and mediainfo results.
        
        This test is skipped if pydub is not available in the environment.
        """
        # Skip if pydub is not installed
        if not PYDUB_AVAILABLE:
            self.skipTest("pydub not available")
        
        # Setup mocks
        mock_audio = MagicMock()
        mock_audio.channels = 2
        mock_audio.sample_width = 2
        mock_audio.frame_rate = 44100
        mock_audio.frame_width = 4
        mock_audio.dBFS = -20.5
        mock_audio.__len__.return_value = 180000  # 3 minutes in milliseconds
        
        mock_AudioSegment.from_file.return_value = mock_audio
        
        mock_mediainfo.return_value = {
            'bit_rate': '320000',
            'TAG': {
                'title': 'Test Song',
                'artist': 'Test Artist',
                'album': 'Test Album',
                'genre': 'Test Genre',
                'date': '2023'
            }
        }
        
        # Test pydub extraction
        with patch('format_handlers.audio_handler.format_detector') as mock_detector:
            mock_detector.detect_format.return_value = ("mp3", "audio/mpeg")
            
            # Mock validate_input to return True
            with patch.object(self.handler, 'validate_input', return_value=True):
                content = self.handler.extract_content(self.test_audio_path)
                
                # Verify the content
                self.assertIsInstance(content, Content)
                self.assertEqual(content.source_format, "mp3")
                self.assertEqual(content.source_path, self.test_audio_path)
                
                # Verify metadata
                self.assertEqual(content.metadata['format'], "mp3")
                self.assertEqual(content.metadata['channels'], 2)
                self.assertEqual(content.metadata['sample_width_bytes'], 2)
                self.assertEqual(content.metadata['frame_rate_hz'], 44100)
                self.assertEqual(content.metadata['loudness_dbfs'], -20.5)
                self.assertEqual(content.metadata['bitrate_kbps'], 320.0)
                self.assertEqual(content.metadata['title'], 'Test Song')
                self.assertEqual(content.metadata['artist'], 'Test Artist')
                self.assertEqual(content.metadata['album'], 'Test Album')
                
                # Verify sections
                self.assertEqual(len(content.sections), 3)
                self.assertEqual(content.sections[0]['type'], "audio_info")
                self.assertEqual(content.sections[1]['type'], "metadata")
                self.assertEqual(content.sections[2]['type'], "waveform")


if __name__ == '__main__':
    unittest.main()