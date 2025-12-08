"""Search bar component for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable
from ..theme import get_theme


class SearchBar(ctk.CTkFrame):
    """
    Search bar component with icon and clear button.
    Includes debouncing for search-as-you-type.
    """

    def __init__(
        self,
        master,
        placeholder: str = "Search...",
        on_search: Optional[Callable[[str], None]] = None,
        debounce_ms: int = 300,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.input_bg,
            corner_radius=10,
            border_width=1,
            border_color=self.theme.input_border,
            **kwargs
        )

        self.on_search = on_search
        self.debounce_ms = debounce_ms
        self._debounce_id = None

        self._create_ui(placeholder)

    def _create_ui(self, placeholder: str):
        """Create search bar UI."""
        # Search icon
        icon_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI Emoji", 14),
            text_color=self.theme.text_muted,
            width=30
        )
        icon_label.pack(side="left", padx=(12, 0))

        # Entry field
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=0,
            text_color=self.theme.input_fg,
            placeholder_text_color=self.theme.input_placeholder
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Return>", self._on_enter)

        # Clear button (hidden initially)
        self.clear_btn = ctk.CTkButton(
            self,
            text="",
            font=("Segoe UI Emoji", 12),
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=self.theme.bg_hover,
            text_color=self.theme.text_muted,
            command=self.clear
        )
        # Initially hidden
        self._update_clear_visibility()

    def _on_key_release(self, event=None):
        """Handle key release with debouncing."""
        # Cancel previous debounce
        if self._debounce_id:
            self.after_cancel(self._debounce_id)

        # Update clear button visibility
        self._update_clear_visibility()

        # Schedule new search
        self._debounce_id = self.after(self.debounce_ms, self._trigger_search)

    def _on_enter(self, event=None):
        """Handle enter key - immediate search."""
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._trigger_search()

    def _trigger_search(self):
        """Trigger the search callback."""
        self._debounce_id = None
        query = self.entry.get().strip()
        if self.on_search:
            self.on_search(query)

    def _update_clear_visibility(self):
        """Show/hide clear button based on content."""
        if self.entry.get():
            self.clear_btn.pack(side="right", padx=8)
        else:
            self.clear_btn.pack_forget()

    def clear(self):
        """Clear the search field."""
        self.entry.delete(0, "end")
        self._update_clear_visibility()
        if self.on_search:
            self.on_search("")

    def get(self) -> str:
        """Get current search query."""
        return self.entry.get().strip()

    def set(self, value: str):
        """Set search query."""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self._update_clear_visibility()

    def focus(self):
        """Focus the search entry."""
        self.entry.focus_set()


class FilterBar(ctk.CTkFrame):
    """
    Filter bar with multiple filter options.
    Used for filtering deck views.
    """

    def __init__(
        self,
        master,
        filters: list = None,
        on_filter_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.on_filter_change = on_filter_change
        self.current_filter = "all"
        self.filter_buttons = {}

        filters = filters or [
            ("all", "All"),
            ("recent", "Recent"),
            ("favorites", "Favorites"),
            ("due", "Due")
        ]

        self._create_ui(filters)

    def _create_ui(self, filters: list):
        """Create filter bar UI."""
        for key, label in filters:
            btn = ctk.CTkButton(
                self,
                text=label,
                font=ctk.CTkFont(size=12),
                fg_color=self.theme.accent if key == self.current_filter else "transparent",
                text_color=self.theme.text_primary,
                hover_color=self.theme.bg_hover,
                height=30,
                corner_radius=15,
                command=lambda k=key: self._set_filter(k)
            )
            btn.pack(side="left", padx=4)
            self.filter_buttons[key] = btn

    def _set_filter(self, filter_key: str):
        """Set active filter."""
        # Update button states
        for key, btn in self.filter_buttons.items():
            if key == filter_key:
                btn.configure(fg_color=self.theme.accent)
            else:
                btn.configure(fg_color="transparent")

        self.current_filter = filter_key

        if self.on_filter_change:
            self.on_filter_change(filter_key)

    def get_filter(self) -> str:
        """Get current filter."""
        return self.current_filter
