"""Tests for the study engine."""

import pytest
from datetime import datetime, timedelta

from src.core.study_engine import (
    StudyEngine,
    StudyMode,
    SM2Algorithm,
    LeitnerSystem,
    ResponseQuality,
    CardState,
    StudySessionState
)


class TestSM2Algorithm:
    """Test cases for SM-2 algorithm."""

    def test_perfect_response(self):
        """Test perfect response increases interval."""
        ease, interval, reps, next_review = SM2Algorithm.calculate_next_review(
            ease_factor=2.5,
            interval=1,
            repetitions=1,
            quality=5
        )

        assert ease >= 2.5  # Should increase or stay same
        assert interval > 1
        assert reps == 2
        assert next_review > datetime.now()

    def test_failed_response(self):
        """Test failed response resets interval."""
        ease, interval, reps, next_review = SM2Algorithm.calculate_next_review(
            ease_factor=2.5,
            interval=10,
            repetitions=5,
            quality=1
        )

        assert interval == 1  # Reset to 1
        assert reps == 0  # Reset repetitions
        assert ease < 2.5  # Decreased ease

    def test_ease_factor_bounds(self):
        """Test ease factor stays within bounds."""
        # Test minimum bound after many failures
        ease = 2.5
        for _ in range(20):
            ease, _, _, _ = SM2Algorithm.calculate_next_review(ease, 1, 0, 0)

        assert ease >= 1.3  # Minimum ease factor

    def test_first_review(self):
        """Test first review scheduling."""
        ease, interval, reps, _ = SM2Algorithm.calculate_next_review(
            ease_factor=2.5,
            interval=0,
            repetitions=0,
            quality=4
        )

        assert interval == 1
        assert reps == 1

    def test_second_review(self):
        """Test second review scheduling."""
        ease, interval, reps, _ = SM2Algorithm.calculate_next_review(
            ease_factor=2.5,
            interval=1,
            repetitions=1,
            quality=4
        )

        assert interval == 6
        assert reps == 2

    def test_quality_to_binary(self):
        """Test quality conversion from binary."""
        assert SM2Algorithm.quality_from_binary(True) == 5
        assert SM2Algorithm.quality_from_binary(True, hesitation=True) == 4
        assert SM2Algorithm.quality_from_binary(False) == 1


class TestLeitnerSystem:
    """Test cases for Leitner box system."""

    def test_correct_answer_promotion(self):
        """Test correct answer moves card up a box."""
        leitner = LeitnerSystem()

        next_box = leitner.get_next_box(1, correct=True)
        assert next_box == 2

        next_box = leitner.get_next_box(3, correct=True)
        assert next_box == 4

    def test_incorrect_answer_demotion(self):
        """Test incorrect answer moves card to box 1."""
        leitner = LeitnerSystem()

        next_box = leitner.get_next_box(5, correct=False)
        assert next_box == 1

        next_box = leitner.get_next_box(3, correct=False)
        assert next_box == 1

    def test_max_box_limit(self):
        """Test card stays in max box on correct."""
        leitner = LeitnerSystem(num_boxes=5)

        next_box = leitner.get_next_box(5, correct=True)
        assert next_box == 5

    def test_intervals(self):
        """Test box intervals."""
        leitner = LeitnerSystem()

        assert leitner.get_interval(1) == 1
        assert leitner.get_interval(2) == 2
        assert leitner.get_interval(3) == 4


