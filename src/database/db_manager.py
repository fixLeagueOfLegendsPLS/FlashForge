"""Database manager with CRUD operations for FlashForge."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, func, or_, and_, desc
from sqlalchemy.orm import sessionmaker, Session, joinedload

from .models import Base, Deck, Card, Tag, StudySession, DailyStats, AppSettings
from .migrations import MigrationManager
from ..utils.constants import DB_PATH, DATA_DIR


class DatabaseManager:
    """
    Centralized database manager for all CRUD operations.
    Thread-safe with session management.
    """

    _instance: Optional['DatabaseManager'] = None

    def __new__(cls) -> 'DatabaseManager':
        """Singleton pattern for database manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._setup_database()

    def _setup_database(self) -> None:
        """Initialize database connection and run migrations."""
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Create engine with WAL mode for better performance
        self.engine = create_engine(
            f"sqlite:///{DB_PATH}",
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            }
        )

        # Enable WAL mode
        with self.engine.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            conn.execute("PRAGMA foreign_keys=ON")

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Run migrations
        migration_manager = MigrationManager(self.engine)
        migration_manager.migrate()

    @contextmanager
    def session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ==================== DECK OPERATIONS ====================

    def create_deck(
        self,
        name: str,
        description: str = "",
        color: str = "#6366f1",
        icon: str = "📚"
    ) -> Deck:
        """Create a new deck."""
        with self.session() as session:
            deck = Deck(
                name=name,
                description=description,
                color=color,
                icon=icon
            )
            session.add(deck)
            session.flush()
            return deck

    def get_deck(self, deck_id: int) -> Optional[Deck]:
        """Get a deck by ID with cards loaded."""
        with self.session() as session:
            deck = session.query(Deck).options(
                joinedload(Deck.cards),
                joinedload(Deck.tags)
            ).filter(Deck.id == deck_id).first()
            return deck

    def get_all_decks(
        self,
        include_archived: bool = False,
        favorites_only: bool = False
    ) -> List[Deck]:
        """Get all decks with optional filters."""
        with self.session() as session:
            query = session.query(Deck).options(joinedload(Deck.cards))

            if not include_archived:
                query = query.filter(Deck.is_archived == False)

            if favorites_only:
                query = query.filter(Deck.is_favorite == True)

            return query.order_by(desc(Deck.updated_at)).all()

    def update_deck(
        self,
        deck_id: int,
        **kwargs
    ) -> Optional[Deck]:
        """Update deck fields."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                for key, value in kwargs.items():
                    if hasattr(deck, key):
                        setattr(deck, key, value)
                deck.updated_at = datetime.now()
            return deck

    def delete_deck(self, deck_id: int) -> bool:
        """Delete a deck and all its cards."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                session.delete(deck)
                return True
            return False

    def toggle_deck_favorite(self, deck_id: int) -> bool:
        """Toggle deck favorite status. Returns new status."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                deck.is_favorite = not deck.is_favorite
                return deck.is_favorite
            return False

    def archive_deck(self, deck_id: int, archive: bool = True) -> bool:
        """Archive or unarchive a deck."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                deck.is_archived = archive
                return True
            return False

    def search_decks(self, query: str) -> List[Deck]:
        """Search decks by name or description."""
        with self.session() as session:
            search_term = f"%{query}%"
            return session.query(Deck).options(joinedload(Deck.cards)).filter(
                or_(
                    Deck.name.ilike(search_term),
                    Deck.description.ilike(search_term)
                )
            ).all()

    # ==================== CARD OPERATIONS ====================

    def create_card(
        self,
        deck_id: int,
        term: str,
        definition: str,
        hint: str = None,
        example: str = None,
        notes: str = None,
        image_path: str = None,
        audio_path: str = None
    ) -> Card:
        """Create a new card in a deck."""
        with self.session() as session:
            # Get max position
            max_pos = session.query(func.max(Card.position)).filter(
                Card.deck_id == deck_id
            ).scalar() or 0

            card = Card(
                deck_id=deck_id,
                term=term,
                definition=definition,
                hint=hint,
                example=example,
                notes=notes,
                image_path=image_path,
                audio_path=audio_path,
                position=max_pos + 1
            )
            session.add(card)
            session.flush()

            # Update deck timestamp
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                deck.updated_at = datetime.now()

            return card

    def create_cards_bulk(
        self,
        deck_id: int,
        cards_data: List[Dict[str, Any]]
    ) -> List[Card]:
        """Create multiple cards at once (efficient for import)."""
        with self.session() as session:
            # Get max position
            max_pos = session.query(func.max(Card.position)).filter(
                Card.deck_id == deck_id
            ).scalar() or 0

            cards = []
            for i, data in enumerate(cards_data):
                card = Card(
                    deck_id=deck_id,
                    term=data.get('term', ''),
                    definition=data.get('definition', ''),
                    hint=data.get('hint'),
                    example=data.get('example'),
                    notes=data.get('notes'),
                    image_path=data.get('image_path'),
                    audio_path=data.get('audio_path'),
                    position=max_pos + i + 1
                )
                session.add(card)
                cards.append(card)

            session.flush()

            # Update deck timestamp
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                deck.updated_at = datetime.now()

            return cards

    def get_card(self, card_id: int) -> Optional[Card]:
        """Get a card by ID."""
        with self.session() as session:
            return session.query(Card).filter(Card.id == card_id).first()

    def get_deck_cards(
        self,
        deck_id: int,
        starred_only: bool = False,
        due_only: bool = False
    ) -> List[Card]:
        """Get all cards in a deck with optional filters."""
        with self.session() as session:
            query = session.query(Card).filter(
                Card.deck_id == deck_id,
                Card.is_suspended == False
            )

            if starred_only:
                query = query.filter(Card.is_starred == True)

            if due_only:
                now = datetime.now()
                query = query.filter(
                    or_(
                        Card.next_review == None,
                        Card.next_review <= now
                    )
                )

            return query.order_by(Card.position).all()

    def update_card(self, card_id: int, **kwargs) -> Optional[Card]:
        """Update card fields."""
        with self.session() as session:
            card = session.query(Card).filter(Card.id == card_id).first()
            if card:
                for key, value in kwargs.items():
                    if hasattr(card, key):
                        setattr(card, key, value)
                card.updated_at = datetime.now()
            return card

    def delete_card(self, card_id: int) -> bool:
        """Delete a card."""
        with self.session() as session:
            card = session.query(Card).filter(Card.id == card_id).first()
            if card:
                deck_id = card.deck_id
                session.delete(card)

                # Update deck timestamp
                deck = session.query(Deck).filter(Deck.id == deck_id).first()
                if deck:
                    deck.updated_at = datetime.now()

                return True
            return False

    def toggle_card_star(self, card_id: int) -> bool:
        """Toggle card starred status. Returns new status."""
        with self.session() as session:
            card = session.query(Card).filter(Card.id == card_id).first()
            if card:
                card.is_starred = not card.is_starred
                return card.is_starred
            return False

    def suspend_card(self, card_id: int, suspend: bool = True) -> bool:
        """Suspend or unsuspend a card."""
        with self.session() as session:
            card = session.query(Card).filter(Card.id == card_id).first()
            if card:
                card.is_suspended = suspend
                return True
            return False

    def reorder_cards(self, deck_id: int, card_ids: List[int]) -> None:
        """Reorder cards in a deck."""
        with self.session() as session:
            for position, card_id in enumerate(card_ids):
                session.query(Card).filter(Card.id == card_id).update(
                    {"position": position}
                )

    def search_cards(self, query: str, deck_id: int = None) -> List[Card]:
        """Search cards by term or definition."""
        with self.session() as session:
            search_term = f"%{query}%"
            base_query = session.query(Card).filter(
                or_(
                    Card.term.ilike(search_term),
                    Card.definition.ilike(search_term)
                )
            )

            if deck_id:
                base_query = base_query.filter(Card.deck_id == deck_id)

            return base_query.all()

    def update_card_sm2(
        self,
        card_id: int,
        quality: int  # 0-5
    ) -> Optional[Card]:
        """Update card using SM-2 algorithm."""
        from ..utils.helpers import calculate_next_review

        with self.session() as session:
            card = session.query(Card).filter(Card.id == card_id).first()
            if not card:
                return None

            # Record the answer
            card.times_seen += 1
            card.last_seen_at = datetime.now()

            if quality >= 3:
                card.times_correct += 1
                card.repetitions += 1
            else:
                card.times_incorrect += 1
                card.repetitions = 0

            # Calculate next review
            new_ease, new_interval, next_review = calculate_next_review(
                card.ease_factor,
                card.interval,
                quality
            )

            card.ease_factor = new_ease
            card.interval = new_interval
            card.next_review = next_review

            return card

    # ==================== TAG OPERATIONS ====================

    def create_tag(self, name: str, color: str = "#6366f1") -> Tag:
        """Create a new tag."""
        with self.session() as session:
            tag = Tag(name=name, color=color)
            session.add(tag)
            session.flush()
            return tag

    def get_all_tags(self) -> List[Tag]:
        """Get all tags."""
        with self.session() as session:
            return session.query(Tag).order_by(Tag.name).all()

    def add_tag_to_deck(self, deck_id: int, tag_id: int) -> bool:
        """Add a tag to a deck."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            tag = session.query(Tag).filter(Tag.id == tag_id).first()

            if deck and tag and tag not in deck.tags:
                deck.tags.append(tag)
                return True
            return False

    def remove_tag_from_deck(self, deck_id: int, tag_id: int) -> bool:
        """Remove a tag from a deck."""
        with self.session() as session:
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            tag = session.query(Tag).filter(Tag.id == tag_id).first()

            if deck and tag and tag in deck.tags:
                deck.tags.remove(tag)
                return True
            return False

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        with self.session() as session:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                session.delete(tag)
                return True
            return False

    # ==================== STUDY SESSION OPERATIONS ====================

    def start_study_session(self, deck_id: int, mode: str) -> StudySession:
        """Start a new study session."""
        with self.session() as session:
            study_session = StudySession(
                deck_id=deck_id,
                mode=mode
            )
            session.add(study_session)
            session.flush()

            # Update deck last studied
            deck = session.query(Deck).filter(Deck.id == deck_id).first()
            if deck:
                deck.last_studied_at = datetime.now()

            return study_session

    def update_study_session(
        self,
        session_id: int,
        cards_studied: int = None,
        cards_correct: int = None,
        cards_incorrect: int = None
    ) -> Optional[StudySession]:
        """Update study session statistics."""
        with self.session() as db_session:
            study_session = db_session.query(StudySession).filter(
                StudySession.id == session_id
            ).first()

            if study_session:
                if cards_studied is not None:
                    study_session.cards_studied = cards_studied
                if cards_correct is not None:
                    study_session.cards_correct = cards_correct
                if cards_incorrect is not None:
                    study_session.cards_incorrect = cards_incorrect

            return study_session

    def end_study_session(self, session_id: int) -> Optional[StudySession]:
        """End a study session."""
        with self.session() as db_session:
            study_session = db_session.query(StudySession).filter(
                StudySession.id == session_id
            ).first()

            if study_session:
                study_session.ended_at = datetime.now()

                # Update daily stats
                self._update_daily_stats(db_session, study_session)

            return study_session

    def _update_daily_stats(self, session: Session, study_session: StudySession) -> None:
        """Update daily statistics from a study session."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        daily_stat = session.query(DailyStats).filter(
            DailyStats.date == today
        ).first()

        if not daily_stat:
            daily_stat = DailyStats(date=today)
            session.add(daily_stat)

        daily_stat.cards_studied += study_session.cards_studied
        daily_stat.cards_correct += study_session.cards_correct
        daily_stat.cards_incorrect += study_session.cards_incorrect
        daily_stat.time_spent_seconds += study_session.duration_seconds
        daily_stat.sessions_count += 1

    def get_study_sessions(
        self,
        deck_id: int = None,
        days: int = 30
    ) -> List[StudySession]:
        """Get study sessions with optional filters."""
        with self.session() as session:
            query = session.query(StudySession)

            if deck_id:
                query = query.filter(StudySession.deck_id == deck_id)

            cutoff = datetime.now() - timedelta(days=days)
            query = query.filter(StudySession.started_at >= cutoff)

            return query.order_by(desc(StudySession.started_at)).all()

    # ==================== STATISTICS ====================

    def get_daily_stats(self, days: int = 30) -> List[DailyStats]:
        """Get daily statistics for the last N days."""
        with self.session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            return session.query(DailyStats).filter(
                DailyStats.date >= cutoff
            ).order_by(DailyStats.date).all()

    def get_streak(self) -> int:
        """Get current study streak in days."""
        with self.session() as session:
            stats = session.query(DailyStats).order_by(
                desc(DailyStats.date)
            ).all()

            if not stats:
                return 0

            streak = 0
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            for i, stat in enumerate(stats):
                expected_date = today - timedelta(days=i)
                stat_date = stat.date.replace(hour=0, minute=0, second=0, microsecond=0)

                if stat_date == expected_date and stat.cards_studied > 0:
                    streak += 1
                elif i == 0 and stat_date == today - timedelta(days=1):
                    # Allow yesterday if today not studied yet
                    expected_date = today - timedelta(days=1)
                    if stat_date == expected_date and stat.cards_studied > 0:
                        streak += 1
                else:
                    break

            return streak

    def get_total_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        with self.session() as session:
            total_decks = session.query(func.count(Deck.id)).scalar()
            total_cards = session.query(func.count(Card.id)).scalar()

            stats_sum = session.query(
                func.sum(DailyStats.cards_studied),
                func.sum(DailyStats.time_spent_seconds),
                func.sum(DailyStats.sessions_count)
            ).first()

            return {
                "total_decks": total_decks or 0,
                "total_cards": total_cards or 0,
                "total_cards_studied": stats_sum[0] or 0,
                "total_time_seconds": stats_sum[1] or 0,
                "total_sessions": stats_sum[2] or 0,
                "streak": self.get_streak()
            }

    def get_cards_due_count(self) -> int:
        """Get total number of cards due for review."""
        with self.session() as session:
            now = datetime.now()
            return session.query(func.count(Card.id)).filter(
                Card.is_suspended == False,
                or_(
                    Card.next_review == None,
                    Card.next_review <= now
                )
            ).scalar() or 0

    # ==================== SETTINGS ====================

    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get an application setting."""
        with self.session() as session:
            setting = session.query(AppSettings).filter(
                AppSettings.key == key
            ).first()
            return setting.value if setting else default

    def set_setting(self, key: str, value: str) -> None:
        """Set an application setting."""
        with self.session() as session:
            setting = session.query(AppSettings).filter(
                AppSettings.key == key
            ).first()

            if setting:
                setting.value = value
            else:
                setting = AppSettings(key=key, value=value)
                session.add(setting)
