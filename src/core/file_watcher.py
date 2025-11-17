"""File system watcher for real-time index updates."""
import os
import time
import threading
from pathlib import Path
from typing import Set, Callable, Optional, List
from queue import Queue, Empty
from datetime import datetime


class FileWatcher:
    """Watches file system for changes and updates index."""

    def __init__(self, indexer, config_manager, update_callback: Optional[Callable] = None):
        """Initialize file watcher.

        Args:
            indexer: FileIndexer instance
            config_manager: ConfigManager instance
            update_callback: Optional callback for updates
        """
        self.indexer = indexer
        self.config = config_manager
        self.update_callback = update_callback

        self.watch_paths: Set[Path] = set()
        self.running = False
        self.thread = None
        self.file_cache: dict = {}  # path -> (mtime, size)
        self.update_queue = Queue()

        # Polling interval (seconds)
        self.poll_interval = 5

    def add_watch_path(self, path: str) -> None:
        """Add a path to watch.

        Args:
            path: Path to watch
        """
        path_obj = Path(path)
        if path_obj.exists():
            self.watch_paths.add(path_obj)
            # Initialize cache for this path
            self._cache_directory(path_obj)

    def remove_watch_path(self, path: str) -> None:
        """Remove a path from watch list.

        Args:
            path: Path to remove
        """
        path_obj = Path(path)
        self.watch_paths.discard(path_obj)

    def start(self) -> None:
        """Start watching for changes."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()

        # Start update processor
        self.update_thread = threading.Thread(target=self._process_updates, daemon=True)
        self.update_thread.start()

    def stop(self) -> None:
        """Stop watching."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if hasattr(self, 'update_thread'):
            self.update_thread.join(timeout=2)

    def _watch_loop(self) -> None:
        """Main watch loop (runs in separate thread)."""
        excluded_dirs = set(self.config.get('index.excluded_dirs', []))
        excluded_exts = set(self.config.get('index.excluded_extensions', []))

        while self.running:
            try:
                for watch_path in list(self.watch_paths):
                    if not watch_path.exists():
                        continue

                    # Walk directory and check for changes
                    for root, dirs, files in os.walk(watch_path):
                        # Filter excluded directories
                        dirs[:] = [d for d in dirs if d not in excluded_dirs]

                        for filename in files:
                            if not self.running:
                                return

                            file_path = Path(root) / filename

                            # Skip excluded extensions
                            if file_path.suffix in excluded_exts:
                                continue

                            # Check for changes
                            self._check_file(file_path)

                # Sleep before next poll
                time.sleep(self.poll_interval)

            except Exception as e:
                print(f"Error in watch loop: {e}")
                time.sleep(self.poll_interval)

    def _check_file(self, file_path: Path) -> None:
        """Check if file has changed.

        Args:
            file_path: Path to check
        """
        try:
            stat = file_path.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            path_str = str(file_path)
            cached = self.file_cache.get(path_str)

            if cached is None:
                # New file
                self.update_queue.put(('add', file_path))
                self.file_cache[path_str] = (mtime, size)

            elif cached != (mtime, size):
                # Modified file
                self.update_queue.put(('modify', file_path))
                self.file_cache[path_str] = (mtime, size)

        except (OSError, PermissionError):
            # File might have been deleted
            path_str = str(file_path)
            if path_str in self.file_cache:
                self.update_queue.put(('delete', file_path))
                del self.file_cache[path_str]

    def _cache_directory(self, directory: Path) -> None:
        """Build initial cache for a directory.

        Args:
            directory: Directory to cache
        """
        excluded_dirs = set(self.config.get('index.excluded_dirs', []))
        excluded_exts = set(self.config.get('index.excluded_extensions', []))

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for filename in files:
                file_path = Path(root) / filename

                if file_path.suffix in excluded_exts:
                    continue

                try:
                    stat = file_path.stat()
                    self.file_cache[str(file_path)] = (stat.st_mtime, stat.st_size)
                except (OSError, PermissionError):
                    pass

    def _process_updates(self) -> None:
        """Process queued updates (runs in separate thread)."""
        while self.running:
            try:
                # Get update with timeout
                action, file_path = self.update_queue.get(timeout=1)

                if action == 'add' or action == 'modify':
                    # Update index
                    try:
                        self.indexer.update_file(file_path)
                        if self.update_callback:
                            self.update_callback(action, str(file_path))
                    except Exception as e:
                        print(f"Error indexing {file_path}: {e}")

                elif action == 'delete':
                    # Remove from index
                    try:
                        self.indexer.remove_path(str(file_path))
                        if self.update_callback:
                            self.update_callback(action, str(file_path))
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")

                self.update_queue.task_done()

            except Empty:
                continue
            except Exception as e:
                print(f"Error processing update: {e}")

    def get_stats(self) -> dict:
        """Get watcher statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'running': self.running,
            'watch_paths': [str(p) for p in self.watch_paths],
            'cached_files': len(self.file_cache),
            'pending_updates': self.update_queue.qsize(),
        }
