"""Settings screen for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable, Dict, Any
from ..theme import get_theme, ThemeManager, THEMES
from ...utils.constants import DECK_COLORS


class SettingsScreen(ctk.CTkFrame):
    """
    Settings screen for application configuration.
    """

    def __init__(
        self,
        master,
        on_back: Optional[Callable] = None,
        on_save: Optional[Callable[[Dict], None]] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(master, fg_color=self.theme.bg_primary, **kwargs)

        self.on_back = on_back
        self.on_save = on_save

        self.settings = {}

        self._create_ui()

    def _create_ui(self):
        """Create settings screen UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text=" Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(side="left")

        # Main content
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # Appearance section
        self._create_appearance_section(content)

        # Study section
        self._create_study_section(content)

        # Import/Export section
        self._create_import_export_section(content)

        # Data section
        self._create_data_section(content)

        # About section
        self._create_about_section(content)

    def _create_section(self, parent, title: str, icon: str, row: int) -> ctk.CTkFrame:
        """Create a settings section."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_secondary, corner_radius=12)
        frame.grid(row=row, column=0, sticky="ew", pady=10)

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title_label = ctk.CTkLabel(
            header,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.text_primary
        )
        title_label.pack(side="left")

        # Content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 15))

        return content

    def _create_setting_row(
        self,
        parent,
        label: str,
        description: str = None
    ) -> ctk.CTkFrame:
        """Create a row for a setting."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)
        row.grid_columnconfigure(0, weight=1)

        # Labels
        label_frame = ctk.CTkFrame(row, fg_color="transparent")
        label_frame.grid(row=0, column=0, sticky="w")

        lbl = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=self.theme.text_primary
        )
        lbl.pack(anchor="w")

        if description:
            desc = ctk.CTkLabel(
                label_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=self.theme.text_muted
            )
            desc.pack(anchor="w")

        # Control area
        control = ctk.CTkFrame(row, fg_color="transparent")
        control.grid(row=0, column=1, sticky="e")

        return control

    def _create_appearance_section(self, parent):
        """Create appearance settings."""
        content = self._create_section(parent, "Appearance", "", 0)

        # Theme
        control = self._create_setting_row(content, "Theme", "Choose your preferred color scheme")
        self.theme_var = ctk.StringVar(value="dark")
        theme_menu = ctk.CTkOptionMenu(
            control,
            values=["Dark", "Light", "AMOLED"],
            variable=self.theme_var,
            command=self._on_theme_change
        )
        theme_menu.pack()

        # Accent color
        control = self._create_setting_row(content, "Accent Color", "Customize the accent color")
        colors_frame = ctk.CTkFrame(control, fg_color="transparent")
        colors_frame.pack()

        self.accent_var = ctk.StringVar(value=self.theme.accent)
        for color in DECK_COLORS[:8]:
            btn = ctk.CTkButton(
                colors_frame,
                text="",
                width=25,
                height=25,
                fg_color=color,
                hover_color=color,
                corner_radius=5,
                command=lambda c=color: self._set_accent(c)
            )
            btn.pack(side="left", padx=2)

        # Font size
        control = self._create_setting_row(content, "Font Size", "Adjust text size")
        self.font_size_var = ctk.IntVar(value=14)
        font_slider = ctk.CTkSlider(
            control,
            from_=12,
            to=20,
            number_of_steps=8,
            variable=self.font_size_var,
            width=150
        )
        font_slider.pack(side="left")

        font_label = ctk.CTkLabel(
            control,
            textvariable=self.font_size_var,
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        font_label.pack(side="left", padx=(10, 0))

        # Animations
        control = self._create_setting_row(content, "Animations", "Enable smooth animations")
        self.animations_var = ctk.BooleanVar(value=True)
        animations_switch = ctk.CTkSwitch(
            control,
            text="",
            variable=self.animations_var,
            onvalue=True,
            offvalue=False
        )
        animations_switch.pack()

    def _create_study_section(self, parent):
        """Create study settings."""
        content = self._create_section(parent, "Study", "", 1)

        # Cards per session
        control = self._create_setting_row(content, "Cards per Session", "Default number of cards to study")
        self.cards_per_session_var = ctk.IntVar(value=20)
        cards_entry = ctk.CTkEntry(
            control,
            textvariable=self.cards_per_session_var,
            width=60,
            justify="center"
        )
        cards_entry.pack()

        # Algorithm
        control = self._create_setting_row(content, "Learning Algorithm", "Choose how cards are scheduled")
        self.algorithm_var = ctk.StringVar(value="SM-2")
        algo_menu = ctk.CTkOptionMenu(
            control,
            values=["SM-2 (Recommended)", "Leitner System", "Simple"],
            variable=self.algorithm_var
        )
        algo_menu.pack()

        # Sound effects
        control = self._create_setting_row(content, "Sound Effects", "Play sounds for correct/incorrect")
        self.sound_var = ctk.BooleanVar(value=True)
        sound_switch = ctk.CTkSwitch(
            control,
            text="",
            variable=self.sound_var
        )
        sound_switch.pack()

        # Show progress
        control = self._create_setting_row(content, "Show Progress", "Display progress bar during study")
        self.progress_var = ctk.BooleanVar(value=True)
        progress_switch = ctk.CTkSwitch(
            control,
            text="",
            variable=self.progress_var
        )
        progress_switch.pack()

    def _create_import_export_section(self, parent):
        """Create import/export settings."""
        content = self._create_section(parent, "Import / Export", "", 2)

        # Default encoding
        control = self._create_setting_row(content, "Default Encoding", "File encoding for import/export")
        self.encoding_var = ctk.StringVar(value="UTF-8")
        encoding_menu = ctk.CTkOptionMenu(
            control,
            values=["UTF-8", "UTF-16", "Windows-1251", "ISO-8859-1"],
            variable=self.encoding_var
        )
        encoding_menu.pack()

        # Auto backup
        control = self._create_setting_row(content, "Auto Backup", "Automatically backup before major operations")
        self.backup_var = ctk.BooleanVar(value=True)
        backup_switch = ctk.CTkSwitch(
            control,
            text="",
            variable=self.backup_var
        )
        backup_switch.pack()

    def _create_data_section(self, parent):
        """Create data management settings."""
        content = self._create_section(parent, "Data", "", 3)

        # Database location
        control = self._create_setting_row(content, "Database Location", "Where your data is stored")
        db_label = ctk.CTkLabel(
            control,
            text="~/.flashforge/flashforge.db",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.text_muted
        )
        db_label.pack()

        # Export all data
        control = self._create_setting_row(content, "Export All Data", "Export everything as a backup")
        export_btn = ctk.CTkButton(
            control,
            text="Export",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=30,
            width=80,
            command=self._export_all
        )
        export_btn.pack()

        # Reset statistics
        control = self._create_setting_row(content, "Reset Statistics", "Clear all learning progress")
        reset_stats_btn = ctk.CTkButton(
            control,
            text="Reset",
            fg_color=self.theme.warning,
            height=30,
            width=80,
            command=self._reset_stats
        )
        reset_stats_btn.pack()

        # Reset application
        control = self._create_setting_row(content, "Reset Application", "Delete all data and start fresh")
        reset_btn = ctk.CTkButton(
            control,
            text="Reset",
            fg_color=self.theme.error,
            height=30,
            width=80,
            command=self._reset_app
        )
        reset_btn.pack()

    def _create_about_section(self, parent):
        """Create about section."""
        content = self._create_section(parent, "About", "", 4)

        # Version
        version_frame = ctk.CTkFrame(content, fg_color="transparent")
        version_frame.pack(fill="x", pady=5)

        version_label = ctk.CTkLabel(
            version_frame,
            text="FlashForge v1.0.0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.text_primary
        )
        version_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            version_frame,
            text="A local Quizlet alternative without limitations",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        desc_label.pack(anchor="w")

        # Links
        links_frame = ctk.CTkFrame(content, fg_color="transparent")
        links_frame.pack(fill="x", pady=10)

        github_btn = ctk.CTkButton(
            links_frame,
            text=" GitHub",
            fg_color=self.theme.button_secondary_bg,
            text_color=self.theme.button_secondary_fg,
            height=32,
            command=lambda: self._open_url("https://github.com")
        )
        github_btn.pack(side="left", padx=(0, 10))

        license_label = ctk.CTkLabel(
            links_frame,
            text="MIT License",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.text_muted
        )
        license_label.pack(side="left")

    def _on_theme_change(self, theme_name: str):
        """Handle theme change."""
        theme_map = {
            "Dark": "dark",
            "Light": "light",
            "AMOLED": "amoled"
        }
        ThemeManager.set_theme(theme_map.get(theme_name, "dark"))

    def _set_accent(self, color: str):
        """Set accent color."""
        self.accent_var.set(color)
        ThemeManager.set_accent_color(color)

    def _export_all(self):
        """Export all data."""
        # Would trigger full data export
        pass

    def _reset_stats(self):
        """Reset statistics."""
        # Show confirmation dialog
        pass

    def _reset_app(self):
        """Reset application."""
        # Show confirmation dialog
        pass

    def _open_url(self, url: str):
        """Open URL in browser."""
        import webbrowser
        webbrowser.open(url)

    def load_settings(self, settings: Dict[str, Any]):
        """Load settings into UI."""
        self.settings = settings

        # Apply to UI controls
        if 'theme' in settings:
            self.theme_var.set(settings['theme'].capitalize())

        if 'accent_color' in settings:
            self.accent_var.set(settings['accent_color'])

        if 'font_size' in settings:
            self.font_size_var.set(settings['font_size'])

        if 'animations_enabled' in settings:
            self.animations_var.set(settings['animations_enabled'])

        if 'cards_per_session' in settings:
            self.cards_per_session_var.set(settings['cards_per_session'])

        if 'sound_enabled' in settings:
            self.sound_var.set(settings['sound_enabled'])

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings from UI."""
        return {
            'theme': self.theme_var.get().lower(),
            'accent_color': self.accent_var.get(),
            'font_size': self.font_size_var.get(),
            'animations_enabled': self.animations_var.get(),
            'cards_per_session': self.cards_per_session_var.get(),
            'algorithm': self.algorithm_var.get(),
            'sound_enabled': self.sound_var.get(),
            'show_progress': self.progress_var.get(),
            'default_encoding': self.encoding_var.get(),
            'auto_backup': self.backup_var.get()
        }
