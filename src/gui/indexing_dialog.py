"""Indexing progress dialog."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QListWidget,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path


class IndexingThread(QThread):
    """Thread for indexing files."""

    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished_indexing = pyqtSignal(dict)  # statistics
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, indexer, directories, reindex=False):
        """Initialize indexing thread.

        Args:
            indexer: FileIndexer instance
            directories: List of directories to index
            reindex: Whether to clear index first
        """
        super().__init__()
        self.indexer = indexer
        self.directories = directories
        self.reindex = reindex
        self.cancelled = False

    def run(self):
        """Run indexing process."""
        try:
            # Clear index if reindexing
            if self.reindex:
                self.indexer.clear_index()

            total_stats = {'indexed': 0, 'skipped': 0, 'errors': 0}

            # Index each directory
            for directory in self.directories:
                if self.cancelled:
                    break

                try:
                    stats = self.indexer.index_directory(
                        directory,
                        progress_callback=self._progress_callback
                    )

                    # Accumulate stats
                    for key in total_stats:
                        total_stats[key] += stats.get(key, 0)

                except Exception as e:
                    self.error_occurred.emit(f"Error indexing {directory}: {str(e)}")

            # Optimize index
            if not self.cancelled:
                self.indexer.optimize_index()

            self.finished_indexing.emit(total_stats)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _progress_callback(self, current: int, total: int, filename: str):
        """Progress callback.

        Args:
            current: Current file number
            total: Total files
            filename: Current filename
        """
        if not self.cancelled:
            self.progress_updated.emit(current, total, filename)

    def cancel(self):
        """Cancel indexing."""
        self.cancelled = True


class IndexingDialog(QDialog):
    """Dialog for indexing progress."""

    def __init__(self, app_controller, parent=None, reindex=False):
        """Initialize indexing dialog.

        Args:
            app_controller: Application controller
            parent: Parent widget
            reindex: Whether to reindex (clear first)
        """
        super().__init__(parent)
        self.app_controller = app_controller
        self.reindex = reindex
        self.indexing_thread = None

        self.setWindowTitle("Index Directories" if not reindex else "Reindex All")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setModal(True)

        self._init_ui()

        if reindex:
            # Start indexing immediately
            self._start_indexing()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        if not self.reindex:
            # Directory selection (only if not reindexing)
            dir_label = QLabel("Select directories to index:")
            layout.addWidget(dir_label)

            # Directory list
            self.dir_list = QListWidget()
            layout.addWidget(self.dir_list)

            # Directory buttons
            dir_buttons_layout = QHBoxLayout()
            layout.addLayout(dir_buttons_layout)

            add_button = QPushButton("Add Directory...")
            add_button.clicked.connect(self._add_directory)
            dir_buttons_layout.addWidget(add_button)

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(self._remove_directory)
            dir_buttons_layout.addWidget(remove_button)

            dir_buttons_layout.addStretch()

        # Progress section
        progress_label = QLabel("Progress:")
        layout.addWidget(progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Log area
        log_label = QLabel("Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        button_layout.addStretch()

        # Start/Cancel button
        self.action_button = QPushButton("Start Indexing" if not self.reindex else "Cancel")
        self.action_button.clicked.connect(self._on_action_button)
        button_layout.addWidget(self.action_button)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.close_button.setEnabled(not self.reindex)
        button_layout.addWidget(self.close_button)

    def _add_directory(self):
        """Add directory to index list."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Index",
            ""
        )

        if directory:
            # Check if already in list
            for i in range(self.dir_list.count()):
                if self.dir_list.item(i).text() == directory:
                    return

            self.dir_list.addItem(directory)

    def _remove_directory(self):
        """Remove directory from list."""
        current_item = self.dir_list.currentItem()
        if current_item:
            self.dir_list.takeItem(self.dir_list.row(current_item))

    def _on_action_button(self):
        """Handle action button click."""
        if self.indexing_thread and self.indexing_thread.isRunning():
            # Cancel indexing
            self.log_text.append("Cancelling...")
            self.indexing_thread.cancel()
            self.action_button.setEnabled(False)
        else:
            # Start indexing
            self._start_indexing()

    def _start_indexing(self):
        """Start indexing process."""
        # Get directories
        if self.reindex:
            directories = self.app_controller.config.get('indexing.watch_paths', [])
            if not directories:
                QMessageBox.warning(
                    self,
                    "No Directories",
                    "No directories are configured for indexing."
                )
                self.reject()
                return
        else:
            directories = []
            for i in range(self.dir_list.count()):
                directories.append(self.dir_list.item(i).text())

            if not directories:
                QMessageBox.warning(
                    self,
                    "No Directories",
                    "Please add at least one directory to index."
                )
                return

        # Disable controls
        if hasattr(self, 'dir_list'):
            self.dir_list.setEnabled(False)
        self.action_button.setText("Cancel")
        self.close_button.setEnabled(False)

        # Clear log
        self.log_text.clear()
        self.log_text.append(f"Starting indexing of {len(directories)} director{'y' if len(directories) == 1 else 'ies'}...")

        # Create and start thread
        self.indexing_thread = IndexingThread(
            self.app_controller.indexer,
            directories,
            self.reindex
        )

        self.indexing_thread.progress_updated.connect(self._on_progress)
        self.indexing_thread.finished_indexing.connect(self._on_finished)
        self.indexing_thread.error_occurred.connect(self._on_error)

        self.indexing_thread.start()

    def _on_progress(self, current: int, total: int, filename: str):
        """Handle progress update.

        Args:
            current: Current file number
            total: Total files
            filename: Current filename
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)

        # Truncate long filenames
        if len(filename) > 80:
            filename = "..." + filename[-77:]

        self.status_label.setText(f"Indexing ({current}/{total}): {filename}")

    def _on_finished(self, stats: dict):
        """Handle indexing completion.

        Args:
            stats: Indexing statistics
        """
        self.progress_bar.setValue(100)
        self.status_label.setText("Indexing complete")

        self.log_text.append("\n=== Indexing Complete ===")
        self.log_text.append(f"Files indexed: {stats['indexed']}")
        self.log_text.append(f"Files skipped: {stats['skipped']}")
        self.log_text.append(f"Errors: {stats['errors']}")

        # Re-enable controls
        if hasattr(self, 'dir_list'):
            self.dir_list.setEnabled(True)
        self.action_button.setText("Start Indexing")
        self.action_button.setEnabled(not self.reindex)
        self.close_button.setEnabled(True)

        # Show success message
        QMessageBox.information(
            self,
            "Indexing Complete",
            f"Successfully indexed {stats['indexed']} files."
        )

        if self.reindex:
            self.accept()

    def _on_error(self, error_msg: str):
        """Handle indexing error.

        Args:
            error_msg: Error message
        """
        self.log_text.append(f"ERROR: {error_msg}")
        self.status_label.setText("Error occurred")

    def closeEvent(self, event):
        """Handle dialog close.

        Args:
            event: Close event
        """
        if self.indexing_thread and self.indexing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Cancel Indexing",
                "Indexing is in progress. Cancel it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.indexing_thread.cancel()
                self.indexing_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
