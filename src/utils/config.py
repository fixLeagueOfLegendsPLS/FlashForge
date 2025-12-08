"""Configuration management for FlashForge."""

import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from .constants import CONFIG_PATH, DATA_DIR


@dataclass
class AppearanceConfig:
    """Appearance settings."""
    theme: str = "dark"
    accent_color: str = "#6366f1"
    font_size: int = 14
    animations_enabled: bool = True


@dataclass
class StudyConfig:
    """Study settings."""
    cards_per_session: int = 20
    algorithm: str = "sm2"  # sm2, leitner, simple
    sound_enabled: bool = True
    auto_play_audio: bool = False
    show_progress: bool = True


@dataclass
class ImportExportConfig:
    """Import/Export settings."""
    default_term_separator: str = "\t"
    default_card_separator: str = "\n"
    default_encoding: str = "utf-8"
    auto_backup: bool = True
    backup_count: int = 5


@dataclass
class KeyboardConfig:
    """Keyboard shortcut settings."""
    flip_card: str = "space"
    know: str = "Right"
    dont_know: str = "Left"
    star: str = "s"
    hint: str = "h"
    edit: str = "e"


@dataclass
class ConfigData:
    """Complete application configuration."""
    appearance: AppearanceConfig = field(default_factory=AppearanceConfig)
    study: StudyConfig = field(default_factory=StudyConfig)
    import_export: ImportExportConfig = field(default_factory=ImportExportConfig)
    keyboard: KeyboardConfig = field(default_factory=KeyboardConfig)
    window_width: int = 1280
    window_height: int = 800
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    last_deck_id: Optional[int] = None
    recent_decks: list = field(default_factory=list)


class Config:
    """Configuration manager with auto-save."""

    _instance: Optional['Config'] = None
    _config: ConfigData

    def __new__(cls) -> 'Config':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize configuration."""
        self._config = ConfigData()
        self._ensure_dirs()
        self.load()

    def _ensure_dirs(self) -> None:
        """Ensure all data directories exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "backups").mkdir(exist_ok=True)
        (DATA_DIR / "images").mkdir(exist_ok=True)
        (DATA_DIR / "audio").mkdir(exist_ok=True)

    def load(self) -> None:
        """Load configuration from file."""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._apply_dict(data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                self._config = ConfigData()

    def save(self) -> None:
        """Save configuration to file."""
        self._ensure_dirs()
        data = self._to_dict()
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'appearance': asdict(self._config.appearance),
            'study': asdict(self._config.study),
            'import_export': asdict(self._config.import_export),
            'keyboard': asdict(self._config.keyboard),
            'window_width': self._config.window_width,
            'window_height': self._config.window_height,
            'window_x': self._config.window_x,
            'window_y': self._config.window_y,
            'last_deck_id': self._config.last_deck_id,
            'recent_decks': self._config.recent_decks,
        }

    def _apply_dict(self, data: dict) -> None:
        """Apply dictionary to config."""
        if 'appearance' in data:
            self._config.appearance = AppearanceConfig(**data['appearance'])
        if 'study' in data:
            self._config.study = StudyConfig(**data['study'])
        if 'import_export' in data:
            self._config.import_export = ImportExportConfig(**data['import_export'])
        if 'keyboard' in data:
            self._config.keyboard = KeyboardConfig(**data['keyboard'])

        for key in ['window_width', 'window_height', 'window_x', 'window_y',
                    'last_deck_id', 'recent_decks']:
            if key in data:
                setattr(self._config, key, data[key])

    # Property accessors
    @property
    def appearance(self) -> AppearanceConfig:
        return self._config.appearance

    @property
    def study(self) -> StudyConfig:
        return self._config.study

    @property
    def import_export(self) -> ImportExportConfig:
        return self._config.import_export

    @property
    def keyboard(self) -> KeyboardConfig:
        return self._config.keyboard

    @property
    def window_width(self) -> int:
        return self._config.window_width

    @window_width.setter
    def window_width(self, value: int) -> None:
        self._config.window_width = value

    @property
    def window_height(self) -> int:
        return self._config.window_height

    @window_height.setter
    def window_height(self, value: int) -> None:
        self._config.window_height = value

    @property
    def window_x(self) -> Optional[int]:
        return self._config.window_x

    @window_x.setter
    def window_x(self, value: Optional[int]) -> None:
        self._config.window_x = value

    @property
    def window_y(self) -> Optional[int]:
        return self._config.window_y

    @window_y.setter
    def window_y(self, value: Optional[int]) -> None:
        self._config.window_y = value

    @property
    def last_deck_id(self) -> Optional[int]:
        return self._config.last_deck_id

    @last_deck_id.setter
    def last_deck_id(self, value: Optional[int]) -> None:
        self._config.last_deck_id = value

    @property
    def recent_decks(self) -> list:
        return self._config.recent_decks

    def add_recent_deck(self, deck_id: int) -> None:
        """Add deck to recent list."""
        if deck_id in self._config.recent_decks:
            self._config.recent_decks.remove(deck_id)
        self._config.recent_decks.insert(0, deck_id)
        self._config.recent_decks = self._config.recent_decks[:10]
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key path (e.g., 'appearance.theme')."""
        parts = key.split('.')
        obj = self._config
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        return obj

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key path."""
        parts = key.split('.')
        obj = self._config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return
        if hasattr(obj, parts[-1]):
            setattr(obj, parts[-1], value)
            self.save()
