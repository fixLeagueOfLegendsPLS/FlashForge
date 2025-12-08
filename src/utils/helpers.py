"""Helper functions for FlashForge."""

import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from pathlib import Path


def normalize_text(text: str, ignore_case: bool = True,
                   ignore_punctuation: bool = True,
                   ignore_extra_spaces: bool = True) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""

    result = text

    if ignore_case:
        result = result.lower()

    if ignore_punctuation:
        result = re.sub(r'[^\w\s]', '', result)

    if ignore_extra_spaces:
        result = ' '.join(result.split())

    return result.strip()


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_percentage(s1: str, s2: str, normalize: bool = True) -> float:
    """Calculate similarity percentage between two strings."""
    if normalize:
        s1 = normalize_text(s1)
        s2 = normalize_text(s2)

    if not s1 and not s2:
        return 100.0
    if not s1 or not s2:
        return 0.0

    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))

    return (1 - distance / max_len) * 100


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        if secs:
            return f"{minutes} мин {secs} сек"
        return f"{minutes} мин"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes:
            return f"{hours} ч {minutes} мин"
        return f"{hours} ч"


def format_date(dt: Optional[datetime], relative: bool = True) -> str:
    """Format datetime to human readable string."""
    if not dt:
        return "Никогда"

    if not relative:
        return dt.strftime("%d.%m.%Y %H:%M")

    now = datetime.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "Только что"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes} мин назад"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} ч назад"
    elif diff < timedelta(days=2):
        return "Вчера"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} дн назад"
    else:
        return dt.strftime("%d.%m.%Y")


def format_number(n: int) -> str:
    """Format number with thousands separator."""
    return f"{n:,}".replace(",", " ")


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length - len(suffix)].rstrip() + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize string for use as filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove control characters
    filename = ''.join(c for c in filename if unicodedata.category(c) != 'Cc')

    # Limit length
    if len(filename) > 200:
        filename = filename[:200]

    return filename.strip() or "unnamed"


def get_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """Get unique filename in directory."""
    sanitized = sanitize_filename(base_name)
    path = directory / f"{sanitized}{extension}"

    counter = 1
    while path.exists():
        path = directory / f"{sanitized}_{counter}{extension}"
        counter += 1

    return path


def parse_color(color: str) -> Tuple[int, int, int]:
    """Parse hex color to RGB tuple."""
    color = color.lstrip('#')
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))


def color_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(color: str, amount: float = 0.2) -> str:
    """Lighten a hex color."""
    r, g, b = parse_color(color)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return color_to_hex(r, g, b)


def darken_color(color: str, amount: float = 0.2) -> str:
    """Darken a hex color."""
    r, g, b = parse_color(color)
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return color_to_hex(r, g, b)


def get_contrast_color(color: str) -> str:
    """Get black or white depending on background luminance."""
    r, g, b = parse_color(color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#ffffff" if luminance < 0.5 else "#000000"


def detect_encoding(file_path: Path) -> str:
    """Try to detect file encoding."""
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'cp1251', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue

    return 'utf-8'  # Default fallback


def split_cards_text(text: str, card_separator: str,
                     term_separator: str) -> List[Tuple[str, str]]:
    """Split text into list of (term, definition) tuples."""
    cards = []

    # Handle escaped separators
    card_sep = card_separator.replace('\\n', '\n').replace('\\t', '\t')
    term_sep = term_separator.replace('\\n', '\n').replace('\\t', '\t')

    # Split by card separator
    raw_cards = text.split(card_sep)

    for raw_card in raw_cards:
        raw_card = raw_card.strip()
        if not raw_card:
            continue

        # Split by term separator
        parts = raw_card.split(term_sep, 1)
        if len(parts) == 2:
            term = parts[0].strip()
            definition = parts[1].strip()
            if term or definition:
                cards.append((term, definition))

    return cards


def calculate_next_review(ease_factor: float, interval: int,
                          quality: int) -> Tuple[float, int, datetime]:
    """
    Calculate next review date using SM-2 algorithm.

    quality: 0-5 (0-2 = fail, 3-5 = pass)
    Returns: (new_ease_factor, new_interval_days, next_review_date)
    """
    from .constants import SM2_MIN_EASE, SM2_MAX_EASE

    # Update ease factor
    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(SM2_MIN_EASE, min(SM2_MAX_EASE, new_ease))

    # Calculate new interval
    if quality < 3:
        # Failed - reset
        new_interval = 1
    else:
        if interval == 0:
            new_interval = 1
        elif interval == 1:
            new_interval = 6
        else:
            new_interval = int(interval * new_ease)

    next_review = datetime.now() + timedelta(days=new_interval)

    return new_ease, new_interval, next_review
