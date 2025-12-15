"""Configuration handling for Obsidian Alfred Capture."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for Obsidian API and daily note settings."""

    api_key: str
    api_port: int
    vault_path: str
    daily_note_folder: str
    daily_note_format: str

    # Heading configuration
    task_heading: str = "Todo"
    idea_heading: str = "Ideas"
    journal_heading: str = "Journal"
    bookmark_heading: str = "Bookmarks"

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If not provided,
                      loads from default locations.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        api_key = os.environ.get("OBSIDIAN_API_KEY")
        if not api_key:
            raise ValueError("OBSIDIAN_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            api_port=int(os.environ.get("OBSIDIAN_API_PORT", "27124")),
            vault_path=os.environ.get("VAULT_PATH", ""),
            daily_note_folder=os.environ.get("DAILY_NOTE_FOLDER", "10-Daily"),
            daily_note_format=os.environ.get("DAILY_NOTE_FORMAT", "%Y-%m-%d"),
            task_heading=os.environ.get("TASK_HEADING", "Todo"),
            idea_heading=os.environ.get("IDEA_HEADING", "Ideas"),
            journal_heading=os.environ.get("JOURNAL_HEADING", "Journal"),
            bookmark_heading=os.environ.get("BOOKMARK_HEADING", "Bookmarks"),
        )

    @classmethod
    def from_alfred(cls) -> "Config":
        """Load configuration from Alfred workflow environment variables.

        Alfred passes workflow variables as environment variables,
        so this is equivalent to from_env() but documents the intent.
        """
        return cls.from_env()
