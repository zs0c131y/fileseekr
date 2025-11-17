# FileSeekr

A smart search application for cross-device file searching. **Search any file from anywhere with Ctrl+Shift+Space** - just like Spotlight on macOS, but for all platforms!

## ✨ Key Features

- **🔥 Global Hotkey**: Press `Ctrl+Shift+Space` from anywhere to search
- **🎯 System Tray Integration**: Runs silently in background, always ready
- **🧠 Smart Search**: Natural language query parsing using NLP
- **⚡ Lightning Fast**: Powered by Whoosh indexing engine
- **🖥️ Cross-Platform**: Works on Windows, macOS, and Linux
- **🎨 Beautiful Overlay**: Spotlight-style search interface
- **📁 Real-Time Updates**: Automatic file system watching and index updates
- **🔍 Advanced Filters**: Search by file type, size, date, extension, and more
- **📝 Content Search**: Search inside text files
- **🎯 Fuzzy Matching**: Find files even with typos
- **🚀 Auto-Start**: Launches on system boot

## 📦 Installation

### Quick Install (Recommended)

**Windows**: Download and run `FileSeekr-Setup.exe`
**macOS**: Download `FileSeekr.dmg`, drag to Applications
**Linux**: Run `sudo ./installers/install_linux.sh`

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

### Manual Installation (Developers)

#### Requirements

- Python 3.8-3.11
- pip package manager

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Install spaCy Language Model (Optional but Recommended)

For enhanced NLP capabilities:

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Usage

### System Tray Mode (Recommended)

Run FileSeekr in the background with global hotkey support:

```bash
python main_tray.py
```

- Press **Ctrl+Shift+Space** to search from anywhere
- Check system tray for FileSeekr icon
- Right-click tray icon for options

### Traditional GUI Mode

Run with a persistent window:

```bash
python main.py
```

Or:

```bash
python main_tray.py --no-tray
```

### First-Time Setup

1. **Launch FileSeekr** (appears in system tray)
2. **Right-click** the tray icon → **Index Directories...**
3. **Add folders** to index (Documents, Downloads, Projects, etc.)
4. **Click** "Start Indexing"
5. **Press Ctrl+Shift+Space** to search!

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

**Global (System-wide):**
- `Ctrl+Shift+Space` - Open search overlay from anywhere

**In Search Overlay:**
- `Type` - Search instantly
- `↑` / `↓` - Navigate results
- `Enter` - Open selected file
- `Esc` - Close overlay

**In Main Window:**
- `Ctrl+I` - Index directories
- `Ctrl+R` - Reindex all
- `Ctrl+L` - Clear results
- `Ctrl+,` - Settings
- `Ctrl+Q` - Quit

### System Tray Menu

Right-click the FileSeekr tray icon:
- **Search** - Open search overlay
- **Open Main Window** - Open full application
- **Index Directories...** - Manage indexed folders
- **Settings...** - Configure FileSeekr
- **About** - Version and info
- **Quit** - Exit FileSeekr

### Auto-Start Management

```bash
# Enable auto-start on system boot
python main_tray.py --enable-autostart

# Disable auto-start
python main_tray.py --disable-autostart
```

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

## 🔨 Building Executables

### Quick Build

Use the unified build script:

```bash
# Build system tray version (recommended)
python build.py

# Build traditional GUI version
python build.py --mode=gui

# Build both versions
python build.py --mode=both

# Build and show installer instructions
python build.py --installer
```

The executable will be created in the `dist/` directory.

### Platform-Specific Installers

**Windows Installer (NSIS):**
```bash
# First build the executable
python build.py

# Then create installer (requires NSIS)
makensis installers/windows_installer.nsi
```

**macOS DMG:**
```bash
./installers/build_macos.sh
```

**Linux Installation:**
```bash
sudo ./installers/install_linux.sh
```

### Manual PyInstaller Build

```bash
# System tray mode
pyinstaller --clean --onefile --windowed main_tray.py

# GUI mode
pyinstaller --clean --onefile --windowed main.py
```

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
