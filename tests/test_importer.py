"""Tests for the card importer."""

import pytest
import tempfile
import json
from pathlib import Path

from src.core.importer import CardImporter, import_cards


class TestCardImporter:
    """Test cases for CardImporter."""

    def test_basic_tab_separated(self):
        """Test importing tab-separated cards."""
        content = "Hello\tПривет\nWorld\tМир\nGoodbye\tПока"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n')
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 3
            assert result.cards[0]['term'] == 'Hello'
            assert result.cards[0]['definition'] == 'Привет'
        finally:
            Path(temp_path).unlink()

    def test_semicolon_separator(self):
        """Test importing with semicolon separator."""
        content = "Hello;Привет\nWorld;Мир"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator=';', card_separator='\n')
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 2
        finally:
            Path(temp_path).unlink()

    def test_custom_multi_char_separator(self):
        """Test importing with multi-character separator like '::'."""
        content = "Hello::Привет\nWorld::Мир"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='::', card_separator='\n')
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 2
            assert result.cards[0]['term'] == 'Hello'
            assert result.cards[0]['definition'] == 'Привет'
        finally:
            Path(temp_path).unlink()

    def test_skip_header(self):
        """Test skipping header row."""
        content = "Term\tDefinition\nHello\tПривет\nWorld\tМир"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n', skip_header=True)
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 2
            assert result.cards[0]['term'] == 'Hello'  # Not "Term"
        finally:
            Path(temp_path).unlink()

    def test_skip_empty_lines(self):
        """Test skipping empty lines."""
        content = "Hello\tПривет\n\nWorld\tМир\n\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n', skip_empty=True)
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 2
        finally:
            Path(temp_path).unlink()

    def test_strip_whitespace(self):
        """Test stripping whitespace."""
        content = "  Hello  \t  Привет  \n  World  \t  Мир  "

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n', strip_whitespace=True)
            result = importer.import_file(temp_path)

            assert result.success
            assert result.cards[0]['term'] == 'Hello'
            assert result.cards[0]['definition'] == 'Привет'
        finally:
            Path(temp_path).unlink()

    def test_json_import(self):
        """Test importing from JSON."""
        data = {
            "name": "Test Deck",
            "cards": [
                {"term": "Hello", "definition": "Привет"},
                {"term": "World", "definition": "Мир"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            importer = CardImporter()
            result = importer.import_file(temp_path)

            assert result.success
            assert result.imported_count == 2
        finally:
            Path(temp_path).unlink()

    def test_preview(self):
        """Test preview functionality."""
        content = "A\t1\nB\t2\nC\t3\nD\t4\nE\t5\nF\t6"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n')
            preview = importer.preview(temp_path, limit=3)

            assert len(preview.cards) == 3
            assert preview.total_count == 6
            assert preview.cards[0]['term'] == 'A'
        finally:
            Path(temp_path).unlink()

    def test_format_detection(self):
        """Test automatic format detection."""
        # Tab-separated
        tab_content = "Hello\tПривет\nWorld\tМир"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(tab_content)
            temp_path = f.name

        try:
            importer = CardImporter()
            detected = importer.detect_format(temp_path)

            assert detected['term_separator'] == '\t'
            assert detected['confidence'] > 0.5
        finally:
            Path(temp_path).unlink()

    def test_import_with_hints(self):
        """Test importing cards with hints."""
        content = "Hello\tПривет\tGreeting\nWorld\tМир\tPlanet"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n', import_hints=True)
            result = importer.import_file(temp_path)

            assert result.success
            assert result.cards[0]['hint'] == 'Greeting'
        finally:
            Path(temp_path).unlink()

    def test_long_text_no_limit(self):
        """Test that there's no limit on text length."""
        # Create a very long term and definition
        long_term = "A" * 10000
        long_definition = "B" * 10000

        content = f"{long_term}\t{long_definition}"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n')
            result = importer.import_file(temp_path)

            assert result.success
            assert len(result.cards[0]['term']) == 10000
            assert len(result.cards[0]['definition']) == 10000
        finally:
            Path(temp_path).unlink()

    def test_import_from_text(self):
        """Test importing from text string."""
        text = "Hello\tПривет\nWorld\tМир"

        importer = CardImporter(term_separator='\t', card_separator='\n')
        result = importer.import_from_text(text)

        assert result.success
        assert result.imported_count == 2

    def test_validation_errors(self):
        """Test validation catches errors."""
        content = "Hello\t\n\tМир\nWorld\tМир"  # First has empty definition, second has empty term

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter(term_separator='\t', card_separator='\n')
            result = importer.import_file(temp_path)

            # Should import valid cards and report errors
            assert result.imported_count == 1
            assert len(result.errors) == 2
        finally:
            Path(temp_path).unlink()

    def test_preset_quizlet(self):
        """Test Quizlet preset."""
        importer = CardImporter.from_preset('quizlet')

        assert importer.term_separator == '\t'
        assert importer.card_separator == '\n'

    def test_encoding_detection(self):
        """Test encoding detection for non-UTF8 files."""
        # This is a simplified test - full test would need actual encoded files
        content = "Hello\tПривет"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            importer = CardImporter()
            detected = importer.detect_format(temp_path)

            assert 'encoding' in detected
        finally:
            Path(temp_path).unlink()


class TestImportConvenienceFunction:
    """Test the import_cards convenience function."""

    def test_basic_import(self):
        """Test basic import using convenience function."""
        content = "Hello\tПривет\nWorld\tМир"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            result = import_cards(temp_path, term_separator='\t', card_separator='\n')

            assert result.success
            assert result.imported_count == 2
        finally:
            Path(temp_path).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
