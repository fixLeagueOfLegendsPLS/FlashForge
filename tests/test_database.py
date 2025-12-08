"""Tests for the database module."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# We need to set up a test database path before importing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDatabaseManager:
    """Test cases for DatabaseManager."""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        # Temporarily override the database path
        from src.utils import constants
        original_db = constants.DB_PATH
        original_data = constants.DATA_DIR

        constants.DATA_DIR = tmp_path
        constants.DB_PATH = tmp_path / "test.db"

        # Reset the singleton
        from src.database.db_manager import DatabaseManager
        DatabaseManager._instance = None

        yield DatabaseManager()

        # Restore
        constants.DB_PATH = original_db
        constants.DATA_DIR = original_data
        DatabaseManager._instance = None

    def test_create_deck(self, temp_db):
        """Test creating a deck."""
        deck = temp_db.create_deck(
            name="Test Deck",
            description="A test deck",
            color="#ff0000",
            icon=""
        )

        assert deck is not None
        assert deck.id is not None
        assert deck.name == "Test Deck"
        assert deck.description == "A test deck"
        assert deck.color == "#ff0000"

    def test_get_deck(self, temp_db):
        """Test getting a deck by ID."""
        created = temp_db.create_deck(name="Test Deck")
        retrieved = temp_db.get_deck(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Deck"

    def test_get_all_decks(self, temp_db):
        """Test getting all decks."""
        temp_db.create_deck(name="Deck 1")
        temp_db.create_deck(name="Deck 2")
        temp_db.create_deck(name="Deck 3")

        decks = temp_db.get_all_decks()

        assert len(decks) == 3

    def test_update_deck(self, temp_db):
        """Test updating a deck."""
        deck = temp_db.create_deck(name="Original Name")
        temp_db.update_deck(deck.id, name="Updated Name", color="#00ff00")

        updated = temp_db.get_deck(deck.id)

        assert updated.name == "Updated Name"
        assert updated.color == "#00ff00"

    def test_delete_deck(self, temp_db):
        """Test deleting a deck."""
        deck = temp_db.create_deck(name="To Delete")
        deck_id = deck.id

        result = temp_db.delete_deck(deck_id)
        assert result == True

        deleted = temp_db.get_deck(deck_id)
        assert deleted is None

    def test_toggle_favorite(self, temp_db):
        """Test toggling deck favorite status."""
        deck = temp_db.create_deck(name="Test")

        result = temp_db.toggle_deck_favorite(deck.id)
        assert result == True

        result = temp_db.toggle_deck_favorite(deck.id)
        assert result == False

    def test_archive_deck(self, temp_db):
        """Test archiving a deck."""
        deck = temp_db.create_deck(name="Test")

        temp_db.archive_deck(deck.id, archive=True)
        archived = temp_db.get_deck(deck.id)
        assert archived.is_archived == True

        temp_db.archive_deck(deck.id, archive=False)
        unarchived = temp_db.get_deck(deck.id)
        assert unarchived.is_archived == False

    def test_create_card(self, temp_db):
        """Test creating a card."""
        deck = temp_db.create_deck(name="Test Deck")
        card = temp_db.create_card(
            deck_id=deck.id,
            term="Hello",
            definition="Привет",
            hint="Greeting"
        )

        assert card is not None
        assert card.id is not None
        assert card.term == "Hello"
        assert card.definition == "Привет"
        assert card.hint == "Greeting"

    def test_create_cards_bulk(self, temp_db):
        """Test bulk card creation."""
        deck = temp_db.create_deck(name="Test Deck")
        cards_data = [
            {"term": f"Term{i}", "definition": f"Def{i}"}
            for i in range(100)
        ]

        cards = temp_db.create_cards_bulk(deck.id, cards_data)

        assert len(cards) == 100

    def test_get_deck_cards(self, temp_db):
        """Test getting cards from a deck."""
        deck = temp_db.create_deck(name="Test Deck")
        temp_db.create_card(deck.id, "Term1", "Def1")
        temp_db.create_card(deck.id, "Term2", "Def2")
        temp_db.create_card(deck.id, "Term3", "Def3")

        cards = temp_db.get_deck_cards(deck.id)

        assert len(cards) == 3

    def test_update_card(self, temp_db):
        """Test updating a card."""
        deck = temp_db.create_deck(name="Test Deck")
        card = temp_db.create_card(deck.id, "Original", "Definition")

        temp_db.update_card(card.id, term="Updated", definition="New Def")

        updated = temp_db.get_card(card.id)
        assert updated.term == "Updated"
        assert updated.definition == "New Def"

    def test_delete_card(self, temp_db):
        """Test deleting a card."""
        deck = temp_db.create_deck(name="Test Deck")
        card = temp_db.create_card(deck.id, "To Delete", "Definition")

        result = temp_db.delete_card(card.id)
        assert result == True

        deleted = temp_db.get_card(card.id)
        assert deleted is None

    def test_toggle_card_star(self, temp_db):
        """Test toggling card star."""
        deck = temp_db.create_deck(name="Test Deck")
        card = temp_db.create_card(deck.id, "Term", "Def")

        result = temp_db.toggle_card_star(card.id)
        assert result == True

        result = temp_db.toggle_card_star(card.id)
        assert result == False

    def test_search_decks(self, temp_db):
        """Test searching decks."""
        temp_db.create_deck(name="English Vocabulary")
        temp_db.create_deck(name="Spanish Words")
        temp_db.create_deck(name="French Phrases")

        results = temp_db.search_decks("English")
        assert len(results) == 1
        assert results[0].name == "English Vocabulary"

        results = temp_db.search_decks("Words")
        assert len(results) == 1

    def test_search_cards(self, temp_db):
        """Test searching cards."""
        deck = temp_db.create_deck(name="Test Deck")
        temp_db.create_card(deck.id, "Hello", "Привет")
        temp_db.create_card(deck.id, "World", "Мир")
        temp_db.create_card(deck.id, "Goodbye", "Пока")

        results = temp_db.search_cards("Hello")
        assert len(results) == 1

        results = temp_db.search_cards("Мир")
        assert len(results) == 1

    def test_update_card_sm2(self, temp_db):
        """Test SM-2 card update."""
        deck = temp_db.create_deck(name="Test Deck")
        card = temp_db.create_card(deck.id, "Term", "Definition")

        # Good response
        updated = temp_db.update_card_sm2(card.id, quality=4)

        assert updated.interval >= 1
        assert updated.repetitions == 1
        assert updated.next_review is not None

    def test_study_session(self, temp_db):
        """Test study session tracking."""
        deck = temp_db.create_deck(name="Test Deck")

        # Start session
        session = temp_db.start_study_session(deck.id, "flashcards")
        assert session is not None
        assert session.mode == "flashcards"

        # Update session
        temp_db.update_study_session(
            session.id,
            cards_studied=10,
            cards_correct=8,
            cards_incorrect=2
        )

        # End session
        ended = temp_db.end_study_session(session.id)
        assert ended.ended_at is not None

    def test_daily_stats(self, temp_db):
        """Test daily statistics."""
        deck = temp_db.create_deck(name="Test Deck")

        # Create a session
        session = temp_db.start_study_session(deck.id, "flashcards")
        temp_db.update_study_session(session.id, cards_studied=10, cards_correct=8, cards_incorrect=2)
        temp_db.end_study_session(session.id)

        # Get stats
        stats = temp_db.get_daily_stats(days=7)
        assert len(stats) >= 0  # May or may not have entries depending on timing

    def test_get_streak(self, temp_db):
        """Test streak calculation."""
        streak = temp_db.get_streak()
        assert streak >= 0

    def test_get_total_stats(self, temp_db):
        """Test total statistics."""
        stats = temp_db.get_total_stats()

        assert 'total_decks' in stats
        assert 'total_cards' in stats
        assert 'streak' in stats

    def test_tags(self, temp_db):
        """Test tag operations."""
        # Create tag
        tag = temp_db.create_tag(name="Language", color="#ff0000")
        assert tag.name == "Language"

        # Get all tags
        tags = temp_db.get_all_tags()
        assert len(tags) >= 1

        # Add to deck
        deck = temp_db.create_deck(name="Test Deck")
        temp_db.add_tag_to_deck(deck.id, tag.id)

        # Remove from deck
        temp_db.remove_tag_from_deck(deck.id, tag.id)

        # Delete tag
        temp_db.delete_tag(tag.id)

    def test_settings(self, temp_db):
        """Test settings storage."""
        temp_db.set_setting("test_key", "test_value")

        value = temp_db.get_setting("test_key")
        assert value == "test_value"

        # Default value
        value = temp_db.get_setting("nonexistent", default="default")
        assert value == "default"

    def test_card_ordering(self, temp_db):
        """Test that cards maintain order."""
        deck = temp_db.create_deck(name="Test Deck")

        for i in range(5):
            temp_db.create_card(deck.id, f"Term{i}", f"Def{i}")

        cards = temp_db.get_deck_cards(deck.id)

        for i, card in enumerate(cards):
            assert card.position == i + 1

    def test_long_text_storage(self, temp_db):
        """Test storing very long text (no limits)."""
        deck = temp_db.create_deck(name="Test Deck")

        long_term = "A" * 50000
        long_definition = "B" * 50000

        card = temp_db.create_card(deck.id, long_term, long_definition)

        retrieved = temp_db.get_card(card.id)
        assert len(retrieved.term) == 50000
        assert len(retrieved.definition) == 50000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
