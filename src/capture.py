"""Capture logic for tasks, ideas, journal entries, and bookmarks."""

from datetime import datetime

from .api import ObsidianAPI
from .config import Config
from .daily_note import create_daily_note_content


class Capture:
    """Handle capture of different content types to Obsidian daily notes."""

    def __init__(self, api: ObsidianAPI, config: Config):
        """Initialize the capture handler.

        Args:
            api: The Obsidian API client.
            config: Configuration object.
        """
        self.api = api
        self.config = config

    def ensure_daily_note(self) -> bool:
        """Ensure today's daily note exists, creating from template if needed.

        Returns:
            True if daily note exists or was created successfully.
        """
        existing = self.api.get_daily_note()
        if existing is not None:
            return True

        # Create from template
        content = create_daily_note_content(self.config)
        return self.api.create_daily_note(content)

    def task(self, text: str) -> bool:
        """Capture text as a task.

        Format: - [ ] {text}

        Args:
            text: The task description.

        Returns:
            True if capture was successful.
        """
        self.ensure_daily_note()
        formatted = f"- [ ] {text}"
        return self.api.append_to_heading(self.config.task_heading, formatted)

    def idea(self, text: str) -> bool:
        """Capture text as an idea.

        Format: - {text}

        Args:
            text: The idea text.

        Returns:
            True if capture was successful.
        """
        self.ensure_daily_note()
        formatted = f"- {text}"
        return self.api.append_to_heading(self.config.idea_heading, formatted)

    def journal(self, text: str) -> bool:
        """Capture text as a journal entry with timestamp.

        Format: - {HH:MM} {text}

        Args:
            text: The journal entry text.

        Returns:
            True if capture was successful.
        """
        self.ensure_daily_note()
        timestamp = datetime.now().strftime("%H:%M")
        formatted = f"- {timestamp} {text}"
        return self.api.append_to_heading(self.config.journal_heading, formatted)

    def bookmark(self, title: str, url: str) -> bool:
        """Capture a bookmark.

        Format: - [{title}]({url})

        Args:
            title: The page title.
            url: The page URL.

        Returns:
            True if capture was successful.
        """
        self.ensure_daily_note()
        # Escape any brackets in the title
        safe_title = title.replace("[", "\\[").replace("]", "\\]")
        formatted = f"- [{safe_title}]({url})"
        return self.api.append_to_heading(self.config.bookmark_heading, formatted)
