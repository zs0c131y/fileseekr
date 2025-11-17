"""Tests for NLPQueryParser."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.nlp_parser import NLPQueryParser


class TestNLPQueryParser:
    """Test suite for NLPQueryParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return NLPQueryParser()

    def test_basic_query(self, parser):
        """Test basic query parsing."""
        result = parser.parse("test query")
        assert result['query'] == "test query"
        assert isinstance(result['filters'], dict)

    def test_filetype_extraction(self, parser):
        """Test file type extraction."""
        result = parser.parse("find image files")
        assert result['filters'].get('filetype') == 'image'

    def test_extension_extraction(self, parser):
        """Test extension extraction."""
        result = parser.parse("search for .py files")
        assert result['filters'].get('extension') == 'py'

    def test_extension_with_prefix(self, parser):
        """Test extension with ext: prefix."""
        result = parser.parse("ext:pdf documents")
        assert result['filters'].get('extension') == 'pdf'

    def test_size_keyword(self, parser):
        """Test size keyword extraction."""
        result = parser.parse("large files")
        assert 'size_min' in result['filters']

    def test_directory_extraction(self, parser):
        """Test directory extraction."""
        result = parser.parse("in:/home/user documents")
        assert result['filters'].get('directory') == '/home/user'

    def test_multiple_filters(self, parser):
        """Test parsing multiple filters."""
        result = parser.parse("large image files ext:jpg")
        assert result['filters'].get('filetype') == 'image'
        assert result['filters'].get('extension') == 'jpg'
        assert 'size_min' in result['filters']

    def test_empty_query(self, parser):
        """Test empty query."""
        result = parser.parse("")
        assert result['query'] == ''
        assert result['filters'] == {}
