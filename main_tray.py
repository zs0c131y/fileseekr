#!/usr/bin/env python3
"""FileSeekr - System Tray Mode.

Runs FileSeekr as a system tray application with global hotkey support.
Press Ctrl+Shift+Space to search files from anywhere.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
import argparse

from src.app_controller import AppController
from src.gui.overlay_window import OverlaySearchWindow
from src.gui.system_tray import SystemTrayApp
from src.utils.hotkey_manager import HotkeyManager
from src.utils.autostart import AutoStartManager


def check_single_instance():
    """Check if another instance is already running.

    Returns:
        True if this is the only instance
    """
    # Simple lock file approach
    lock_file = Path.home() / '.fileseekr.lock'

    if lock_file.exists():
        try:
            # Check if process is still running
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())

            # Try to check if process exists (Unix-like systems)
            try:
                os.kill(pid, 0)
                # Process exists
                return False
            except (OSError, ProcessLookupError):
                # Process doesn't exist, remove stale lock
                lock_file.unlink()
        except Exception:
            # Error reading lock, remove it
            try:
                lock_file.unlink()
            except Exception:
                pass

    # Create lock file
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception:
        return True  # Allow running if we can't create lock


def cleanup_lock():
    """Remove lock file on exit."""
    lock_file = Path.home() / '.fileseekr.lock'
    try:
        if lock_file.exists():
            lock_file.unlink()
    except Exception:
        pass


def main():
    """Main application entry point for system tray mode."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='FileSeekr - Smart File Search')
    parser.add_argument(
        '--enable-autostart',
        action='store_true',
        help='Enable auto-start on system boot'
    )
    parser.add_argument(
        '--disable-autostart',
        action='store_true',
        help='Disable auto-start on system boot'
    )
    parser.add_argument(
        '--no-tray',
        action='store_true',
        help='Run without system tray (traditional mode)'
    )
    args = parser.parse_args()

    # Handle auto-start arguments
    if args.enable_autostart or args.disable_autostart:
        autostart_mgr = AutoStartManager()

        if args.enable_autostart:
            if autostart_mgr.enable():
                print("✓ Auto-start enabled")
                return 0
            else:
                print("✗ Failed to enable auto-start")
                return 1
        elif args.disable_autostart:
            if autostart_mgr.disable():
                print("✓ Auto-start disabled")
                return 0
            else:
                print("✗ Failed to disable auto-start")
                return 1

    # Check for single instance (only in tray mode)
    if not args.no_tray:
        if not check_single_instance():
            print("FileSeekr is already running in the system tray.")
            print("Press Ctrl+Shift+Space to search, or check the system tray icon.")
            return 1

    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("FileSeekr")
    app.setOrganizationName("FileSeekr")
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    # Set application style
    app.setStyle('Fusion')

    # Create application controller
    controller = AppController()

    if args.no_tray:
        # Traditional mode - show main window
        from src.gui.main_window import MainWindow

        window = MainWindow(controller)
        window.show()

        # Run application
        exit_code = app.exec_()

        # Cleanup
        controller.shutdown()
        sys.exit(exit_code)

    else:
        # System tray mode
        try:
            # Create overlay window
            overlay_window = OverlaySearchWindow(controller)

            # Create hotkey manager
            hotkey_manager = HotkeyManager()

            # Set hotkey callback to toggle overlay
            hotkey_manager.set_callback(overlay_window.toggle_overlay)

            # Create system tray app
            tray_app = SystemTrayApp(controller, overlay_window, hotkey_manager)

            # Start hotkey listener
            hotkey_manager.start()

            print("FileSeekr is running in the system tray.")
            print("Press Ctrl+Shift+Space to search files.")
            print("Right-click the tray icon for more options.")

            # Run application
            exit_code = app.exec_()

            # Cleanup
            cleanup_lock()
            hotkey_manager.stop()
            controller.shutdown()

            sys.exit(exit_code)

        except Exception as e:
            cleanup_lock()
            QMessageBox.critical(
                None,
                "FileSeekr Error",
                f"Failed to start FileSeekr:\n\n{str(e)}\n\n"
                "Please check the console for details."
            )
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == '__main__':
    sys.exit(main())
