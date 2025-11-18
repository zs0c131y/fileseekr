"""Overlay search window for quick access (like Spotlight)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QFrame,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent, QRect
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import os
from datetime import datetime


class OverlaySearchWindow(QWidget):
    """Overlay search window that appears on top of all windows."""

    # Signals
    file_selected = pyqtSignal(str)

    def __init__(self, app_controller):
        """Initialize overlay window.

        Args:
            app_controller: Application controller instance
        """
        super().__init__()
        self.app_controller = app_controller
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        """Initialize user interface."""
        # Window flags for overlay behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Set window attributes
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)

        # Main container with rounded corners and shadow
        self.container = QFrame(self)
        self.container.setObjectName("container")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.container)

        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(10)

        # Title bar
        title_layout = QHBoxLayout()
        container_layout.addLayout(title_layout)

        title_label = QLabel("FileSeekr")
        title_label.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Hotkey hint
        hint_label = QLabel("Ctrl+Shift+Space")
        hint_label.setObjectName("hint")
        hint_font = QFont()
        hint_font.setPointSize(9)
        hint_label.setFont(hint_font)
        title_layout.addWidget(hint_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search files... (type to search)")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.returnPressed.connect(self._on_return_pressed)

        # Make search input larger
        search_font = QFont()
        search_font.setPointSize(14)
        self.search_input.setFont(search_font)
        self.search_input.setMinimumHeight(45)

        container_layout.addWidget(self.search_input)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setObjectName("resultsList")
        self.results_list.setMinimumHeight(400)
        self.results_list.itemDoubleClicked.connect(self._on_item_activated)
        self.results_list.itemActivated.connect(self._on_item_activated)

        # Enable keyboard navigation
        self.results_list.setFocusPolicy(Qt.NoFocus)

        container_layout.addWidget(self.results_list)

        # Status bar
        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        container_layout.addWidget(self.status_label)

        # Install event filter for Escape key
        self.installEventFilter(self)

        # Set fixed width and calculate height
        self.setFixedWidth(700)
        self.setMinimumHeight(600)

    def _apply_styles(self):
        """Apply modern stylesheet."""
        self.setStyleSheet("""
            QFrame#container {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #d0d0d0;
            }

            QLabel#title {
                color: #333;
            }

            QLabel#hint {
                color: #999;
                background-color: #f5f5f5;
                border-radius: 4px;
                padding: 4px 8px;
            }

            QLineEdit#searchInput {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                background-color: #f9f9f9;
                color: #333;
            }

            QLineEdit#searchInput:focus {
                border: 2px solid #4CAF50;
                background-color: white;
            }

            QListWidget#resultsList {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
                outline: none;
            }

            QListWidget#resultsList::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }

            QListWidget#resultsList::item:selected {
                background-color: #4CAF50;
                color: white;
            }

            QListWidget#resultsList::item:hover {
                background-color: #e8f5e9;
            }

            QLabel#status {
                color: #666;
            }
        """)

    def _on_search_changed(self, text: str):
        """Handle search text change.

        Args:
            text: Search text
        """
        # Debounce search (wait 300ms after typing stops)
        self.search_timer.stop()
        if text.strip():
            self.search_timer.start(300)
        else:
            self.results_list.clear()
            self.status_label.setText("")

    def _perform_search(self):
        """Perform the actual search."""
        query = self.search_input.text().strip()
        if not query:
            return

        try:
            # Perform search
            results = self.app_controller.search(query, max_results=20)

            # Clear previous results
            self.results_list.clear()

            # Display results
            if results:
                for result in results:
                    item = QListWidgetItem()

                    # Format display text
                    filename = result.filename
                    directory = result.directory

                    # Truncate long paths
                    if len(directory) > 60:
                        directory = "..." + directory[-57:]

                    # Main text: filename
                    # Secondary text: directory and size
                    size_str = self._format_size(result.size)
                    modified_str = ""
                    if result.modified:
                        modified_str = result.modified.strftime("%Y-%m-%d")

                    display_text = f"{filename}\n{directory}"
                    if size_str or modified_str:
                        display_text += f"\n{size_str}"
                        if modified_str:
                            display_text += f"  •  {modified_str}"

                    item.setText(display_text)
                    item.setData(Qt.UserRole, result.path)

                    self.results_list.addItem(item)

                # Select first item
                self.results_list.setCurrentRow(0)

                # Update status
                self.status_label.setText(f"Found {len(results)} result(s)")

            else:
                self.status_label.setText("No results found")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _on_return_pressed(self):
        """Handle Enter key in search input."""
        # Activate selected item or first item
        current_item = self.results_list.currentItem()
        if current_item:
            self._on_item_activated(current_item)
        elif self.results_list.count() > 0:
            self._on_item_activated(self.results_list.item(0))

    def _on_item_activated(self, item: QListWidgetItem):
        """Handle item activation (double-click or Enter).

        Args:
            item: Activated item
        """
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            # Open file
            from PyQt5.QtCore import QUrl
            from PyQt5.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

            # Emit signal
            self.file_selected.emit(file_path)

            # Hide window
            self.hide_overlay()

    def eventFilter(self, obj, event):
        """Filter events for keyboard shortcuts.

        Args:
            obj: Object
            event: Event

        Returns:
            True if event handled
        """
        if event.type() == QEvent.KeyPress:
            key = event.key()

            # Escape to close
            if key == Qt.Key_Escape:
                self.hide_overlay()
                return True

            # Up/Down for navigation
            elif key == Qt.Key_Down:
                if self.results_list.count() > 0:
                    current_row = self.results_list.currentRow()
                    if current_row < self.results_list.count() - 1:
                        self.results_list.setCurrentRow(current_row + 1)
                return True

            elif key == Qt.Key_Up:
                if self.results_list.count() > 0:
                    current_row = self.results_list.currentRow()
                    if current_row > 0:
                        self.results_list.setCurrentRow(current_row - 1)
                return True

        return super().eventFilter(obj, event)

    def show_overlay(self):
        """Show the overlay window centered on screen."""
        # Center on screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 3  # Upper third

        self.move(x, y)

        # Clear previous search
        self.search_input.clear()
        self.results_list.clear()
        self.status_label.setText("")

        # Show and focus
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()

    def hide_overlay(self):
        """Hide the overlay window."""
        self.hide()

    def toggle_overlay(self):
        """Toggle overlay visibility."""
        if self.isVisible():
            self.hide_overlay()
        else:
            self.show_overlay()
