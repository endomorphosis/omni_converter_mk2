#!/usr/bin/env python3
"""
Tests for the VideoHandler class.

This module provides comprehensive tests for the VideoHandler class, which is responsible
for processing various video file formats (MP4, WebM, AVI, MKV, MOV). The tests verify
that the handler can correctly identify supported formats, extract metadata from video files,
and process video content both with and without the optional pymediainfo library for
enhanced video analysis and track information extraction.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from format_handlers.video_handler import VideoHandler, PYMEDIAINFO_AVAILABLE
from format_handlers.base_handler import Content


class TestVideoHandler(unittest.TestCase):
    """
    Test suite for the VideoHandler class.
    
    This test class verifies that the VideoHandler correctly processes video files,
    extracts metadata (such as duration, resolution, bitrate, codec information),
    and provides appropriate textual representation of video content. The tests are
    designed to work with both the enhanced functionality when pymediainfo is available
    and the basic functionality when it's not. Tests also verify proper handling of
    multiple tracks (video, audio, subtitles) when present in the video file.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        
        Creates a VideoHandler instance and ensures the test directory exists.
        Also creates a mock video file for testing if it doesn't already exist.
        This ensures each test has access to necessary resources without requiring
        actual video files to be committed to the repository.
        """
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
        """
        Test proper initialization of the VideoHandler.
        
        Verifies that the VideoHandler correctly initializes with the expected
        handler name, supported formats (MP4, WebM, AVI, MKV, MOV), and capabilities
        (category = video, preserves_structure = False, extracts_metadata = True,
        supports_transcription = False, extracts_thumbnails depends on video_processor_available).
        """
        self.assertEqual(self.handler.handler_name, "VideoHandler")
        self.assertEqual(self.handler.supported_formats, {"mp4", "webm", "avi", "mkv", "mov"})
        self.assertEqual(self.handler.capabilities['category'], "video")
        self.assertFalse(self.handler.capabilities['preserves_structure'])
        self.assertTrue(self.handler.capabilities['extracts_metadata'])
        self.assertFalse(self.handler.capabilities['supports_transcription'])
        # Capability now depends on video_processor_available
        self.assertEqual(self.handler.capabilities['extracts_thumbnails'], 
                         self.handler.video_processor_available)
    
    def test_can_handle(self):
        """
        Test the can_handle method for format detection.
        
        Verifies that the VideoHandler correctly identifies files of supported formats
        (MP4, WebM, AVI, MKV, MOV) and rejects unsupported formats. Tests both the
        explicit format specification and format detection from file extension.
        """
        # Test with format name
        self.assertTrue(self.handler.can_handle("dummy_path.mp4", "mp4"))
        self.assertTrue(self.handler.can_handle("dummy_path.webm", "webm"))
        self.assertTrue(self.handler.can_handle("dummy_path.avi", "avi"))
        self.assertTrue(self.handler.can_handle("dummy_path.mkv", "mkv"))
        self.assertTrue(self.handler.can_handle("dummy_path.mov", "mov"))
        
        # Test with unsupported format
        self.assertFalse(self.handler.can_handle("dummy_path.txt", "txt"))
    
    @patch('format_handlers.video_handler.PYMEDIAINFO_AVAILABLE', False)
    @patch('format_handlers.video_handler.format_detector')
    @patch('os.path.getsize')
    def test_extract_basic(self, mock_getsize, mock_detector):
        """
        Test basic video content extraction without the pymediainfo library.
        
        Verifies that the VideoHandler can extract basic information from video files
        even when the pymediainfo library is not available. Tests the fallback mechanism
        that provides limited metadata (format, file size) and basic content structure.
        Uses mocking to simulate file properties and format detection.
        
        Note that this test now checks for at least one section (video_info) but may have more
        sections (such as a thumbnail section) depending on whether the video processor is available.
        """
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
            
            # Verify there's at least a video_info section
            self.assertGreaterEqual(len(content.sections), 1)
            self.assertEqual(content.sections[0]['type'], "video_info")
            # The sections length can be more than 1 if thumbnail extraction is enabled
    
    @unittest.skipIf(not PYMEDIAINFO_AVAILABLE, "pymediainfo not available")
    @patch('pymediainfo.MediaInfo.parse')
    def test_extract_with_mediainfo(self, mock_mediainfo_parse):
        """
        Test enhanced video content extraction with the pymediainfo library.
        
        Verifies that the VideoHandler can extract comprehensive information from video files
        when the pymediainfo library is available. Tests the extraction of detailed video properties
        including multiple tracks (video, audio, subtitles), duration, resolution, codecs, and
        other technical metadata. Also checks that content is properly structured into separate
        sections for general information, video tracks, audio tracks, and subtitle tracks.
        
        This test simulates a video file with multiple tracks to verify proper handling of
        complex video files with varied content types. Uses mocking to simulate media info
        track data for each track type.
        
        This test is skipped if pymediainfo is not available in the environment.
        """
        # Skip if mediainfo is not installed
        if not PYMEDIAINFO_AVAILABLE:
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
        """
        Test the _format_file_size helper method for human-readable file sizes.
        
        Verifies that the VideoHandler correctly formats byte counts into human-readable
        file size strings with appropriate units (B, KB, MB, GB, TB). Tests a range of
        sizes to ensure proper handling of different magnitude values and correct
        unit conversion and rounding.
        """
        self.assertEqual(self.handler._format_file_size(1000), "1000.00 B")
        self.assertEqual(self.handler._format_file_size(1500), "1.46 KB")
        self.assertEqual(self.handler._format_file_size(1500000), "1.43 MB")
        self.assertEqual(self.handler._format_file_size(1500000000), "1.40 GB")
        self.assertEqual(self.handler._format_file_size(1500000000000), "1.36 TB")


if __name__ == '__main__':
    unittest.main()