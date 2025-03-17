#!/usr/bin/env python3
"""
Tests for the AudioHandler class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from format_handlers.audio_handler import AudioHandler, PYDUB_AVAILABLE
from format_handlers.base_handler import Content


class TestAudioHandler(unittest.TestCase):
    """Tests for AudioHandler."""
    
    def setUp(self):
        """Set up for tests."""
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
        """Test initialization."""
        self.assertEqual(self.handler.handler_name, "AudioHandler")
        self.assertEqual(self.handler.supported_formats, {"mp3", "wav", "ogg", "flac", "aac"})
        self.assertEqual(self.handler.capabilities['category'], "audio")
        self.assertFalse(self.handler.capabilities['preserves_structure'])
        self.assertTrue(self.handler.capabilities['extracts_metadata'])
        self.assertFalse(self.handler.capabilities['supports_transcription'])
    
    def test_can_handle(self):
        """Test can_handle method."""
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
        """Test extraction without pydub."""
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
        """Test extraction with pydub."""
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