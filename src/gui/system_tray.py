"""System tray application for FileSeekr."""
from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QApplication
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import sys


class SystemTrayApp:
    """System tray application for FileSeekr."""

    def __init__(self, app_controller, overlay_window, hotkey_manager):
        """Initialize system tray app.

        Args:
            app_controller: Application controller
            overlay_window: Overlay window instance
            hotkey_manager: Hotkey manager instance
        """
        self.app_controller = app_controller
        self.overlay_window = overlay_window
        self.hotkey_manager = hotkey_manager
        self.main_window = None

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self._create_icon())
        self.tray_icon.setToolTip("FileSeekr - Quick File Search")

        # Create menu
        self._create_menu()

        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Show tray icon
        self.tray_icon.show()

        # Show welcome message
        QTimer.singleShot(1000, self._show_welcome)

    def _create_icon(self) -> QIcon:
        """Create tray icon.

        Returns:
            QIcon instance
        """
        # Create a simple icon (you can replace with actual icon file)
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw magnifying glass
        # Circle
        painter.setPen(QPen(QColor("#4CAF50"), 6))
        painter.drawEllipse(10, 10, 35, 35)

        # Handle
        painter.setPen(QPen(QColor("#4CAF50"), 8))
        painter.drawLine(38, 38, 55, 55)

        painter.end()

        return QIcon(pixmap)

    def _create_menu(self):
        """Create system tray menu."""
        menu = QMenu()

        # Search action
        search_action = QAction("Search (Ctrl+Shift+Space)", menu)
        search_action.triggered.connect(self._show_overlay)
        menu.addAction(search_action)

        menu.addSeparator()

        # Open main window
        main_window_action = QAction("Open Main Window", menu)
        main_window_action.triggered.connect(self._show_main_window)
        menu.addAction(main_window_action)

        # Index directories
        index_action = QAction("Index Directories...", menu)
        index_action.triggered.connect(self._index_directories)
        menu.addAction(index_action)

        # Settings
        settings_action = QAction("Settings...", menu)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Index stats
        self.stats_action = QAction("Index: Loading...", menu)
        self.stats_action.setEnabled(False)
        menu.addAction(self.stats_action)

        menu.addSeparator()

        # About
        about_action = QAction("About FileSeekr", menu)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # Quit
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._quit_application)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # Update stats periodically
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(10000)  # Update every 10 seconds

        # Initial update
        QTimer.singleShot(500, self._update_stats)

    def _show_overlay(self):
        """Show overlay search window."""
        self.overlay_window.show_overlay()

    def _show_main_window(self):
        """Show main application window."""
        if self.main_window is None:
            from .main_window import MainWindow
            self.main_window = MainWindow(self.app_controller)

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _index_directories(self):
        """Open indexing dialog."""
        # Ensure main window exists
        if self.main_window is None:
            self._show_main_window()

        # Show indexing dialog
        self.main_window._show_index_dialog()

    def _show_settings(self):
        """Open settings dialog."""
        # Ensure main window exists
        if self.main_window is None:
            self._show_main_window()

        # Show settings dialog
        self.main_window._show_settings()

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            None,
            "About FileSeekr",
            "<h2>FileSeekr</h2>"
            "<p>Smart file search with global hotkey access</p>"
            "<p>Version 1.0.0</p>"
            "<p><b>Hotkey:</b> Ctrl+Shift+Space</p>"
            "<p>Built with Python, PyQt5, Whoosh, and spaCy</p>"
        )

    def _update_stats(self):
        """Update index statistics in menu."""
        try:
            stats = self.app_controller.get_index_stats()
            count = stats.get('document_count', 0)
            self.stats_action.setText(f"Index: {count:,} files")
        except Exception:
            self.stats_action.setText("Index: Error")

    def _on_tray_activated(self, reason):
        """Handle tray icon activation.

        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_overlay()

    def _show_welcome(self):
        """Show welcome notification."""
        self.tray_icon.showMessage(
            "FileSeekr is running",
            "Press Ctrl+Shift+Space to search files",
            QSystemTrayIcon.Information,
            3000
        )

    def _quit_application(self):
        """Quit the application."""
        # Stop hotkey manager
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        # Stop file watcher
        if hasattr(self.app_controller, 'file_watcher'):
            self.app_controller.file_watcher.stop()

        # Quit application
        QApplication.quit()
