"""
Study engine for FlashForge.
Implements SM-2 and Leitner learning algorithms.
"""

import random
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from ..utils.constants import (
    SM2_DEFAULT_EASE,
    SM2_MIN_EASE,
    SM2_MAX_EASE,
    LEITNER_BOXES,
    LEITNER_INTERVALS
)


class ResponseQuality(Enum):
    """Response quality ratings for SM-2 algorithm."""
    BLACKOUT = 0      # Complete blackout
    INCORRECT = 1     # Incorrect, remembered when shown
    INCORRECT_EASY = 2  # Incorrect, but easy to recall
    CORRECT_HARD = 3  # Correct with difficulty
    CORRECT = 4       # Correct with hesitation
    PERFECT = 5       # Perfect response


class StudyMode(Enum):
    """Available study modes."""
    FLASHCARDS = "flashcards"
    LEARN = "learn"
    WRITE = "write"
    TEST = "test"
    MATCH = "match"
    GRAVITY = "gravity"


@dataclass
class CardState:
    """Current state of a card in a study session."""
    card_id: int
    term: str
    definition: str
    hint: Optional[str] = None
    example: Optional[str] = None

    # SM-2 parameters
    ease_factor: float = SM2_DEFAULT_EASE
    interval: int = 0
    repetitions: int = 0
    next_review: Optional[datetime] = None

    # Session state
    times_shown: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    is_starred: bool = False
    last_response: Optional[ResponseQuality] = None


@dataclass
class StudySessionState:
    """State of an ongoing study session."""
    deck_id: int
    mode: StudyMode
    cards: List[CardState]
    current_index: int = 0
    started_at: datetime = field(default_factory=datetime.now)

    # Session statistics
    cards_studied: int = 0
    correct_count: int = 0
    incorrect_count: int = 0

    # Settings
    shuffle: bool = True
    show_definition_first: bool = False
    starred_only: bool = False

    @property
    def current_card(self) -> Optional[CardState]:
        """Get current card."""
        if 0 <= self.current_index < len(self.cards):
            return self.cards[self.current_index]
        return None

    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        if not self.cards:
            return 0.0
        return (self.current_index / len(self.cards)) * 100

    @property
    def accuracy(self) -> float:
        """Get current accuracy."""
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0.0
        return (self.correct_count / total) * 100

    @property
    def is_complete(self) -> bool:
        """Check if session is complete."""
        return self.current_index >= len(self.cards)

    @property
    def remaining(self) -> int:
        """Get remaining cards count."""
        return max(0, len(self.cards) - self.current_index)


class SM2Algorithm:
    """
    SuperMemo 2 (SM-2) spaced repetition algorithm.

    The algorithm calculates optimal review intervals based on:
    - Ease factor (difficulty of the card)
    - Number of successful repetitions
    - Quality of response (0-5 scale)
    """

    @staticmethod
    def calculate_next_review(
        ease_factor: float,
        interval: int,
        repetitions: int,
        quality: int
    ) -> Tuple[float, int, int, datetime]:
        """
        Calculate next review parameters.

        Args:
            ease_factor: Current ease factor (1.3-3.0)
            interval: Current interval in days
            repetitions: Number of successful repetitions
            quality: Response quality (0-5)

        Returns:
            Tuple of (new_ease_factor, new_interval, new_repetitions, next_review_date)
        """
        # Update ease factor
        new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease = max(SM2_MIN_EASE, min(SM2_MAX_EASE, new_ease))

        # Calculate new interval and repetitions
        if quality < 3:
            # Failed - reset
            new_interval = 1
            new_repetitions = 0
        else:
            # Success
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = int(interval * new_ease)

        next_review = datetime.now() + timedelta(days=new_interval)

        return new_ease, new_interval, new_repetitions, next_review

    @staticmethod
    def quality_from_binary(correct: bool, hesitation: bool = False) -> int:
        """
        Convert binary correct/incorrect to quality score.

        Args:
            correct: Whether the answer was correct
            hesitation: Whether there was hesitation

        Returns:
            Quality score (0-5)
        """
        if correct:
            return 4 if hesitation else 5
        else:
            return 1


