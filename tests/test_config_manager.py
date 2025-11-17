"""Tests for ConfigManager."""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager."""

    def test_default_config_creation(self):
        """Test that default config is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            assert config_path.exists()
            assert config.get('index.index_path') == 'data/index'

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            value = config.get('index.max_file_size_mb')
            assert value == 100

    def test_set_nested_value(self):
        """Test setting nested configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            config.set('index.max_file_size_mb', 200)
            assert config.get('index.max_file_size_mb') == 200

    def test_add_watch_path(self):
        """Test adding watch paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            config.add_watch_path('/test/path')
            paths = config.get('indexing.watch_paths')
            assert '/test/path' in paths

    def test_remove_watch_path(self):
        """Test removing watch paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            config.add_watch_path('/test/path')
            config.remove_watch_path('/test/path')
            paths = config.get('indexing.watch_paths')
            assert '/test/path' not in paths

    def test_default_value(self):
        """Test getting default value for missing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            config = ConfigManager(str(config_path))

            value = config.get('nonexistent.key', 'default')
            assert value == 'default'