class TestStudyEngine:
    """Test cases for the study engine."""

    @pytest.fixture
    def sample_cards(self):
        """Create sample card data."""
        return [
            {
                'id': 1,
                'term': 'Hello',
                'definition': 'Привет',
                'hint': 'Greeting',
                'ease_factor': 2.5,
                'interval': 0,
                'repetitions': 0
            },
            {
                'id': 2,
                'term': 'World',
                'definition': 'Мир',
                'ease_factor': 2.5,
                'interval': 0,
                'repetitions': 0
            },
            {
                'id': 3,
                'term': 'Goodbye',
                'definition': 'Пока',
                'ease_factor': 2.5,
                'interval': 0,
                'repetitions': 0
            }
        ]

    def test_start_session(self, sample_cards):
        """Test starting a study session."""
        engine = StudyEngine()
        session = engine.start_session(
            deck_id=1,
            cards=sample_cards,
            mode=StudyMode.FLASHCARDS
        )

        assert session is not None
        assert len(session.cards) == 3
        assert session.deck_id == 1
        assert session.mode == StudyMode.FLASHCARDS

    def test_get_current_card(self, sample_cards):
        """Test getting current card."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        card = engine.get_current_card()
        assert card is not None
        assert card.term == 'Hello'

    def test_record_correct_response(self, sample_cards):
        """Test recording a correct response."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        card, update = engine.record_response(correct=True)

        assert card.times_correct == 1
        assert card.times_shown == 1
        assert engine.current_session.correct_count == 1

    def test_record_incorrect_response(self, sample_cards):
        """Test recording an incorrect response."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        card, update = engine.record_response(correct=False)

        assert card.times_incorrect == 1
        assert engine.current_session.incorrect_count == 1

    def test_next_card(self, sample_cards):
        """Test moving to next card."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        engine.record_response(correct=True)
        next_card = engine.next_card()

        assert next_card is not None
        assert next_card.term == 'World'
        assert engine.current_session.current_index == 1

    def test_session_complete(self, sample_cards):
        """Test session completion detection."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        for _ in range(3):
            engine.record_response(correct=True)
            engine.next_card()

        assert engine.current_session.is_complete

    def test_session_summary(self, sample_cards):
        """Test session summary generation."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        engine.record_response(correct=True)
        engine.next_card()
        engine.record_response(correct=False)
        engine.next_card()

        summary = engine.get_session_summary()

        assert summary['cards_studied'] == 2
        assert summary['correct'] == 1
        assert summary['incorrect'] == 1
        assert summary['accuracy'] == 50.0

    def test_toggle_star(self, sample_cards):
        """Test toggling star on current card."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        result = engine.toggle_star()
        assert result == True  # Now starred

        result = engine.toggle_star()
        assert result == False  # Now unstarred

    def test_skip_card(self, sample_cards):
        """Test skipping a card."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        first_card = engine.get_current_card()
        engine.skip_card()

        new_current = engine.get_current_card()
        assert new_current.term != first_card.term

    def test_session_with_limit(self, sample_cards):
        """Test session with card limit."""
        engine = StudyEngine()
        session = engine.start_session(
            deck_id=1,
            cards=sample_cards,
            limit=2
        )

        assert len(session.cards) == 2

    def test_starred_only_filter(self, sample_cards):
        """Test filtering starred cards only."""
        sample_cards[0]['is_starred'] = True

        engine = StudyEngine()
        session = engine.start_session(
            deck_id=1,
            cards=sample_cards,
            starred_only=True
        )

        assert len(session.cards) == 1
        assert session.cards[0].is_starred

    def test_reset_session(self, sample_cards):
        """Test resetting a session."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        engine.record_response(correct=True)
        engine.next_card()

        engine.reset_session()

        assert engine.current_session.current_index == 0
        assert engine.current_session.cards_studied == 0
        assert engine.current_session.correct_count == 0

    def test_end_session(self, sample_cards):
        """Test ending a session."""
        engine = StudyEngine()
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        engine.record_response(correct=True)
        summary = engine.end_session()

        assert summary['cards_studied'] == 1
        assert engine.current_session is None

    def test_due_cards(self, sample_cards):
        """Test getting due cards."""
        # Set up cards with different review dates
        sample_cards[0]['next_review'] = datetime.now() - timedelta(days=1)  # Overdue
        sample_cards[1]['next_review'] = datetime.now() + timedelta(days=1)  # Future
        sample_cards[2]['times_seen'] = 0  # New card

        engine = StudyEngine()
        due = engine.get_due_cards(sample_cards, include_new=True)

        assert len(due) == 2  # Overdue + New

    def test_leitner_algorithm(self, sample_cards):
        """Test using Leitner algorithm."""
        engine = StudyEngine(algorithm='leitner')
        engine.start_session(deck_id=1, cards=sample_cards, shuffle=False)

        card, update = engine.record_response(correct=True)

        assert 'interval' in update
        assert update['interval'] >= 1


class TestCardState:
    """Test cases for CardState dataclass."""

    def test_card_state_defaults(self):
        """Test CardState default values."""
        state = CardState(
            card_id=1,
            term='Hello',
            definition='Привет'
        )

        assert state.ease_factor == 2.5
        assert state.interval == 0
        assert state.times_shown == 0
        assert not state.is_starred


class TestStudySessionState:
    """Test cases for StudySessionState dataclass."""

    def test_progress_calculation(self):
        """Test progress percentage calculation."""
        cards = [
            CardState(card_id=i, term=f'Term{i}', definition=f'Def{i}')
            for i in range(10)
        ]

        session = StudySessionState(
            deck_id=1,
            mode=StudyMode.FLASHCARDS,
            cards=cards,
            current_index=5
        )

        assert session.progress_percent == 50.0

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        session = StudySessionState(
            deck_id=1,
            mode=StudyMode.FLASHCARDS,
            cards=[],
            correct_count=7,
            incorrect_count=3
        )

        assert session.accuracy == 70.0

    def test_remaining_count(self):
        """Test remaining cards count."""
        cards = [
            CardState(card_id=i, term=f'Term{i}', definition=f'Def{i}')
            for i in range(10)
        ]

        session = StudySessionState(
            deck_id=1,
            mode=StudyMode.FLASHCARDS,
            cards=cards,
            current_index=3
        )

        assert session.remaining == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
