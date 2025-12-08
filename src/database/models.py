"""SQLAlchemy models for FlashForge database."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Table, Index, event
)
from sqlalchemy.orm import (
    declarative_base, relationship, Mapped, mapped_column, Session
)
from sqlalchemy.sql import func

Base = declarative_base()


# Association table for many-to-many relationship between Deck and Tag
deck_tags = Table(
    'deck_tags',
    Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Deck(Base):
    """
    Deck model - collection of flashcards.
    No limits on description size.
    """
    __tablename__ = 'decks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # No limit!
    color: Mapped[str] = mapped_column(String(7), default='#6366f1')
    icon: Mapped[str] = mapped_column(String(10), default='📚')

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    last_studied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    cards: Mapped[List["Card"]] = relationship(
        "Card",
        back_populates="deck",
        cascade="all, delete-orphan",
        order_by="Card.position"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=deck_tags,
        back_populates="decks"
    )
    study_sessions: Mapped[List["StudySession"]] = relationship(
        "StudySession",
        back_populates="deck",
        cascade="all, delete-orphan"
    )

    @property
    def card_count(self) -> int:
        """Get number of cards in deck."""
        return len(self.cards)

    @property
    def mastered_count(self) -> int:
        """Get number of mastered cards (interval >= 21 days)."""
        return sum(1 for card in self.cards if card.interval >= 21)

    @property
    def progress_percentage(self) -> float:
        """Get learning progress as percentage."""
        if not self.cards:
            return 0.0
        return (self.mastered_count / len(self.cards)) * 100

    @property
    def due_count(self) -> int:
        """Get number of cards due for review."""
        now = datetime.now()
        return sum(
            1 for card in self.cards
            if card.next_review and card.next_review <= now and not card.is_suspended
        )

    def __repr__(self) -> str:
        return f"<Deck(id={self.id}, name='{self.name}', cards={self.card_count})>"


class Card(Base):
    """
    Flashcard model.
    IMPORTANT: No limits on term, definition, or any text fields!
    """
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('decks.id', ondelete='CASCADE'), nullable=False
    )

    # Main content - NO LIMITS!
    term: Mapped[str] = mapped_column(Text, nullable=False)  # TEXT = unlimited
    definition: Mapped[str] = mapped_column(Text, nullable=False)  # TEXT = unlimited

    # Additional content - NO LIMITS!
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Media
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # SM-2 Algorithm fields
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)  # days
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Statistics
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    times_incorrect: Mapped[int] = mapped_column(Integer, default=0)
    times_seen: Mapped[int] = mapped_column(Integer, default=0)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Organization
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")

    @property
    def accuracy(self) -> float:
        """Get accuracy percentage."""
        total = self.times_correct + self.times_incorrect
        if total == 0:
            return 0.0
        return (self.times_correct / total) * 100

    @property
    def is_due(self) -> bool:
        """Check if card is due for review."""
        if self.is_suspended:
            return False
        if not self.next_review:
            return True
        return self.next_review <= datetime.now()

    @property
    def is_new(self) -> bool:
        """Check if card has never been studied."""
        return self.times_seen == 0

    @property
    def is_learning(self) -> bool:
        """Check if card is in learning phase."""
        return 0 < self.interval < 21

    @property
    def is_mastered(self) -> bool:
        """Check if card is mastered."""
        return self.interval >= 21

    def record_answer(self, correct: bool) -> None:
        """Record an answer attempt."""
        self.times_seen += 1
        self.last_seen_at = datetime.now()
        if correct:
            self.times_correct += 1
        else:
            self.times_incorrect += 1

    def __repr__(self) -> str:
        term_preview = self.term[:30] + "..." if len(self.term) > 30 else self.term
        return f"<Card(id={self.id}, term='{term_preview}')>"


# Index for faster queries
Index('idx_cards_deck_id', Card.deck_id)
Index('idx_cards_next_review', Card.next_review)
Index('idx_cards_is_starred', Card.is_starred)
Index('idx_decks_is_favorite', Deck.is_favorite)
Index('idx_decks_is_archived', Deck.is_archived)


class Tag(Base):
    """Tag model for organizing decks."""
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default='#6366f1')

    # Relationships
    decks: Mapped[List["Deck"]] = relationship(
        "Deck",
        secondary=deck_tags,
        back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"


class StudySession(Base):
    """Study session model for tracking learning history."""
    __tablename__ = 'study_sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('decks.id', ondelete='CASCADE'), nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    mode: Mapped[str] = mapped_column(String(50), nullable=False)  # flashcards/learn/test/match/write
    cards_studied: Mapped[int] = mapped_column(Integer, default=0)
    cards_correct: Mapped[int] = mapped_column(Integer, default=0)
    cards_incorrect: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def duration_seconds(self) -> int:
        """Get session duration in seconds."""
        if not self.ended_at:
            return int((datetime.now() - self.started_at).total_seconds())
        return int((self.ended_at - self.started_at).total_seconds())

    @property
    def accuracy(self) -> float:
        """Get session accuracy percentage."""
        total = self.cards_correct + self.cards_incorrect
        if total == 0:
            return 0.0
        return (self.cards_correct / total) * 100

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="study_sessions")

    def __repr__(self) -> str:
        return f"<StudySession(id={self.id}, mode='{self.mode}', cards={self.cards_studied})>"


Index('idx_study_sessions_deck_id', StudySession.deck_id)
Index('idx_study_sessions_started_at', StudySession.started_at)


class AppSettings(Base):
    """Application settings stored in database."""
    __tablename__ = 'app_settings'

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serialized

    def __repr__(self) -> str:
        return f"<AppSettings(key='{self.key}')>"


class DailyStats(Base):
    """Daily statistics for tracking progress."""
    __tablename__ = 'daily_stats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, unique=True, nullable=False)

    cards_studied: Mapped[int] = mapped_column(Integer, default=0)
    cards_correct: Mapped[int] = mapped_column(Integer, default=0)
    cards_incorrect: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def accuracy(self) -> float:
        """Get daily accuracy percentage."""
        total = self.cards_correct + self.cards_incorrect
        if total == 0:
            return 0.0
        return (self.cards_correct / total) * 100

    def __repr__(self) -> str:
        return f"<DailyStats(date={self.date.date()}, cards={self.cards_studied})>"


Index('idx_daily_stats_date', DailyStats.date)


# Event listeners for auto-updating timestamps
@event.listens_for(Card, 'before_insert')
def set_card_position(mapper, connection, target):
    """Set card position to end of deck when inserting."""
    if target.position == 0:
        # This will be updated by the database manager
        pass


@event.listens_for(Deck, 'before_update')
def update_deck_timestamp(mapper, connection, target):
    """Update deck timestamp when modified."""
    target.updated_at = datetime.now()


@event.listens_for(Card, 'before_update')
def update_card_timestamp(mapper, connection, target):
    """Update card timestamp when modified."""
    target.updated_at = datetime.now()
