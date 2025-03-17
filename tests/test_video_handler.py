#!/usr/bin/env python3
"""
Tests for the VideoHandler class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from format_handlers.video_handler import VideoHandler, MEDIAINFO_AVAILABLE
from format_handlers.base_handler import Content


class TestVideoHandler(unittest.TestCase):
    """Tests for VideoHandler."""
    
    def setUp(self):
        """Set up for tests."""
        self.handler = VideoHandler()
        
        # Create test directory if it doesn't exist
        os.makedirs("test_files", exist_ok=True)
        
        # Create mock video file if needed
        self.test_video_path = "test_files/test.mp4"
        if not os.path.exists(self.test_video_path):
            # Create a simple mock file
            with open(self.test_video_path, "wb") as f:
                f.write(b"MOCK VIDEO FILE")
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.handler.handler_name, "VideoHandler")
        self.assertEqual(self.handler.supported_formats, {"mp4", "webm", "avi", "mkv", "mov"})
        self.assertEqual(self.handler.capabilities['category'], "video")
        self.assertFalse(self.handler.capabilities['preserves_structure'])
        self.assertTrue(self.handler.capabilities['extracts_metadata'])
        self.assertFalse(self.handler.capabilities['supports_transcription'])
        self.assertFalse(self.handler.capabilities['extracts_thumbnails'])
    
    def test_can_handle(self):
        """Test can_handle method."""
        # Test with format name
        self.assertTrue(self.handler.can_handle("dummy_path.mp4", "mp4"))
        self.assertTrue(self.handler.can_handle("dummy_path.webm", "webm"))
        self.assertTrue(self.handler.can_handle("dummy_path.avi", "avi"))
        self.assertTrue(self.handler.can_handle("dummy_path.mkv", "mkv"))
        self.assertTrue(self.handler.can_handle("dummy_path.mov", "mov"))
        
        # Test with unsupported format
        self.assertFalse(self.handler.can_handle("dummy_path.txt", "txt"))
    
    @patch('format_handlers.video_handler.MEDIAINFO_AVAILABLE', False)
    @patch('format_handlers.video_handler.format_detector')
    @patch('os.path.getsize')
    def test_extract_basic(self, mock_getsize, mock_detector):
        """Test extraction without mediainfo."""
        # Setup mocks
        mock_detector.detect_format.return_value = ("mp4", "video/mp4")
        mock_getsize.return_value = 12345678
        
        # Mock validate_input to return True
        with patch.object(self.handler, 'validate_input', return_value=True):
            # Test basic extraction
            content = self.handler.extract_content(self.test_video_path)
            
            # Verify the content
            self.assertIsInstance(content, Content)
            self.assertEqual(content.source_format, "mp4")
            self.assertEqual(content.source_path, self.test_video_path)
            
            # Verify metadata
            self.assertEqual(content.metadata['format'], "mp4")
            self.assertEqual(content.metadata['file_size_bytes'], 12345678)
            
            # Verify sections
            self.assertEqual(len(content.sections), 1)
            self.assertEqual(content.sections[0]['type'], "video_info")
    
    @unittest.skipIf(not MEDIAINFO_AVAILABLE, "pymediainfo not available")
    @patch('pymediainfo.MediaInfo.parse')
    def test_extract_with_mediainfo(self, mock_mediainfo_parse):
        """Test extraction with mediainfo."""
        # Skip if mediainfo is not installed
        if not MEDIAINFO_AVAILABLE:
            self.skipTest("pymediainfo not available")
        
        # Setup mocks
        mock_tracks = []
        
        # Create mock General track
        general_track = MagicMock()
        general_track.track_type = 'General'
        general_track.duration = 120000  # 2 minutes in milliseconds
        general_track.file_size = 12345678
        general_track.overall_bit_rate = 1000000  # 1 Mbps
        mock_tracks.append(general_track)
        
        # Create mock Video track
        video_track = MagicMock()
        video_track.track_type = 'Video'
        video_track.width = 1920
        video_track.height = 1080
        video_track.frame_rate = 30
        video_track.codec = 'AVC'
        video_track.bit_depth = 8
        video_track.bit_rate = 800000  # 800 kbps
        mock_tracks.append(video_track)
        
        # Create mock Audio track
        audio_track = MagicMock()
        audio_track.track_type = 'Audio'
        audio_track.channel_s = 2
        audio_track.sampling_rate = 48000
        audio_track.codec = 'AAC'
        audio_track.language = 'en'
        audio_track.bit_rate = 192000  # 192 kbps
        mock_tracks.append(audio_track)
        
        # Create mock Subtitle track
        subtitle_track = MagicMock()
        subtitle_track.track_type = 'Text'
        subtitle_track.language = 'en'
        subtitle_track.format = 'SRT'
        mock_tracks.append(subtitle_track)
        
        # Setup mock MediaInfo with tracks
        mock_media_info = MagicMock()
        mock_media_info.tracks = mock_tracks
        mock_mediainfo_parse.return_value = mock_media_info
        
        # Mock detect_format
        with patch('format_handlers.video_handler.format_detector') as mock_detector:
            mock_detector.detect_format.return_value = ("mp4", "video/mp4")
            
            # Mock validate_input to return True
            with patch.object(self.handler, 'validate_input', return_value=True):
                # Test mediainfo extraction
                content = self.handler.extract_content(self.test_video_path)
                
                # Verify the content
                self.assertIsInstance(content, Content)
                self.assertEqual(content.source_format, "mp4")
                self.assertEqual(content.source_path, self.test_video_path)
                
                # Verify metadata
                self.assertEqual(content.metadata['format'], "mp4")
                self.assertEqual(content.metadata['duration_ms'], 120000)
                self.assertEqual(content.metadata['file_size_bytes'], 12345678)
                self.assertEqual(content.metadata['overall_bitrate_kbps'], 1000)
                self.assertEqual(content.metadata['video_track_count'], 1)
                self.assertEqual(content.metadata['audio_track_count'], 1)
                self.assertEqual(content.metadata['text_track_count'], 1)
                
                # Verify video track info in the metadata
                video_tracks = content.metadata['video_tracks']
                self.assertEqual(len(video_tracks), 1)
                self.assertEqual(video_tracks[0]['width'], 1920)
                self.assertEqual(video_tracks[0]['height'], 1080)
                self.assertEqual(video_tracks[0]['frame_rate'], 30)
                self.assertEqual(video_tracks[0]['codec'], 'AVC')
                
                # Verify audio track info in the metadata
                audio_tracks = content.metadata['audio_tracks']
                self.assertEqual(len(audio_tracks), 1)
                self.assertEqual(audio_tracks[0]['channel_s'], 2)
                self.assertEqual(audio_tracks[0]['sampling_rate'], 48000)
                self.assertEqual(audio_tracks[0]['codec'], 'AAC')
                self.assertEqual(audio_tracks[0]['language'], 'en')
                
                # Verify sections
                self.assertGreaterEqual(len(content.sections), 5)  # At least 5 sections
                section_types = [section['type'] for section in content.sections]
                self.assertIn('general_info', section_types)
                self.assertIn('video_tracks', section_types)
                self.assertIn('audio_tracks', section_types)
                self.assertIn('text_tracks', section_types)
                self.assertIn('thumbnail', section_types)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        self.assertEqual(self.handler._format_file_size(1000), "1000.00 B")
        self.assertEqual(self.handler._format_file_size(1500), "1.46 KB")
        self.assertEqual(self.handler._format_file_size(1500000), "1.43 MB")
        self.assertEqual(self.handler._format_file_size(1500000000), "1.40 GB")
        self.assertEqual(self.handler._format_file_size(1500000000000), "1.36 TB")


if __name__ == '__main__':
    unittest.main()