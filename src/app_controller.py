"""Main application controller."""
from pathlib import Path
from typing import List, Dict, Any, Optional

from .utils.config_manager import ConfigManager
from .core.indexer import FileIndexer
from .core.search_engine import SearchEngine
from .core.nlp_parser import NLPQueryParser
from .core.file_watcher import FileWatcher


class AppController:
    """Main application controller coordinating all components."""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize application controller.

        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        self.config = ConfigManager(config_path)

        # Initialize core components
        index_path = self.config.get('index.index_path', 'data/index')
        self.indexer = FileIndexer(index_path, self.config)
        self.search_engine = SearchEngine(self.indexer, self.config)
        self.nlp_parser = NLPQueryParser()

        # Initialize file watcher
        self.file_watcher = None
        if self.config.get('index.watch_for_changes', True):
            self._init_file_watcher()

    def _init_file_watcher(self):
        """Initialize file watcher."""
        self.file_watcher = FileWatcher(
            self.indexer,
            self.config,
            update_callback=self._on_file_update
        )

        # Add watch paths
        watch_paths = self.config.get('indexing.watch_paths', [])
        for path in watch_paths:
            if Path(path).exists():
                self.file_watcher.add_watch_path(path)

        # Start watching
        if watch_paths:
            self.file_watcher.start()

    def _on_file_update(self, action: str, file_path: str):
        """Handle file update from watcher.

        Args:
            action: Update action (add, modify, delete)
            file_path: File path
        """
        print(f"File {action}: {file_path}")

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        use_nlp: bool = True
    ) -> List:
        """Perform search.

        Args:
            query: Search query
            filters: Optional filters
            use_nlp: Whether to use NLP parsing

        Returns:
            List of search results
        """
        if not query.strip():
            return []

        # Parse query with NLP if enabled
        if use_nlp:
            parsed = self.nlp_parser.parse(query)
            search_query = parsed['query']
            nlp_filters = parsed['filters']

            # Merge with provided filters (provided filters take precedence)
            if filters:
                nlp_filters.update(filters)
            filters = nlp_filters
        else:
            search_query = query

        # Perform search
        results = self.search_engine.search(search_query, filters=filters)

        return results

    def search_by_filename(self, filename_pattern: str) -> List:
        """Search by filename pattern.

        Args:
            filename_pattern: Filename pattern

        Returns:
            List of search results
        """
        return self.search_engine.search_by_filename(filename_pattern)

    def search_by_content(self, content_query: str) -> List:
        """Search in file contents.

        Args:
            content_query: Content search query

        Returns:
            List of search results
        """
        return self.search_engine.search_by_content(content_query)

    def index_directory(
        self,
        directory: str,
        progress_callback=None
    ) -> Dict[str, int]:
        """Index a directory.

        Args:
            directory: Directory to index
            progress_callback: Optional progress callback

        Returns:
            Indexing statistics
        """
        stats = self.indexer.index_directory(directory, progress_callback)

        # Add to watch list if file watcher is active
        if self.file_watcher and Path(directory).exists():
            self.file_watcher.add_watch_path(directory)
            # Also add to config
            self.config.add_watch_path(directory)

        return stats

    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics.

        Returns:
            Statistics dictionary
        """
        return self.indexer.get_index_stats()

    def get_file_info(self, file_path: str) -> Optional[Any]:
        """Get information about a file.

        Args:
            file_path: Path to file

        Returns:
            File information or None
        """
        return self.search_engine.get_file_info(file_path)

    def clear_index(self):
        """Clear the entire index."""
        self.indexer.clear_index()

    def optimize_index(self):
        """Optimize the index."""
        self.indexer.optimize_index()

    def shutdown(self):
        """Shutdown application and cleanup."""
        if self.file_watcher:
            self.file_watcher.stop()
