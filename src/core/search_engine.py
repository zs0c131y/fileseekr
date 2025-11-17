"""Search engine for querying indexed files."""
from typing import List, Dict, Any, Optional
from whoosh.qparser import MultifieldParser, QueryParser, FuzzyTermPlugin
from whoosh.query import Query, Term, And, Or, Not
from whoosh import scoring
from pathlib import Path
import re


class SearchResult:
    """Represents a search result."""

    def __init__(self, document: Dict[str, Any], score: float, highlights: Dict[str, str] = None):
        """Initialize search result.

        Args:
            document: Document data from index
            score: Relevance score
            highlights: Highlighted snippets
        """
        self.path = document.get('path', '')
        self.filename = document.get('filename', '')
        self.extension = document.get('extension', '')
        self.size = document.get('size', 0)
        self.modified = document.get('modified')
        self.created = document.get('created')
        self.filetype = document.get('filetype', 'unknown')
        self.directory = document.get('directory', '')
        self.score = score
        self.highlights = highlights or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'path': self.path,
            'filename': self.filename,
            'extension': self.extension,
            'size': self.size,
            'modified': self.modified,
            'created': self.created,
            'filetype': self.filetype,
            'directory': self.directory,
            'score': self.score,
            'highlights': self.highlights,
        }

    def __repr__(self) -> str:
        return f"SearchResult(path={self.path}, score={self.score:.2f})"


class SearchEngine:
    """Advanced search engine with NLP capabilities."""

    def __init__(self, indexer, config_manager):
        """Initialize search engine.

        Args:
            indexer: FileIndexer instance
            config_manager: ConfigManager instance
        """
        self.indexer = indexer
        self.config = config_manager
        self.ix = indexer.ix

        # Create parser for multi-field search
        self.parser = MultifieldParser(
            ['filename', 'content', 'directory'],
            schema=self.ix.schema,
            fieldboosts={'filename': 2.0, 'content': 1.0, 'directory': 0.5}
        )

        # Add fuzzy search if enabled
        if self.config.get('search.enable_fuzzy', True):
            self.parser.add_plugin(FuzzyTermPlugin())

    def search(
        self,
        query_string: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for files.

        Args:
            query_string: Search query
            max_results: Maximum number of results
            filters: Optional filters (extension, filetype, etc.)

        Returns:
            List of search results
        """
        if not query_string.strip():
            return []

        if max_results is None:
            max_results = self.config.get('search.max_results', 100)

        # Parse query
        query = self._build_query(query_string, filters)

        # Execute search
        results = []
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            search_results = searcher.search(
                query,
                limit=max_results,
                terms=True
            )

            # Allow highlighting
            search_results.fragmenter.maxchars = self.config.get('search.snippet_size', 200)
            search_results.fragmenter.surround = 50

            for hit in search_results:
                # Get highlights
                highlights = {}
                if 'content' in hit:
                    content_highlight = hit.highlights('content')
                    if content_highlight:
                        highlights['content'] = content_highlight

                if 'filename' in hit:
                    filename_highlight = hit.highlights('filename')
                    if filename_highlight:
                        highlights['filename'] = filename_highlight

                # Create result
                result = SearchResult(
                    document=dict(hit),
                    score=hit.score,
                    highlights=highlights
                )
                results.append(result)

        return results

    def _build_query(self, query_string: str, filters: Optional[Dict[str, Any]] = None) -> Query:
        """Build Whoosh query from string and filters.

        Args:
            query_string: Search query string
            filters: Optional filters

        Returns:
            Whoosh Query object
        """
        # Process query string for special syntax
        processed_query = self._preprocess_query(query_string)

        # Parse main query
        main_query = self.parser.parse(processed_query)

        # Add filters
        if filters:
            filter_queries = []

            if 'extension' in filters and filters['extension']:
                ext = filters['extension'].lower()
                if not ext.startswith('.'):
                    ext = '.' + ext
                filter_queries.append(Term('extension', ext))

            if 'filetype' in filters and filters['filetype']:
                filter_queries.append(Term('filetype', filters['filetype'].lower()))

            if 'directory' in filters and filters['directory']:
                dir_query = QueryParser('directory', self.ix.schema).parse(filters['directory'])
                filter_queries.append(dir_query)

            if 'size_min' in filters and filters['size_min'] is not None:
                from whoosh.query import NumericRange
                filter_queries.append(
                    NumericRange('size', filters['size_min'], None)
                )

            if 'size_max' in filters and filters['size_max'] is not None:
                from whoosh.query import NumericRange
                filter_queries.append(
                    NumericRange('size', None, filters['size_max'])
                )

            # Combine with main query
            if filter_queries:
                main_query = And([main_query] + filter_queries)

        return main_query

    def _preprocess_query(self, query_string: str) -> str:
        """Preprocess query string for better search.

        Args:
            query_string: Raw query string

        Returns:
            Processed query string
        """
        # Handle fuzzy search syntax (word~)
        if self.config.get('search.enable_fuzzy', True):
            fuzzy_distance = self.config.get('search.fuzzy_distance', 2)
            # Add fuzzy to non-quoted words if not already present
            parts = []
            in_quotes = False
            for word in query_string.split():
                if '"' in word:
                    in_quotes = not in_quotes
                    parts.append(word)
                elif not in_quotes and '~' not in word and not word.endswith('*'):
                    parts.append(f"{word}~{fuzzy_distance}")
                else:
                    parts.append(word)
            query_string = ' '.join(parts)

        return query_string

    def search_by_filename(self, filename_pattern: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Search specifically by filename pattern.

        Args:
            filename_pattern: Filename pattern (supports wildcards)
            max_results: Maximum results

        Returns:
            List of search results
        """
        if max_results is None:
            max_results = self.config.get('search.max_results', 100)

        parser = QueryParser('filename', self.ix.schema)
        query = parser.parse(filename_pattern)

        results = []
        with self.ix.searcher() as searcher:
            search_results = searcher.search(query, limit=max_results)

            for hit in search_results:
                result = SearchResult(
                    document=dict(hit),
                    score=hit.score
                )
                results.append(result)

        return results

    def search_by_content(self, content_query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Search specifically in file contents.

        Args:
            content_query: Content search query
            max_results: Maximum results

        Returns:
            List of search results
        """
        if max_results is None:
            max_results = self.config.get('search.max_results', 100)

        parser = QueryParser('content', self.ix.schema)
        query = parser.parse(content_query)

        results = []
        with self.ix.searcher() as searcher:
            search_results = searcher.search(query, limit=max_results, terms=True)
            search_results.fragmenter.maxchars = self.config.get('search.snippet_size', 200)

            for hit in search_results:
                highlights = {}
                content_highlight = hit.highlights('content')
                if content_highlight:
                    highlights['content'] = content_highlight

                result = SearchResult(
                    document=dict(hit),
                    score=hit.score,
                    highlights=highlights
                )
                results.append(result)

        return results

    def get_file_info(self, file_path: str) -> Optional[SearchResult]:
        """Get information about a specific file.

        Args:
            file_path: Path to file

        Returns:
            SearchResult or None
        """
        with self.ix.searcher() as searcher:
            results = searcher.documents(path=file_path)
            for doc in results:
                return SearchResult(document=dict(doc), score=1.0)

        return None
