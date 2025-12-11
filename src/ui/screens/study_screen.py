"""Study screen for FlashForge - Flashcards and Learn modes."""

import customtkinter as ctk
from typing import Optional, Callable, Dict, Any
from ..theme import get_theme
from ..components.card_widget import FlipCard
from ..components.progress_bar import StudyProgressBar


class StudyScreen(ctk.CTkFrame):
    """
    Study screen for flashcard and learn modes.
    """

    def __init__(
        self,
        master,
        mode: str = "flashcards",  # flashcards, learn, write
        on_back: Optional[Callable] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_card_update: Optional[Callable[[int, Dict], None]] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(master, fg_color=self.theme.bg_primary, **kwargs)

        self.mode = mode
        self.on_back = on_back
        self.on_complete = on_complete
        self.on_card_update = on_card_update

        self.deck_name = ""
        self.cards = []
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.is_flipped = False

        self._create_ui()
        self._bind_keys()

    def _create_ui(self):
        """Create the study screen UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self._create_header()

        # Card area
        self._create_card_area()

        # Controls
        self._create_controls()

    def _create_header(self):
        """Create header with back button and progress."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Back button
        back_btn = ctk.CTkButton(
            header,
            text=" Back",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.theme.text_secondary,
            hover_color=self.theme.bg_hover,
            width=80,
            command=self._handle_back
        )
        back_btn.grid(row=0, column=0, sticky="w")

        # Deck name
        self.deck_label = ctk.CTkLabel(
            header,
            text=self.deck_name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.text_primary
        )
        self.deck_label.grid(row=0, column=1)

        # Card counter
        self.counter_label = ctk.CTkLabel(
            header,
            text="0/0",
            font=ctk.CTkFont(size=14),
            text_color=self.theme.text_muted
        )
        self.counter_label.grid(row=0, column=2, sticky="e")

        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="",
            font=("Segoe UI Emoji", 16),
            fg_color="transparent",
            text_color=self.theme.text_muted,
            hover_color=self.theme.bg_hover,
            width=40,
            command=self._show_settings
        )
        settings_btn.grid(row=0, column=3, sticky="e", padx=(10, 0))

        # Progress bar below header
        self.progress_bar = StudyProgressBar(
            self,
            total=0,
            current=0,
            show_text=False,
            height=4
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(55, 0))

    def _create_card_area(self):
        """Create the main card display area."""
        card_frame = ctk.CTkFrame(self, fg_color="transparent")
        card_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=20)
        card_frame.grid_columnconfigure(0, weight=1)
        card_frame.grid_rowconfigure(0, weight=1)

        # Flip card
        self.flip_card = FlipCard(
            card_frame,
            term="",
            definition="",
            on_flip=self._on_card_flip
        )
        self.flip_card.grid(row=0, column=0, sticky="nsew")

        # Action buttons below card
        action_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, pady=(10, 0))

        # Star button
        self.star_btn = ctk.CTkButton(
            action_frame,
            text="",
            font=("Segoe UI Emoji", 18),
            fg_color="transparent",
            text_color=self.theme.text_muted,
            hover_color=self.theme.bg_hover,
            width=40,
            height=40,
            command=self._toggle_star
        )
        self.star_btn.pack(side="left", padx=5)

        # Hint button
        self.hint_btn = ctk.CTkButton(
            action_frame,
            text="",
            font=("Segoe UI Emoji", 18),
            fg_color="transparent",
            text_color=self.theme.text_muted,
            hover_color=self.theme.bg_hover,
            width=40,
            height=40,
            command=self._show_hint
        )
        self.hint_btn.pack(side="left", padx=5)

        # Edit button
        edit_btn = ctk.CTkButton(
            action_frame,
            text="",
            font=("Segoe UI Emoji", 18),
            fg_color="transparent",
            text_color=self.theme.text_muted,
            hover_color=self.theme.bg_hover,
            width=40,
            height=40,
            command=self._edit_card
        )
        edit_btn.pack(side="left", padx=5)

    def _create_controls(self):
        """Create response controls."""
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=60, pady=(0, 40))
        controls.grid_columnconfigure((0, 1), weight=1)

        if self.mode == "flashcards":
            # Simple know/don't know buttons with better sizing
            self.dont_know_btn = ctk.CTkButton(
                controls,
                text="Don't Know",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.theme.error,
                hover_color="#dc2626",
                height=55,
                corner_radius=12,
                command=lambda: self._respond(False)
            )
            self.dont_know_btn.grid(row=0, column=0, sticky="ew", padx=(0, 12))

            self.know_btn = ctk.CTkButton(
                controls,
                text="Know",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.theme.success,
                hover_color="#16a34a",
                height=55,
                corner_radius=12,
                command=lambda: self._respond(True)
            )
            self.know_btn.grid(row=0, column=1, sticky="ew", padx=(12, 0))

        elif self.mode == "learn":
            # SM-2 quality buttons with better sizing
            btn_frame = ctk.CTkFrame(controls, fg_color="transparent")
            btn_frame.grid(row=0, column=0, columnspan=2)

            qualities = [
                ("Again", 0, self.theme.error),
                ("Hard", 2, self.theme.warning),
                ("Good", 3, self.theme.info),
                ("Easy", 5, self.theme.success),
            ]

            for text, quality, color in qualities:
                btn = ctk.CTkButton(
                    btn_frame,
                    text=text,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    fg_color=color,
                    height=50,
                    width=110,
                    corner_radius=10,
                    command=lambda q=quality: self._respond_quality(q)
                )
                btn.pack(side="left", padx=8)

        # Keyboard hint with better styling
        hint_frame = ctk.CTkFrame(controls, fg_color=self.theme.bg_secondary, corner_radius=8)
        hint_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))

        hint_label = ctk.CTkLabel(
            hint_frame,
            text="  Space: flip  |  ←/→: respond  |  S: star  |  H: hint",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.text_muted
        )
        hint_label.pack(padx=15, pady=8)

    def _bind_keys(self):
        """Bind keyboard shortcuts."""
        self._root = self.winfo_toplevel()
        self._bindings = []

        keys = [
            ("<space>", lambda e: self.flip_card.flip()),
            ("<Left>", lambda e: self._respond(False)),
            ("<Right>", lambda e: self._respond(True)),
            ("<Key-1>", lambda e: self._respond_quality(0)),
            ("<Key-2>", lambda e: self._respond_quality(2)),
            ("<Key-3>", lambda e: self._respond_quality(3)),
            ("<Key-4>", lambda e: self._respond_quality(5)),
            ("<Key-s>", lambda e: self._toggle_star()),
            ("<Key-h>", lambda e: self._show_hint()),
            ("<Escape>", lambda e: self._handle_back()),
        ]

        for key, callback in keys:
            binding_id = self._root.bind(key, callback, "+")
            self._bindings.append((key, binding_id))

    def _unbind_keys(self):
        """Unbind keyboard shortcuts."""
        if hasattr(self, '_root') and hasattr(self, '_bindings'):
            for key, binding_id in self._bindings:
                try:
                    self._root.unbind(key, binding_id)
                except Exception:
                    pass
            self._bindings = []

    def set_deck(self, deck_name: str, cards: list):
        """Set the deck to study."""
        self.deck_name = deck_name
        self.cards = cards
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0

        self.deck_label.configure(text=deck_name)
        self.progress_bar.set_progress(0, len(cards))

        if cards:
            self._show_card(0)
        else:
            self._show_complete()

    def _show_card(self, index: int):
        """Show card at index."""
        if 0 <= index < len(self.cards):
            card = self.cards[index]
            self.flip_card.set_card(
                term=card.get('term', ''),
                definition=card.get('definition', ''),
                hint=card.get('hint')
            )

            # Update counter
            self.counter_label.configure(text=f"{index + 1}/{len(self.cards)}")

            # Update star button
            is_starred = card.get('is_starred', False)
            self.star_btn.configure(
                text="" if is_starred else "",
                text_color=self.theme.warning if is_starred else self.theme.text_muted
            )

    def _on_card_flip(self, is_flipped: bool):
        """Handle card flip."""
        self.is_flipped = is_flipped

    def _respond(self, correct: bool):
        """Record a response (flashcards mode)."""
        if self.current_index >= len(self.cards):
            return

        card = self.cards[self.current_index]

        if correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1

        # Notify parent for database update
        if self.on_card_update:
            self.on_card_update(card['id'], {
                'correct': correct,
                'quality': 4 if correct else 1
            })

        self._next_card()

    def _respond_quality(self, quality: int):
        """Record a response with quality (learn mode)."""
        if self.current_index >= len(self.cards):
            return

        card = self.cards[self.current_index]
        correct = quality >= 3

        if correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1

        if self.on_card_update:
            self.on_card_update(card['id'], {
                'correct': correct,
                'quality': quality
            })

        self._next_card()

    def _next_card(self):
        """Move to next card."""
        self.current_index += 1
        self.progress_bar.set_progress(self.current_index)

        if self.current_index >= len(self.cards):
            self._show_complete()
        else:
            self._show_card(self.current_index)

    def _show_complete(self):
        """Show completion screen."""
        # Hide card and controls
        self.flip_card.grid_forget()

        # Show completion message
        complete_frame = ctk.CTkFrame(self, fg_color="transparent")
        complete_frame.grid(row=1, column=0, sticky="nsew")
        complete_frame.grid_columnconfigure(0, weight=1)
        complete_frame.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(complete_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Completion icon
        icon = ctk.CTkLabel(
            content,
            text="",
            font=("Segoe UI Emoji", 64)
        )
        icon.pack()

        # Message
        msg = ctk.CTkLabel(
            content,
            text="Session Complete!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.theme.text_primary
        )
        msg.pack(pady=(20, 10))

        # Stats
        total = self.correct_count + self.incorrect_count
        accuracy = (self.correct_count / total * 100) if total > 0 else 0

        stats = ctk.CTkLabel(
            content,
            text=f"Correct: {self.correct_count} | Incorrect: {self.incorrect_count}\nAccuracy: {accuracy:.0f}%",
            font=ctk.CTkFont(size=16),
            text_color=self.theme.text_secondary
        )
        stats.pack(pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=20)

        study_again_btn = ctk.CTkButton(
            btn_frame,
            text="Study Again",
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.accent,
            height=40,
            command=self._restart
        )
        study_again_btn.pack(side="left", padx=5)

        done_btn = ctk.CTkButton(
            btn_frame,
            text="Done",
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=40,
            command=self._handle_back
        )
        done_btn.pack(side="left", padx=5)

        # Notify completion
        if self.on_complete:
            self.on_complete({
                'correct': self.correct_count,
                'incorrect': self.incorrect_count,
                'total': total
            })

    def _restart(self):
        """Restart the study session."""
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.progress_bar.set_progress(0)

        # Unbind old keys
        self._unbind_keys()

        # Rebuild UI
        for widget in self.winfo_children():
            widget.destroy()

        self._create_ui()
        self._bind_keys()
        self._show_card(0)

    def _toggle_star(self):
        """Toggle star on current card."""
        if self.current_index < len(self.cards):
            card = self.cards[self.current_index]
            card['is_starred'] = not card.get('is_starred', False)

            is_starred = card['is_starred']
            self.star_btn.configure(
                text="" if is_starred else "",
                text_color=self.theme.warning if is_starred else self.theme.text_muted
            )

            # Notify for database update
            if self.on_card_update:
                self.on_card_update(card['id'], {'is_starred': is_starred})

    def _show_hint(self):
        """Show hint for current card."""
        if self.current_index < len(self.cards):
            card = self.cards[self.current_index]
            hint = card.get('hint')
            if hint:
                # Show hint dialog
                HintDialog(self, hint)

    def _edit_card(self):
        """Edit current card."""
        # Would open edit dialog
        pass

    def _show_settings(self):
        """Show study settings."""
        # Would open settings dialog
        pass

    def _handle_back(self):
        """Handle back button."""
        self._unbind_keys()
        if self.on_back:
            self.on_back()

    def destroy(self):
        """Clean up on destroy."""
        self._unbind_keys()
        super().destroy()


class HintDialog(ctk.CTkToplevel):
    """Simple dialog to show hint."""

    def __init__(self, master, hint: str):
        super().__init__(master)

        self.theme = get_theme()
        self.title("Hint")
        self.geometry("400x200")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.configure(fg_color=self.theme.bg_primary)

        # Hint icon
        icon = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI Emoji", 32)
        )
        icon.pack(pady=(20, 10))

        # Hint text
        hint_label = ctk.CTkLabel(
            self,
            text=hint,
            font=ctk.CTkFont(size=14),
            text_color=self.theme.text_primary,
            wraplength=350
        )
        hint_label.pack(padx=20, pady=10)

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Got it",
            fg_color=self.theme.accent,
            height=35,
            command=self.destroy
        )
        close_btn.pack(pady=20)

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 400) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
