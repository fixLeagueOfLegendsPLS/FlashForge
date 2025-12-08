"""Progress bar components for FlashForge."""

import customtkinter as ctk
from typing import Optional
from ..theme import get_theme


class StudyProgressBar(ctk.CTkFrame):
    """
    Progress bar for study sessions.
    Shows current progress with card count.
    """

    def __init__(
        self,
        master,
        total: int = 0,
        current: int = 0,
        show_text: bool = True,
        height: int = 8,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.total = total
        self.current = current
        self.show_text = show_text
        self.bar_height = height

        self._create_ui()

    def _create_ui(self):
        """Create progress bar UI."""
        # Text label (if enabled)
        if self.show_text:
            self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.text_frame.pack(fill="x")

            self.progress_label = ctk.CTkLabel(
                self.text_frame,
                text=self._get_text(),
                font=ctk.CTkFont(size=12),
                text_color=self.theme.text_secondary
            )
            self.progress_label.pack(side="left")

            self.percent_label = ctk.CTkLabel(
                self.text_frame,
                text=self._get_percent_text(),
                font=ctk.CTkFont(size=12),
                text_color=self.theme.text_muted
            )
            self.percent_label.pack(side="right")

        # Progress bar container
        self.bar_container = ctk.CTkFrame(
            self,
            fg_color=self.theme.progress_bg,
            corner_radius=self.bar_height // 2,
            height=self.bar_height
        )
        self.bar_container.pack(fill="x", pady=(4, 0) if self.show_text else 0)
        self.bar_container.pack_propagate(False)

        # Progress bar fill
        self.bar_fill = ctk.CTkFrame(
            self.bar_container,
            fg_color=self.theme.progress_fg,
            corner_radius=self.bar_height // 2
        )
        self._update_bar()

    def _get_text(self) -> str:
        """Get progress text."""
        return f"{self.current} / {self.total}"

    def _get_percent_text(self) -> str:
        """Get percentage text."""
        if self.total == 0:
            return "0%"
        percent = int((self.current / self.total) * 100)
        return f"{percent}%"

    def _update_bar(self):
        """Update progress bar fill width."""
        if self.total == 0:
            width = 0
        else:
            width = self.current / self.total

        self.bar_fill.place(relx=0, rely=0, relwidth=max(0.01, width), relheight=1)

    def set_progress(self, current: int, total: int = None):
        """Set progress values."""
        self.current = current
        if total is not None:
            self.total = total

        if self.show_text:
            self.progress_label.configure(text=self._get_text())
            self.percent_label.configure(text=self._get_percent_text())

        self._update_bar()

    def increment(self):
        """Increment current by 1."""
        self.set_progress(self.current + 1)

    def reset(self, total: int = None):
        """Reset progress."""
        self.current = 0
        if total is not None:
            self.total = total
        self.set_progress(0, self.total)


class CircularProgress(ctk.CTkFrame):
    """
    Circular progress indicator.
    Used for overall deck progress display.
    """

    def __init__(
        self,
        master,
        size: int = 80,
        progress: float = 0,
        line_width: int = 8,
        show_percent: bool = True,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color="transparent",
            width=size,
            height=size,
            **kwargs
        )

        self.size = size
        self.progress = progress
        self.line_width = line_width
        self.show_percent = show_percent

        self._create_ui()

    def _create_ui(self):
        """Create circular progress UI using a canvas."""
        # We'll use CTkProgressBar in determinate mode as CTK doesn't have circular
        # For a proper circular, we'd need to use Canvas

        # Simple fallback: use regular progress bar and text
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Percentage text
        percent_text = f"{int(self.progress)}%"
        self.label = ctk.CTkLabel(
            self,
            text=percent_text,
            font=ctk.CTkFont(size=self.size // 4, weight="bold"),
            text_color=self.theme.accent
        )
        self.label.grid(row=0, column=0)

    def set_progress(self, progress: float):
        """Set progress value (0-100)."""
        self.progress = progress
        self.label.configure(text=f"{int(progress)}%")


class StreakIndicator(ctk.CTkFrame):
    """
    Streak indicator with fire emoji and count.
    """

    def __init__(
        self,
        master,
        streak: int = 0,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.bg_secondary,
            corner_radius=10,
            **kwargs
        )

        self.streak = streak
        self._create_ui()

    def _create_ui(self):
        """Create streak indicator UI."""
        # Fire emoji
        fire_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI Emoji", 20)
        )
        fire_label.pack(side="left", padx=(12, 4), pady=8)

        # Streak count
        self.count_label = ctk.CTkLabel(
            self,
            text=str(self.streak),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.theme.warning
        )
        self.count_label.pack(side="left", padx=(0, 4))

        # Days text
        days_label = ctk.CTkLabel(
            self,
            text="day streak" if self.streak == 1 else "day streak",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        days_label.pack(side="left", padx=(0, 12))

    def set_streak(self, streak: int):
        """Update streak count."""
        self.streak = streak
        self.count_label.configure(text=str(streak))


class StatCard(ctk.CTkFrame):
    """
    Statistics card displaying a metric with icon.
    """

    def __init__(
        self,
        master,
        title: str,
        value: str,
        icon: str = "",
        subtitle: str = None,
        color: str = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(
            master,
            fg_color=self.theme.bg_secondary,
            corner_radius=12,
            **kwargs
        )

        self.color = color or self.theme.accent
        self._create_ui(title, value, icon, subtitle)

    def _create_ui(self, title: str, value: str, icon: str, subtitle: str):
        """Create stat card UI."""
        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=("Segoe UI Emoji", 24),
                text_color=self.color
            )
            icon_label.pack(anchor="w", padx=16, pady=(16, 8))

        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.text_primary
        )
        self.value_label.pack(anchor="w", padx=16)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_muted
        )
        title_label.pack(anchor="w", padx=16, pady=(4, 0))

        # Subtitle (optional)
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=self.theme.text_muted
            )
            subtitle_label.pack(anchor="w", padx=16, pady=(2, 16))
        else:
            # Padding at bottom
            spacer = ctk.CTkFrame(self, fg_color="transparent", height=16)
            spacer.pack(fill="x")

    def set_value(self, value: str):
        """Update the value."""
        self.value_label.configure(text=value)
