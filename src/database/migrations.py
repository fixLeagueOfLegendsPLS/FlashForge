"""Database migrations for FlashForge."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from .models import Base
from ..utils.constants import DB_PATH, BACKUPS_DIR, DB_BACKUP_COUNT


class MigrationManager:
    """Handles database migrations and backups."""

    CURRENT_VERSION = 1

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_db_version(self) -> int:
        """Get current database schema version."""
        inspector = inspect(self.engine)

        if 'app_settings' not in inspector.get_table_names():
            return 0

        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT value FROM app_settings WHERE key = 'db_version'")
            )
            row = result.fetchone()
            if row:
                return int(row[0])
        return 0

    def set_db_version(self, version: int) -> None:
        """Set database schema version."""
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT OR REPLACE INTO app_settings (key, value)
                    VALUES ('db_version', :version)
                """),
                {"version": str(version)}
            )
            conn.commit()

    def backup_database(self) -> Optional[Path]:
        """Create a backup of the database."""
        if not DB_PATH.exists():
            return None

        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUPS_DIR / f"flashforge_backup_{timestamp}.db"

        shutil.copy2(DB_PATH, backup_path)

        # Clean old backups
        self._cleanup_old_backups()

        return backup_path

    def _cleanup_old_backups(self) -> None:
        """Remove old backups keeping only the most recent ones."""
        if not BACKUPS_DIR.exists():
            return

        backups = sorted(
            BACKUPS_DIR.glob("flashforge_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[DB_BACKUP_COUNT:]:
            old_backup.unlink()

    def create_tables(self) -> None:
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def migrate(self) -> None:
        """Run all necessary migrations."""
        current_version = self.get_db_version()

        if current_version < self.CURRENT_VERSION:
            # Backup before migration
            self.backup_database()

        # Run migrations in order
        if current_version < 1:
            self._migrate_to_v1()

        # Add more migrations here as needed:
        # if current_version < 2:
        #     self._migrate_to_v2()

    def _migrate_to_v1(self) -> None:
        """Initial schema creation."""
        self.create_tables()
        self.set_db_version(1)

    # Future migration example:
    # def _migrate_to_v2(self) -> None:
    #     """Example migration to version 2."""
    #     with self.engine.connect() as conn:
    #         # Add new column
    #         conn.execute(text(
    #             "ALTER TABLE cards ADD COLUMN new_field TEXT"
    #         ))
    #         conn.commit()
    #     self.set_db_version(2)

    def reset_database(self) -> None:
        """
        Reset database to initial state.
        WARNING: This will delete all data!
        """
        self.backup_database()

        # Drop all tables
        Base.metadata.drop_all(self.engine)

        # Recreate
        self.create_tables()
        self.set_db_version(self.CURRENT_VERSION)

    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        Restore database from a backup file.
        Returns True if successful.
        """
        if not backup_path.exists():
            return False

        # Close all connections (caller should handle this)
        # Backup current database
        self.backup_database()

        # Replace with backup
        shutil.copy2(backup_path, DB_PATH)

        return True
