"""Card widget components for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable
from ..theme import get_theme, ThemeManager


class CardWidget(ctk.CTkFrame):
    """
    Widget for displaying a deck card preview.
    Used in the home screen deck list.
    """

    def __init__(
        self,
        master,
        deck_id: int,
        name: str,
        icon: str,
        card_count: int,
        color: str,
        progress: float = 0,
        on_click: Optional[Callable] = None,
        on_study: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.card_bg,
            corner_radius=12,
            **kwargs
        )

        self.deck_id = deck_id
        self.on_click = on_click
        self.on_study = on_study
        self.on_edit = on_edit

        # Make clickable
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._create_ui(name, icon, card_count, color, progress)

    def _create_ui(
        self,
        name: str,
        icon: str,
        card_count: int,
        color: str,
        progress: float
    ):
        """Create the card UI."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Color header
        header = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=12,
            height=60
        )
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        header.bind("<Button-1>", self._handle_click)

        # Icon
        icon_label = ctk.CTkLabel(
            header,
            text=icon,
            font=("Segoe UI Emoji", 28),
            text_color="#ffffff"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        icon_label.bind("<Button-1>", self._handle_click)

        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 12))
        content.bind("<Button-1>", self._handle_click)

        # Name
        name_label = ctk.CTkLabel(
            content,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.text_primary,
            anchor="w"
        )
        name_label.pack(fill="x")
        name_label.bind("<Button-1>", self._handle_click)

        # Card count
        count_label = ctk.CTkLabel(
            content,
            text=f"{card_count} cards",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted,
            anchor="w"
        )
        count_label.pack(fill="x", pady=(2, 6))
        count_label.bind("<Button-1>", self._handle_click)

        # Progress bar
        progress_frame = ctk.CTkFrame(content, fg_color="transparent", height=6)
        progress_frame.pack(fill="x")
        progress_frame.pack_propagate(False)

        progress_bg = ctk.CTkFrame(
            progress_frame,
            fg_color=self.theme.progress_bg,
            corner_radius=3,
            height=6
        )
        progress_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        if progress > 0:
            progress_fg = ctk.CTkFrame(
                progress_frame,
                fg_color=color,
                corner_radius=3,
                height=6
            )
            progress_fg.place(relx=0, rely=0, relwidth=progress/100, relheight=1)

    def _handle_click(self, event=None):
        """Handle card click."""
        if self.on_click:
            self.on_click(self.deck_id)

    def _on_enter(self, event=None):
        """Handle mouse enter."""
        self.configure(fg_color=self.theme.bg_hover)

    def _on_leave(self, event=None):
        """Handle mouse leave."""
        self.configure(fg_color=self.theme.card_bg)


class FlipCard(ctk.CTkFrame):
    """
    Animated flip card for study mode.
    Shows front (term) and back (definition).
    """

    def __init__(
        self,
        master,
        term: str = "",
        definition: str = "",
        hint: str = None,
        on_flip: Optional[Callable] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.term = term
        self.definition = definition
        self.hint = hint
        self.on_flip = on_flip
        self.is_flipped = False

        self._create_ui()

        # Bind click to flip
        self.bind("<Button-1>", self.flip)

    def _create_ui(self):
        """Create the flip card UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Card container
        self.card_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme.card_bg,
            corner_radius=20,
            border_width=2,
            border_color=self.theme.border
        )
        self.card_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_rowconfigure(0, weight=1)
        self.card_frame.bind("<Button-1>", self.flip)

        # Content label
        self.content_label = ctk.CTkLabel(
            self.card_frame,
            text=self.term,
            font=ctk.CTkFont(size=24),
            text_color=self.theme.text_primary,
            wraplength=500,
            justify="center"
        )
        self.content_label.grid(row=0, column=0, padx=30, pady=30)
        self.content_label.bind("<Button-1>", self.flip)

        # Flip hint
        self.flip_hint = ctk.CTkLabel(
            self.card_frame,
            text="Click to flip",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        self.flip_hint.grid(row=1, column=0, pady=(0, 15))
        self.flip_hint.bind("<Button-1>", self.flip)

        # Side indicator
        self.side_label = ctk.CTkLabel(
            self.card_frame,
            text="TERM",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.theme.accent
        )
        self.side_label.place(relx=0.5, y=15, anchor="center")

    def flip(self, event=None):
        """Flip the card."""
        self.is_flipped = not self.is_flipped

        if self.is_flipped:
            self.content_label.configure(text=self.definition)
            self.side_label.configure(text="DEFINITION")
            self.card_frame.configure(
                fg_color=self.theme.bg_tertiary,
                border_color=self.theme.accent
            )
        else:
            self.content_label.configure(text=self.term)
            self.side_label.configure(text="TERM")
            self.card_frame.configure(
                fg_color=self.theme.card_bg,
                border_color=self.theme.border
            )

        if self.on_flip:
            self.on_flip(self.is_flipped)

    def set_card(self, term: str, definition: str, hint: str = None):
        """Set new card content."""
        self.term = term
        self.definition = definition
        self.hint = hint
        self.is_flipped = False

        self.content_label.configure(text=self.term)
        self.side_label.configure(text="TERM")
        self.card_frame.configure(
            fg_color=self.theme.card_bg,
            border_color=self.theme.border
        )

    def show_hint(self):
        """Show hint if available."""
        if self.hint:
            # Could show as tooltip or temporary overlay
            pass

    def reset(self):
        """Reset card to front side."""
        if self.is_flipped:
            self.flip()


class MiniCard(ctk.CTkFrame):
    """Small card widget for lists and grids."""

    def __init__(
        self,
        master,
        term: str,
        definition: str = "",
        is_starred: bool = False,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.bg_secondary,
            corner_radius=8,
            **kwargs
        )

        self.on_click = on_click

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._create_ui(term, definition, is_starred)

    def _create_ui(self, term: str, definition: str, is_starred: bool):
        """Create mini card UI."""
        # Term
        term_label = ctk.CTkLabel(
            self,
            text=term if len(term) < 50 else term[:47] + "...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.theme.text_primary,
            anchor="w"
        )
        term_label.pack(fill="x", padx=12, pady=(10, 2))
        term_label.bind("<Button-1>", self._handle_click)

        # Definition preview
        def_preview = definition[:80] + "..." if len(definition) > 80 else definition
        def_label = ctk.CTkLabel(
            self,
            text=def_preview,
            font=ctk.CTkFont(size=11),
            text_color=self.theme.text_secondary,
            anchor="w"
        )
        def_label.pack(fill="x", padx=12, pady=(0, 10))
        def_label.bind("<Button-1>", self._handle_click)

        # Star indicator
        if is_starred:
            star = ctk.CTkLabel(
                self,
                text="",
                font=("Segoe UI Emoji", 12),
                text_color=self.theme.warning
            )
            star.place(relx=1, x=-25, y=8)

    def _handle_click(self, event=None):
        if self.on_click:
            self.on_click()

    def _on_enter(self, event=None):
        self.configure(fg_color=self.theme.bg_hover)

    def _on_leave(self, event=None):
        self.configure(fg_color=self.theme.bg_secondary)