class LeitnerSystem:
    """
    Leitner box system for spaced repetition.

    Cards move through boxes:
    - Correct answer: move to next box (longer interval)
    - Incorrect answer: move back to box 1
    """

    def __init__(self, num_boxes: int = LEITNER_BOXES):
        self.num_boxes = num_boxes
        self.intervals = LEITNER_INTERVALS[:num_boxes]

    def get_next_box(self, current_box: int, correct: bool) -> int:
        """
        Get next box based on answer.

        Args:
            current_box: Current box number (1-indexed)
            correct: Whether answer was correct

        Returns:
            Next box number
        """
        if correct:
            return min(current_box + 1, self.num_boxes)
        else:
            return 1

    def get_interval(self, box: int) -> int:
        """Get review interval for a box in days."""
        if 1 <= box <= self.num_boxes:
            return self.intervals[box - 1]
        return self.intervals[0]

    def calculate_next_review(self, box: int) -> datetime:
        """Calculate next review date for a box."""
        interval = self.get_interval(box)
        return datetime.now() + timedelta(days=interval)


class StudyEngine:
    """
    Main study engine that manages study sessions.
    Supports multiple study modes and algorithms.
    """

    def __init__(self, algorithm: str = "sm2"):
        """
        Initialize study engine.

        Args:
            algorithm: Learning algorithm to use ("sm2" or "leitner")
        """
        self.algorithm = algorithm
        self.sm2 = SM2Algorithm()
        self.leitner = LeitnerSystem()
        self.current_session: Optional[StudySessionState] = None

    def start_session(
        self,
        deck_id: int,
        cards: List[Dict[str, Any]],
        mode: StudyMode = StudyMode.FLASHCARDS,
        shuffle: bool = True,
        show_definition_first: bool = False,
        starred_only: bool = False,
        limit: int = None
    ) -> StudySessionState:
        """
        Start a new study session.

        Args:
            deck_id: ID of the deck being studied
            cards: List of card data dictionaries
            mode: Study mode
            shuffle: Whether to shuffle cards
            show_definition_first: Show definition before term
            starred_only: Only include starred cards
            limit: Maximum number of cards (None for all)

        Returns:
            StudySessionState for the new session
        """
        # Filter and convert cards
        card_states = []
        for card_data in cards:
            if starred_only and not card_data.get('is_starred'):
                continue

            card_states.append(CardState(
                card_id=card_data['id'],
                term=card_data['term'],
                definition=card_data['definition'],
                hint=card_data.get('hint'),
                example=card_data.get('example'),
                ease_factor=card_data.get('ease_factor', SM2_DEFAULT_EASE),
                interval=card_data.get('interval', 0),
                repetitions=card_data.get('repetitions', 0),
                next_review=card_data.get('next_review'),
                is_starred=card_data.get('is_starred', False)
            ))

        # Apply limit
        if limit and len(card_states) > limit:
            if shuffle:
                random.shuffle(card_states)
            card_states = card_states[:limit]
        elif shuffle:
            random.shuffle(card_states)

        self.current_session = StudySessionState(
            deck_id=deck_id,
            mode=mode,
            cards=card_states,
            shuffle=shuffle,
            show_definition_first=show_definition_first,
            starred_only=starred_only
        )

        return self.current_session

    def get_current_card(self) -> Optional[CardState]:
        """Get the current card in the session."""
        if self.current_session:
            return self.current_session.current_card
        return None

    def record_response(
        self,
        correct: bool,
        quality: int = None
    ) -> Tuple[Optional[CardState], Dict[str, Any]]:
        """
        Record a response for the current card.

        Args:
            correct: Whether the response was correct
            quality: Optional quality rating (0-5 for SM-2)

        Returns:
            Tuple of (updated card state, SM-2 update data)
        """
        if not self.current_session or not self.current_session.current_card:
            return None, {}

        card = self.current_session.current_card

        # Update card statistics
        card.times_shown += 1
        if correct:
            card.times_correct += 1
            self.current_session.correct_count += 1
        else:
            card.times_incorrect += 1
            self.current_session.incorrect_count += 1

        self.current_session.cards_studied += 1

        # Calculate SM-2 updates
        update_data = {}

        if self.algorithm == "sm2":
            if quality is None:
                quality = SM2Algorithm.quality_from_binary(correct)

            card.last_response = ResponseQuality(quality)

            new_ease, new_interval, new_reps, next_review = SM2Algorithm.calculate_next_review(
                card.ease_factor,
                card.interval,
                card.repetitions,
                quality
            )

            update_data = {
                'ease_factor': new_ease,
                'interval': new_interval,
                'repetitions': new_reps,
                'next_review': next_review,
                'times_correct': card.times_correct,
                'times_incorrect': card.times_incorrect,
                'times_seen': card.times_shown,
                'last_seen_at': datetime.now()
            }

            # Update card state
            card.ease_factor = new_ease
            card.interval = new_interval
            card.repetitions = new_reps
            card.next_review = next_review

        elif self.algorithm == "leitner":
            current_box = min(card.repetitions + 1, LEITNER_BOXES)
            new_box = self.leitner.get_next_box(current_box, correct)
            next_review = self.leitner.calculate_next_review(new_box)

            update_data = {
                'repetitions': new_box - 1,
                'interval': self.leitner.get_interval(new_box),
                'next_review': next_review,
                'times_correct': card.times_correct,
                'times_incorrect': card.times_incorrect,
                'times_seen': card.times_shown,
                'last_seen_at': datetime.now()
            }

            card.repetitions = new_box - 1
            card.interval = self.leitner.get_interval(new_box)
            card.next_review = next_review

        return card, update_data

    def next_card(self) -> Optional[CardState]:
        """
        Move to next card.

        Returns:
            Next card state or None if session complete
        """
        if not self.current_session:
            return None

        self.current_session.current_index += 1

        if self.current_session.is_complete:
            return None

        return self.current_session.current_card

    def previous_card(self) -> Optional[CardState]:
        """Move to previous card."""
        if not self.current_session:
            return None

        if self.current_session.current_index > 0:
            self.current_session.current_index -= 1

        return self.current_session.current_card

    def skip_card(self) -> Optional[CardState]:
        """Skip current card (move to end of queue)."""
        if not self.current_session or not self.current_session.current_card:
            return None

        card = self.current_session.cards.pop(self.current_session.current_index)
        self.current_session.cards.append(card)

        return self.current_session.current_card

    def toggle_star(self) -> bool:
        """Toggle star on current card."""
        if not self.current_session or not self.current_session.current_card:
            return False

        card = self.current_session.current_card
        card.is_starred = not card.is_starred
        return card.is_starred

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        if not self.current_session:
            return {}

        session = self.current_session
        duration = (datetime.now() - session.started_at).total_seconds()

        return {
            'deck_id': session.deck_id,
            'mode': session.mode.value,
            'total_cards': len(session.cards),
            'cards_studied': session.cards_studied,
            'correct': session.correct_count,
            'incorrect': session.incorrect_count,
            'accuracy': session.accuracy,
            'duration_seconds': int(duration),
            'started_at': session.started_at,
            'is_complete': session.is_complete
        }

    def end_session(self) -> Dict[str, Any]:
        """End current session and return summary."""
        summary = self.get_session_summary()
        self.current_session = None
        return summary

    def reset_session(self) -> None:
        """Reset session to beginning."""
        if self.current_session:
            self.current_session.current_index = 0
            self.current_session.cards_studied = 0
            self.current_session.correct_count = 0
            self.current_session.incorrect_count = 0
            self.current_session.started_at = datetime.now()

            # Reset card states
            for card in self.current_session.cards:
                card.times_shown = 0
                card.times_correct = 0
                card.times_incorrect = 0
                card.last_response = None

            if self.current_session.shuffle:
                random.shuffle(self.current_session.cards)

    def get_due_cards(
        self,
        cards: List[Dict[str, Any]],
        include_new: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get cards that are due for review.

        Args:
            cards: List of all cards
            include_new: Include cards never studied

        Returns:
            List of due cards
        """
        now = datetime.now()
        due = []

        for card in cards:
            next_review = card.get('next_review')
            is_new = card.get('times_seen', 0) == 0

            if is_new and include_new:
                due.append(card)
            elif next_review and next_review <= now:
                due.append(card)

        # Sort by urgency (most overdue first)
        due.sort(key=lambda c: c.get('next_review') or datetime.min)

        return due
