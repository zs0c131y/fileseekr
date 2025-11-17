"""File indexing engine using Whoosh."""
import os
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.query import Query
import hashlib


class FileIndexer:
    """Indexes files for fast searching."""

    # Define search schema
    SCHEMA = Schema(
        path=ID(stored=True, unique=True),
        filename=TEXT(stored=True),
        extension=TEXT(stored=True),
        content=TEXT(stored=True),
        size=NUMERIC(stored=True),
        modified=DATETIME(stored=True),
        created=DATETIME(stored=True),
        filetype=TEXT(stored=True),
        directory=TEXT(stored=True),
        checksum=ID(stored=True),
    )

    def __init__(self, index_path: str, config_manager):
        """Initialize file indexer.

        Args:
            index_path: Path to store index
            config_manager: Configuration manager instance
        """
        self.index_path = Path(index_path)
        self.config = config_manager
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Create or open index
        if index.exists_in(str(self.index_path)):
            self.ix = index.open_dir(str(self.index_path))
        else:
            self.ix = index.create_in(str(self.index_path), self.SCHEMA)

        # Initialize mimetypes
        mimetypes.init()

    def index_directory(
        self,
        directory: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, int]:
        """Index all files in a directory recursively.

        Args:
            directory: Directory to index
            progress_callback: Optional callback(current, total, filename)

        Returns:
            Statistics dictionary
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        excluded_dirs = set(self.config.get('index.excluded_dirs', []))
        excluded_exts = set(self.config.get('index.excluded_extensions', []))
        max_size_mb = self.config.get('index.max_file_size_mb', 100)
        max_size_bytes = max_size_mb * 1024 * 1024

        # Collect files to index
        files_to_index = []
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for filename in files:
                file_path = Path(root) / filename

                # Skip excluded extensions
                if file_path.suffix in excluded_exts:
                    continue

                # Skip hidden files if configured
                if not self.config.get('ui.show_hidden_files', False):
                    if filename.startswith('.'):
                        continue

                # Skip files that are too large
                try:
                    if file_path.stat().st_size > max_size_bytes:
                        continue
                except (OSError, PermissionError):
                    continue

                files_to_index.append(file_path)

        # Index files
        stats = {'indexed': 0, 'skipped': 0, 'errors': 0}
        total_files = len(files_to_index)

        writer = self.ix.writer()
        try:
            for i, file_path in enumerate(files_to_index):
                if progress_callback:
                    progress_callback(i + 1, total_files, str(file_path))

                try:
                    self._index_file(file_path, writer)
                    stats['indexed'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error indexing {file_path}: {e}")

            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e

        return stats

    def _index_file(self, file_path: Path, writer) -> None:
        """Index a single file.

        Args:
            file_path: Path to file
            writer: Whoosh writer instance
        """
        try:
            stat = file_path.stat()

            # Get file metadata
            filename = file_path.name
            extension = file_path.suffix.lower()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            created = datetime.fromtimestamp(stat.st_ctime)
            directory = str(file_path.parent)

            # Determine file type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                filetype = mime_type.split('/')[0]  # 'text', 'image', 'audio', etc.
            else:
                filetype = 'unknown'

            # Read content for text files
            content = ""
            if filetype == 'text' and size < 1024 * 1024:  # Only index text < 1MB
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    pass

            # Calculate checksum
            checksum = self._calculate_checksum(file_path)

            # Add to index
            writer.update_document(
                path=str(file_path),
                filename=filename,
                extension=extension,
                content=content,
                size=size,
                modified=modified,
                created=created,
                filetype=filetype,
                directory=directory,
                checksum=checksum,
            )

        except (OSError, PermissionError) as e:
            raise Exception(f"Cannot access file: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            MD5 checksum
        """
        try:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception:
            return ""

    def remove_path(self, path: str) -> int:
        """Remove a path from the index.

        Args:
            path: Path to remove

        Returns:
            Number of documents removed
        """
        writer = self.ix.writer()
        count = writer.delete_by_term('path', path)
        writer.commit()
        return count

    def update_file(self, file_path: Path) -> None:
        """Update a single file in the index.

        Args:
            file_path: Path to file
        """
        writer = self.ix.writer()
        try:
            self._index_file(file_path, writer)
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e

    def clear_index(self) -> None:
        """Clear all documents from the index."""
        writer = self.ix.writer()
        writer.commit(mergetype=index.CLEAR)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics.

        Returns:
            Statistics dictionary
        """
        with self.ix.searcher() as searcher:
            doc_count = searcher.doc_count_all()

        return {
            'document_count': doc_count,
            'index_path': str(self.index_path),
            'last_modified': datetime.fromtimestamp(
                self.index_path.stat().st_mtime
            ) if self.index_path.exists() else None,
        }

    def optimize_index(self) -> None:
        """Optimize the index for better performance."""
        writer = self.ix.writer()
        writer.commit(optimize=True)
