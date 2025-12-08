"""
Universal card importer for FlashForge.
Supports multiple formats with customizable delimiters.
NO LIMITS on text size!
"""

import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

from ..utils.constants import (
    SEPARATOR_PRESETS,
    SUPPORTED_ENCODINGS,
    DEFAULT_TERM_SEPARATOR,
    DEFAULT_CARD_SEPARATOR
)
from ..utils.helpers import detect_encoding


@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool
    cards: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    total_lines: int
    imported_count: int
    skipped_count: int


@dataclass
class ImportPreview:
    """Preview of import before committing."""
    cards: List[Dict[str, Any]]
    total_count: int
    errors: List[str]
    warnings: List[str]


class CardImporter:
    """
    Universal card importer with support for any delimiters.

    Features:
    - NO LIMITS on text size
    - Customizable delimiters (single or multi-character)
    - Auto-detection of format
    - Preview before import
    - Validation with error reporting
    """

    PRESETS = SEPARATOR_PRESETS

    def __init__(
        self,
        term_separator: str = DEFAULT_TERM_SEPARATOR,
        card_separator: str = DEFAULT_CARD_SEPARATOR,
        encoding: str = 'utf-8',
        skip_header: bool = False,
        strip_whitespace: bool = True,
        skip_empty: bool = True,
        import_hints: bool = False,
        hint_separator: str = None
    ):
        """
        Initialize the importer.

        Args:
            term_separator: Separator between term and definition
            card_separator: Separator between cards
            encoding: File encoding
            skip_header: Skip first line as header
            strip_whitespace: Strip whitespace from values
            skip_empty: Skip empty cards
            import_hints: Try to import hints as third column
            hint_separator: Separator for hint (if different from term_separator)
        """
        self.term_separator = self._unescape(term_separator)
        self.card_separator = self._unescape(card_separator)
        self.encoding = encoding
        self.skip_header = skip_header
        self.strip_whitespace = strip_whitespace
        self.skip_empty = skip_empty
        self.import_hints = import_hints
        self.hint_separator = self._unescape(hint_separator) if hint_separator else self.term_separator

    @staticmethod
    def _unescape(text: str) -> str:
        """Convert escape sequences to actual characters."""
        if not text:
            return text
        return (text
                .replace('\\n', '\n')
                .replace('\\t', '\t')
                .replace('\\r', '\r'))

    @staticmethod
    def _escape(text: str) -> str:
        """Convert actual characters to escape sequences for display."""
        if not text:
            return text
        return (text
                .replace('\n', '\\n')
                .replace('\t', '\\t')
                .replace('\r', '\\r'))

    @classmethod
    def from_preset(cls, preset_name: str, **kwargs) -> 'CardImporter':
        """Create importer from a preset."""
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}")

        preset = cls.PRESETS[preset_name]
        return cls(
            term_separator=preset['term_sep'],
            card_separator=preset['card_sep'],
            **kwargs
        )

    def detect_format(self, file_path: str) -> Dict[str, Any]:
        """
        Auto-detect file format and separators.

        Returns dict with detected settings and confidence.
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        # Try to detect encoding
        detected_encoding = detect_encoding(path)

        # Read sample
        try:
            with open(path, 'r', encoding=detected_encoding) as f:
                sample = f.read(10000)  # Read first 10KB
        except Exception:
            return {
                'encoding': 'utf-8',
                'term_separator': '\t',
                'card_separator': '\n',
                'confidence': 0.0,
                'format': 'unknown'
            }

        result = {
            'encoding': detected_encoding,
            'confidence': 0.0,
            'format': 'text'
        }

        # JSON detection
        if extension == '.json' or sample.strip().startswith('{') or sample.strip().startswith('['):
            try:
                json.loads(sample if sample.strip().startswith('[') else '[' + sample + ']')
                result['format'] = 'json'
                result['confidence'] = 1.0
                return result
            except json.JSONDecodeError:
                pass

        # CSV detection
        if extension == '.csv':
            result['format'] = 'csv'
            result['term_separator'] = ','
            result['card_separator'] = '\n'
            result['confidence'] = 0.9
            return result

        # TSV detection
        if extension == '.tsv' or '\t' in sample:
            tab_count = sample.count('\t')
            line_count = sample.count('\n') + 1
            if tab_count >= line_count * 0.8:  # Most lines have tabs
                result['term_separator'] = '\t'
                result['card_separator'] = '\n'
                result['confidence'] = 0.9
                result['format'] = 'tsv'
                return result

        # Try common separators
        separators = [
            ('\t', '\n', 'tab'),
            (';', '\n', 'semicolon'),
            ('::', '\n', 'double_colon'),
            (' - ', '\n', 'dash'),
            ('|', '\n', 'pipe'),
            (',', '\n', 'comma'),
        ]

        best_sep = None
        best_score = 0

        for term_sep, card_sep, name in separators:
            lines = sample.split(card_sep)
            valid_lines = 0

            for line in lines[:20]:  # Check first 20 lines
                if term_sep in line:
                    parts = line.split(term_sep)
                    if len(parts) >= 2 and all(p.strip() for p in parts[:2]):
                        valid_lines += 1

            score = valid_lines / min(len(lines), 20) if lines else 0

            if score > best_score:
                best_score = score
                best_sep = (term_sep, card_sep, name)

        if best_sep and best_score > 0.5:
            result['term_separator'] = best_sep[0]
            result['card_separator'] = best_sep[1]
            result['confidence'] = best_score
            result['format'] = best_sep[2]
        else:
            # Default fallback
            result['term_separator'] = '\t'
            result['card_separator'] = '\n'
            result['confidence'] = 0.3

        return result

    def preview(self, file_path: str, limit: int = 5) -> ImportPreview:
        """
        Preview first N cards from file.

        Args:
            file_path: Path to file
            limit: Maximum number of cards to preview

        Returns:
            ImportPreview with cards and any errors/warnings
        """
        path = Path(file_path)
        errors = []
        warnings = []
        cards = []

        if not path.exists():
            return ImportPreview([], 0, ["File not found"], [])

        try:
            # Detect if JSON
            if path.suffix.lower() == '.json':
                cards, total, errs = self._parse_json(path, limit)
                errors.extend(errs)
            else:
                cards, total, errs, warns = self._parse_text(path, limit)
                errors.extend(errs)
                warnings.extend(warns)

            return ImportPreview(cards, total, errors, warnings)

        except Exception as e:
            return ImportPreview([], 0, [f"Error reading file: {str(e)}"], [])

    def import_file(self, file_path: str) -> ImportResult:
        """
        Import all cards from file.

        Args:
            file_path: Path to file

        Returns:
            ImportResult with all cards and statistics
        """
        path = Path(file_path)

        if not path.exists():
            return ImportResult(
                success=False,
                cards=[],
                errors=["File not found"],
                warnings=[],
                total_lines=0,
                imported_count=0,
                skipped_count=0
            )

        try:
            if path.suffix.lower() == '.json':
                cards, total, errors = self._parse_json(path, limit=None)
                warnings = []
            else:
                cards, total, errors, warnings = self._parse_text(path, limit=None)

            # Validate cards
            valid_cards, validation_errors = self.validate(cards)
            errors.extend(validation_errors)

            return ImportResult(
                success=len(valid_cards) > 0,
                cards=valid_cards,
                errors=errors,
                warnings=warnings,
                total_lines=total,
                imported_count=len(valid_cards),
                skipped_count=total - len(valid_cards)
            )

        except Exception as e:
            return ImportResult(
                success=False,
                cards=[],
                errors=[f"Error importing file: {str(e)}"],
                warnings=[],
                total_lines=0,
                imported_count=0,
                skipped_count=0
            )

    def _parse_json(
        self,
        path: Path,
        limit: Optional[int]
    ) -> Tuple[List[Dict], int, List[str]]:
        """Parse JSON file."""
        errors = []

        with open(path, 'r', encoding=self.encoding) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                return [], 0, [f"Invalid JSON: {str(e)}"]

        cards = []

        # Handle different JSON structures
        if isinstance(data, dict):
            # Single deck format: {"name": "...", "cards": [...]}
            if 'cards' in data:
                card_list = data['cards']
            else:
                # Try to use dict values as cards
                card_list = list(data.values()) if data else []
        elif isinstance(data, list):
            card_list = data
        else:
            return [], 0, ["Invalid JSON structure"]

        total = len(card_list)

        for i, item in enumerate(card_list):
            if limit and len(cards) >= limit:
                break

            if isinstance(item, dict):
                term = item.get('term', item.get('front', item.get('question', '')))
                definition = item.get('definition', item.get('back', item.get('answer', '')))
                hint = item.get('hint', item.get('hint', None))
                example = item.get('example', None)
                notes = item.get('notes', None)

                if term or definition:
                    cards.append({
                        'term': str(term) if term else '',
                        'definition': str(definition) if definition else '',
                        'hint': str(hint) if hint else None,
                        'example': str(example) if example else None,
                        'notes': str(notes) if notes else None
                    })
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                cards.append({
                    'term': str(item[0]),
                    'definition': str(item[1]),
                    'hint': str(item[2]) if len(item) > 2 else None
                })

        return cards, total, errors

    def _parse_text(
        self,
        path: Path,
        limit: Optional[int]
    ) -> Tuple[List[Dict], int, List[str], List[str]]:
        """Parse text file with custom separators."""
        errors = []
        warnings = []
        cards = []

        try:
            with open(path, 'r', encoding=self.encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with detected encoding
            detected = detect_encoding(path)
            with open(path, 'r', encoding=detected) as f:
                content = f.read()
            warnings.append(f"File encoding changed to {detected}")

        # Split into card chunks
        if self.card_separator == '\n':
            # Special handling for line-by-line
            raw_cards = content.split('\n')
        else:
            raw_cards = content.split(self.card_separator)

        total = len(raw_cards)

        # Skip header if needed
        start_idx = 1 if self.skip_header and raw_cards else 0

        for i, raw_card in enumerate(raw_cards[start_idx:], start=start_idx):
            if limit and len(cards) >= limit:
                break

            raw_card = raw_card.strip() if self.strip_whitespace else raw_card

            if not raw_card:
                if not self.skip_empty:
                    warnings.append(f"Line {i+1}: Empty card skipped")
                continue

            # Split by term separator
            parts = raw_card.split(self.term_separator)

            if len(parts) < 2:
                warnings.append(f"Line {i+1}: No separator found, skipped")
                continue

            term = parts[0].strip() if self.strip_whitespace else parts[0]
            definition = parts[1].strip() if self.strip_whitespace else parts[1]

            # Check for hint in third column
            hint = None
            if self.import_hints and len(parts) > 2:
                hint = parts[2].strip() if self.strip_whitespace else parts[2]

            if not term and not definition:
                if not self.skip_empty:
                    warnings.append(f"Line {i+1}: Empty term and definition, skipped")
                continue

            cards.append({
                'term': term,
                'definition': definition,
                'hint': hint if hint else None
            })

        return cards, total, errors, warnings

    def validate(self, cards: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate cards and return valid ones with errors.

        Args:
            cards: List of card dictionaries

        Returns:
            Tuple of (valid_cards, errors)
        """
        valid = []
        errors = []

        for i, card in enumerate(cards):
            term = card.get('term', '').strip()
            definition = card.get('definition', '').strip()

            if not term and not definition:
                errors.append(f"Card {i+1}: Both term and definition are empty")
                continue

            if not term:
                errors.append(f"Card {i+1}: Term is empty")
                continue

            if not definition:
                errors.append(f"Card {i+1}: Definition is empty")
                continue

            valid.append(card)

        return valid, errors

    def import_from_text(self, text: str) -> ImportResult:
        """
        Import cards from text string (e.g., pasted content).

        Args:
            text: Text content to parse

        Returns:
            ImportResult
        """
        cards = []
        warnings = []

        # Split into card chunks
        if self.card_separator == '\n':
            raw_cards = text.split('\n')
        else:
            raw_cards = text.split(self.card_separator)

        total = len(raw_cards)
        start_idx = 1 if self.skip_header else 0

        for i, raw_card in enumerate(raw_cards[start_idx:], start=start_idx):
            raw_card = raw_card.strip() if self.strip_whitespace else raw_card

            if not raw_card:
                continue

            parts = raw_card.split(self.term_separator)

            if len(parts) < 2:
                warnings.append(f"Line {i+1}: No separator found")
                continue

            term = parts[0].strip() if self.strip_whitespace else parts[0]
            definition = parts[1].strip() if self.strip_whitespace else parts[1]
            hint = parts[2].strip() if len(parts) > 2 and self.import_hints else None

            if term or definition:
                cards.append({
                    'term': term,
                    'definition': definition,
                    'hint': hint
                })

        valid_cards, validation_errors = self.validate(cards)

        return ImportResult(
            success=len(valid_cards) > 0,
            cards=valid_cards,
            errors=validation_errors,
            warnings=warnings,
            total_lines=total,
            imported_count=len(valid_cards),
            skipped_count=total - len(valid_cards)
        )


def import_cards(
    file_path: str,
    term_separator: str = '\t',
    card_separator: str = '\n',
    **kwargs
) -> ImportResult:
    """
    Convenience function to import cards from a file.

    Args:
        file_path: Path to file
        term_separator: Separator between term and definition
        card_separator: Separator between cards
        **kwargs: Additional arguments for CardImporter

    Returns:
        ImportResult
    """
    importer = CardImporter(
        term_separator=term_separator,
        card_separator=card_separator,
        **kwargs
    )
    return importer.import_file(file_path)
