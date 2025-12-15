"""Tests for configuration handling."""

import os
from unittest import mock

import pytest

from src.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_from_env_with_all_variables(self):
        """Test loading config with all environment variables set."""
        env = {
            "OBSIDIAN_API_KEY": "test-api-key",
            "OBSIDIAN_API_PORT": "27125",
            "VAULT_PATH": "/path/to/vault",
            "DAILY_NOTE_FOLDER": "daily",
            "DAILY_NOTE_FORMAT": "%Y/%m/%d",
            "TASK_HEADING": "Tasks",
            "IDEA_HEADING": "Notes",
            "JOURNAL_HEADING": "Log",
            "BOOKMARK_HEADING": "Links",
        }

        with mock.patch.dict(os.environ, env, clear=True):
            config = Config.from_env()

        assert config.api_key == "test-api-key"
        assert config.api_port == 27125
        assert config.vault_path == "/path/to/vault"
        assert config.daily_note_folder == "daily"
        assert config.daily_note_format == "%Y/%m/%d"
        assert config.task_heading == "Tasks"
        assert config.idea_heading == "Notes"
        assert config.journal_heading == "Log"
        assert config.bookmark_heading == "Links"

    def test_from_env_with_defaults(self):
        """Test loading config with only required variables."""
        env = {
            "OBSIDIAN_API_KEY": "test-api-key",
        }

        with mock.patch.dict(os.environ, env, clear=True):
            config = Config.from_env()

        assert config.api_key == "test-api-key"
        assert config.api_port == 27124  # default
        assert config.vault_path == ""
        assert config.daily_note_folder == "10-Daily"  # default
        assert config.daily_note_format == "%Y-%m-%d"  # default
        assert config.task_heading == "Todo"  # default
        assert config.idea_heading == "Ideas"  # default
        assert config.journal_heading == "Journal"  # default
        assert config.bookmark_heading == "Bookmarks"  # default

    def test_from_env_missing_api_key(self):
        """Test that missing API key raises ValueError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OBSIDIAN_API_KEY"):
                Config.from_env()

    def test_from_alfred_delegates_to_from_env(self):
        """Test that from_alfred uses from_env."""
        env = {
            "OBSIDIAN_API_KEY": "alfred-key",
        }

        with mock.patch.dict(os.environ, env, clear=True):
            config = Config.from_alfred()

        assert config.api_key == "alfred-key"
