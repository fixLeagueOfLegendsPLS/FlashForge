"""Import screen for FlashForge - Card import with preview."""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from ..theme import get_theme
from ...core.importer import CardImporter
from ...utils.constants import SEPARATOR_PRESETS, SUPPORTED_ENCODINGS


class ImportScreen(ctk.CTkToplevel):
    """
    Import screen with customizable delimiters and preview.
    This is a key feature - allows importing with ANY separators.
    """

    def __init__(
        self,
        master,
        on_import: Optional[Callable[[str, List[Dict]], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.theme = get_theme()
        self.on_import = on_import

        self.file_path = None
        self.importer = None
        self.preview_cards = []

        self.title("Import Cards")
        self.geometry("800x700")
        self.minsize(700, 600)

        self.transient(master)
        self.grab_set()

        self.configure(fg_color=self.theme.bg_primary)

        self._create_ui()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 800) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 700) // 2
        self.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create import screen UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Title
        title = ctk.CTkLabel(
            self,
            text=" Import Cards",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.grid(row=0, column=0, sticky="w", padx=25, pady=(20, 15))

        # File selection
        self._create_file_section()

        # Separator settings
        self._create_separator_section()

        # Options
        self._create_options_section()

        # Preview
        self._create_preview_section()

        # Buttons
        self._create_buttons()

    def _create_file_section(self):
        """Create file selection section."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=25, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(
            frame,
            text="File:",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_secondary
        )
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.file_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Select a file to import...",
            height=36,
            state="disabled"
        )
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            frame,
            text="Browse...",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=36,
            width=100,
            command=self._browse_file
        )
        browse_btn.grid(row=0, column=2)

    def _create_separator_section(self):
        """Create separator settings section."""
        frame = ctk.CTkFrame(self, fg_color=self.theme.bg_secondary, corner_radius=10)
        frame.grid(row=2, column=0, sticky="ew", padx=25, pady=10)
        frame.grid_columnconfigure((0, 1), weight=1)

        # Section title
        title = ctk.CTkLabel(
            frame,
            text="Separator Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Preset selection
        preset_label = ctk.CTkLabel(
            frame,
            text="Preset:",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        preset_label.grid(row=1, column=0, sticky="w", padx=15)

        preset_names = ["Custom"] + [p['name'] for p in SEPARATOR_PRESETS.values()]
        self.preset_var = ctk.StringVar(value="Custom")
        self.preset_menu = ctk.CTkOptionMenu(
            frame,
            values=preset_names,
            variable=self.preset_var,
            command=self._on_preset_change
        )
        self.preset_menu.grid(row=1, column=1, sticky="w", padx=15, pady=5)

        # Term separator
        term_sep_frame = ctk.CTkFrame(frame, fg_color="transparent")
        term_sep_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        term_label = ctk.CTkLabel(
            term_sep_frame,
            text="Between term and definition:",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        term_label.pack(anchor="w")

        # Radio buttons for common separators
        self.term_sep_var = ctk.StringVar(value="\\t")

        separators_frame = ctk.CTkFrame(term_sep_frame, fg_color="transparent")
        separators_frame.pack(fill="x", pady=5)

        for text, value in [("Tab (\\t)", "\\t"), ("Semicolon (;)", ";"),
                           ("Comma (,)", ","), ("Double colon (::)", "::")]:
            rb = ctk.CTkRadioButton(
                separators_frame,
                text=text,
                variable=self.term_sep_var,
                value=value,
                command=self._update_preview
            )
            rb.pack(side="left", padx=10)

        # Custom separator
        custom_frame = ctk.CTkFrame(term_sep_frame, fg_color="transparent")
        custom_frame.pack(fill="x", pady=5)

        custom_rb = ctk.CTkRadioButton(
            custom_frame,
            text="Custom:",
            variable=self.term_sep_var,
            value="custom",
            command=self._update_preview
        )
        custom_rb.pack(side="left")

        self.custom_term_sep = ctk.CTkEntry(
            custom_frame,
            width=100,
            height=30,
            placeholder_text="e.g. |"
        )
        self.custom_term_sep.pack(side="left", padx=10)
        self.custom_term_sep.bind("<KeyRelease>", lambda e: self._update_preview())

        # Card separator
        card_sep_frame = ctk.CTkFrame(frame, fg_color="transparent")
        card_sep_frame.grid(row=2, column=1, sticky="ew", padx=15, pady=10)

        card_label = ctk.CTkLabel(
            card_sep_frame,
            text="Between cards:",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        card_label.pack(anchor="w")

        self.card_sep_var = ctk.StringVar(value="\\n")

        card_seps_frame = ctk.CTkFrame(card_sep_frame, fg_color="transparent")
        card_seps_frame.pack(fill="x", pady=5)

        for text, value in [("New line (\\n)", "\\n"), ("Double newline (\\n\\n)", "\\n\\n"),
                           ("Semicolon (;)", ";")]:
            rb = ctk.CTkRadioButton(
                card_seps_frame,
                text=text,
                variable=self.card_sep_var,
                value=value,
                command=self._update_preview
            )
            rb.pack(anchor="w", pady=2)

    def _create_options_section(self):
        """Create additional options section."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", padx=25, pady=10)

        # Options title
        title = ctk.CTkLabel(
            frame,
            text="Options",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(anchor="w", pady=(0, 10))

        options_row = ctk.CTkFrame(frame, fg_color="transparent")
        options_row.pack(fill="x")

        # Checkboxes
        self.skip_header_var = ctk.BooleanVar(value=False)
        skip_header = ctk.CTkCheckBox(
            options_row,
            text="First line is header (skip)",
            variable=self.skip_header_var,
            command=self._update_preview
        )
        skip_header.pack(side="left", padx=(0, 20))

        self.strip_var = ctk.BooleanVar(value=True)
        strip_ws = ctk.CTkCheckBox(
            options_row,
            text="Strip whitespace",
            variable=self.strip_var,
            command=self._update_preview
        )
        strip_ws.pack(side="left", padx=20)

        self.skip_empty_var = ctk.BooleanVar(value=True)
        skip_empty = ctk.CTkCheckBox(
            options_row,
            text="Skip empty lines",
            variable=self.skip_empty_var,
            command=self._update_preview
        )
        skip_empty.pack(side="left", padx=20)

        # Encoding
        enc_frame = ctk.CTkFrame(frame, fg_color="transparent")
        enc_frame.pack(fill="x", pady=(10, 0))

        enc_label = ctk.CTkLabel(
            enc_frame,
            text="Encoding:",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_secondary
        )
        enc_label.pack(side="left")

        self.encoding_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            enc_frame,
            values=SUPPORTED_ENCODINGS,
            variable=self.encoding_var,
            command=lambda e: self._update_preview()
        )
        enc_menu.pack(side="left", padx=10)

    def _create_preview_section(self):
        """Create preview section."""
        frame = ctk.CTkFrame(self, fg_color=self.theme.bg_secondary, corner_radius=10)
        frame.grid(row=4, column=0, sticky="nsew", padx=25, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))

        title = ctk.CTkLabel(
            header,
            text="Preview (first 5 cards)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(side="left")

        self.count_label = ctk.CTkLabel(
            header,
            text="Found: 0 cards",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        self.count_label.pack(side="right")

        # Preview table
        self.preview_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color=self.theme.bg_tertiary,
            corner_radius=8
        )
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.preview_frame.grid_columnconfigure((1, 2), weight=1)

        # Table header
        headers = ["#", "Term", "Definition"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.preview_frame,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.theme.text_secondary
            )
            lbl.grid(row=0, column=i, sticky="w", padx=10, pady=5)

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.preview_frame,
            text="Select a file to preview cards",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_muted
        )
        self.placeholder.grid(row=1, column=0, columnspan=3, pady=30)

        # Error label
        self.error_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.error
        )
        self.error_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 10))

    def _create_buttons(self):
        """Create action buttons."""
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="ew", padx=25, pady=(10, 20))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=40,
            width=100,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="Import",
            fg_color=self.theme.accent,
            height=40,
            width=120,
            state="disabled",
            command=self._do_import
        )
        self.import_btn.pack(side="right")

    def _browse_file(self):
        """Open file browser."""
        filetypes = [
            ("All supported", "*.txt *.csv *.tsv *.json"),
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("TSV files", "*.tsv"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]

        path = filedialog.askopenfilename(
            parent=self,
            title="Select file to import",
            filetypes=filetypes
        )

        if path:
            self.file_path = path
            self.file_entry.configure(state="normal")
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)
            self.file_entry.configure(state="disabled")

            # Auto-detect format
            self._auto_detect()
            self._update_preview()

    def _auto_detect(self):
        """Auto-detect file format."""
        if not self.file_path:
            return

        importer = CardImporter()
        detected = importer.detect_format(self.file_path)

        # Update encoding
        self.encoding_var.set(detected.get('encoding', 'utf-8'))

        # Update separators if confidence is high
        if detected.get('confidence', 0) > 0.7:
            term_sep = detected.get('term_separator', '\t')
            card_sep = detected.get('card_separator', '\n')

            # Map to UI values
            term_sep_escaped = term_sep.replace('\t', '\\t').replace('\n', '\\n')
            card_sep_escaped = card_sep.replace('\t', '\\t').replace('\n', '\\n')

            if term_sep_escaped in ['\\t', ';', ',', '::']:
                self.term_sep_var.set(term_sep_escaped)
            else:
                self.term_sep_var.set('custom')
                self.custom_term_sep.delete(0, 'end')
                self.custom_term_sep.insert(0, term_sep_escaped)

            if card_sep_escaped in ['\\n', '\\n\\n', ';']:
                self.card_sep_var.set(card_sep_escaped)

    def _on_preset_change(self, preset_name: str):
        """Handle preset selection."""
        if preset_name == "Custom":
            return

        for key, preset in SEPARATOR_PRESETS.items():
            if preset['name'] == preset_name:
                term_sep = preset['term_sep'].replace('\t', '\\t').replace('\n', '\\n')
                card_sep = preset['card_sep'].replace('\t', '\\t').replace('\n', '\\n')

                if term_sep in ['\\t', ';', ',', '::']:
                    self.term_sep_var.set(term_sep)
                else:
                    self.term_sep_var.set('custom')
                    self.custom_term_sep.delete(0, 'end')
                    self.custom_term_sep.insert(0, term_sep)

                if card_sep in ['\\n', '\\n\\n', ';']:
                    self.card_sep_var.set(card_sep)

                self._update_preview()
                break

    def _get_term_separator(self) -> str:
        """Get selected term separator."""
        val = self.term_sep_var.get()
        if val == 'custom':
            return self.custom_term_sep.get() or '\t'
        return val

    def _get_card_separator(self) -> str:
        """Get selected card separator."""
        return self.card_sep_var.get()

    def _update_preview(self):
        """Update the preview."""
        if not self.file_path:
            return

        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            if widget not in [self.placeholder]:
                widget.destroy()

        self.placeholder.grid_forget()
        self.error_label.configure(text="")

        # Create importer with current settings
        try:
            self.importer = CardImporter(
                term_separator=self._get_term_separator(),
                card_separator=self._get_card_separator(),
                encoding=self.encoding_var.get(),
                skip_header=self.skip_header_var.get(),
                strip_whitespace=self.strip_var.get(),
                skip_empty=self.skip_empty_var.get()
            )

            preview = self.importer.preview(self.file_path, limit=5)

            if preview.errors:
                self.error_label.configure(text=preview.errors[0])

            self.preview_cards = preview.cards
            self.count_label.configure(text=f"Found: {preview.total_count} cards")

            # Recreate header
            headers = ["#", "Term", "Definition"]
            for i, h in enumerate(headers):
                lbl = ctk.CTkLabel(
                    self.preview_frame,
                    text=h,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.theme.text_secondary
                )
                lbl.grid(row=0, column=i, sticky="w", padx=10, pady=5)

            # Add preview rows
            for i, card in enumerate(preview.cards):
                # Number
                num_lbl = ctk.CTkLabel(
                    self.preview_frame,
                    text=str(i + 1),
                    font=ctk.CTkFont(size=12),
                    text_color=self.theme.text_muted
                )
                num_lbl.grid(row=i + 1, column=0, sticky="w", padx=10, pady=3)

                # Term
                term = card.get('term', '')[:50]
                if len(card.get('term', '')) > 50:
                    term += "..."
                term_lbl = ctk.CTkLabel(
                    self.preview_frame,
                    text=term,
                    font=ctk.CTkFont(size=12),
                    text_color=self.theme.text_primary,
                    anchor="w"
                )
                term_lbl.grid(row=i + 1, column=1, sticky="w", padx=10, pady=3)

                # Definition
                definition = card.get('definition', '')[:60]
                if len(card.get('definition', '')) > 60:
                    definition += "..."
                def_lbl = ctk.CTkLabel(
                    self.preview_frame,
                    text=definition,
                    font=ctk.CTkFont(size=12),
                    text_color=self.theme.text_primary,
                    anchor="w"
                )
                def_lbl.grid(row=i + 1, column=2, sticky="w", padx=10, pady=3)

            # Enable import button if we have cards
            if preview.cards:
                self.import_btn.configure(state="normal")
            else:
                self.import_btn.configure(state="disabled")

        except Exception as e:
            self.error_label.configure(text=f"Error: {str(e)}")
            self.import_btn.configure(state="disabled")

    def _do_import(self):
        """Perform the import."""
        if not self.file_path or not self.importer:
            return

        result = self.importer.import_file(self.file_path)

        if result.success and self.on_import:
            # Get deck name from file
            deck_name = Path(self.file_path).stem

            # Ask for deck name
            dialog = DeckNameDialog(self, deck_name)
            self.wait_window(dialog)

            if dialog.result:
                self.on_import(dialog.result, result.cards)
                self.destroy()
        elif result.errors:
            self.error_label.configure(text=result.errors[0])


class DeckNameDialog(ctk.CTkToplevel):
    """Dialog to enter deck name for import."""

    def __init__(self, master, default_name: str = ""):
        super().__init__(master)

        self.theme = get_theme()
        self.result = None

        self.title("Deck Name")
        self.geometry("400x150")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.configure(fg_color=self.theme.bg_primary)

        # Label
        label = ctk.CTkLabel(
            self,
            text="Enter a name for the imported deck:",
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_primary
        )
        label.pack(padx=20, pady=(20, 10))

        # Entry
        self.name_entry = ctk.CTkEntry(
            self,
            height=36,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", padx=20, pady=10)
        self.name_entry.insert(0, default_name)
        self.name_entry.select_range(0, "end")
        self.name_entry.focus()
        self.name_entry.bind("<Return>", lambda e: self._confirm())

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=35,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=5)

        ok_btn = ctk.CTkButton(
            btn_frame,
            text="Import",
            fg_color=self.theme.accent,
            height=35,
            command=self._confirm
        )
        ok_btn.pack(side="left", padx=5)

        # Center
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 400) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")

    def _confirm(self):
        name = self.name_entry.get().strip()
        if name:
            self.result = name
            self.destroy()
