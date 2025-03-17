#!/usr/bin/env python3
"""
Tests for the documentation generator.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from claudes_toolbox.documentation_generator.utils.cli import load_ignore_paths, save_ignore_paths
from claudes_toolbox.documentation_generator.utils.file_processor import FileProcessor


class TestDocumentationGenerator(unittest.TestCase):
    """Tests for the documentation generator."""
    
    def test_load_ignore_paths(self):
        """Test loading ignore paths from a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("# Comment line\n")
            f.write("/path/to/ignore1\n")
            f.write("/path/to/ignore2\n")
            f.write("  # Another comment\n")
            f.write("  \n")
            f.write("/path/with/spaces  \n")
        
        try:
            paths = load_ignore_paths(f.name)
            self.assertEqual(paths, ["/path/to/ignore1", "/path/to/ignore2", "/path/with/spaces"])
        finally:
            os.unlink(f.name)
    
    def test_save_ignore_paths(self):
        """Test saving ignore paths to a file."""
        paths = ["/path/to/ignore1", "/path/to/ignore2"]
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            pass
        
        try:
            save_ignore_paths(f.name, paths)
            with open(f.name, 'r') as f:
                lines = f.readlines()
            
            self.assertEqual(len(lines), 3)  # header + 2 paths
            self.assertTrue(lines[0].startswith("#"))
            self.assertEqual(lines[1].strip(), "/path/to/ignore1")
            self.assertEqual(lines[2].strip(), "/path/to/ignore2")
        finally:
            os.unlink(f.name)
    
    def test_should_ignore(self):
        """Test the should_ignore method of FileProcessor."""
        ignore_paths = ["/path/to/ignore", "/another/path"]
        processor = FileProcessor(".", ignore_paths)
        
        with patch('os.path.abspath') as mock_abspath:
            # Test case: Path is exactly an ignore path
            mock_abspath.side_effect = lambda x: x  # Identity function for testing
            self.assertTrue(processor.should_ignore("/path/to/ignore"))
            
            # Test case: Path is a subdirectory of an ignore path
            self.assertTrue(processor.should_ignore("/path/to/ignore/subdir"))
            
            # Test case: Path is not in ignore paths
            self.assertFalse(processor.should_ignore("/path/not/ignored"))
            
            # Test case: Path is similar but not a subdirectory
            self.assertFalse(processor.should_ignore("/path/to/ignore_not"))


if __name__ == '__main__':
    unittest.main()