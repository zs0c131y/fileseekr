"""Settings dialog for configuring FileSeekr."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QGroupBox, QListWidget, QMessageBox,
    QFileDialog, QFormLayout
)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, config_manager, parent=None):
        """Initialize settings dialog.

        Args:
            config_manager: Configuration manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Create tabs
        tabs.addTab(self._create_indexing_tab(), "Indexing")
        tabs.addTab(self._create_search_tab(), "Search")
        tabs.addTab(self._create_ui_tab(), "Interface")

        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        button_layout.addStretch()

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_button)

    def _create_indexing_tab(self) -> QWidget:
        """Create indexing settings tab.

        Returns:
            Tab widget
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Watch paths group
        paths_group = QGroupBox("Watched Directories")
        paths_layout = QVBoxLayout()
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)

        # Paths list
        self.paths_list = QListWidget()
        paths_layout.addWidget(self.paths_list)

        # Path buttons
        path_buttons_layout = QHBoxLayout()
        paths_layout.addLayout(path_buttons_layout)

        add_path_button = QPushButton("Add...")
        add_path_button.clicked.connect(self._add_watch_path)
        path_buttons_layout.addWidget(add_path_button)

        remove_path_button = QPushButton("Remove")
        remove_path_button.clicked.connect(self._remove_watch_path)
        path_buttons_layout.addWidget(remove_path_button)

        path_buttons_layout.addStretch()

        # Options group
        options_group = QGroupBox("Indexing Options")
        options_layout = QFormLayout()
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Auto index on startup
        self.auto_index_checkbox = QCheckBox()
        options_layout.addRow("Auto-index on startup:", self.auto_index_checkbox)

        # Watch for changes
        self.watch_changes_checkbox = QCheckBox()
        options_layout.addRow("Watch for file changes:", self.watch_changes_checkbox)

        # Max file size
        self.max_size_spinbox = QSpinBox()
        self.max_size_spinbox.setRange(1, 1000)
        self.max_size_spinbox.setSuffix(" MB")
        options_layout.addRow("Max file size to index:", self.max_size_spinbox)

        # Index interval
        self.index_interval_spinbox = QSpinBox()
        self.index_interval_spinbox.setRange(5, 1440)
        self.index_interval_spinbox.setSuffix(" minutes")
        options_layout.addRow("Re-index interval:", self.index_interval_spinbox)

        layout.addStretch()

        return widget

    def _create_search_tab(self) -> QWidget:
        """Create search settings tab.

        Returns:
            Tab widget
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Search options group
        options_group = QGroupBox("Search Options")
        options_layout = QFormLayout()
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Max results
        self.max_results_spinbox = QSpinBox()
        self.max_results_spinbox.setRange(10, 10000)
        options_layout.addRow("Maximum results:", self.max_results_spinbox)

        # Enable fuzzy search
        self.fuzzy_checkbox = QCheckBox()
        options_layout.addRow("Enable fuzzy search:", self.fuzzy_checkbox)

        # Fuzzy distance
        self.fuzzy_distance_spinbox = QSpinBox()
        self.fuzzy_distance_spinbox.setRange(1, 5)
        options_layout.addRow("Fuzzy search distance:", self.fuzzy_distance_spinbox)

        # Snippet size
        self.snippet_size_spinbox = QSpinBox()
        self.snippet_size_spinbox.setRange(50, 500)
        self.snippet_size_spinbox.setSuffix(" characters")
        options_layout.addRow("Snippet size:", self.snippet_size_spinbox)

        layout.addStretch()

        return widget

    def _create_ui_tab(self) -> QWidget:
        """Create UI settings tab.

        Returns:
            Tab widget
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # UI options group
        options_group = QGroupBox("Interface Options")
        options_layout = QFormLayout()
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Show hidden files
        self.show_hidden_checkbox = QCheckBox()
        options_layout.addRow("Show hidden files:", self.show_hidden_checkbox)

        layout.addStretch()

        return widget

    def _load_settings(self):
        """Load current settings into UI."""
        # Indexing tab
        watch_paths = self.config.get('indexing.watch_paths', [])
        for path in watch_paths:
            self.paths_list.addItem(path)

        self.auto_index_checkbox.setChecked(
            self.config.get('indexing.auto_index_on_startup', True)
        )
        self.watch_changes_checkbox.setChecked(
            self.config.get('index.watch_for_changes', True)
        )
        self.max_size_spinbox.setValue(
            self.config.get('index.max_file_size_mb', 100)
        )
        self.index_interval_spinbox.setValue(
            self.config.get('indexing.index_interval_minutes', 60)
        )

        # Search tab
        self.max_results_spinbox.setValue(
            self.config.get('search.max_results', 100)
        )
        self.fuzzy_checkbox.setChecked(
            self.config.get('search.enable_fuzzy', True)
        )
        self.fuzzy_distance_spinbox.setValue(
            self.config.get('search.fuzzy_distance', 2)
        )
        self.snippet_size_spinbox.setValue(
            self.config.get('search.snippet_size', 200)
        )

        # UI tab
        self.show_hidden_checkbox.setChecked(
            self.config.get('ui.show_hidden_files', False)
        )

    def _apply_settings(self):
        """Apply settings to configuration."""
        # Indexing settings
        watch_paths = []
        for i in range(self.paths_list.count()):
            watch_paths.append(self.paths_list.item(i).text())

        self.config.set('indexing.watch_paths', watch_paths)
        self.config.set('indexing.auto_index_on_startup',
                       self.auto_index_checkbox.isChecked())
        self.config.set('index.watch_for_changes',
                       self.watch_changes_checkbox.isChecked())
        self.config.set('index.max_file_size_mb',
                       self.max_size_spinbox.value())
        self.config.set('indexing.index_interval_minutes',
                       self.index_interval_spinbox.value())

        # Search settings
        self.config.set('search.max_results',
                       self.max_results_spinbox.value())
        self.config.set('search.enable_fuzzy',
                       self.fuzzy_checkbox.isChecked())
        self.config.set('search.fuzzy_distance',
                       self.fuzzy_distance_spinbox.value())
        self.config.set('search.snippet_size',
                       self.snippet_size_spinbox.value())

        # UI settings
        self.config.set('ui.show_hidden_files',
                       self.show_hidden_checkbox.isChecked())

    def _add_watch_path(self):
        """Add a directory to watch list."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Watch",
            ""
        )

        if directory:
            # Check if already in list
            for i in range(self.paths_list.count()):
                if self.paths_list.item(i).text() == directory:
                    QMessageBox.information(
                        self,
                        "Already Added",
                        "This directory is already in the watch list."
                    )
                    return

            self.paths_list.addItem(directory)

    def _remove_watch_path(self):
        """Remove selected directory from watch list."""
        current_item = self.paths_list.currentItem()
        if current_item:
            self.paths_list.takeItem(self.paths_list.row(current_item))

    def accept(self):
        """Handle dialog acceptance."""
        self._apply_settings()
        super().accept()
