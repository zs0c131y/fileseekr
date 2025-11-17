#!/usr/bin/env python3
"""FileSeekr - Smart File Search Application.

A cross-platform file search application with NLP-powered queries,
fast indexing, and an intuitive GUI.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.app_controller import AppController
from src.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("FileSeekr")
    app.setOrganizationName("FileSeekr")

    # Set application style
    app.setStyle('Fusion')

    # Create application controller
    controller = AppController()

    # Auto-index on startup if configured
    if controller.config.get('indexing.auto_index_on_startup', True):
        watch_paths = controller.config.get('indexing.watch_paths', [])
        if watch_paths:
            print("Auto-indexing configured directories...")
            # This will be done in background by file watcher

    # Create and show main window
    window = MainWindow(controller)
    window.show()

    # Run application
    exit_code = app.exec_()

    # Cleanup
    controller.shutdown()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
