"""NLP-powered query parser for natural language search."""
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import spacy


class NLPQueryParser:
    """Parses natural language queries into structured search parameters."""

    def __init__(self):
        """Initialize NLP parser."""
        self.nlp = None
        self._load_model()

        # File type mappings
        self.filetype_keywords = {
            'document': ['doc', 'docx', 'pdf', 'txt', 'document', 'documents'],
            'image': ['image', 'images', 'picture', 'pictures', 'photo', 'photos', 'jpg', 'jpeg', 'png', 'gif'],
            'video': ['video', 'videos', 'movie', 'movies', 'mp4', 'avi', 'mkv'],
            'audio': ['audio', 'music', 'song', 'songs', 'mp3', 'wav', 'sound'],
            'code': ['code', 'script', 'program', 'py', 'js', 'java', 'cpp'],
            'spreadsheet': ['spreadsheet', 'excel', 'csv', 'xls', 'xlsx'],
        }

        # Size keywords
        self.size_keywords = {
            'small': (0, 1024 * 1024),  # < 1MB
            'medium': (1024 * 1024, 10 * 1024 * 1024),  # 1-10MB
            'large': (10 * 1024 * 1024, 100 * 1024 * 1024),  # 10-100MB
            'huge': (100 * 1024 * 1024, None),  # > 100MB
        }

        # Time keywords
        self.time_keywords = {
            'today': 0,
            'yesterday': 1,
            'week': 7,
            'month': 30,
            'year': 365,
        }

    def _load_model(self):
        """Load spaCy model (with fallback)."""
        try:
            # Try to load English model
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            # Model not installed, create blank model
            print("Warning: spaCy model 'en_core_web_sm' not found. Using basic parsing.")
            print("Install with: python -m spacy download en_core_web_sm")
            self.nlp = spacy.blank('en')

    def parse(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured parameters.

        Args:
            query: Natural language query

        Returns:
            Dictionary with query, filters, and metadata
        """
        query = query.strip()
        if not query:
            return {'query': '', 'filters': {}, 'metadata': {}}

        # Extract filters and clean query
        filters = {}
        metadata = {}
        cleaned_query = query

        # Extract file type
        filetype, cleaned_query = self._extract_filetype(cleaned_query)
        if filetype:
            filters['filetype'] = filetype
            metadata['filetype_detected'] = True

        # Extract extension (e.g., ".py", "ext:pdf")
        extension, cleaned_query = self._extract_extension(cleaned_query)
        if extension:
            filters['extension'] = extension
            metadata['extension_detected'] = True

        # Extract size constraints
        size_filter, cleaned_query = self._extract_size(cleaned_query)
        if size_filter:
            filters.update(size_filter)
            metadata['size_detected'] = True

        # Extract time constraints
        time_filter, cleaned_query = self._extract_time(cleaned_query)
        if time_filter:
            filters.update(time_filter)
            metadata['time_detected'] = True

        # Extract directory/path hints
        directory, cleaned_query = self._extract_directory(cleaned_query)
        if directory:
            filters['directory'] = directory
            metadata['directory_detected'] = True

        # Use spaCy for entity recognition if available
        if self.nlp and hasattr(self.nlp, 'pipe_names'):
            doc = self.nlp(cleaned_query)
            # Extract named entities that might be filenames or topics
            entities = [ent.text for ent in doc.ents]
            if entities:
                metadata['entities'] = entities

        return {
            'query': cleaned_query.strip(),
            'filters': filters,
            'metadata': metadata,
        }

    def _extract_filetype(self, query: str) -> Tuple[Optional[str], str]:
        """Extract file type from query.

        Args:
            query: Search query

        Returns:
            Tuple of (filetype, cleaned_query)
        """
        query_lower = query.lower()

        for filetype, keywords in self.filetype_keywords.items():
            for keyword in keywords:
                # Look for standalone keyword or "type:keyword"
                pattern = r'\b(type:|filetype:)?' + re.escape(keyword) + r'\b'
                match = re.search(pattern, query_lower)
                if match:
                    # Remove from query
                    cleaned = re.sub(pattern, '', query, flags=re.IGNORECASE)
                    return filetype, cleaned

        return None, query

    def _extract_extension(self, query: str) -> Tuple[Optional[str], str]:
        """Extract file extension from query.

        Args:
            query: Search query

        Returns:
            Tuple of (extension, cleaned_query)
        """
        # Pattern: ext:py, .py, extension:pdf, etc.
        patterns = [
            r'\b(ext|extension):\s*\.?(\w+)\b',
            r'\b\.(\w{2,5})\b(?=\s|$)',  # Standalone .ext
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                ext = match.group(2) if match.lastindex >= 2 else match.group(1)
                cleaned = re.sub(pattern, '', query, flags=re.IGNORECASE)
                return ext, cleaned

        return None, query

    def _extract_size(self, query: str) -> Tuple[Optional[Dict[str, int]], str]:
        """Extract size constraints from query.

        Args:
            query: Search query

        Returns:
            Tuple of (size_filter_dict, cleaned_query)
        """
        query_lower = query.lower()

        # Check for size keywords
        for size_name, (min_size, max_size) in self.size_keywords.items():
            pattern = r'\b' + size_name + r'\s+(file|files)?\b'
            if re.search(pattern, query_lower):
                size_filter = {}
                if min_size is not None:
                    size_filter['size_min'] = min_size
                if max_size is not None:
                    size_filter['size_max'] = max_size

                cleaned = re.sub(pattern, '', query, flags=re.IGNORECASE)
                return size_filter, cleaned

        # Check for explicit size (e.g., "size > 5MB", "larger than 1GB")
        size_pattern = r'\b(size|larger than|smaller than|>|<)\s*(\d+)\s*(mb|gb|kb|bytes?)?\b'
        match = re.search(size_pattern, query_lower)
        if match:
            operator = match.group(1)
            value = int(match.group(2))
            unit = match.group(3) or 'mb'

            # Convert to bytes
            multipliers = {'kb': 1024, 'mb': 1024**2, 'gb': 1024**3, 'byte': 1, 'bytes': 1}
            size_bytes = value * multipliers.get(unit, 1024**2)

            size_filter = {}
            if operator in ['>', 'larger than', 'size >']:
                size_filter['size_min'] = size_bytes
            elif operator in ['<', 'smaller than', 'size <']:
                size_filter['size_max'] = size_bytes

            cleaned = re.sub(size_pattern, '', query, flags=re.IGNORECASE)
            return size_filter, cleaned

        return None, query

    def _extract_time(self, query: str) -> Tuple[Optional[Dict[str, datetime]], str]:
        """Extract time constraints from query.

        Args:
            query: Search query

        Returns:
            Tuple of (time_filter_dict, cleaned_query)
        """
        query_lower = query.lower()
        now = datetime.now()

        # Check for time keywords
        for time_name, days_ago in self.time_keywords.items():
            patterns = [
                r'\b(from|modified|created|within)\s+' + time_name + r'\b',
                r'\b' + time_name + r"'?s?\b",
            ]

            for pattern in patterns:
                if re.search(pattern, query_lower):
                    since_date = now - timedelta(days=days_ago)
                    time_filter = {'modified_after': since_date}

                    cleaned = re.sub(pattern, '', query, flags=re.IGNORECASE)
                    return time_filter, cleaned

        return None, query

    def _extract_directory(self, query: str) -> Tuple[Optional[str], str]:
        """Extract directory/path hints from query.

        Args:
            query: Search query

        Returns:
            Tuple of (directory, cleaned_query)
        """
        # Pattern: in:/path/to/dir, directory:/path, path:/path
        patterns = [
            r'\b(in|directory|path|folder):\s*([^\s]+)\b',
            r'\bin\s+([/\\][\w/\\]+)\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                directory = match.group(2) if match.lastindex >= 2 else match.group(1)
                cleaned = re.sub(pattern, '', query, flags=re.IGNORECASE)
                return directory, cleaned

        return None, query

    def suggest_corrections(self, query: str) -> List[str]:
        """Suggest query corrections or improvements.

        Args:
            query: Search query

        Returns:
            List of suggestions
        """
        suggestions = []

        # Suggest adding file type if none specified
        parsed = self.parse(query)
        if not parsed['filters'].get('filetype') and not parsed['filters'].get('extension'):
            suggestions.append("Try adding a file type (e.g., 'image', 'document', '.py')")

        # Suggest using wildcards
        if '*' not in query and '?' not in query:
            suggestions.append("Use wildcards: * for multiple characters, ? for single character")

        return suggestions
