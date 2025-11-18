# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for FileSeekr (System Tray Mode)."""

import os
import platform

block_cipher = None

a = Analysis(
    ['main_tray.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('README.md', '.'),
        ('QUICK_START.md', '.'),
    ],
    hiddenimports=[
        'whoosh.filedb.filestore',
        'whoosh.filedb.filepostings',
        'whoosh.filedb.filetables',
        'spacy',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pynput.keyboard',
        'pynput.mouse',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileSeekr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

# For macOS app bundle
if platform.system() == 'Darwin':
    app = BUNDLE(
        exe,
        name='FileSeekr.app',
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
        bundle_identifier='com.fileseekr.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSUIElement': '1',  # Run as menu bar app
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'LSApplicationCategoryType': 'public.app-category.utilities',
        },
    )
