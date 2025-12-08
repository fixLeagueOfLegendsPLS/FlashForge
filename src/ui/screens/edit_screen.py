"""Edit screen for FlashForge - Card and deck editing."""

import customtkinter as ctk
from typing import Optional, Callable, List, Dict, Any
from ..theme import get_theme
from ..components.card_widget import MiniCard


class EditScreen(ctk.CTkFrame):
    """
    Screen for editing decks and cards.
    """

    def __init__(
        self,
        master,
        on_back: Optional[Callable] = None,
        on_save: Optional[Callable[[Dict], None]] = None,
        on_study: Optional[Callable[[int], None]] = None,
        on_delete_deck: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(master, fg_color=self.theme.bg_primary, **kwargs)

        self.on_back = on_back
        self.on_save = on_save
        self.on_study = on_study
        self.on_delete_deck = on_delete_deck

        self.deck = None
        self.cards = []
        self.selected_card_index = None

        self._create_ui()

    def _create_ui(self):
        """Create edit screen UI."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel - card list
        self._create_card_list_panel()

        # Right panel - editor
        self._create_editor_panel()

    def _create_card_list_panel(self):
        """Create left panel with card list."""
        panel = ctk.CTkFrame(self, fg_color=self.theme.bg_secondary, width=350)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_propagate(False)
        panel.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        back_btn = ctk.CTkButton(
            header,
            text=" Back",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            text_color=self.theme.text_secondary,
            hover_color=self.theme.bg_hover,
            width=60,
            command=self._handle_back
        )
        back_btn.pack(side="left")

        # Deck info
        self.deck_name_label = ctk.CTkLabel(
            panel,
            text="Deck Name",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.theme.text_primary
        )
        self.deck_name_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 0))

        self.card_count_label = ctk.CTkLabel(
            panel,
            text="0 cards",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        self.card_count_label.grid(row=1, column=0, sticky="w", padx=15, pady=(30, 10))

        # Card list
        self.card_list = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent"
        )
        self.card_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Add card button
        add_btn = ctk.CTkButton(
            panel,
            text="+ Add Card",
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.accent,
            height=40,
            command=self._add_card
        )
        add_btn.grid(row=3, column=0, sticky="ew", padx=15, pady=15)

        # Action buttons
        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))

        study_btn = ctk.CTkButton(
            actions,
            text=" Study",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.success,
            height=36,
            command=self._study_deck
        )
        study_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        delete_btn = ctk.CTkButton(
            actions,
            text=" Delete",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.error,
            height=36,
            command=self._delete_deck
        )
        delete_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _create_editor_panel(self):
        """Create right panel with card editor."""
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        panel.grid_columnconfigure(0, weight=1)

        # Editor title
        self.editor_title = ctk.CTkLabel(
            panel,
            text="Select a card to edit",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme.text_primary
        )
        self.editor_title.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Term field
        term_label = ctk.CTkLabel(
            panel,
            text="Term",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        term_label.grid(row=1, column=0, sticky="w")

        self.term_entry = ctk.CTkTextbox(
            panel,
            height=100,
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.input_bg,
            border_width=1,
            border_color=self.theme.input_border
        )
        self.term_entry.grid(row=2, column=0, sticky="ew", pady=(5, 15))

        # Definition field
        def_label = ctk.CTkLabel(
            panel,
            text="Definition",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        def_label.grid(row=3, column=0, sticky="w")

        self.def_entry = ctk.CTkTextbox(
            panel,
            height=150,
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.input_bg,
            border_width=1,
            border_color=self.theme.input_border
        )
        self.def_entry.grid(row=4, column=0, sticky="ew", pady=(5, 15))

        # Optional fields (collapsible)
        optional_label = ctk.CTkLabel(
            panel,
            text="Optional Fields",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_muted
        )
        optional_label.grid(row=5, column=0, sticky="w", pady=(10, 5))

        # Hint
        hint_label = ctk.CTkLabel(
            panel,
            text="Hint",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        hint_label.grid(row=6, column=0, sticky="w")

        self.hint_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Optional hint...",
            height=36,
            font=ctk.CTkFont(size=13)
        )
        self.hint_entry.grid(row=7, column=0, sticky="ew", pady=(5, 10))

        # Example
        example_label = ctk.CTkLabel(
            panel,
            text="Example",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        example_label.grid(row=8, column=0, sticky="w")

        self.example_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Optional example...",
            height=36,
            font=ctk.CTkFont(size=13)
        )
        self.example_entry.grid(row=9, column=0, sticky="ew", pady=(5, 20))

        # Action buttons
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew")

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Card",
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.accent,
            height=40,
            state="disabled",
            command=self._save_card
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.delete_card_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Card",
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.error,
            height=40,
            state="disabled",
            command=self._delete_card
        )
        self.delete_card_btn.pack(side="left")

        # Next/Previous buttons
        nav_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text=" Prev",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=40,
            state="disabled",
            command=self._prev_card
        )
        self.prev_btn.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ",
            font=ctk.CTkFont(size=13),
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=40,
            state="disabled",
            command=self._next_card
        )
        self.next_btn.pack(side="left")

    def set_deck(self, deck: Dict[str, Any], cards: List[Dict[str, Any]]):
        """Set the deck to edit."""
        self.deck = deck
        self.cards = cards
        self.selected_card_index = None

        # Update UI
        self.deck_name_label.configure(text=deck.get('name', 'Untitled'))
        self.card_count_label.configure(text=f"{len(cards)} cards")

        # Populate card list
        self._populate_card_list()

        # Select first card if available
        if cards:
            self._select_card(0)

    def _populate_card_list(self):
        """Populate the card list."""
        # Clear existing
        for widget in self.card_list.winfo_children():
            widget.destroy()

        # Add cards
        for i, card in enumerate(self.cards):
            card_widget = MiniCard(
                self.card_list,
                term=card.get('term', ''),
                definition=card.get('definition', ''),
                is_starred=card.get('is_starred', False),
                on_click=lambda idx=i: self._select_card(idx)
            )
            card_widget.pack(fill="x", pady=3)

    def _select_card(self, index: int):
        """Select a card for editing."""
        if 0 <= index < len(self.cards):
            self.selected_card_index = index
            card = self.cards[index]

            # Update editor
            self.editor_title.configure(text=f"Editing Card {index + 1}")

            # Clear and set values
            self.term_entry.delete("1.0", "end")
            self.term_entry.insert("1.0", card.get('term', ''))

            self.def_entry.delete("1.0", "end")
            self.def_entry.insert("1.0", card.get('definition', ''))

            self.hint_entry.delete(0, "end")
            self.hint_entry.insert(0, card.get('hint', '') or '')

            self.example_entry.delete(0, "end")
            self.example_entry.insert(0, card.get('example', '') or '')

            # Enable buttons
            self.save_btn.configure(state="normal")
            self.delete_card_btn.configure(state="normal")
            self.prev_btn.configure(state="normal" if index > 0 else "disabled")
            self.next_btn.configure(state="normal" if index < len(self.cards) - 1 else "disabled")

    def _add_card(self):
        """Add a new card."""
        new_card = {
            'id': None,  # Will be set when saved
            'term': '',
            'definition': '',
            'hint': None,
            'example': None,
            'is_starred': False
        }
        self.cards.append(new_card)

        # Update UI
        self.card_count_label.configure(text=f"{len(self.cards)} cards")
        self._populate_card_list()
        self._select_card(len(self.cards) - 1)

    def _save_card(self):
        """Save current card."""
        if self.selected_card_index is None:
            return

        card = self.cards[self.selected_card_index]
        card['term'] = self.term_entry.get("1.0", "end-1c").strip()
        card['definition'] = self.def_entry.get("1.0", "end-1c").strip()
        card['hint'] = self.hint_entry.get().strip() or None
        card['example'] = self.example_entry.get().strip() or None

        # Refresh list
        self._populate_card_list()

        # Notify parent
        if self.on_save:
            self.on_save(card)

    def _delete_card(self):
        """Delete current card."""
        if self.selected_card_index is None:
            return

        card = self.cards.pop(self.selected_card_index)

        # Update UI
        self.card_count_label.configure(text=f"{len(self.cards)} cards")
        self._populate_card_list()

        # Select next card
        if self.cards:
            new_index = min(self.selected_card_index, len(self.cards) - 1)
            self._select_card(new_index)
        else:
            self.selected_card_index = None
            self._clear_editor()

    def _clear_editor(self):
        """Clear the editor fields."""
        self.editor_title.configure(text="Select a card to edit")
        self.term_entry.delete("1.0", "end")
        self.def_entry.delete("1.0", "end")
        self.hint_entry.delete(0, "end")
        self.example_entry.delete(0, "end")
        self.save_btn.configure(state="disabled")
        self.delete_card_btn.configure(state="disabled")
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")

    def _prev_card(self):
        """Go to previous card."""
        if self.selected_card_index and self.selected_card_index > 0:
            self._select_card(self.selected_card_index - 1)

    def _next_card(self):
        """Go to next card."""
        if self.selected_card_index is not None and self.selected_card_index < len(self.cards) - 1:
            self._select_card(self.selected_card_index + 1)

    def _study_deck(self):
        """Start studying the deck."""
        if self.deck and self.on_study:
            self.on_study(self.deck['id'])

    def _delete_deck(self):
        """Delete the deck."""
        if self.deck and self.on_delete_deck:
            # Show confirmation
            ConfirmDialog(
                self,
                "Delete Deck",
                f"Are you sure you want to delete '{self.deck.get('name', 'this deck')}'?\nThis cannot be undone.",
                on_confirm=lambda: self.on_delete_deck(self.deck['id'])
            )

    def _handle_back(self):
        """Handle back button."""
        if self.on_back:
            self.on_back()

    def get_cards(self) -> List[Dict[str, Any]]:
        """Get all cards."""
        return self.cards


class ConfirmDialog(ctk.CTkToplevel):
    """Confirmation dialog."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
        on_confirm: Optional[Callable] = None
    ):
        super().__init__(master)

        self.theme = get_theme()
        self.on_confirm = on_confirm

        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.configure(fg_color=self.theme.bg_primary)

        # Message
        msg_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=self.theme.text_primary,
            wraplength=350
        )
        msg_label.pack(padx=20, pady=(30, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=36,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=5)

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color=self.theme.error,
            height=36,
            command=self._confirm
        )
        confirm_btn.pack(side="left", padx=5)

        # Center
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 400) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
