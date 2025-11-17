"""Results widget for displaying search results."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton,
    QMenu, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QCursor
import os
from datetime import datetime
from pathlib import Path


class ResultsWidget(QWidget):
    """Widget for displaying search results."""

    # Signals
    file_opened = pyqtSignal(str)

    def __init__(self, config_manager):
        """Initialize results widget.

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config = config_manager
        self.results = []
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Results header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        self.results_label = QLabel("Results: 0")
        header_layout.addWidget(self.results_label)

        header_layout.addStretch()

        # Export button
        export_button = QPushButton("Export Results...")
        export_button.clicked.connect(self._export_results)
        header_layout.addWidget(export_button)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Directory", "Size", "Type", "Modified", "Score"
        ])

        # Table settings
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Filename
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Directory
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Modified
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Score

        # Set minimum width for filename column
        self.table.setColumnWidth(0, 250)

        # Double-click to open file
        self.table.doubleClicked.connect(self._on_double_click)

        # Right-click context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

    def display_results(self, results: list):
        """Display search results.

        Args:
            results: List of SearchResult objects
        """
        self.results = results
        self.results_label.setText(f"Results: {len(results)}")

        # Clear table
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)

        # Populate table
        for i, result in enumerate(results):
            self.table.insertRow(i)

            # Filename
            filename_item = QTableWidgetItem(result.filename)
            filename_item.setData(Qt.UserRole, result.path)
            self.table.setItem(i, 0, filename_item)

            # Directory
            directory_item = QTableWidgetItem(result.directory)
            self.table.setItem(i, 1, directory_item)

            # Size
            size_item = QTableWidgetItem(self._format_size(result.size))
            size_item.setData(Qt.UserRole, result.size)
            self.table.setItem(i, 2, size_item)

            # Type
            type_item = QTableWidgetItem(result.filetype)
            self.table.setItem(i, 3, type_item)

            # Modified
            if result.modified:
                modified_str = result.modified.strftime("%Y-%m-%d %H:%M")
                modified_item = QTableWidgetItem(modified_str)
                modified_item.setData(Qt.UserRole, result.modified)
            else:
                modified_item = QTableWidgetItem("N/A")
            self.table.setItem(i, 4, modified_item)

            # Score
            score_item = QTableWidgetItem(f"{result.score:.2f}")
            score_item.setData(Qt.UserRole, result.score)
            self.table.setItem(i, 5, score_item)

        # Re-enable sorting
        self.table.setSortingEnabled(True)

        # Sort by score (descending) by default
        self.table.sortItems(5, Qt.DescendingOrder)

    def clear(self):
        """Clear all results."""
        self.results = []
        self.table.setRowCount(0)
        self.results_label.setText("Results: 0")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _on_double_click(self, index):
        """Handle double-click on result.

        Args:
            index: Clicked index
        """
        row = index.row()
        path_item = self.table.item(row, 0)
        if path_item:
            file_path = path_item.data(Qt.UserRole)
            self._open_file(file_path)

    def _open_file(self, file_path: str):
        """Open file with default application.

        Args:
            file_path: Path to file
        """
        if not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The file does not exist:\n{file_path}"
            )
            return

        # Open with default application
        url = QUrl.fromLocalFile(file_path)
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(
                self,
                "Cannot Open File",
                f"Could not open file:\n{file_path}"
            )
            return

        self.file_opened.emit(file_path)

    def _show_context_menu(self, position):
        """Show context menu for result.

        Args:
            position: Menu position
        """
        index = self.table.indexAt(position)
        if not index.isValid():
            return

        row = index.row()
        path_item = self.table.item(row, 0)
        if not path_item:
            return

        file_path = path_item.data(Qt.UserRole)

        # Create context menu
        menu = QMenu()

        # Open action
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self._open_file(file_path))

        # Open location action
        open_location_action = menu.addAction("Open File Location")
        open_location_action.triggered.connect(
            lambda: self._open_file_location(file_path)
        )

        menu.addSeparator()

        # Copy path action
        copy_path_action = menu.addAction("Copy Path")
        copy_path_action.triggered.connect(
            lambda: self._copy_path(file_path)
        )

        # Copy filename action
        copy_filename_action = menu.addAction("Copy Filename")
        filename = os.path.basename(file_path)
        copy_filename_action.triggered.connect(
            lambda: self._copy_path(filename)
        )

        menu.addSeparator()

        # Properties action
        properties_action = menu.addAction("Properties...")
        properties_action.triggered.connect(
            lambda: self._show_properties(file_path)
        )

        # Show menu
        menu.exec_(QCursor.pos())

    def _open_file_location(self, file_path: str):
        """Open file location in file explorer.

        Args:
            file_path: Path to file
        """
        directory = os.path.dirname(file_path)
        url = QUrl.fromLocalFile(directory)
        QDesktopServices.openUrl(url)

    def _copy_path(self, text: str):
        """Copy text to clipboard.

        Args:
            text: Text to copy
        """
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _show_properties(self, file_path: str):
        """Show file properties dialog.

        Args:
            file_path: Path to file
        """
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", "The file does not exist.")
            return

        stat = os.stat(file_path)
        path_obj = Path(file_path)

        info = f"""
        <b>File:</b> {path_obj.name}<br>
        <b>Path:</b> {file_path}<br>
        <b>Size:</b> {self._format_size(stat.st_size)}<br>
        <b>Created:</b> {datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}<br>
        <b>Modified:</b> {datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")}<br>
        <b>Accessed:</b> {datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")}
        """

        QMessageBox.information(self, "File Properties", info)

    def _export_results(self):
        """Export results to file."""
        if not self.results:
            QMessageBox.information(
                self,
                "No Results",
                "There are no results to export."
            )
            return

        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "search_results.csv",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                self._export_to_csv(file_path)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export results:\n{str(e)}"
                )

    def _export_to_csv(self, file_path: str):
        """Export results to CSV file.

        Args:
            file_path: Output file path
        """
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "Filename", "Path", "Directory", "Size (bytes)",
                "Type", "Extension", "Modified", "Score"
            ])

            # Write results
            for result in self.results:
                modified_str = result.modified.strftime("%Y-%m-%d %H:%M:%S") if result.modified else ""
                writer.writerow([
                    result.filename,
                    result.path,
                    result.directory,
                    result.size,
                    result.filetype,
                    result.extension,
                    modified_str,
                    f"{result.score:.4f}"
                ])
