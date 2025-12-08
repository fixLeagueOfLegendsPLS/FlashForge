"""
Statistics management for FlashForge.
Tracks learning progress, streaks, and achievements.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from ..utils.constants import STREAK_RESET_HOURS


@dataclass
class DailyProgress:
    """Progress for a single day."""
    date: datetime
    cards_studied: int = 0
    cards_correct: int = 0
    cards_incorrect: int = 0
    time_spent_seconds: int = 0
    sessions_count: int = 0

    @property
    def accuracy(self) -> float:
        total = self.cards_correct + self.cards_incorrect
        if total == 0:
            return 0.0
        return (self.cards_correct / total) * 100


@dataclass
class DeckProgress:
    """Progress for a specific deck."""
    deck_id: int
    deck_name: str
    total_cards: int
    mastered_cards: int = 0
    learning_cards: int = 0
    new_cards: int = 0
    due_cards: int = 0
    last_studied: Optional[datetime] = None

    @property
    def progress_percent(self) -> float:
        if self.total_cards == 0:
            return 0.0
        return (self.mastered_cards / self.total_cards) * 100


@dataclass
class Achievement:
    """Achievement/badge definition."""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None


class StatisticsManager:
    """
    Manages all statistics and progress tracking.
    """

    # Achievement definitions
    ACHIEVEMENTS = [
        Achievement("first_card", "First Steps", "Study your first card", ""),
        Achievement("10_cards", "Getting Started", "Study 10 cards", ""),
        Achievement("100_cards", "Century", "Study 100 cards", ""),
        Achievement("1000_cards", "Millennium", "Study 1000 cards", ""),
        Achievement("first_deck", "Collector", "Create your first deck", ""),
        Achievement("5_decks", "Library", "Create 5 decks", ""),
        Achievement("streak_3", "Consistent", "3 day streak", ""),
        Achievement("streak_7", "Week Warrior", "7 day streak", ""),
        Achievement("streak_30", "Monthly Master", "30 day streak", ""),
        Achievement("streak_100", "Centurion", "100 day streak", ""),
        Achievement("perfect_session", "Perfectionist", "100% accuracy in a session", ""),
        Achievement("speed_demon", "Speed Demon", "Study 50 cards in under 5 minutes", ""),
        Achievement("night_owl", "Night Owl", "Study after midnight", ""),
        Achievement("early_bird", "Early Bird", "Study before 6 AM", ""),
        Achievement("marathon", "Marathon", "Study for over 1 hour", ""),
        Achievement("mastery", "Master", "Master a deck (all cards learned)", ""),
    ]

    def __init__(self):
        self.daily_stats: Dict[str, DailyProgress] = {}
        self.deck_progress: Dict[int, DeckProgress] = {}
        self.achievements: Dict[str, Achievement] = {
            a.id: Achievement(**vars(a)) for a in self.ACHIEVEMENTS
        }
        self._total_cards_studied = 0
        self._total_time_seconds = 0
        self._current_streak = 0

    def record_session(
        self,
        deck_id: int,
        cards_studied: int,
        correct: int,
        incorrect: int,
        duration_seconds: int
    ) -> List[Achievement]:
        """
        Record a study session and check for new achievements.

        Returns:
            List of newly unlocked achievements
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date_key = today.strftime("%Y-%m-%d")

        # Update daily stats
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = DailyProgress(date=today)

        daily = self.daily_stats[date_key]
        daily.cards_studied += cards_studied
        daily.cards_correct += correct
        daily.cards_incorrect += incorrect
        daily.time_spent_seconds += duration_seconds
        daily.sessions_count += 1

        # Update totals
        self._total_cards_studied += cards_studied
        self._total_time_seconds += duration_seconds

        # Check achievements
        unlocked = self._check_achievements(
            cards_studied=cards_studied,
            correct=correct,
            incorrect=incorrect,
            duration_seconds=duration_seconds
        )

        return unlocked

    def get_streak(self) -> int:
        """Calculate current study streak."""
        if not self.daily_stats:
            return 0

        streak = 0
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Check each day going backwards
        for i in range(365):  # Max 1 year
            check_date = today - timedelta(days=i)
            date_key = check_date.strftime("%Y-%m-%d")

            if date_key in self.daily_stats:
                if self.daily_stats[date_key].cards_studied > 0:
                    streak += 1
                else:
                    break
            elif i == 0:
                # Today not studied yet, check yesterday
                continue
            else:
                break

        self._current_streak = streak
        return streak

    def get_heatmap_data(self, days: int = 365) -> Dict[str, int]:
        """
        Get activity heatmap data for the last N days.

        Returns:
            Dict mapping date strings to card counts
        """
        result = {}
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(days):
            date = today - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")

            if date_key in self.daily_stats:
                result[date_key] = self.daily_stats[date_key].cards_studied
            else:
                result[date_key] = 0

        return result

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get summary for the current week."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = today - timedelta(days=today.weekday())

        total_cards = 0
        total_correct = 0
        total_incorrect = 0
        total_time = 0
        days_studied = 0

        for i in range(7):
            date = start_of_week + timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")

            if date_key in self.daily_stats:
                daily = self.daily_stats[date_key]
                total_cards += daily.cards_studied
                total_correct += daily.cards_correct
                total_incorrect += daily.cards_incorrect
                total_time += daily.time_spent_seconds
                if daily.cards_studied > 0:
                    days_studied += 1

        return {
            'cards_studied': total_cards,
            'correct': total_correct,
            'incorrect': total_incorrect,
            'accuracy': (total_correct / (total_correct + total_incorrect) * 100) if (total_correct + total_incorrect) > 0 else 0,
            'time_spent_seconds': total_time,
            'days_studied': days_studied
        }

    def get_monthly_summary(self) -> Dict[str, Any]:
        """Get summary for the current month."""
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_cards = 0
        total_correct = 0
        total_incorrect = 0
        total_time = 0
        days_studied = 0

        current = start_of_month
        while current <= today:
            date_key = current.strftime("%Y-%m-%d")

            if date_key in self.daily_stats:
                daily = self.daily_stats[date_key]
                total_cards += daily.cards_studied
                total_correct += daily.cards_correct
                total_incorrect += daily.cards_incorrect
                total_time += daily.time_spent_seconds
                if daily.cards_studied > 0:
                    days_studied += 1

            current += timedelta(days=1)

        return {
            'cards_studied': total_cards,
            'correct': total_correct,
            'incorrect': total_incorrect,
            'accuracy': (total_correct / (total_correct + total_incorrect) * 100) if (total_correct + total_incorrect) > 0 else 0,
            'time_spent_seconds': total_time,
            'days_studied': days_studied
        }

    def get_all_time_stats(self) -> Dict[str, Any]:
        """Get all-time statistics."""
        total_cards = 0
        total_correct = 0
        total_incorrect = 0
        total_time = 0
        total_sessions = 0

        for daily in self.daily_stats.values():
            total_cards += daily.cards_studied
            total_correct += daily.cards_correct
            total_incorrect += daily.cards_incorrect
            total_time += daily.time_spent_seconds
            total_sessions += daily.sessions_count

        return {
            'total_cards_studied': total_cards,
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'accuracy': (total_correct / (total_correct + total_incorrect) * 100) if (total_correct + total_incorrect) > 0 else 0,
            'total_time_seconds': total_time,
            'total_sessions': total_sessions,
            'streak': self.get_streak(),
            'days_active': len([d for d in self.daily_stats.values() if d.cards_studied > 0])
        }

    def get_daily_breakdown(self, days: int = 30) -> List[DailyProgress]:
        """Get daily breakdown for the last N days."""
        result = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(days):
            date = today - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")

            if date_key in self.daily_stats:
                result.append(self.daily_stats[date_key])
            else:
                result.append(DailyProgress(date=date))

        return result

    def get_hourly_distribution(self) -> Dict[int, int]:
        """
        Get distribution of study activity by hour.
        Useful for finding optimal study times.
        """
        # This would need session-level data with timestamps
        # Returning placeholder
        return {hour: 0 for hour in range(24)}

    def get_difficult_cards(
        self,
        cards: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get the most difficult cards based on accuracy."""
        # Sort by accuracy (ascending) and times seen (descending)
        def difficulty_score(card):
            times_seen = card.get('times_seen', 0)
            if times_seen == 0:
                return float('inf')  # New cards at end
            correct = card.get('times_correct', 0)
            return correct / times_seen

        sorted_cards = sorted(cards, key=difficulty_score)
        return sorted_cards[:limit]

    def _check_achievements(
        self,
        cards_studied: int = 0,
        correct: int = 0,
        incorrect: int = 0,
        duration_seconds: int = 0
    ) -> List[Achievement]:
        """Check and unlock achievements."""
        unlocked = []
        now = datetime.now()

        # First card
        if not self.achievements["first_card"].unlocked and self._total_cards_studied > 0:
            self._unlock("first_card", now)
            unlocked.append(self.achievements["first_card"])

        # Card milestones
        if not self.achievements["10_cards"].unlocked and self._total_cards_studied >= 10:
            self._unlock("10_cards", now)
            unlocked.append(self.achievements["10_cards"])

        if not self.achievements["100_cards"].unlocked and self._total_cards_studied >= 100:
            self._unlock("100_cards", now)
            unlocked.append(self.achievements["100_cards"])

        if not self.achievements["1000_cards"].unlocked and self._total_cards_studied >= 1000:
            self._unlock("1000_cards", now)
            unlocked.append(self.achievements["1000_cards"])

        # Streak achievements
        streak = self.get_streak()
        if not self.achievements["streak_3"].unlocked and streak >= 3:
            self._unlock("streak_3", now)
            unlocked.append(self.achievements["streak_3"])

        if not self.achievements["streak_7"].unlocked and streak >= 7:
            self._unlock("streak_7", now)
            unlocked.append(self.achievements["streak_7"])

        if not self.achievements["streak_30"].unlocked and streak >= 30:
            self._unlock("streak_30", now)
            unlocked.append(self.achievements["streak_30"])

        if not self.achievements["streak_100"].unlocked and streak >= 100:
            self._unlock("streak_100", now)
            unlocked.append(self.achievements["streak_100"])

        # Perfect session
        if not self.achievements["perfect_session"].unlocked:
            if cards_studied >= 10 and incorrect == 0:
                self._unlock("perfect_session", now)
                unlocked.append(self.achievements["perfect_session"])

        # Speed demon
        if not self.achievements["speed_demon"].unlocked:
            if cards_studied >= 50 and duration_seconds <= 300:
                self._unlock("speed_demon", now)
                unlocked.append(self.achievements["speed_demon"])

        # Time-based achievements
        hour = now.hour
        if not self.achievements["night_owl"].unlocked and hour >= 0 and hour < 4:
            self._unlock("night_owl", now)
            unlocked.append(self.achievements["night_owl"])

        if not self.achievements["early_bird"].unlocked and hour >= 4 and hour < 6:
            self._unlock("early_bird", now)
            unlocked.append(self.achievements["early_bird"])

        # Marathon
        if not self.achievements["marathon"].unlocked and duration_seconds >= 3600:
            self._unlock("marathon", now)
            unlocked.append(self.achievements["marathon"])

        return unlocked

    def _unlock(self, achievement_id: str, when: datetime) -> None:
        """Unlock an achievement."""
        if achievement_id in self.achievements:
            self.achievements[achievement_id].unlocked = True
            self.achievements[achievement_id].unlocked_at = when

    def get_achievements(self) -> List[Achievement]:
        """Get all achievements with unlock status."""
        return list(self.achievements.values())

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get only unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]

    def load_from_db(self, daily_stats_data: List[Dict], achievements_data: List[Dict]) -> None:
        """Load statistics from database data."""
        for stat in daily_stats_data:
            date_key = stat['date'].strftime("%Y-%m-%d")
            self.daily_stats[date_key] = DailyProgress(
                date=stat['date'],
                cards_studied=stat.get('cards_studied', 0),
                cards_correct=stat.get('cards_correct', 0),
                cards_incorrect=stat.get('cards_incorrect', 0),
                time_spent_seconds=stat.get('time_spent_seconds', 0),
                sessions_count=stat.get('sessions_count', 0)
            )

        # Update totals
        self._total_cards_studied = sum(d.cards_studied for d in self.daily_stats.values())
        self._total_time_seconds = sum(d.time_spent_seconds for d in self.daily_stats.values())
