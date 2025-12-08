"""Theme management for FlashForge UI."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import customtkinter as ctk


@dataclass
class Theme:
    """Theme definition with all colors and styles."""

    name: str

    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str

    # Text colors
    text_primary: str
    text_secondary: str
    text_muted: str

    # Accent colors
    accent: str
    accent_hover: str
    accent_light: str

    # Status colors
    success: str
    warning: str
    error: str
    info: str

    # Border colors
    border: str
    border_light: str

    # Card specific
    card_bg: str
    card_front: str
    card_back: str

    # Sidebar
    sidebar_bg: str
    sidebar_hover: str
    sidebar_active: str

    # Button styles
    button_primary_bg: str
    button_primary_fg: str
    button_secondary_bg: str
    button_secondary_fg: str

    # Input styles
    input_bg: str
    input_fg: str
    input_border: str
    input_placeholder: str

    # Scrollbar
    scrollbar_bg: str
    scrollbar_fg: str

    # Progress
    progress_bg: str
    progress_fg: str


# Predefined themes
DARK_THEME = Theme(
    name="dark",

    bg_primary="#0f172a",
    bg_secondary="#1e293b",
    bg_tertiary="#334155",
    bg_hover="#475569",

    text_primary="#f8fafc",
    text_secondary="#cbd5e1",
    text_muted="#64748b",

    accent="#6366f1",
    accent_hover="#818cf8",
    accent_light="#312e81",

    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",

    border="#334155",
    border_light="#475569",

    card_bg="#1e293b",
    card_front="#6366f1",
    card_back="#8b5cf6",

    sidebar_bg="#0f172a",
    sidebar_hover="#1e293b",
    sidebar_active="#312e81",

    button_primary_bg="#6366f1",
    button_primary_fg="#ffffff",
    button_secondary_bg="#334155",
    button_secondary_fg="#f8fafc",

    input_bg="#1e293b",
    input_fg="#f8fafc",
    input_border="#475569",
    input_placeholder="#64748b",

    scrollbar_bg="#1e293b",
    scrollbar_fg="#475569",

    progress_bg="#334155",
    progress_fg="#6366f1"
)

LIGHT_THEME = Theme(
    name="light",

    bg_primary="#ffffff",
    bg_secondary="#f8fafc",
    bg_tertiary="#f1f5f9",
    bg_hover="#e2e8f0",

    text_primary="#0f172a",
    text_secondary="#475569",
    text_muted="#94a3b8",

    accent="#6366f1",
    accent_hover="#4f46e5",
    accent_light="#e0e7ff",

    success="#16a34a",
    warning="#d97706",
    error="#dc2626",
    info="#2563eb",

    border="#e2e8f0",
    border_light="#f1f5f9",

    card_bg="#ffffff",
    card_front="#6366f1",
    card_back="#8b5cf6",

    sidebar_bg="#f8fafc",
    sidebar_hover="#e2e8f0",
    sidebar_active="#e0e7ff",

    button_primary_bg="#6366f1",
    button_primary_fg="#ffffff",
    button_secondary_bg="#e2e8f0",
    button_secondary_fg="#0f172a",

    input_bg="#ffffff",
    input_fg="#0f172a",
    input_border="#cbd5e1",
    input_placeholder="#94a3b8",

    scrollbar_bg="#f1f5f9",
    scrollbar_fg="#cbd5e1",

    progress_bg="#e2e8f0",
    progress_fg="#6366f1"
)

AMOLED_THEME = Theme(
    name="amoled",

    bg_primary="#000000",
    bg_secondary="#0a0a0a",
    bg_tertiary="#171717",
    bg_hover="#262626",

    text_primary="#ffffff",
    text_secondary="#a3a3a3",
    text_muted="#525252",

    accent="#6366f1",
    accent_hover="#818cf8",
    accent_light="#1e1b4b",

    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",

    border="#262626",
    border_light="#404040",

    card_bg="#0a0a0a",
    card_front="#6366f1",
    card_back="#8b5cf6",

    sidebar_bg="#000000",
    sidebar_hover="#171717",
    sidebar_active="#1e1b4b",

    button_primary_bg="#6366f1",
    button_primary_fg="#ffffff",
    button_secondary_bg="#262626",
    button_secondary_fg="#ffffff",

    input_bg="#0a0a0a",
    input_fg="#ffffff",
    input_border="#404040",
    input_placeholder="#525252",

    scrollbar_bg="#0a0a0a",
    scrollbar_fg="#404040",

    progress_bg="#262626",
    progress_fg="#6366f1"
)


THEMES: Dict[str, Theme] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "amoled": AMOLED_THEME
}


class ThemeManager:
    """Manages application themes and applies them globally."""

    _instance: Optional['ThemeManager'] = None
    _current_theme: Theme = DARK_THEME
    _callbacks: list = []

    def __new__(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_theme(cls) -> Theme:
        """Get current theme."""
        return cls._current_theme

    @classmethod
    def set_theme(cls, theme_name: str) -> None:
        """Set theme by name."""
        if theme_name in THEMES:
            cls._current_theme = THEMES[theme_name]
            cls._apply_ctk_theme()
            cls._notify_callbacks()

    @classmethod
    def set_accent_color(cls, color: str) -> None:
        """Update accent color in current theme."""
        # Create a new theme with updated accent
        import copy
        new_theme = copy.copy(cls._current_theme)
        new_theme.accent = color
        new_theme.button_primary_bg = color
        new_theme.progress_fg = color
        cls._current_theme = new_theme
        cls._notify_callbacks()

    @classmethod
    def _apply_ctk_theme(cls) -> None:
        """Apply theme to CustomTkinter."""
        theme = cls._current_theme

        # Set appearance mode
        if theme.name == "light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

        # Set default color theme
        ctk.set_default_color_theme("blue")

    @classmethod
    def register_callback(cls, callback: callable) -> None:
        """Register a callback to be called when theme changes."""
        if callback not in cls._callbacks:
            cls._callbacks.append(callback)

    @classmethod
    def unregister_callback(cls, callback: callable) -> None:
        """Unregister a theme change callback."""
        if callback in cls._callbacks:
            cls._callbacks.remove(callback)

    @classmethod
    def _notify_callbacks(cls) -> None:
        """Notify all callbacks of theme change."""
        for callback in cls._callbacks:
            try:
                callback(cls._current_theme)
            except Exception:
                pass

    @classmethod
    def get_font(cls, size: int = 14, weight: str = "normal") -> tuple:
        """Get font tuple for the given size and weight."""
        family = "Segoe UI" if cls._current_theme.name != "amoled" else "Arial"
        return (family, size, weight)

    @classmethod
    def get_icon_font(cls, size: int = 16) -> tuple:
        """Get font for emoji icons."""
        return ("Segoe UI Emoji", size, "normal")


# Initialize theme manager
def init_theme(theme_name: str = "dark") -> None:
    """Initialize the theme system."""
    ThemeManager.set_theme(theme_name)


# Convenience function to get current theme
def get_theme() -> Theme:
    """Get current theme."""
    return ThemeManager.get_theme()
