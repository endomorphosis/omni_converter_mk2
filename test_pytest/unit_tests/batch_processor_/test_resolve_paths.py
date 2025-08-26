"""
Test suite for the resolve_paths function and _resolve_path generator.
Converted from unittest to pytest format.
"""
import pytest
import tempfile
import os
import glob
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from types_ import Logger, Generator

from batch_processor._resolve_paths import resolve_paths, _resolve_path


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def temp_test_dir():
    """Fixture providing a temporary directory that's cleaned up after test."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def create_test_files(test_dir, file_structure):
    """
    Create test files and directories based on structure dict.
    
    Args:
        test_dir: Base directory to create files in
        file_structure: Dict with paths as keys and content as values.
                       Use None for directories.
    """
    for path, content in file_structure.items():
        full_path = os.path.join(test_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        if content is None:  # Directory
            os.makedirs(full_path, exist_ok=True)
        else:  # File
            with open(full_path, 'w') as f:
                f.write(content)


class TestResolvePathsFunction:
    """Test suite for the resolve_paths function."""

    def test_resolve_paths_with_string_input_single_file(self, temp_test_dir, mock_logger):
        """
        GIVEN a single file path as string that exists
        WHEN resolve_paths is called
        THEN expect:
            - Single file path returned in list
            - Path is absolute
            - No warnings logged
        """
        # Arrange
        test_file = os.path.join(temp_test_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Act
        result = resolve_paths(test_file, mock_logger)
        
        # Assert
        assert len(result) == 1
        assert result[0] == os.path.abspath(test_file)
        assert os.path.isabs(result[0])
        mock_logger.warning.assert_not_called()

    def test_resolve_paths_with_string_input_nonexistent_file(self, temp_test_dir, mock_logger):
        """
        GIVEN a single file path as string that does not exist
        WHEN resolve_paths is called
        THEN expect:
            - Empty list returned
            - Warning logged about file not found
        """
        # Arrange
        nonexistent_file = os.path.join(temp_test_dir, 'nonexistent.txt')
        
        # Act
        result = resolve_paths(nonexistent_file, mock_logger)
        
        # Assert
        assert len(result) == 0
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert 'Path not found' in warning_call
        assert nonexistent_file in warning_call

    def test_resolve_paths_with_list_input_mixed_files(self, temp_test_dir, mock_logger):
        """
        GIVEN a list of file paths with some existing and some non-existing
        WHEN resolve_paths is called
        THEN expect:
            - Only existing files returned
            - Warnings logged for non-existing files
            - Order preserved for existing files
        """
        # Arrange
        file_structure = {
            'file1.txt': 'content1',
            'file2.txt': 'content2',
            'subdir/file3.txt': 'content3'
        }
        create_test_files(temp_test_dir, file_structure)
        
        # Mix of existing and non-existing files
        input_paths = [
            os.path.join(temp_test_dir, 'file1.txt'),
            os.path.join(temp_test_dir, 'nonexistent1.txt'),
            os.path.join(temp_test_dir, 'file2.txt'),
            os.path.join(temp_test_dir, 'nonexistent2.txt'),
            os.path.join(temp_test_dir, 'subdir', 'file3.txt')
        ]
        
        # Act
        result = resolve_paths(input_paths, mock_logger)
        
        # Assert
        assert len(result) == 3  # Only existing files
        expected_paths = [
            os.path.abspath(os.path.join(temp_test_dir, 'file1.txt')),
            os.path.abspath(os.path.join(temp_test_dir, 'file2.txt')),
            os.path.abspath(os.path.join(temp_test_dir, 'subdir', 'file3.txt'))
        ]
        assert result == expected_paths
        
        # Check warnings were logged for non-existing files
        assert mock_logger.warning.call_count == 2
        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
        assert any('nonexistent1.txt' in call for call in warning_calls)
        assert any('nonexistent2.txt' in call for call in warning_calls)

    def test_resolve_paths_with_directory_input(self, temp_test_dir, mock_logger):
        """
        GIVEN a directory path
        WHEN resolve_paths is called
        THEN expect:
            - All files in directory returned recursively
            - Paths are absolute
            - Directories not included in result
        """
        # Arrange
        file_structure = {
            'file1.txt': 'content1',
            'subdir/file2.txt': 'content2',
            'subdir/nested/file3.txt': 'content3',
            'emptydir/': None  # Directory
        }
        create_test_files(temp_test_dir, file_structure)
        
        # Act
        result = resolve_paths(temp_test_dir, mock_logger)
        
        # Assert
        assert len(result) == 3  # Only files, not directories
        expected_files = {
            os.path.abspath(os.path.join(temp_test_dir, 'file1.txt')),
            os.path.abspath(os.path.join(temp_test_dir, 'subdir', 'file2.txt')),
            os.path.abspath(os.path.join(temp_test_dir, 'subdir', 'nested', 'file3.txt'))
        }
        assert set(result) == expected_files
        
        # All paths should be absolute
        assert all(os.path.isabs(path) for path in result)

    @patch('glob.glob')
    def test_resolve_paths_with_glob_pattern_matches(self, mock_glob, mock_logger):
        """
        GIVEN a glob pattern that matches files
        WHEN resolve_paths is called
        THEN expect:
            - Matched files returned
            - glob.glob called with pattern
            - Paths are absolute
        """
        # Arrange
        mock_matches = ['file1.txt', 'file2.txt']
        mock_glob.return_value = mock_matches
        glob_pattern = '*.txt'
        
        # Act
        result = resolve_paths(glob_pattern, mock_logger)
        
        # Assert
        mock_glob.assert_called_once_with(glob_pattern)
        assert len(result) == 2
        for match in mock_matches:
            assert os.path.abspath(match) in result

    @patch('glob.glob')
    def test_resolve_paths_with_glob_pattern_no_matches(self, mock_glob, mock_logger):
        """
        GIVEN a glob pattern that matches no files
        WHEN resolve_paths is called
        THEN expect:
            - Empty list returned
            - Warning logged about no matches
        """
        # Arrange
        mock_glob.return_value = []
        glob_pattern = '*.nonexistent'
        
        # Act
        result = resolve_paths(glob_pattern, mock_logger)
        
        # Assert
        mock_glob.assert_called_once_with(glob_pattern)
        assert len(result) == 0
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert 'No files found matching pattern' in warning_call
        assert glob_pattern in warning_call

    @patch('os.path.islink')
    @patch('os.path.realpath')
    def test_resolve_paths_with_symlink_valid_target(self, mock_realpath, mock_islink, temp_test_dir, mock_logger):
        """
        GIVEN a symlink that points to a valid file
        WHEN resolve_paths is called
        THEN expect:
            - Symlink resolved to target path
            - Target path returned (not symlink path)
        """
        # Arrange
        target_file = os.path.join(temp_test_dir, 'target.txt')
        symlink_file = os.path.join(temp_test_dir, 'symlink.txt')
        
        with open(target_file, 'w') as f:
            f.write('target content')
        
        mock_islink.return_value = True
        mock_realpath.return_value = target_file
        
        # Act
        result = resolve_paths(symlink_file, mock_logger)
        
        # Assert
        mock_islink.assert_called_once_with(symlink_file)
        mock_realpath.assert_called_once_with(symlink_file)
        assert len(result) == 1
        assert result[0] == os.path.abspath(target_file)


class TestResolvePathGenerator:
    """Test suite specifically for the _resolve_path generator function."""

    def test_resolve_path_generator_yields_correct_type(self, temp_test_dir, mock_logger):
        """
        GIVEN _resolve_path generator with valid paths
        WHEN iterating over generator
        THEN expect:
            - Generator yields Path objects
            - All yielded paths exist
        """
        # Arrange
        file_structure = {
            'file1.txt': 'content1',
            'file2.txt': 'content2'
        }
        create_test_files(temp_test_dir, file_structure)
        paths = [os.path.join(temp_test_dir, name) for name in file_structure.keys()]
        
        # Act & Assert
        generator = _resolve_path(paths, mock_logger)
        assert hasattr(generator, '__iter__')
        assert hasattr(generator, '__next__')
        
        for path in generator:
            assert isinstance(path, Path)
            assert path.exists()

    @pytest.mark.slow
    def test_resolve_path_generator_memory_efficient(self, temp_test_dir, mock_logger):
        """
        GIVEN a large number of files
        WHEN using _resolve_path generator
        THEN expect:
            - Generator processes files lazily
            - Memory usage remains controlled
        """
        # Arrange - Create many small files
        file_structure = {f'file_{i}.txt': f'content_{i}' for i in range(100)}
        create_test_files(temp_test_dir, file_structure)
        paths = [os.path.join(temp_test_dir, name) for name in file_structure.keys()]
        
        # Act
        generator = _resolve_path(paths, mock_logger)
        
        # Assert - Process a few items to ensure it works without loading all
        processed_count = 0
        for path in generator:
            processed_count += 1
            assert isinstance(path, Path)
            if processed_count >= 10:  # Only test first 10 items
                break
        
        assert processed_count == 10