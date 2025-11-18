#!/usr/bin/env python3
"""Build script for FileSeekr using PyInstaller."""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")


def build_executable(mode='tray'):
    """Build executable with PyInstaller.

    Args:
        mode: 'tray' for system tray mode, 'gui' for traditional GUI mode
    """
    system = platform.system()
    print(f"\nBuilding FileSeekr for {system} ({mode} mode)...")

    # Determine script to build
    if mode == 'tray':
        script = 'main_tray.py'
        name = 'fileseekr'
    else:
        script = 'main.py'
        name = 'fileseekr-gui'

    # Base PyInstaller arguments
    args = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        f'--name={name}',
    ]

    # Platform-specific arguments
    if system == 'Windows':
        args.extend([
            '--windowed',  # No console window
            '--onefile',
            '--icon=assets/icon.ico' if os.path.exists('assets/icon.ico') else '',
        ])
    elif system == 'Darwin':  # macOS
        args.extend([
            '--windowed',
            '--onefile',
            '--osx-bundle-identifier=com.fileseekr.app',
            '--icon=assets/icon.icns' if os.path.exists('assets/icon.icns') else '',
        ])
    else:  # Linux
        args.extend([
            '--onefile',
        ])

    # Add data files
    args.extend([
        '--add-data=config.yaml:.',
        '--add-data=README.md:.',
    ])

    # Hidden imports
    args.extend([
        '--hidden-import=whoosh',
        '--hidden-import=spacy',
        '--hidden-import=PyQt5',
        '--hidden-import=pynput',
        '--hidden-import=yaml',
    ])

    # Add script
    args.append(script)

    # Remove empty strings
    args = [arg for arg in args if arg]

    # Run PyInstaller
    print(f"\nRunning PyInstaller...")
    print(f"Command: {' '.join(args)}\n")

    try:
        subprocess.run(args, check=True)
        print(f"\n✓ Build successful!")
        print(f"Executable created in: dist/{name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False


def create_installer():
    """Create platform-specific installer."""
    system = platform.system()

    if system == 'Windows':
        print("\nTo create Windows installer:")
        print("1. Install NSIS: https://nsis.sourceforge.io/")
        print("2. Run: makensis installers/windows_installer.nsi")

    elif system == 'Darwin':
        print("\nTo create macOS installer:")
        print("Run: ./installers/build_macos.sh")

    elif system == 'Linux':
        print("\nTo install on Linux:")
        print("Run: sudo ./installers/install_linux.sh")


def main():
    """Main build function."""
    import argparse

    parser = argparse.ArgumentParser(description='Build FileSeekr executable')
    parser.add_argument(
        '--mode',
        choices=['tray', 'gui', 'both'],
        default='tray',
        help='Build mode: tray (system tray), gui (traditional), or both'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip cleaning previous builds'
    )
    parser.add_argument(
        '--installer',
        action='store_true',
        help='Show installer creation instructions'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("FileSeekr Build Script")
    print("=" * 60)

    # Clean build
    if not args.no_clean:
        clean_build()

    # Build
    if args.mode == 'both':
        success1 = build_executable('tray')
        success2 = build_executable('gui')
        success = success1 and success2
    else:
        success = build_executable(args.mode)

    if success and args.installer:
        create_installer()

    print("\n" + "=" * 60)
    if success:
        print("Build completed successfully!")
        print("\nNext steps:")
        print("1. Test the executable in dist/")
        print("2. Create installer (use --installer flag for instructions)")
    else:
        print("Build failed. Please check the errors above.")
        return 1

    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
