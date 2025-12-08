"""Home screen for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable, List
from ..theme import get_theme
from ..components.card_widget import CardWidget
from ..components.search_bar import SearchBar
from ..components.progress_bar import StatCard, StreakIndicator


class HomeScreen(ctk.CTkFrame):
    """
    Home screen displaying deck overview and quick stats.
    """

    def __init__(
        self,
        master,
        on_deck_click: Optional[Callable[[int], None]] = None,
        on_create_deck: Optional[Callable] = None,
        on_search: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(master, fg_color=self.theme.bg_primary, **kwargs)

        self.on_deck_click = on_deck_click
        self.on_create_deck = on_create_deck
        self.on_search = on_search

        self.decks = []
        self.deck_widgets = []

        self._create_ui()

    def _create_ui(self):
        """Create the home screen UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header with stats
        self._create_header()

        # Toolbar
        self._create_toolbar()

        # Deck grid
        self._create_deck_grid()

    def _create_header(self):
        """Create header with quick stats."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")

        title = ctk.CTkLabel(
            title_frame,
            text="My Decks",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(side="left")

        # Stats cards
        stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(20, 0))

        # Today's stats
        self.today_card = StatCard(
            stats_frame,
            title="Studied today",
            value="0",
            icon="",
            color=self.theme.success
        )
        self.today_card.pack(side="left", padx=(0, 15))

        # Time stat
        self.time_card = StatCard(
            stats_frame,
            title="Time today",
            value="0 min",
            icon="",
            color=self.theme.info
        )
        self.time_card.pack(side="left", padx=15)

        # Streak
        self.streak_indicator = StreakIndicator(stats_frame, streak=0)
        self.streak_indicator.pack(side="left", padx=15)

        # Due cards
        self.due_card = StatCard(
            stats_frame,
            title="Due for review",
            value="0",
            icon="",
            color=self.theme.warning
        )
        self.due_card.pack(side="left", padx=15)

    def _create_toolbar(self):
        """Create toolbar with search and create button."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=30, pady=15)

        # Search bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search decks...",
            on_search=self._handle_search
        )
        self.search_bar.pack(side="left", fill="x", expand=True)

        # Create deck button
        create_btn = ctk.CTkButton(
            toolbar,
            text="+ Create Deck",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_hover,
            height=40,
            corner_radius=10,
            command=self._handle_create_deck
        )
        create_btn.pack(side="right", padx=(15, 0))

    def _create_deck_grid(self):
        """Create scrollable deck grid."""
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.theme.scrollbar_fg,
            scrollbar_button_hover_color=self.theme.accent
        )
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))

        # Configure grid for deck cards
        for i in range(4):
            self.scroll_frame.grid_columnconfigure(i, weight=1, uniform="deck")

        # Placeholder for empty state
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No decks yet.\nClick '+ Create Deck' to get started!",
            font=ctk.CTkFont(size=16),
            text_color=self.theme.text_muted,
            justify="center"
        )

    def _handle_search(self, query: str):
        """Handle search query."""
        if self.on_search:
            self.on_search(query)

    def _handle_create_deck(self):
        """Handle create deck button."""
        if self.on_create_deck:
            self.on_create_deck()

    def _handle_deck_click(self, deck_id: int):
        """Handle deck card click."""
        if self.on_deck_click:
            self.on_deck_click(deck_id)

    def set_decks(self, decks: List[dict]):
        """Set the decks to display."""
        self.decks = decks

        # Clear existing widgets
        for widget in self.deck_widgets:
            widget.destroy()
        self.deck_widgets.clear()

        if not decks:
            self.empty_label.grid(row=0, column=0, columnspan=4, pady=50)
            return
        else:
            self.empty_label.grid_forget()

        # Create deck cards
        for i, deck in enumerate(decks):
            row = i // 4
            col = i % 4

            card = CardWidget(
                self.scroll_frame,
                deck_id=deck['id'],
                name=deck['name'],
                icon=deck.get('icon', ''),
                card_count=deck.get('card_count', 0),
                color=deck.get('color', self.theme.accent),
                progress=deck.get('progress', 0),
                on_click=self._handle_deck_click
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.deck_widgets.append(card)

    def update_stats(
        self,
        cards_today: int = 0,
        time_today: int = 0,
        streak: int = 0,
        due_count: int = 0
    ):
        """Update the stats display."""
        self.today_card.set_value(str(cards_today))

        # Format time
        if time_today < 60:
            time_str = f"{time_today} sec"
        else:
            time_str = f"{time_today // 60} min"
        self.time_card.set_value(time_str)

        self.streak_indicator.set_streak(streak)
        self.due_card.set_value(str(due_count))

    def refresh(self):
        """Refresh the display."""
        # This would trigger a reload from the database
        pass


class CreateDeckDialog(ctk.CTkToplevel):
    """Dialog for creating a new deck."""

    def __init__(
        self,
        master,
        on_create: Optional[Callable[[str, str, str, str], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.theme = get_theme()
        self.on_create = on_create

        self.title("Create New Deck")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make modal
        self.transient(master)
        self.grab_set()

        self._create_ui()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 500) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create dialog UI."""
        self.configure(fg_color=self.theme.bg_primary)

        # Title
        title = ctk.CTkLabel(
            self,
            text="Create New Deck",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(pady=(20, 20))

        # Form
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Name
        name_label = ctk.CTkLabel(
            form,
            text="Deck Name",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        name_label.pack(anchor="w")

        self.name_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g., Spanish Vocabulary",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", pady=(5, 15))

        # Description
        desc_label = ctk.CTkLabel(
            form,
            text="Description (optional)",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        desc_label.pack(anchor="w")

        self.desc_entry = ctk.CTkTextbox(
            form,
            height=80,
            font=ctk.CTkFont(size=14)
        )
        self.desc_entry.pack(fill="x", pady=(5, 15))

        # Icon and color row
        options_row = ctk.CTkFrame(form, fg_color="transparent")
        options_row.pack(fill="x")

        # Icon
        icon_frame = ctk.CTkFrame(options_row, fg_color="transparent")
        icon_frame.pack(side="left", fill="x", expand=True)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text="Icon",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        icon_label.pack(anchor="w")

        from ..utils.constants import DECK_ICONS
        self.icon_var = ctk.StringVar(value=DECK_ICONS[0] if DECK_ICONS else "")

        self.icon_menu = ctk.CTkOptionMenu(
            icon_frame,
            values=DECK_ICONS[:16] if DECK_ICONS else [""],
            variable=self.icon_var,
            width=80
        )
        self.icon_menu.pack(anchor="w", pady=(5, 0))

        # Color
        color_frame = ctk.CTkFrame(options_row, fg_color="transparent")
        color_frame.pack(side="right", fill="x", expand=True)

        color_label = ctk.CTkLabel(
            color_frame,
            text="Color",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        color_label.pack(anchor="w")

        from ..utils.constants import DECK_COLORS
        self.color_var = ctk.StringVar(value=DECK_COLORS[0] if DECK_COLORS else "#6366f1")

        colors_row = ctk.CTkFrame(color_frame, fg_color="transparent")
        colors_row.pack(anchor="w", pady=(5, 0))

        for color in DECK_COLORS[:8]:
            btn = ctk.CTkButton(
                colors_row,
                text="",
                width=25,
                height=25,
                fg_color=color,
                hover_color=color,
                corner_radius=5,
                command=lambda c=color: self.color_var.set(c)
            )
            btn.pack(side="left", padx=2)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            hover_color=self.theme.bg_hover,
            height=40,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        create_btn = ctk.CTkButton(
            btn_frame,
            text="Create Deck",
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_hover,
            height=40,
            command=self._create
        )
        create_btn.pack(side="right")

    def _create(self):
        """Handle create button."""
        name = self.name_entry.get().strip()
        if not name:
            # Show error
            self.name_entry.configure(border_color=self.theme.error)
            return

        description = self.desc_entry.get("1.0", "end-1c").strip()
        icon = self.icon_var.get()
        color = self.color_var.get()

        if self.on_create:
            self.on_create(name, description, icon, color)

        self.destroy()
