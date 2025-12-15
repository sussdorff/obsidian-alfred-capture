"""Tests for capture logic."""

from datetime import datetime
from unittest import mock

import pytest

from src.api import ObsidianAPI
from src.capture import Capture
from src.config import Config


class TestCapture:
    """Tests for Capture class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config(
            api_key="test-key",
            api_port=27124,
            vault_path="/test/vault",
            daily_note_folder="daily",
            daily_note_format="%Y-%m-%d",
        )

    @pytest.fixture
    def api(self):
        """Create a mock API client."""
        return mock.Mock(spec=ObsidianAPI)

    @pytest.fixture
    def capture(self, api, config):
        """Create a Capture instance with mocked API."""
        return Capture(api, config)

    def test_ensure_daily_note_exists(self, capture, api):
        """Test ensure_daily_note when note already exists."""
        api.get_daily_note.return_value = "# Existing note"

        result = capture.ensure_daily_note()

        assert result is True
        api.get_daily_note.assert_called_once()
        api.create_daily_note.assert_not_called()

    def test_ensure_daily_note_creates(self, capture, api):
        """Test ensure_daily_note creates note when missing."""
        api.get_daily_note.return_value = None
        api.create_daily_note.return_value = True

        with mock.patch("src.capture.create_daily_note_content") as mock_create:
            mock_create.return_value = "# New note from template"
            result = capture.ensure_daily_note()

        assert result is True
        api.create_daily_note.assert_called_once_with("# New note from template")

    def test_task_capture(self, capture, api):
        """Test capturing a task."""
        api.get_daily_note.return_value = "# Existing"
        api.append_to_heading.return_value = True

        result = capture.task("Buy groceries")

        assert result is True
        api.append_to_heading.assert_called_once_with("Todo", "- [ ] Buy groceries")

    def test_idea_capture(self, capture, api):
        """Test capturing an idea."""
        api.get_daily_note.return_value = "# Existing"
        api.append_to_heading.return_value = True

        result = capture.idea("Build a spaceship")

        assert result is True
        api.append_to_heading.assert_called_once_with("Ideas", "- Build a spaceship")

    def test_journal_capture(self, capture, api):
        """Test capturing a journal entry with timestamp."""
        api.get_daily_note.return_value = "# Existing"
        api.append_to_heading.return_value = True

        with mock.patch("src.capture.datetime") as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "14:30"
            result = capture.journal("Had a great meeting")

        assert result is True
        api.append_to_heading.assert_called_once_with(
            "Journal", "- 14:30 Had a great meeting"
        )

    def test_bookmark_capture(self, capture, api):
        """Test capturing a bookmark."""
        api.get_daily_note.return_value = "# Existing"
        api.append_to_heading.return_value = True

        result = capture.bookmark("GitHub", "https://github.com")

        assert result is True
        api.append_to_heading.assert_called_once_with(
            "Bookmarks", "- [GitHub](https://github.com)"
        )

    def test_bookmark_escapes_brackets(self, capture, api):
        """Test that bookmark titles with brackets are escaped."""
        api.get_daily_note.return_value = "# Existing"
        api.append_to_heading.return_value = True

        result = capture.bookmark("[Test] Title", "https://example.com")

        assert result is True
        api.append_to_heading.assert_called_once_with(
            "Bookmarks", r"- [\[Test\] Title](https://example.com)"
        )

    def test_capture_ensures_daily_note(self, capture, api):
        """Test that all capture methods ensure daily note exists."""
        api.get_daily_note.return_value = None
        api.create_daily_note.return_value = True
        api.append_to_heading.return_value = True

        with mock.patch("src.capture.create_daily_note_content", return_value="# New"):
            capture.task("Test task")
            capture.idea("Test idea")
            capture.journal("Test journal")
            capture.bookmark("Test", "https://test.com")

        # Should have tried to create daily note for each capture
        assert api.get_daily_note.call_count == 4
