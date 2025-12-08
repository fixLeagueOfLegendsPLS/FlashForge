"""Statistics screen for FlashForge."""

import customtkinter as ctk
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime, timedelta
from ..theme import get_theme
from ..components.progress_bar import StatCard, StreakIndicator


class StatsScreen(ctk.CTkFrame):
    """
    Statistics screen showing learning progress and achievements.
    """

    def __init__(
        self,
        master,
        on_back: Optional[Callable] = None,
        **kwargs
    ):
        self.theme = get_theme()
        super().__init__(master, fg_color=self.theme.bg_primary, **kwargs)

        self.on_back = on_back

        self._create_ui()

    def _create_ui(self):
        """Create statistics screen UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text=" Statistics",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(side="left")

        # Main content
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # Overview cards
        self._create_overview_section(content)

        # Activity heatmap
        self._create_heatmap_section(content)

        # Weekly breakdown
        self._create_weekly_section(content)

        # Achievements
        self._create_achievements_section(content)

    def _create_overview_section(self, parent):
        """Create overview stats cards."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Row of stat cards
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x")

        self.total_cards_stat = StatCard(
            cards_frame,
            title="Total Cards Studied",
            value="0",
            icon="",
            color=self.theme.accent
        )
        self.total_cards_stat.pack(side="left", padx=(0, 15))

        self.total_time_stat = StatCard(
            cards_frame,
            title="Total Time",
            value="0h",
            icon="",
            color=self.theme.info
        )
        self.total_time_stat.pack(side="left", padx=15)

        self.streak_stat = StreakIndicator(cards_frame, streak=0)
        self.streak_stat.pack(side="left", padx=15)

        self.accuracy_stat = StatCard(
            cards_frame,
            title="Overall Accuracy",
            value="0%",
            icon="",
            color=self.theme.success
        )
        self.accuracy_stat.pack(side="left", padx=15)

    def _create_heatmap_section(self, parent):
        """Create activity heatmap like GitHub."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_secondary, corner_radius=12)
        frame.grid(row=1, column=0, sticky="ew", pady=10)

        # Title
        title = ctk.CTkLabel(
            frame,
            text="Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # Heatmap container
        self.heatmap_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.heatmap_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Generate placeholder heatmap
        self._generate_heatmap({})

    def _generate_heatmap(self, data: Dict[str, int]):
        """Generate heatmap grid."""
        # Clear existing
        for widget in self.heatmap_frame.winfo_children():
            widget.destroy()

        # Create 52 weeks x 7 days grid
        today = datetime.now()
        start_date = today - timedelta(days=364)

        # Month labels
        month_frame = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
        month_frame.pack(fill="x", pady=(0, 5))

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        current_month = -1
        for week in range(53):
            week_date = start_date + timedelta(weeks=week)
            if week_date.month != current_month:
                current_month = week_date.month
                lbl = ctk.CTkLabel(
                    month_frame,
                    text=months[current_month - 1],
                    font=ctk.CTkFont(size=9),
                    text_color=self.theme.text_muted
                )
                lbl.pack(side="left", padx=week * 1)

        # Day labels
        days_frame = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
        days_frame.pack(side="left", padx=(0, 5))

        for day in ["Mon", "", "Wed", "", "Fri", "", ""]:
            lbl = ctk.CTkLabel(
                days_frame,
                text=day,
                font=ctk.CTkFont(size=9),
                text_color=self.theme.text_muted,
                height=11
            )
            lbl.pack()

        # Grid
        grid_frame = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
        grid_frame.pack(side="left", fill="x")

        for week in range(53):
            week_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            week_frame.pack(side="left", padx=1)

            for day in range(7):
                date = start_date + timedelta(weeks=week, days=day)
                if date > today:
                    continue

                date_key = date.strftime("%Y-%m-%d")
                count = data.get(date_key, 0)

                # Color based on count
                if count == 0:
                    color = self.theme.bg_tertiary
                elif count < 10:
                    color = "#22543d"
                elif count < 25:
                    color = "#276749"
                elif count < 50:
                    color = "#2f855a"
                else:
                    color = "#38a169"

                cell = ctk.CTkFrame(
                    week_frame,
                    width=10,
                    height=10,
                    fg_color=color,
                    corner_radius=2
                )
                cell.pack(pady=1)

    def _create_weekly_section(self, parent):
        """Create weekly breakdown chart."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_secondary, corner_radius=12)
        frame.grid(row=2, column=0, sticky="ew", pady=10)

        # Title
        title = ctk.CTkLabel(
            frame,
            text="This Week",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # Bar chart
        self.chart_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.chart_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Generate empty chart
        self._generate_weekly_chart([0] * 7)

    def _generate_weekly_chart(self, data: List[int]):
        """Generate weekly bar chart."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        max_val = max(data) if data else 1

        for i, (day, count) in enumerate(zip(days, data)):
            day_frame = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
            day_frame.pack(side="left", fill="y", expand=True, padx=5)

            # Bar
            bar_height = int((count / max_val) * 100) if max_val > 0 else 0
            bar_container = ctk.CTkFrame(
                day_frame,
                fg_color=self.theme.bg_tertiary,
                height=100,
                width=30,
                corner_radius=5
            )
            bar_container.pack()
            bar_container.pack_propagate(False)

            if bar_height > 0:
                bar = ctk.CTkFrame(
                    bar_container,
                    fg_color=self.theme.accent,
                    corner_radius=5
                )
                bar.place(relx=0, rely=1, relwidth=1, relheight=bar_height/100, anchor="sw")

            # Count label
            count_lbl = ctk.CTkLabel(
                day_frame,
                text=str(count),
                font=ctk.CTkFont(size=11),
                text_color=self.theme.text_secondary
            )
            count_lbl.pack(pady=(5, 0))

            # Day label
            day_lbl = ctk.CTkLabel(
                day_frame,
                text=day,
                font=ctk.CTkFont(size=10),
                text_color=self.theme.text_muted
            )
            day_lbl.pack()

    def _create_achievements_section(self, parent):
        """Create achievements section."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_secondary, corner_radius=12)
        frame.grid(row=3, column=0, sticky="ew", pady=10)

        # Title
        title = ctk.CTkLabel(
            frame,
            text=" Achievements",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.text_primary
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # Achievements grid
        self.achievements_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.achievements_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Generate empty achievements
        self._generate_achievements([])

    def _generate_achievements(self, achievements: List[Dict]):
        """Generate achievements display."""
        for widget in self.achievements_frame.winfo_children():
            widget.destroy()

        # Default achievements to show
        default_achievements = [
            {"icon": "", "name": "First Steps", "desc": "Study your first card", "unlocked": False},
            {"icon": "", "name": "Getting Started", "desc": "Study 10 cards", "unlocked": False},
            {"icon": "", "name": "Century", "desc": "Study 100 cards", "unlocked": False},
            {"icon": "", "name": "Week Warrior", "desc": "7 day streak", "unlocked": False},
            {"icon": "", "name": "Perfectionist", "desc": "100% in a session", "unlocked": False},
            {"icon": "", "name": "Master", "desc": "Master a deck", "unlocked": False},
        ]

        achievements = achievements or default_achievements

        for i, ach in enumerate(achievements):
            if i % 3 == 0:
                row = ctk.CTkFrame(self.achievements_frame, fg_color="transparent")
                row.pack(fill="x", pady=5)

            card = ctk.CTkFrame(
                row,
                fg_color=self.theme.bg_tertiary if ach.get('unlocked') else self.theme.bg_primary,
                corner_radius=10
            )
            card.pack(side="left", fill="x", expand=True, padx=5)

            # Icon
            icon = ctk.CTkLabel(
                card,
                text=ach['icon'],
                font=("Segoe UI Emoji", 24)
            )
            icon.pack(side="left", padx=15, pady=10)

            # Info
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, pady=10)

            name = ctk.CTkLabel(
                info,
                text=ach['name'],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.theme.text_primary if ach.get('unlocked') else self.theme.text_muted
            )
            name.pack(anchor="w")

            desc = ctk.CTkLabel(
                info,
                text=ach['desc'],
                font=ctk.CTkFont(size=11),
                text_color=self.theme.text_muted
            )
            desc.pack(anchor="w")

    def update_stats(self, stats: Dict[str, Any]):
        """Update all statistics displays."""
        # Overview
        self.total_cards_stat.set_value(str(stats.get('total_cards_studied', 0)))

        total_time = stats.get('total_time_seconds', 0)
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        self.total_time_stat.set_value(f"{hours}h {minutes}m" if hours else f"{minutes}m")

        self.streak_stat.set_streak(stats.get('streak', 0))

        accuracy = stats.get('accuracy', 0)
        self.accuracy_stat.set_value(f"{accuracy:.0f}%")

        # Heatmap
        if 'heatmap_data' in stats:
            self._generate_heatmap(stats['heatmap_data'])

        # Weekly chart
        if 'weekly_data' in stats:
            self._generate_weekly_chart(stats['weekly_data'])

        # Achievements
        if 'achievements' in stats:
            self._generate_achievements(stats['achievements'])
