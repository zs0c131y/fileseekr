"""Global hotkey manager for FileSeekr."""
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from typing import Callable, Set, Optional
import threading


class HotkeyManager:
    """Manages global hotkeys for the application."""

    def __init__(self, hotkey_callback: Optional[Callable] = None):
        """Initialize hotkey manager.

        Args:
            hotkey_callback: Function to call when hotkey is pressed
        """
        self.hotkey_callback = hotkey_callback
        self.listener = None
        self.current_keys: Set = set()

        # Default hotkey: Ctrl+Shift+F, S (press in sequence)
        # Or you can use Ctrl+Shift+Space for instant trigger
        self.hotkey_combo = {
            Key.ctrl_l, Key.shift, KeyCode.from_char('f')
        }

        # Alternative: Ctrl+Shift+Space (easier to press)
        self.simple_hotkey = {
            Key.ctrl_l, Key.shift, Key.space
        }

        self.running = False

    def start(self):
        """Start listening for global hotkeys."""
        if self.running:
            return

        self.running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def stop(self):
        """Stop listening for global hotkeys."""
        self.running = False
        if self.listener:
            self.listener.stop()

    def _on_press(self, key):
        """Handle key press.

        Args:
            key: Pressed key
        """
        try:
            # Normalize key (handle both left and right modifiers)
            normalized_key = self._normalize_key(key)
            self.current_keys.add(normalized_key)

            # Check if hotkey combination is pressed
            if self._check_hotkey():
                if self.hotkey_callback:
                    # Run callback in separate thread to avoid blocking
                    threading.Thread(
                        target=self.hotkey_callback,
                        daemon=True
                    ).start()

                # Clear keys to prevent repeated triggers
                self.current_keys.clear()

        except Exception as e:
            print(f"Error in hotkey detection: {e}")

    def _on_release(self, key):
        """Handle key release.

        Args:
            key: Released key
        """
        try:
            normalized_key = self._normalize_key(key)
            self.current_keys.discard(normalized_key)
        except Exception:
            pass

    def _normalize_key(self, key):
        """Normalize key to handle left/right modifiers.

        Args:
            key: Key to normalize

        Returns:
            Normalized key
        """
        # Normalize left/right modifiers
        if key in (Key.ctrl_l, Key.ctrl_r):
            return Key.ctrl_l
        elif key in (Key.shift_l, Key.shift_r):
            return Key.shift
        elif key in (Key.alt_l, Key.alt_r):
            return Key.alt
        return key

    def _check_hotkey(self) -> bool:
        """Check if current keys match hotkey combination.

        Returns:
            True if hotkey is pressed
        """
        # Check simple hotkey (Ctrl+Shift+Space)
        if self.simple_hotkey.issubset(self.current_keys):
            return True

        # Check complex hotkey (Ctrl+Shift+F)
        # Note: For sequence-based hotkeys, you might want a more complex implementation
        if self.hotkey_combo.issubset(self.current_keys):
            return True

        return False

    def set_callback(self, callback: Callable):
        """Set hotkey callback function.

        Args:
            callback: Function to call when hotkey is pressed
        """
        self.hotkey_callback = callback

    def get_hotkey_description(self) -> str:
        """Get human-readable hotkey description.

        Returns:
            Hotkey description string
        """
        return "Ctrl+Shift+Space"
