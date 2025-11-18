# Building FileSeekr for Distribution

Quick guide to build standalone executables that users can download and run without Python.

## Prerequisites

1. **Install Python** (3.8-3.11)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Build Standalone Executable

### Option 1: Using the Spec File (Recommended)

```bash
# Build for your current platform
pyinstaller fileseekr.spec

# Result will be in: dist/FileSeekr or dist/FileSeekr.exe
```

### Option 2: Using the Build Script

```bash
# Build system tray version
python build.py

# Or build both tray and GUI versions
python build.py --mode=both
```

## Platform-Specific Builds

### Windows

```bash
# Build executable
pyinstaller fileseekr.spec

# Output: dist/FileSeekr.exe (~60MB)
# This is a single-file executable users can run directly

# Optional: Create installer (requires NSIS installed)
makensis installers/windows_installer.nsi
# Output: FileSeekr-Setup.exe (~65MB)
```

### macOS

```bash
# Build app bundle
pyinstaller fileseekr.spec

# Output: dist/FileSeekr.app

# Optional: Create DMG for distribution
./installers/build_macos.sh
# Output: FileSeekr-1.0.0.dmg (~50MB)
```

### Linux

```bash
# Build binary
pyinstaller fileseekr.spec

# Output: dist/FileSeekr

# Optional: Create tarball
tar -czf FileSeekr-1.0.0-linux-x64.tar.gz -C dist FileSeekr
```

## Testing the Build

```bash
# Run the executable
./dist/FileSeekr      # Linux/macOS
dist\FileSeekr.exe    # Windows

# Or on macOS
open dist/FileSeekr.app
```

**Test checklist:**
- [ ] Application launches
- [ ] System tray icon appears
- [ ] Global hotkey (Ctrl+Shift+Space) works
- [ ] Can index directories
- [ ] Search returns results
- [ ] Can open files from results
- [ ] Auto-start can be enabled/disabled

## Distributing to Users

### 1. Create GitHub Release

```bash
# Tag your release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Go to GitHub → Releases → "Create a new release"
# Upload your built executables
```

### 2. Upload Files

Upload these files to the GitHub release:

**Windows:**
- `FileSeekr-Setup.exe` (installer)
- `FileSeekr.exe` (portable)

**macOS:**
- `FileSeekr-1.0.0.dmg` (DMG image)

**Linux:**
- `FileSeekr-1.0.0-linux-x64.tar.gz` (binary tarball)
- `install_linux.sh` (installation script)

### 3. Update README Links

Replace `YOUR_USERNAME` in README.md with your actual GitHub username.

## Download Instructions for Users

Once you create a release, users can:

**Windows:**
1. Download `FileSeekr-Setup.exe`
2. Run the installer
3. FileSeekr starts automatically

**macOS:**
1. Download `FileSeekr-1.0.0.dmg`
2. Open DMG, drag to Applications
3. Launch from Applications folder

**Linux:**
1. Download `FileSeekr-1.0.0-linux-x64.tar.gz`
2. Extract: `tar -xzf FileSeekr-1.0.0-linux-x64.tar.gz`
3. Run: `./FileSeekr`

## Troubleshooting Build Issues

### "Module not found" errors

Add the missing module to `hiddenimports` in `fileseekr.spec`:

```python
hiddenimports=[
    'your.missing.module',
    # ... existing imports
],
```

### Executable too large

The executable includes Python runtime (~40MB) + dependencies. To reduce size:

1. Don't include optional dependencies (torch, transformers)
2. Enable UPX compression (already enabled in spec)
3. Exclude unused modules in `fileseekr.spec`

### Antivirus false positives

PyInstaller executables sometimes trigger antivirus. Solutions:

1. **Code sign** your executable (recommended for production)
2. Submit to antivirus vendors for whitelisting
3. Build on the target platform (not cross-compile)

## For CI/CD (Advanced)

You can automate builds using GitHub Actions. See `DISTRIBUTION.md` for details.

## Need Help?

- Check [DISTRIBUTION.md](DISTRIBUTION.md) for comprehensive distribution guide
- See [PyInstaller documentation](https://pyinstaller.org/) for advanced options
- Open an issue on GitHub
