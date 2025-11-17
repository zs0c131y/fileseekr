"""Tests for FileIndexer."""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.config_manager import ConfigManager
from src.core.indexer import FileIndexer


class TestFileIndexer:
    """Test suite for FileIndexer."""

    @pytest.fixture
    def setup(self):
        """Setup test environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create config
            config_path = tmpdir_path / 'config.yaml'
            config = ConfigManager(str(config_path))

            # Create index directory
            index_path = tmpdir_path / 'index'
            index_path.mkdir()

            # Create test files
            test_dir = tmpdir_path / 'test_files'
            test_dir.mkdir()

            (test_dir / 'test1.txt').write_text('Hello World')
            (test_dir / 'test2.py').write_text('print("test")')
            (test_dir / 'test3.md').write_text('# Markdown')

            # Create subdirectory
            sub_dir = test_dir / 'subdir'
            sub_dir.mkdir()
            (sub_dir / 'test4.txt').write_text('Nested file')

            # Create indexer
            indexer = FileIndexer(str(index_path), config)

            yield {
                'tmpdir': tmpdir_path,
                'config': config,
                'indexer': indexer,
                'test_dir': test_dir,
            }

    def test_index_directory(self, setup):
        """Test indexing a directory."""
        indexer = setup['indexer']
        test_dir = setup['test_dir']

        stats = indexer.index_directory(str(test_dir))

        assert stats['indexed'] >= 4  # At least 4 files
        assert stats['errors'] == 0

    def test_index_stats(self, setup):
        """Test getting index statistics."""
        indexer = setup['indexer']
        test_dir = setup['test_dir']

        indexer.index_directory(str(test_dir))
        stats = indexer.get_index_stats()

        assert stats['document_count'] >= 4
        assert 'index_path' in stats

    def test_clear_index(self, setup):
        """Test clearing the index."""
        indexer = setup['indexer']
        test_dir = setup['test_dir']

        indexer.index_directory(str(test_dir))
        indexer.clear_index()

        stats = indexer.get_index_stats()
        assert stats['document_count'] == 0
