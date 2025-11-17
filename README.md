# FileSeekr

A smart search application for cross-device file searching. Making searching files a breeze, not another task to be completed.

## Features

- **Smart Search**: Natural language query parsing using NLP
- **Fast Indexing**: Powered by Whoosh for lightning-fast searches
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern GUI**: Intuitive PyQt5 interface
- **Real-Time Updates**: Automatic file system watching and index updates
- **Advanced Filters**: Search by file type, size, date, extension, and more
- **Content Search**: Search inside text files
- **Fuzzy Matching**: Find files even with typos

## Installation

### Requirements

- Python 3.8-3.11
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install spaCy Language Model (Optional but Recommended)

For enhanced NLP capabilities:

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Running the Application

```bash
python main.py
```

### First-Time Setup

1. **Index Directories**: Go to `File > Index Directories...` and add folders to index
2. **Configure Settings**: Go to `File > Settings...` to customize behavior
3. **Start Searching**: Use natural language queries or keywords

### Search Examples

- **Basic search**: `project files`
- **File type**: `image files`, `python code`, `documents`
- **Extension**: `ext:pdf`, `.py files`
- **Size**: `large files`, `size > 5MB`
- **Time**: `modified today`, `from yesterday`
- **Directory**: `in:/home/user/documents`
- **Combined**: `large image files modified today ext:jpg`
- **Wildcards**: `report*.pdf`, `test?.py`
- **Exact phrase**: `"exact match"`

### Keyboard Shortcuts

- `Ctrl+I` - Index directories
- `Ctrl+R` - Reindex all
- `Ctrl+L` - Clear results
- `Ctrl+,` - Settings
- `Ctrl+Q` - Quit

## Configuration

Configuration is stored in `config.yaml`. You can edit it directly or use the Settings dialog.

### Key Configuration Options

```yaml
index:
  index_path: data/index
  excluded_dirs: ['.git', 'node_modules', '__pycache__']
  excluded_extensions: ['.pyc', '.so', '.dll']
  max_file_size_mb: 100

search:
  max_results: 100
  enable_fuzzy: true
  fuzzy_distance: 2

indexing:
  watch_paths: []  # Directories to index
  auto_index_on_startup: true
```

## Architecture

### Core Components

- **ConfigManager**: Configuration management
- **FileIndexer**: File indexing with Whoosh
- **SearchEngine**: Query execution and ranking
- **NLPQueryParser**: Natural language query parsing with spaCy
- **FileWatcher**: Real-time file system monitoring
- **GUI**: PyQt5-based user interface

### Project Structure

```
fileseekr/
├── src/
│   ├── core/
│   │   ├── indexer.py          # File indexing
│   │   ├── search_engine.py    # Search functionality
│   │   ├── nlp_parser.py       # NLP query parsing
│   │   └── file_watcher.py     # File system watching
│   ├── gui/
│   │   ├── main_window.py      # Main application window
│   │   ├── search_widget.py    # Search interface
│   │   ├── results_widget.py   # Results display
│   │   ├── settings_dialog.py  # Settings dialog
│   │   └── indexing_dialog.py  # Indexing progress
│   ├── utils/
│   │   └── config_manager.py   # Configuration management
│   └── app_controller.py       # Main controller
├── tests/                      # Unit tests
├── data/                       # Index data (created at runtime)
├── main.py                     # Application entry point
├── config.yaml                 # Configuration file
└── requirements.txt            # Python dependencies
```

## Building Executables

### Using PyInstaller

Build standalone executables for distribution:

```bash
# Install PyInstaller
pip install pyinstaller

# Build (creates dist/fileseekr/)
pyinstaller build.spec

# Or use the build script
python build.py
```

The executable will be created in the `dist/` directory.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Type checking (optional)
mypy src/

# Linting (optional)
pylint src/
```

## Technical Details

### Indexing

- Uses Whoosh for full-text indexing
- Indexes filename, content, metadata
- Supports incremental updates
- MD5 checksums for change detection

### Search Features

- Multi-field search (filename, content, directory)
- BM25F ranking algorithm
- Fuzzy matching with configurable distance
- Boolean queries (AND, OR, NOT)
- Wildcards and phrases
- Result highlighting

### Performance

- Efficient index storage
- Lazy loading of results
- Background file watching
- Optimized for large file collections

## Troubleshooting

### spaCy Model Not Found

If you see warnings about missing spaCy model:

```bash
python -m spacy download en_core_web_sm
```

### Index Corruption

If search results are incorrect, try reindexing:

1. Go to `File > Reindex All`
2. Or delete `data/index/` and reindex

### Permission Errors

Run with appropriate permissions to access protected directories.

## License

This project is open source and available under the MIT License.

## Credits

Built with:
- **PyQt5** - GUI framework
- **Whoosh** - Search engine
- **spaCy** - NLP processing
- **Python** - Programming language

## Support

For issues, questions, or contributions, please visit the project repository.

---

**FileSeekr** - Find files fast, search smart.
