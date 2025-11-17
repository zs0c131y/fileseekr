# FileSeekr Quick Start Guide

## Installation

### Windows

1. **Download** the installer: `FileSeekr-Setup.exe`
2. **Run** the installer
3. **Follow** the installation wizard
4. FileSeekr will start automatically and appear in the system tray

That's it! Press **Ctrl+Shift+Space** to search.

### macOS

1. **Download** `FileSeekr-1.0.0.dmg`
2. **Open** the DMG file
3. **Drag** FileSeekr to Applications folder
4. **Launch** FileSeekr from Applications
5. Grant accessibility permissions if prompted

Press **Ctrl+Shift+Space** to search.

### Linux

```bash
# Download and extract FileSeekr
cd fileseekr

# Run the installer
sudo ./installers/install_linux.sh

# Or for user-only install
./installers/install_linux.sh
```

Press **Ctrl+Shift+Space** to search.

## First Use

### 1. Index Your Files

When you first run FileSeekr, you need to tell it which folders to index:

1. **Right-click** the FileSeekr tray icon
2. Select **"Index Directories..."**
3. Click **"Add Directory..."**
4. Choose folders to index (e.g., Documents, Downloads, Projects)
5. Click **"Start Indexing"**

Indexing runs in the background and may take a few minutes depending on the number of files.

### 2. Search Files

Press **Ctrl+Shift+Space** anywhere on your system to open the search overlay.

**Simple searches:**
- `report` - Find files containing "report"
- `project files` - Multiple keywords
- `*.pdf` - Wildcard search

**Advanced searches:**
- `large image files` - Filter by type and size
- `ext:py modified today` - Extension and date filters
- `document from yesterday` - Natural language
- `in:/home/user presentation` - Directory-specific search

### 3. Navigate Results

- **Type** to search instantly
- **↑ ↓** to navigate results
- **Enter** to open selected file
- **Esc** to close search overlay

## Tips & Tricks

### Keyboard Shortcuts

- `Ctrl+Shift+Space` - Open search anywhere
- `Esc` - Close search
- `↑ ↓` - Navigate results
- `Enter` - Open file

### Search Filters

FileSeekr understands natural language:

- **File types**: `image`, `document`, `video`, `audio`, `code`
- **Sizes**: `small`, `medium`, `large`, `huge`, or `size > 5MB`
- **Time**: `today`, `yesterday`, `this week`, `this month`
- **Extensions**: `ext:pdf`, `.py`, `.docx`
- **Directories**: `in:/path/to/folder`

### System Tray Menu

Right-click the tray icon for:
- Quick search
- Open main window (advanced features)
- Index directories
- Settings
- Index statistics

### Auto-Start

FileSeekr starts automatically when you log in. To disable:

**Windows:**
- Remove from Startup in Task Manager

**macOS:**
- System Preferences → Users & Groups → Login Items

**Linux:**
```bash
fileseekr --disable-autostart
```

## Troubleshooting

### Search returns no results

1. Make sure you've indexed directories
2. Check tray icon menu for index count
3. Try reindexing: Right-click tray icon → "Index Directories..."

### Hotkey doesn't work

- **Linux**: May need to grant accessibility permissions
- **macOS**: Grant accessibility permissions in System Preferences
- **Windows**: Try running as administrator once

### Can't find a file you know exists

- The file might be in an excluded directory (like `.git`)
- The file might be too large (default max: 100MB)
- Try reindexing the directory

### Application won't start

- Check if it's already running in the system tray
- Try: `fileseekr --no-tray` for traditional mode
- Check console for error messages

## Getting Help

- **Documentation**: See `README.md`
- **Settings**: Right-click tray icon → Settings
- **Issues**: Report at github.com/yourrepo/issues

## Uninstall

**Windows:**
- Control Panel → Programs → Uninstall FileSeekr

**macOS:**
- Drag FileSeekr from Applications to Trash

**Linux:**
```bash
sudo rm -rf /opt/fileseekr
sudo rm /usr/local/bin/fileseekr
sudo rm /usr/share/applications/fileseekr.desktop
```

---

**Enjoy fast file searching with FileSeekr!** 🚀
