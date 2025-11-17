"""Main application window for FileSeekr."""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox,
    QLabel, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
import sys
from pathlib import Path


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    search_requested = pyqtSignal(str, dict)
    index_requested = pyqtSignal(list)

    def __init__(self, app_controller):
        """Initialize main window.

        Args:
            app_controller: Application controller instance
        """
        super().__init__()
        self.app_controller = app_controller
        self.config = app_controller.config

        self.setWindowTitle("FileSeekr - Smart File Search")
        self.resize(
            self.config.get('ui.window_width', 1000),
            self.config.get('ui.window_height', 700)
        )

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._connect_signals()

    def _init_ui(self):
        """Initialize user interface."""
        # Import here to avoid circular imports
        from .search_widget import SearchWidget
        from .results_widget import ResultsWidget

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Search widget
        self.search_widget = SearchWidget(self.config)
        layout.addWidget(self.search_widget)

        # Results widget
        self.results_widget = ResultsWidget(self.config)
        layout.addWidget(self.results_widget, stretch=1)

        # Set margins
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Index menu item
        index_action = QAction("&Index Directories...", self)
        index_action.setShortcut(QKeySequence("Ctrl+I"))
        index_action.triggered.connect(self._show_index_dialog)
        file_menu.addAction(index_action)

        # Reindex menu item
        reindex_action = QAction("&Reindex All", self)
        reindex_action.setShortcut(QKeySequence("Ctrl+R"))
        reindex_action.triggered.connect(self._reindex_all)
        file_menu.addAction(reindex_action)

        file_menu.addSeparator()

        # Settings menu item
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit menu item
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Clear results
        clear_action = QAction("&Clear Results", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.results_widget.clear)
        view_menu.addAction(clear_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About
        about_action = QAction("&About FileSeekr", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        # Search tips
        tips_action = QAction("Search &Tips", self)
        tips_action.triggered.connect(self._show_search_tips)
        help_menu.addAction(tips_action)

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Index stats label
        self.index_stats_label = QLabel("Index: 0 files")
        self.status_bar.addPermanentWidget(self.index_stats_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Update index stats periodically
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_index_stats)
        self.stats_timer.start(5000)  # Update every 5 seconds

        # Initial update
        self._update_index_stats()

    def _connect_signals(self):
        """Connect signals and slots."""
        # Search widget signals
        self.search_widget.search_triggered.connect(self._on_search)
        self.search_widget.clear_triggered.connect(self.results_widget.clear)

        # Results widget signals
        self.results_widget.file_opened.connect(self._on_file_opened)

    def _on_search(self, query: str, filters: dict):
        """Handle search request.

        Args:
            query: Search query
            filters: Search filters
        """
        self.status_bar.showMessage(f"Searching for: {query}")

        # Perform search
        results = self.app_controller.search(query, filters)

        # Display results
        self.results_widget.display_results(results)

        # Update status
        self.status_bar.showMessage(
            f"Found {len(results)} result(s) for: {query}", 3000
        )

    def _on_file_opened(self, file_path: str):
        """Handle file opened event.

        Args:
            file_path: Path to opened file
        """
        self.status_bar.showMessage(f"Opened: {file_path}", 3000)

    def _show_index_dialog(self):
        """Show indexing dialog."""
        from .indexing_dialog import IndexingDialog

        dialog = IndexingDialog(self.app_controller, self)
        dialog.exec_()

    def _reindex_all(self):
        """Reindex all watched directories."""
        reply = QMessageBox.question(
            self,
            "Reindex All",
            "This will reindex all watched directories. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            watch_paths = self.config.get('indexing.watch_paths', [])
            if watch_paths:
                from .indexing_dialog import IndexingDialog
                dialog = IndexingDialog(self.app_controller, self, reindex=True)
                dialog.exec_()
            else:
                QMessageBox.information(
                    self,
                    "No Paths",
                    "No directories are configured for indexing. "
                    "Please add directories first."
                )

    def _show_settings(self):
        """Show settings dialog."""
        from .settings_dialog import SettingsDialog

        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            # Settings were saved, apply them
            self._apply_settings()

    def _apply_settings(self):
        """Apply settings changes."""
        # Update UI based on new settings
        self.resize(
            self.config.get('ui.window_width', 1000),
            self.config.get('ui.window_height', 700)
        )

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About FileSeekr",
            "<h2>FileSeekr</h2>"
            "<p>A smart search application for cross-device file searching.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Built with Python, PyQt5, Whoosh, and spaCy</p>"
        )

    def _show_search_tips(self):
        """Show search tips dialog."""
        tips = """
        <h3>Search Tips</h3>
        <ul>
            <li><b>Basic search:</b> Just type keywords</li>
            <li><b>File type:</b> Add "image", "document", "video", etc.</li>
            <li><b>Extension:</b> Use ".py", "ext:pdf", etc.</li>
            <li><b>Size:</b> "large files", "size > 5MB"</li>
            <li><b>Time:</b> "modified today", "from yesterday"</li>
            <li><b>Directory:</b> "in:/path/to/dir"</li>
            <li><b>Wildcards:</b> Use * for multiple chars, ? for single char</li>
            <li><b>Exact phrase:</b> Use "quotes around phrase"</li>
        </ul>
        """
        QMessageBox.information(self, "Search Tips", tips)

    def _update_index_stats(self):
        """Update index statistics in status bar."""
        try:
            stats = self.app_controller.get_index_stats()
            count = stats.get('document_count', 0)
            self.index_stats_label.setText(f"Index: {count:,} files")
        except Exception as e:
            self.index_stats_label.setText("Index: Error")

    def show_progress(self, visible: bool = True):
        """Show or hide progress bar.

        Args:
            visible: Whether to show progress bar
        """
        if visible:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

    def update_progress(self, current: int, total: int):
        """Update progress bar.

        Args:
            current: Current progress
            total: Total items
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window size
        self.config.set('ui.window_width', self.width())
        self.config.set('ui.window_height', self.height())

        # Stop file watcher
        if hasattr(self.app_controller, 'file_watcher'):
            self.app_controller.file_watcher.stop()

        event.accept()
