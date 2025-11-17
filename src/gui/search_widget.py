"""Search widget for query input and filters."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QComboBox, QCheckBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class SearchWidget(QWidget):
    """Widget for search input and filters."""

    # Signals
    search_triggered = pyqtSignal(str, dict)  # query, filters
    clear_triggered = pyqtSignal()

    def __init__(self, config_manager):
        """Initialize search widget.

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config = config_manager
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Search input row
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        # Search label
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Enter search query (supports natural language)..."
        )
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input, stretch=1)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._on_search)
        self.search_button.setDefault(True)
        search_layout.addWidget(self.search_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._on_clear)
        search_layout.addWidget(self.clear_button)

        # Filters group
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # File type filter
        type_label = QLabel("Type:")
        filters_layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "All",
            "Document",
            "Image",
            "Video",
            "Audio",
            "Code",
            "Spreadsheet"
        ])
        filters_layout.addWidget(self.type_combo)

        # Extension filter
        ext_label = QLabel("Extension:")
        filters_layout.addWidget(ext_label)

        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText(".py, .pdf, etc.")
        self.ext_input.setMaximumWidth(150)
        filters_layout.addWidget(self.ext_input)

        # Size filter
        size_label = QLabel("Size:")
        filters_layout.addWidget(size_label)

        self.size_combo = QComboBox()
        self.size_combo.addItems([
            "Any",
            "Small (< 1MB)",
            "Medium (1-10MB)",
            "Large (10-100MB)",
            "Huge (> 100MB)"
        ])
        filters_layout.addWidget(self.size_combo)

        # Fuzzy search checkbox
        self.fuzzy_checkbox = QCheckBox("Fuzzy search")
        self.fuzzy_checkbox.setChecked(self.config.get('search.enable_fuzzy', True))
        filters_layout.addWidget(self.fuzzy_checkbox)

        filters_layout.addStretch()

        # Set focus to search input
        self.search_input.setFocus()

    def _on_search(self):
        """Handle search button click."""
        query = self.search_input.text().strip()
        if not query:
            return

        # Build filters
        filters = {}

        # File type
        file_type = self.type_combo.currentText().lower()
        if file_type != "all":
            filters['filetype'] = file_type

        # Extension
        extension = self.ext_input.text().strip()
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            filters['extension'] = extension

        # Size
        size_text = self.size_combo.currentText()
        if size_text != "Any":
            if "Small" in size_text:
                filters['size_max'] = 1024 * 1024
            elif "Medium" in size_text:
                filters['size_min'] = 1024 * 1024
                filters['size_max'] = 10 * 1024 * 1024
            elif "Large" in size_text:
                filters['size_min'] = 10 * 1024 * 1024
                filters['size_max'] = 100 * 1024 * 1024
            elif "Huge" in size_text:
                filters['size_min'] = 100 * 1024 * 1024

        # Emit search signal
        self.search_triggered.emit(query, filters)

    def _on_clear(self):
        """Handle clear button click."""
        self.search_input.clear()
        self.ext_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.size_combo.setCurrentIndex(0)
        self.clear_triggered.emit()
        self.search_input.setFocus()

    def get_query(self) -> str:
        """Get current search query.

        Returns:
            Current query text
        """
        return self.search_input.text().strip()

    def set_query(self, query: str):
        """Set search query.

        Args:
            query: Query text
        """
        self.search_input.setText(query)
