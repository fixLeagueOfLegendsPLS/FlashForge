"""
Card exporter for FlashForge.
Supports multiple output formats.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..database.models import Deck, Card


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    file_path: str
    card_count: int
    error: Optional[str] = None


class CardExporter:
    """
    Export cards to various formats.

    Supported formats:
    - TXT (customizable separators)
    - CSV
    - TSV
    - JSON
    - HTML (standalone viewer)
    - Anki compatible
    """

    def __init__(
        self,
        term_separator: str = '\t',
        card_separator: str = '\n',
        encoding: str = 'utf-8',
        include_stats: bool = False,
        starred_only: bool = False,
        fields: List[str] = None
    ):
        """
        Initialize exporter.

        Args:
            term_separator: Separator between term and definition
            card_separator: Separator between cards
            encoding: Output file encoding
            include_stats: Include learning statistics
            starred_only: Export only starred cards
            fields: Fields to export (default: term, definition)
        """
        self.term_separator = term_separator.replace('\\t', '\t').replace('\\n', '\n')
        self.card_separator = card_separator.replace('\\t', '\t').replace('\\n', '\n')
        self.encoding = encoding
        self.include_stats = include_stats
        self.starred_only = starred_only
        self.fields = fields or ['term', 'definition']

    def export_to_txt(
        self,
        cards: List[Dict[str, Any]],
        output_path: str
    ) -> ExportResult:
        """Export cards to plain text file."""
        try:
            lines = []
            for card in cards:
                if self.starred_only and not card.get('is_starred'):
                    continue

                parts = [str(card.get(field, '')) for field in self.fields]
                lines.append(self.term_separator.join(parts))

            content = self.card_separator.join(lines)

            with open(output_path, 'w', encoding=self.encoding) as f:
                f.write(content)

            return ExportResult(
                success=True,
                file_path=output_path,
                card_count=len(lines)
            )
        except Exception as e:
            return ExportResult(
                success=False,
                file_path=output_path,
                card_count=0,
                error=str(e)
            )

    def export_to_csv(
        self,
        cards: List[Dict[str, Any]],
        output_path: str
    ) -> ExportResult:
        """Export cards to CSV file."""
        try:
            with open(output_path, 'w', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f)

                # Header
                header = self.fields.copy()
                if self.include_stats:
                    header.extend(['times_correct', 'times_incorrect', 'ease_factor'])
                writer.writerow(header)

                # Data
                count = 0
                for card in cards:
                    if self.starred_only and not card.get('is_starred'):
                        continue

                    row = [card.get(field, '') for field in self.fields]
                    if self.include_stats:
                        row.extend([
                            card.get('times_correct', 0),
                            card.get('times_incorrect', 0),
                            card.get('ease_factor', 2.5)
                        ])
                    writer.writerow(row)
                    count += 1

            return ExportResult(
                success=True,
                file_path=output_path,
                card_count=count
            )
        except Exception as e:
            return ExportResult(
                success=False,
                file_path=output_path,
                card_count=0,
                error=str(e)
            )

    def export_to_json(
        self,
        cards: List[Dict[str, Any]],
        output_path: str,
        deck_name: str = "Exported Deck",
        deck_description: str = ""
    ) -> ExportResult:
        """Export cards to JSON file."""
        try:
            export_cards = []
            for card in cards:
                if self.starred_only and not card.get('is_starred'):
                    continue

                card_data = {field: card.get(field, '') for field in self.fields}

                if self.include_stats:
                    card_data.update({
                        'times_correct': card.get('times_correct', 0),
                        'times_incorrect': card.get('times_incorrect', 0),
                        'ease_factor': card.get('ease_factor', 2.5),
                        'interval': card.get('interval', 0)
                    })

                # Include optional fields if present
                for field in ['hint', 'example', 'notes']:
                    if card.get(field):
                        card_data[field] = card[field]

                export_cards.append(card_data)

            data = {
                'name': deck_name,
                'description': deck_description,
                'exported_at': datetime.now().isoformat(),
                'card_count': len(export_cards),
                'cards': export_cards
            }

            with open(output_path, 'w', encoding=self.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return ExportResult(
                success=True,
                file_path=output_path,
                card_count=len(export_cards)
            )
        except Exception as e:
            return ExportResult(
                success=False,
                file_path=output_path,
                card_count=0,
                error=str(e)
            )

    def export_to_html(
        self,
        cards: List[Dict[str, Any]],
        output_path: str,
        deck_name: str = "Flashcards"
    ) -> ExportResult:
        """Export cards to standalone HTML file with viewer."""
        try:
            filtered_cards = []
            for card in cards:
                if self.starred_only and not card.get('is_starred'):
                    continue
                filtered_cards.append({
                    'term': card.get('term', ''),
                    'definition': card.get('definition', ''),
                    'hint': card.get('hint', ''),
                })

            html_content = self._generate_html(deck_name, filtered_cards)

            with open(output_path, 'w', encoding=self.encoding) as f:
                f.write(html_content)

            return ExportResult(
                success=True,
                file_path=output_path,
                card_count=len(filtered_cards)
            )
        except Exception as e:
            return ExportResult(
                success=False,
                file_path=output_path,
                card_count=0,
                error=str(e)
            )

    def _generate_html(self, title: str, cards: List[Dict]) -> str:
        """Generate standalone HTML with embedded flashcard viewer."""
        cards_json = json.dumps(cards, ensure_ascii=False)

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - FlashForge Export</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            color: #fff;
        }}
        h1 {{
            margin: 20px 0;
            font-size: 2rem;
            color: #818cf8;
        }}
        .progress {{
            margin-bottom: 20px;
            color: #94a3b8;
        }}
        .card-container {{
            perspective: 1000px;
            width: 100%;
            max-width: 600px;
            height: 350px;
            cursor: pointer;
        }}
        .card {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.6s;
        }}
        .card.flipped {{
            transform: rotateY(180deg);
        }}
        .card-face {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        .card-front {{
            background: linear-gradient(145deg, #1e293b, #334155);
            border: 2px solid #475569;
        }}
        .card-back {{
            background: linear-gradient(145deg, #312e81, #4338ca);
            transform: rotateY(180deg);
        }}
        .card-content {{
            font-size: 1.5rem;
            text-align: center;
            line-height: 1.6;
            max-height: 250px;
            overflow-y: auto;
        }}
        .card-label {{
            position: absolute;
            top: 15px;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #818cf8;
        }}
        .hint {{
            margin-top: 15px;
            font-size: 0.9rem;
            color: #94a3b8;
            font-style: italic;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        button {{
            padding: 12px 30px;
            font-size: 1rem;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-secondary {{
            background: #334155;
            color: #fff;
        }}
        .btn-primary {{
            background: #6366f1;
            color: #fff;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
        }}
        .keyboard-hint {{
            margin-top: 20px;
            color: #64748b;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="progress">Card <span id="current">1</span> of <span id="total">{len(cards)}</span></div>

    <div class="card-container" onclick="flipCard()">
        <div class="card" id="card">
            <div class="card-face card-front">
                <span class="card-label">Term</span>
                <div class="card-content" id="term"></div>
            </div>
            <div class="card-face card-back">
                <span class="card-label">Definition</span>
                <div class="card-content" id="definition"></div>
                <div class="hint" id="hint"></div>
            </div>
        </div>
    </div>

    <div class="controls">
        <button class="btn-secondary" onclick="prevCard()">Previous</button>
        <button class="btn-primary" onclick="nextCard()">Next</button>
    </div>

    <div class="keyboard-hint">
        Space: Flip | Arrow keys: Navigate | S: Shuffle
    </div>

    <script>
        const cards = {cards_json};
        let currentIndex = 0;
        let isFlipped = false;

        function showCard() {{
            const card = cards[currentIndex];
            document.getElementById('term').textContent = card.term;
            document.getElementById('definition').textContent = card.definition;
            document.getElementById('hint').textContent = card.hint ? 'Hint: ' + card.hint : '';
            document.getElementById('current').textContent = currentIndex + 1;
            document.getElementById('card').classList.remove('flipped');
            isFlipped = false;
        }}

        function flipCard() {{
            document.getElementById('card').classList.toggle('flipped');
            isFlipped = !isFlipped;
        }}

        function nextCard() {{
            currentIndex = (currentIndex + 1) % cards.length;
            showCard();
        }}

        function prevCard() {{
            currentIndex = (currentIndex - 1 + cards.length) % cards.length;
            showCard();
        }}

        function shuffle() {{
            for (let i = cards.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [cards[i], cards[j]] = [cards[j], cards[i]];
            }}
            currentIndex = 0;
            showCard();
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{ e.preventDefault(); flipCard(); }}
            if (e.code === 'ArrowRight') nextCard();
            if (e.code === 'ArrowLeft') prevCard();
            if (e.code === 'KeyS') shuffle();
        }});

        showCard();
    </script>
</body>
</html>'''

    def export_to_anki(
        self,
        cards: List[Dict[str, Any]],
        output_path: str
    ) -> ExportResult:
        """Export cards in Anki-compatible format (tab-separated)."""
        return self.export_to_txt(
            cards,
            output_path
        )


def export_deck(
    deck: Deck,
    output_path: str,
    format: str = 'txt',
    **kwargs
) -> ExportResult:
    """
    Convenience function to export a deck.

    Args:
        deck: Deck object to export
        output_path: Output file path
        format: Export format (txt, csv, json, html, anki)
        **kwargs: Additional arguments for CardExporter

    Returns:
        ExportResult
    """
    exporter = CardExporter(**kwargs)

    # Convert cards to dictionaries
    cards_data = []
    for card in deck.cards:
        cards_data.append({
            'term': card.term,
            'definition': card.definition,
            'hint': card.hint,
            'example': card.example,
            'notes': card.notes,
            'is_starred': card.is_starred,
            'times_correct': card.times_correct,
            'times_incorrect': card.times_incorrect,
            'ease_factor': card.ease_factor,
            'interval': card.interval
        })

    format = format.lower()

    if format == 'txt':
        return exporter.export_to_txt(cards_data, output_path)
    elif format == 'csv':
        return exporter.export_to_csv(cards_data, output_path)
    elif format == 'json':
        return exporter.export_to_json(
            cards_data, output_path,
            deck_name=deck.name,
            deck_description=deck.description or ''
        )
    elif format == 'html':
        return exporter.export_to_html(cards_data, output_path, deck_name=deck.name)
    elif format == 'anki':
        return exporter.export_to_anki(cards_data, output_path)
    else:
        return ExportResult(
            success=False,
            file_path=output_path,
            card_count=0,
            error=f"Unsupported format: {format}"
        )
