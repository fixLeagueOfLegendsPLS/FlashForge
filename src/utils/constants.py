"""Constants for FlashForge application."""

import os
import sys
from pathlib import Path

# Application info
APP_NAME = "FlashForge"
APP_VERSION = "1.0.0"
APP_AUTHOR = "FlashForge Team"

# Determine data directory based on platform
def get_data_dir() -> Path:
    """Get the appropriate data directory for the current platform."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return base / APP_NAME

# Paths
DATA_DIR = get_data_dir()
DB_PATH = DATA_DIR / "flashforge.db"
BACKUPS_DIR = DATA_DIR / "backups"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"
CONFIG_PATH = DATA_DIR / "config.json"

# Portable mode check - if data folder exists next to executable, use that
PORTABLE_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
if PORTABLE_DATA_DIR.exists():
    DATA_DIR = PORTABLE_DATA_DIR
    DB_PATH = DATA_DIR / "flashforge.db"
    BACKUPS_DIR = DATA_DIR / "backups"
    IMAGES_DIR = DATA_DIR / "images"
    AUDIO_DIR = DATA_DIR / "audio"
    CONFIG_PATH = DATA_DIR / "config.json"

# Database
DB_BACKUP_COUNT = 5  # Number of backups to keep

# Study modes
STUDY_MODES = {
    "flashcards": "Flashcards",
    "learn": "Learn",
    "write": "Write",
    "test": "Test",
    "match": "Match",
    "gravity": "Gravity"
}

# SM-2 Algorithm defaults
SM2_DEFAULT_EASE = 2.5
SM2_MIN_EASE = 1.3
SM2_MAX_EASE = 3.0
SM2_EASE_BONUS = 0.15
SM2_EASE_PENALTY = 0.2

# Leitner boxes
LEITNER_BOXES = 5
LEITNER_INTERVALS = [1, 2, 4, 7, 14]  # Days

# Import/Export
SUPPORTED_IMPORT_FORMATS = [".txt", ".csv", ".tsv", ".json"]
SUPPORTED_EXPORT_FORMATS = [".txt", ".csv", ".json", ".html", ".pdf"]

# Default separators
DEFAULT_TERM_SEPARATOR = "\t"
DEFAULT_CARD_SEPARATOR = "\n"

# Separator presets
SEPARATOR_PRESETS = {
    "quizlet": {"term_sep": "\t", "card_sep": "\n", "name": "Quizlet"},
    "anki": {"term_sep": "\t", "card_sep": "\n", "name": "Anki"},
    "csv": {"term_sep": ",", "card_sep": "\n", "name": "CSV"},
    "semicolon": {"term_sep": ";", "card_sep": "\n", "name": "Semicolon"},
    "double_colon": {"term_sep": "::", "card_sep": "\n", "name": "Double Colon"},
    "pipe": {"term_sep": "|", "card_sep": "\n", "name": "Pipe"},
}

# Supported encodings
SUPPORTED_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "utf-16",
    "cp1251",
    "cp1252",
    "iso-8859-1",
    "ascii"
]

# UI Constants
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 700
SIDEBAR_WIDTH = 250
CARD_FLIP_DURATION = 300  # ms

# Colors (will be overridden by theme)
COLORS = {
    "primary": "#6366f1",  # Indigo
    "secondary": "#8b5cf6",  # Purple
    "success": "#22c55e",  # Green
    "warning": "#f59e0b",  # Amber
    "error": "#ef4444",  # Red
    "info": "#3b82f6",  # Blue
}

# Deck colors for selection
DECK_COLORS = [
    "#ef4444",  # Red
    "#f97316",  # Orange
    "#f59e0b",  # Amber
    "#eab308",  # Yellow
    "#84cc16",  # Lime
    "#22c55e",  # Green
    "#14b8a6",  # Teal
    "#06b6d4",  # Cyan
    "#3b82f6",  # Blue
    "#6366f1",  # Indigo
    "#8b5cf6",  # Violet
    "#a855f7",  # Purple
    "#d946ef",  # Fuchsia
    "#ec4899",  # Pink
    "#f43f5e",  # Rose
]

# Deck icons (emoji)
DECK_ICONS = [
    "📚", "📖", "📝", "✏️", "🎓", "🏫", "💡", "🧠",
    "🔬", "🧪", "🔭", "📐", "📊", "💻", "🌐", "🗣️",
    "🇬🇧", "🇫🇷", "🇩🇪", "🇪🇸", "🇮🇹", "🇯🇵", "🇨🇳", "🇷🇺",
    "🎵", "🎨", "⚽", "🏀", "🎮", "🎬", "📷", "✈️",
    "🌍", "🌿", "🐍", "🦋", "⚡", "🔥", "💎", "⭐"
]

# Keyboard shortcuts
SHORTCUTS = {
    "new_deck": "<Control-n>",
    "import": "<Control-i>",
    "export": "<Control-e>",
    "search": "<Control-f>",
    "settings": "<Control-comma>",
    "quit": "<Control-q>",
    "flip_card": "<space>",
    "know": "<Right>",
    "dont_know": "<Left>",
    "star": "s",
    "hint": "h",
    "edit": "e",
    "escape": "<Escape>",
}

# Levenshtein threshold for Write mode (percentage)
LEVENSHTEIN_STRICT = 100  # Exact match
LEVENSHTEIN_NORMAL = 85   # Allow small typos
LEVENSHTEIN_LENIENT = 70  # Allow more typos

# Test mode
TEST_QUESTION_TYPES = ["multiple_choice", "true_false", "written", "matching"]
TEST_DEFAULT_QUESTIONS = 20
TEST_CHOICES_COUNT = 4

# Match game
MATCH_GRID_SIZES = {
    "small": (3, 4),   # 12 cards (6 pairs)
    "medium": (4, 4),  # 16 cards (8 pairs)
    "large": (4, 5),   # 20 cards (10 pairs)
}

# Statistics
STREAK_RESET_HOURS = 36  # Hours without study before streak resets

# Animations
ANIMATION_ENABLED = True
ANIMATION_DURATION = 200  # ms
