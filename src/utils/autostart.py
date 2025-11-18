"""Auto-start utilities for different platforms."""
import os
import sys
import platform
from pathlib import Path


class AutoStartManager:
    """Manages application auto-start on system boot."""

    def __init__(self, app_name: str = "FileSeekr"):
        """Initialize auto-start manager.

        Args:
            app_name: Application name
        """
        self.app_name = app_name
        self.system = platform.system()

    def is_enabled(self) -> bool:
        """Check if auto-start is enabled.

        Returns:
            True if enabled
        """
        if self.system == "Windows":
            return self._is_enabled_windows()
        elif self.system == "Darwin":
            return self._is_enabled_macos()
        elif self.system == "Linux":
            return self._is_enabled_linux()
        return False

    def enable(self) -> bool:
        """Enable auto-start.

        Returns:
            True if successful
        """
        try:
            if self.system == "Windows":
                return self._enable_windows()
            elif self.system == "Darwin":
                return self._enable_macos()
            elif self.system == "Linux":
                return self._enable_linux()
            return False
        except Exception as e:
            print(f"Error enabling auto-start: {e}")
            return False

    def disable(self) -> bool:
        """Disable auto-start.

        Returns:
            True if successful
        """
        try:
            if self.system == "Windows":
                return self._disable_windows()
            elif self.system == "Darwin":
                return self._disable_macos()
            elif self.system == "Linux":
                return self._disable_linux()
            return False
        except Exception as e:
            print(f"Error disabling auto-start: {e}")
            return False

    # Windows implementation
    def _is_enabled_windows(self) -> bool:
        """Check if auto-start is enabled on Windows."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False

    def _enable_windows(self) -> bool:
        """Enable auto-start on Windows."""
        try:
            import winreg

            # Get executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )

            # Set value
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            print(f"Windows auto-start error: {e}")
            return False

    def _disable_windows(self) -> bool:
        """Disable auto-start on Windows."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            try:
                winreg.DeleteValue(key, self.app_name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    # macOS implementation
    def _is_enabled_macos(self) -> bool:
        """Check if auto-start is enabled on macOS."""
        plist_path = self._get_macos_plist_path()
        return plist_path.exists()

    def _enable_macos(self) -> bool:
        """Enable auto-start on macOS."""
        try:
            plist_path = self._get_macos_plist_path()
            plist_path.parent.mkdir(parents=True, exist_ok=True)

            # Get executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = sys.executable
                script_path = os.path.abspath(sys.argv[0])

            # Create plist content
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fileseekr.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
"""
            if not getattr(sys, 'frozen', False):
                plist_content += f"        <string>{script_path}</string>\n"

            plist_content += """    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""

            # Write plist file
            with open(plist_path, 'w') as f:
                f.write(plist_content)

            return True
        except Exception as e:
            print(f"macOS auto-start error: {e}")
            return False

    def _disable_macos(self) -> bool:
        """Disable auto-start on macOS."""
        try:
            plist_path = self._get_macos_plist_path()
            if plist_path.exists():
                plist_path.unlink()
            return True
        except Exception:
            return False

    def _get_macos_plist_path(self) -> Path:
        """Get macOS plist file path.

        Returns:
            Path to plist file
        """
        home = Path.home()
        return home / "Library" / "LaunchAgents" / "com.fileseekr.app.plist"

    # Linux implementation
    def _is_enabled_linux(self) -> bool:
        """Check if auto-start is enabled on Linux."""
        desktop_file = self._get_linux_desktop_path()
        return desktop_file.exists()

    def _enable_linux(self) -> bool:
        """Enable auto-start on Linux."""
        try:
            desktop_file = self._get_linux_desktop_path()
            desktop_file.parent.mkdir(parents=True, exist_ok=True)

            # Get executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f"{sys.executable} {os.path.abspath(sys.argv[0])}"

            # Create desktop entry
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=FileSeekr
Comment=Smart file search application
Exec={exe_path}
Icon=system-search
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""

            # Write desktop file
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)

            # Make executable
            os.chmod(desktop_file, 0o755)

            return True
        except Exception as e:
            print(f"Linux auto-start error: {e}")
            return False

    def _disable_linux(self) -> bool:
        """Disable auto-start on Linux."""
        try:
            desktop_file = self._get_linux_desktop_path()
            if desktop_file.exists():
                desktop_file.unlink()
            return True
        except Exception:
            return False

    def _get_linux_desktop_path(self) -> Path:
        """Get Linux desktop file path.

        Returns:
            Path to desktop file
        """
        # Use XDG_CONFIG_HOME if set, otherwise use default
        config_home = os.environ.get('XDG_CONFIG_HOME')
        if config_home:
            config_dir = Path(config_home)
        else:
            config_dir = Path.home() / ".config"

        return config_dir / "autostart" / "fileseekr.desktop"
