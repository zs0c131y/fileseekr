# FileSeekr Distribution Guide

This guide explains how to build and distribute FileSeekr as a standalone application.

## For Maintainers: Creating Releases

### Step 1: Build the Executable

**Windows:**
```bash
# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller fileseekr.spec

# Result: dist/FileSeekr.exe (single file, ~50-100MB)
```

**macOS:**
```bash
# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller fileseekr.spec

# Result: dist/FileSeekr.app (app bundle)

# Optional: Create DMG for distribution
./installers/build_macos.sh
# Result: FileSeekr-1.0.0.dmg
```

**Linux:**
```bash
# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller fileseekr.spec

# Result: dist/FileSeekr (single binary)

# Optional: Create tarball
tar -czf FileSeekr-1.0.0-linux-x64.tar.gz -C dist FileSeekr
```

### Step 2: Create Installers (Optional)

**Windows Installer (requires NSIS):**
```bash
# After building exe with PyInstaller
makensis installers/windows_installer.nsi

# Result: FileSeekr-Setup.exe
```

**macOS DMG:**
```bash
# Run the build script
./installers/build_macos.sh

# Result: FileSeekr-1.0.0.dmg
```

**Linux (users run install script):**
- No pre-built installer needed
- Users run `installers/install_linux.sh` from source

### Step 3: Create GitHub Release

1. Go to GitHub → Releases → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `FileSeekr v1.0.0 - Smart File Search`
4. Upload binaries:
   - `FileSeekr-Setup.exe` (Windows installer)
   - `FileSeekr.exe` (Windows portable)
   - `FileSeekr-1.0.0.dmg` (macOS)
   - `FileSeekr-1.0.0-linux-x64.tar.gz` (Linux)
   - `Source code (zip)`
   - `Source code (tar.gz)`

5. Release notes:
```markdown
## FileSeekr v1.0.0

Smart file search with global hotkey support - press Ctrl+Shift+Space from anywhere!

### Downloads

**Windows:**
- [FileSeekr-Setup.exe](link) - Installer (recommended)
- [FileSeekr.exe](link) - Portable executable

**macOS:**
- [FileSeekr-1.0.0.dmg](link) - DMG installer

**Linux:**
- [FileSeekr-1.0.0-linux-x64.tar.gz](link) - Binary tarball
- Or use the install script from source

### Installation

See [QUICK_START.md](QUICK_START.md) for installation instructions.

### What's New

- 🔥 Global hotkey (Ctrl+Shift+Space) to search from anywhere
- 🎯 System tray integration
- 🎨 Beautiful overlay search window
- 🚀 Auto-start on boot
- Cross-platform: Windows, macOS, Linux
```

## For End Users: Download Options

### Option 1: Pre-built Binaries (Easiest)

**Download from GitHub Releases:**
https://github.com/YOUR_USERNAME/fileseekr/releases/latest

**Windows Users:**
1. Download `FileSeekr-Setup.exe`
2. Run the installer
3. FileSeekr starts automatically
4. Press Ctrl+Shift+Space to search!

**macOS Users:**
1. Download `FileSeekr-1.0.0.dmg`
2. Open DMG and drag to Applications
3. Launch FileSeekr
4. Press Ctrl+Shift+Space to search!

**Linux Users:**
1. Download `FileSeekr-1.0.0-linux-x64.tar.gz`
2. Extract: `tar -xzf FileSeekr-1.0.0-linux-x64.tar.gz`
3. Run: `./FileSeekr`
4. Press Ctrl+Shift+Space to search!

### Option 2: Install from Source (Developers)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/fileseekr.git
cd fileseekr

# Install dependencies
pip install -r requirements.txt

# Optional: Install spaCy model for better NLP
python -m spacy download en_core_web_sm

# Run system tray mode
python main_tray.py

# Or run traditional GUI mode
python main.py
```

## File Sizes (Approximate)

- **Windows EXE**: ~60MB (includes Python runtime)
- **Windows Installer**: ~65MB
- **macOS .app**: ~70MB
- **macOS DMG**: ~50MB (compressed)
- **Linux Binary**: ~65MB
- **Source Code**: ~500KB

## Building Tips

### Reduce Executable Size

1. **Exclude unused modules** in `fileseekr.spec`:
```python
excludes=[
    'matplotlib', 'numpy', 'pandas', 'scipy',
    'IPython', 'jupyter', 'tkinter'
],
```

2. **Use UPX compression**:
```python
upx=True,
```

3. **Don't include transformer models** (optional dependency):
   - Skip torch and transformers in requirements
   - Reduces size by ~500MB

### Code Signing (Recommended)

**Windows:**
```bash
signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist/FileSeekr.exe
```

**macOS:**
```bash
codesign --force --deep --sign "Developer ID Application: Your Name" dist/FileSeekr.app
```

## Troubleshooting Builds

### "Module not found" errors
- Add missing module to `hiddenimports` in `.spec` file

### Large executable size
- Check `excludes` list
- Enable UPX compression
- Don't bundle transformer models

### Antivirus false positives
- Code sign your executables
- Submit to antivirus vendors for whitelisting

## Distribution Checklist

Before releasing:

- [ ] Test executable on clean system (no Python installed)
- [ ] Verify global hotkey works
- [ ] Check auto-start functionality
- [ ] Test file indexing and search
- [ ] Verify installer creates shortcuts
- [ ] Check uninstaller works correctly
- [ ] Update version numbers everywhere
- [ ] Create release notes
- [ ] Tag release in git
- [ ] Upload binaries to GitHub Releases

## Continuous Integration (Future)

Consider setting up GitHub Actions to automatically build releases:

```yaml
# .github/workflows/release.yml
name: Build Release
on:
  push:
    tags:
      - 'v*'
jobs:
  build-windows:
    runs-on: windows-latest
    # ... build Windows exe
  build-macos:
    runs-on: macos-latest
    # ... build macOS app
  build-linux:
    runs-on: ubuntu-latest
    # ... build Linux binary
```

This automates the build process when you create a new tag.
