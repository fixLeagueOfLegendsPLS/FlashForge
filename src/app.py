"""Main application class for FlashForge."""

import customtkinter as ctk
from typing import Optional, Dict, Any
from datetime import datetime

from .database import DatabaseManager
from .ui.theme import ThemeManager, init_theme, get_theme
from .ui.components.sidebar import Sidebar
from .ui.screens.home_screen import HomeScreen, CreateDeckDialog
from .ui.screens.study_screen import StudyScreen
from .ui.screens.edit_screen import EditScreen
from .ui.screens.import_screen import ImportScreen
from .ui.screens.stats_screen import StatsScreen
from .ui.screens.settings_screen import SettingsScreen
from .core.study_engine import StudyEngine, StudyMode
from .utils.config import Config
from .utils.constants import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, APP_NAME, APP_VERSION


class FlashForgeApp(ctk.CTk):
    """
    Main FlashForge application.
    """

    def __init__(self):
        super().__init__()

        # Initialize configuration
        self.config = Config()

        # Initialize theme
        init_theme(self.config.appearance.theme)
        self.theme = get_theme()

        # Initialize database
        self.db = DatabaseManager()

        # Initialize study engine
        self.study_engine = StudyEngine(
            algorithm=self.config.study.algorithm
        )

        # Setup window
        self._setup_window()

        # Create UI
        self._create_ui()

        # Load initial data
        self._load_data()

        # Register theme callback
        ThemeManager.register_callback(self._on_theme_change)

    def _setup_window(self):
        """Setup main window."""
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Set position if saved
        if self.config.window_x is not None and self.config.window_y is not None:
            self.geometry(f"+{self.config.window_x}+{self.config.window_y}")

        # Configure theme colors
        self.configure(fg_color=self.theme.bg_primary)

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Bind keyboard shortcuts
        self._bind_shortcuts()

    def _create_ui(self):
        """Create main UI structure."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self._navigate,
            on_import=self._show_import,
            on_export=self._show_export
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Create screens (but don't show yet)
        self.screens: Dict[str, ctk.CTkFrame] = {}

        # Home screen
        self.home_screen = HomeScreen(
            self.content_frame,
            on_deck_click=self._on_deck_click,
            on_create_deck=self._show_create_deck,
            on_search=self._search_decks
        )
        self.screens["home"] = self.home_screen

        # Stats screen
        self.stats_screen = StatsScreen(self.content_frame)
        self.screens["stats"] = self.stats_screen

        # Settings screen
        self.settings_screen = SettingsScreen(
            self.content_frame,
            on_save=self._save_settings
        )
        self.screens["settings"] = self.settings_screen

        # Show home by default
        self._show_screen("home")

    def _bind_shortcuts(self):
        """Bind global keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self._show_create_deck())
        self.bind("<Control-i>", lambda e: self._show_import())
        self.bind("<Control-e>", lambda e: self._show_export())
        self.bind("<Control-f>", lambda e: self._focus_search())
        self.bind("<Control-comma>", lambda e: self._navigate("settings"))
        self.bind("<Control-q>", lambda e: self._on_close())

    def _show_screen(self, name: str):
        """Show a screen by name."""
        # Hide all screens
        for screen in self.screens.values():
            screen.grid_forget()

        # Show requested screen
        if name in self.screens:
            self.screens[name].grid(row=0, column=0, sticky="nsew")
            self.current_screen = name

    def _navigate(self, section: str):
        """Handle navigation from sidebar."""
        if section == "all_decks":
            self._show_screen("home")
            self._refresh_decks()
        elif section == "favorites":
            self._show_screen("home")
            self._refresh_decks(favorites_only=True)
        elif section == "due_review":
            self._show_screen("home")
            self._refresh_decks(due_only=True)
        elif section == "tags":
            self._show_screen("home")
            # Would show tags view
        elif section == "stats":
            self._show_screen("stats")
            self._refresh_stats()
        elif section == "settings":
            self._show_screen("settings")
            self._load_settings()

    def _load_data(self):
        """Load initial data."""
        self._refresh_decks()
        self._refresh_stats()

    def _refresh_decks(self, favorites_only: bool = False, due_only: bool = False):
        """Refresh deck list."""
        decks = self.db.get_all_decks(favorites_only=favorites_only)

        deck_list = []
        for deck in decks:
            deck_data = {
                'id': deck.id,
                'name': deck.name,
                'icon': deck.icon,
                'color': deck.color,
                'card_count': deck.card_count,
                'progress': deck.progress_percentage
            }
            deck_list.append(deck_data)

        self.home_screen.set_decks(deck_list)

        # Update stats
        stats = self.db.get_total_stats()
        today_stats = self.db.get_daily_stats(days=1)
        today_cards = today_stats[0].cards_studied if today_stats else 0
        today_time = today_stats[0].time_spent_seconds if today_stats else 0

        self.home_screen.update_stats(
            cards_today=today_cards,
            time_today=today_time,
            streak=stats.get('streak', 0),
            due_count=self.db.get_cards_due_count()
        )

    def _refresh_stats(self):
        """Refresh statistics."""
        stats = self.db.get_total_stats()
        daily = self.db.get_daily_stats(days=365)

        # Build heatmap data
        heatmap = {}
        for day in daily:
            key = day.date.strftime("%Y-%m-%d")
            heatmap[key] = day.cards_studied

        # Build weekly data
        weekly = [0] * 7
        recent = self.db.get_daily_stats(days=7)
        for day in recent:
            weekday = day.date.weekday()
            weekly[weekday] = day.cards_studied

        self.stats_screen.update_stats({
            'total_cards_studied': stats.get('total_cards_studied', 0),
            'total_time_seconds': stats.get('total_time_seconds', 0),
            'streak': stats.get('streak', 0),
            'accuracy': stats.get('accuracy', 0),
            'heatmap_data': heatmap,
            'weekly_data': weekly
        })

    def _on_deck_click(self, deck_id: int):
        """Handle deck click."""
        self._show_deck(deck_id)

    def _show_deck(self, deck_id: int):
        """Show deck detail/study options."""
        deck = self.db.get_deck(deck_id)
        if not deck:
            return

        # For now, go directly to edit screen
        # Could show a deck detail dialog with study options
        cards = self.db.get_deck_cards(deck_id)
        cards_data = [
            {
                'id': c.id,
                'term': c.term,
                'definition': c.definition,
                'hint': c.hint,
                'example': c.example,
                'is_starred': c.is_starred
            }
            for c in cards
        ]

        # Create edit screen
        edit_screen = EditScreen(
            self.content_frame,
            on_back=lambda: self._navigate("all_decks"),
            on_save=lambda card: self._save_card(deck_id, card),
            on_study=self._start_study,
            on_delete_deck=self._delete_deck
        )
        edit_screen.set_deck(
            {'id': deck.id, 'name': deck.name, 'description': deck.description},
            cards_data
        )

        # Show it
        self.screens["edit"] = edit_screen
        self._show_screen("edit")

    def _start_study(self, deck_id: int, mode: str = "flashcards"):
        """Start a study session."""
        deck = self.db.get_deck(deck_id)
        if not deck:
            return

        cards = self.db.get_deck_cards(deck_id)
        if not cards:
            return

        cards_data = [
            {
                'id': c.id,
                'term': c.term,
                'definition': c.definition,
                'hint': c.hint,
                'example': c.example,
                'is_starred': c.is_starred,
                'ease_factor': c.ease_factor,
                'interval': c.interval,
                'repetitions': c.repetitions,
                'next_review': c.next_review
            }
            for c in cards
        ]

        # Start study session in engine
        self.study_engine.start_session(
            deck_id=deck_id,
            cards=cards_data,
            mode=StudyMode(mode)
        )

        # Create study session in DB
        session = self.db.start_study_session(deck_id, mode)
        self._current_session_id = session.id

        # Create study screen
        study_screen = StudyScreen(
            self.content_frame,
            mode=mode,
            on_back=self._end_study,
            on_complete=self._on_study_complete,
            on_card_update=self._on_card_study_update
        )
        study_screen.set_deck(deck.name, cards_data)

        self.screens["study"] = study_screen
        self._show_screen("study")

    def _on_card_study_update(self, card_id: int, update_data: Dict):
        """Handle card update from study."""
        quality = update_data.get('quality', 3)
        self.db.update_card_sm2(card_id, quality)

    def _on_study_complete(self, results: Dict):
        """Handle study session completion."""
        if hasattr(self, '_current_session_id'):
            self.db.update_study_session(
                self._current_session_id,
                cards_studied=results.get('total', 0),
                cards_correct=results.get('correct', 0),
                cards_incorrect=results.get('incorrect', 0)
            )
            self.db.end_study_session(self._current_session_id)

    def _end_study(self):
        """End study and return to home."""
        if hasattr(self, '_current_session_id'):
            self.db.end_study_session(self._current_session_id)

        self._navigate("all_decks")

    def _show_create_deck(self):
        """Show create deck dialog."""
        dialog = CreateDeckDialog(
            self,
            on_create=self._create_deck
        )

    def _create_deck(self, name: str, description: str, icon: str, color: str):
        """Create a new deck."""
        self.db.create_deck(
            name=name,
            description=description,
            icon=icon,
            color=color
        )
        self._refresh_decks()

    def _delete_deck(self, deck_id: int):
        """Delete a deck."""
        self.db.delete_deck(deck_id)
        self._navigate("all_decks")

    def _save_card(self, deck_id: int, card_data: Dict):
        """Save a card."""
        if card_data.get('id'):
            self.db.update_card(card_data['id'], **card_data)
        else:
            self.db.create_card(
                deck_id=deck_id,
                term=card_data.get('term', ''),
                definition=card_data.get('definition', ''),
                hint=card_data.get('hint'),
                example=card_data.get('example')
            )

    def _search_decks(self, query: str):
        """Search decks."""
        if query:
            decks = self.db.search_decks(query)
        else:
            decks = self.db.get_all_decks()

        deck_list = [
            {
                'id': d.id,
                'name': d.name,
                'icon': d.icon,
                'color': d.color,
                'card_count': d.card_count,
                'progress': d.progress_percentage
            }
            for d in decks
        ]
        self.home_screen.set_decks(deck_list)

    def _show_import(self):
        """Show import screen."""
        ImportScreen(
            self,
            on_import=self._do_import
        )

    def _do_import(self, deck_name: str, cards: list):
        """Perform import."""
        # Create deck
        deck = self.db.create_deck(name=deck_name)

        # Create cards
        self.db.create_cards_bulk(deck.id, cards)

        # Refresh
        self._refresh_decks()

    def _show_export(self):
        """Show export dialog."""
        # Would show export dialog
        pass

    def _focus_search(self):
        """Focus search bar."""
        if hasattr(self.home_screen, 'search_bar'):
            self.home_screen.search_bar.focus()

    def _load_settings(self):
        """Load settings into settings screen."""
        self.settings_screen.load_settings({
            'theme': self.config.appearance.theme,
            'accent_color': self.config.appearance.accent_color,
            'font_size': self.config.appearance.font_size,
            'animations_enabled': self.config.appearance.animations_enabled,
            'cards_per_session': self.config.study.cards_per_session,
            'sound_enabled': self.config.study.sound_enabled
        })

    def _save_settings(self, settings: Dict):
        """Save settings."""
        # Apply to config
        self.config.appearance.theme = settings.get('theme', 'dark')
        self.config.appearance.accent_color = settings.get('accent_color', '#6366f1')
        self.config.appearance.font_size = settings.get('font_size', 14)
        self.config.appearance.animations_enabled = settings.get('animations_enabled', True)
        self.config.study.cards_per_session = settings.get('cards_per_session', 20)
        self.config.study.sound_enabled = settings.get('sound_enabled', True)

        self.config.save()

    def _on_theme_change(self, theme):
        """Handle theme change."""
        self.theme = theme
        self.configure(fg_color=theme.bg_primary)

    def _on_close(self):
        """Handle window close."""
        # Save window position and size
        self.config.window_width = self.winfo_width()
        self.config.window_height = self.winfo_height()
        self.config.window_x = self.winfo_x()
        self.config.window_y = self.winfo_y()
        self.config.save()

        self.destroy()


def run():
    """Run the FlashForge application."""
    app = FlashForgeApp()
    app.mainloop()
