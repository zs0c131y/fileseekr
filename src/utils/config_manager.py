"""Configuration management for FileSeekr."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class ConfigManager:
    """Manages application configuration."""

    DEFAULT_CONFIG = {
        'index': {
            'index_path': 'data/index',
            'excluded_dirs': [
                '.git', '.svn', 'node_modules', '__pycache__',
                '.venv', 'venv', 'build', 'dist'
            ],
            'excluded_extensions': ['.pyc', '.pyo', '.so', '.dylib', '.dll'],
            'max_file_size_mb': 100,
            'watch_for_changes': True,
        },
        'search': {
            'max_results': 100,
            'enable_fuzzy': True,
            'fuzzy_distance': 2,
            'enable_semantic': False,  # Requires transformers
            'snippet_size': 200,
        },
        'ui': {
            'theme': 'light',
            'window_width': 1000,
            'window_height': 700,
            'show_hidden_files': False,
        },
        'indexing': {
            'watch_paths': [],  # Will be populated by user
            'auto_index_on_startup': True,
            'index_interval_minutes': 60,
        }
    }

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists() and self.config_path.stat().st_size > 0:
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
                return config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self, config: Dict[str, Any] = None) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save (defaults to current config)
        """
        if config is None:
            config = self.config

        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path.

        Args:
            key_path: Dot-separated key path (e.g., 'index.index_path')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path.

        Args:
            key_path: Dot-separated key path (e.g., 'index.index_path')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.save_config()

    def add_watch_path(self, path: str) -> None:
        """Add a path to watch for indexing.

        Args:
            path: Path to add
        """
        watch_paths = self.get('indexing.watch_paths', [])
        if path not in watch_paths:
            watch_paths.append(path)
            self.set('indexing.watch_paths', watch_paths)

    def remove_watch_path(self, path: str) -> None:
        """Remove a path from watch list.

        Args:
            path: Path to remove
        """
        watch_paths = self.get('indexing.watch_paths', [])
        if path in watch_paths:
            watch_paths.remove(path)
            self.set('indexing.watch_paths', watch_paths)
