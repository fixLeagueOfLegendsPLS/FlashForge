"""Sidebar navigation component for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable, Dict
from ..theme import get_theme, ThemeManager


class SidebarItem(ctk.CTkFrame):
    """Individual sidebar navigation item."""

    def __init__(
        self,
        master,
        text: str,
        icon: str = "",
        on_click: Optional[Callable] = None,
        badge: str = None,
        is_active: bool = False,
        indent: int = 0,
        **kwargs
    ):
        self.theme = get_theme()
        self._is_active = is_active

        super().__init__(
            master,
            fg_color=self.theme.sidebar_active if is_active else "transparent",
            corner_radius=8,
            height=40,
            **kwargs
        )
        self.pack_propagate(False)

        self.on_click = on_click
        self.text = text

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._create_ui(text, icon, badge, indent)

    def _create_ui(self, text: str, icon: str, badge: str, indent: int):
        """Create item UI."""
        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=("Segoe UI Emoji", 16),
                width=30
            )
            icon_label.pack(side="left", padx=(12 + indent, 4))
            icon_label.bind("<Button-1>", self._handle_click)

        # Text
        text_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_primary if self._is_active else self.theme.text_secondary,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True)
        text_label.bind("<Button-1>", self._handle_click)

        # Badge
        if badge:
            badge_label = ctk.CTkLabel(
                self,
                text=badge,
                font=ctk.CTkFont(size=11),
                text_color=self.theme.text_muted,
                width=30
            )
            badge_label.pack(side="right", padx=12)

    def _handle_click(self, event=None):
        if self.on_click:
            self.on_click()

    def _on_enter(self, event=None):
        if not self._is_active:
            self.configure(fg_color=self.theme.sidebar_hover)

    def _on_leave(self, event=None):
        if not self._is_active:
            self.configure(fg_color="transparent")

    def set_active(self, active: bool):
        """Set active state."""
        self._is_active = active
        self.configure(
            fg_color=self.theme.sidebar_active if active else "transparent"
        )


class Sidebar(ctk.CTkFrame):
    """
    Main sidebar navigation component.
    Contains navigation items, quick actions, and user info.
    """

    def __init__(
        self,
        master,
        on_navigate: Optional[Callable[[str], None]] = None,
        on_import: Optional[Callable] = None,
        on_export: Optional[Callable] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.sidebar_bg,
            corner_radius=0,
            width=250,
            **kwargs
        )
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.on_import = on_import
        self.on_export = on_export

        self.items: Dict[str, SidebarItem] = {}
        self.current_section = "all_decks"

        self._create_ui()

        # Register for theme changes
        ThemeManager.register_callback(self._on_theme_change)

    def _create_ui(self):
        """Create sidebar UI."""
        # Logo/Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        title_frame.pack(fill="x", padx=16, pady=(16, 8))
        title_frame.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            title_frame,
            text="FlashForge",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.theme.accent
        )
        logo_label.pack(side="left", pady=10)

        # Navigation items
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=8, pady=8)

        # Main navigation
        self._add_nav_item(nav_frame, "all_decks", "All Decks", "")
        self._add_nav_item(nav_frame, "favorites", "Favorites", "")
        self._add_nav_item(nav_frame, "due_review", "Due for Review", "")
        self._add_nav_item(nav_frame, "tags", "Tags", "")
        self._add_nav_item(nav_frame, "stats", "Statistics", "")
        self._add_nav_item(nav_frame, "settings", "Settings", "")

        # Separator
        separator = ctk.CTkFrame(self, fg_color=self.theme.border, height=1)
        separator.pack(fill="x", padx=16, pady=16)

        # Quick actions
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=16)

        # Import button
        import_btn = ctk.CTkButton(
            actions_frame,
            text=" Import",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            hover_color=self.theme.bg_hover,
            height=36,
            corner_radius=8,
            command=self._handle_import
        )
        import_btn.pack(fill="x", pady=4)

        # Export button
        export_btn = ctk.CTkButton(
            actions_frame,
            text=" Export",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            hover_color=self.theme.bg_hover,
            height=36,
            corner_radius=8,
            command=self._handle_export
        )
        export_btn.pack(fill="x", pady=4)

        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Version info at bottom
        version_label = ctk.CTkLabel(
            self,
            text="FlashForge v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=self.theme.text_muted
        )
        version_label.pack(side="bottom", pady=16)

    def _add_nav_item(
        self,
        parent,
        key: str,
        text: str,
        icon: str,
        badge: str = None
    ):
        """Add a navigation item."""
        item = SidebarItem(
            parent,
            text=text,
            icon=icon,
            badge=badge,
            is_active=(key == self.current_section),
            on_click=lambda k=key: self._navigate(k)
        )
        item.pack(fill="x", pady=2)
        self.items[key] = item

    def _navigate(self, section: str):
        """Handle navigation."""
        # Update active states
        for key, item in self.items.items():
            item.set_active(key == section)

        self.current_section = section

        if self.on_navigate:
            self.on_navigate(section)

    def _handle_import(self):
        """Handle import button click."""
        if self.on_import:
            self.on_import()

    def _handle_export(self):
        """Handle export button click."""
        if self.on_export:
            self.on_export()

    def set_active_section(self, section: str):
        """Programmatically set active section."""
        self._navigate(section)

    def update_badge(self, section: str, badge: str):
        """Update badge on a navigation item."""
        # Would need to recreate item or add badge update method
        pass

    def _on_theme_change(self, theme):
        """Handle theme change."""
        self.theme = theme
        self.configure(fg_color=theme.sidebar_bg)
        # Would need to update all child widgets too

    def destroy(self):
        """Clean up on destroy."""
        ThemeManager.unregister_callback(self._on_theme_change)
        super().destroy()
