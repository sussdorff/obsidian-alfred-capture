"""Integration tests for Obsidian Alfred Capture.

These tests run against a real Obsidian instance with the Local REST API plugin.
They are skipped by default and only run when:
1. pytest is invoked with -m integration
2. The test vault has the Local REST API plugin configured
3. Obsidian is running with the test vault open

Setup:
1. Open test-vault/ in Obsidian
2. Enable the Local REST API plugin
3. Run: uv run pytest -m integration
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.api import ObsidianAPI, ObsidianAPIError
from src.capture import Capture
from src.config import Config

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
TEST_VAULT = PROJECT_ROOT / "test-vault"
PLUGIN_CONFIG = TEST_VAULT / ".obsidian/plugins/obsidian-local-rest-api/data.json"


def load_test_vault_config() -> dict | None:
    """Load API configuration from test vault's plugin config."""
    if not PLUGIN_CONFIG.exists():
        return None

    try:
        data = json.loads(PLUGIN_CONFIG.read_text())
        api_key = data.get("apiKey", "")
        if not api_key:
            return None
        return {
            "api_key": api_key,
            "port": data.get("port", 27124),
        }
    except (json.JSONDecodeError, KeyError):
        return None


def integration_test_available() -> bool:
    """Check if integration tests can run."""
    config = load_test_vault_config()
    return config is not None and bool(config.get("api_key"))


# Skip all tests in this module if integration tests aren't available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not integration_test_available(),
        reason="Integration tests require test-vault with Local REST API configured",
    ),
]


@pytest.fixture(scope="module")
def config() -> Config:
    """Load configuration from test vault."""
    vault_config = load_test_vault_config()
    return Config(
        api_key=vault_config["api_key"],
        api_port=vault_config["port"],
        vault_path=str(TEST_VAULT),
        daily_note_folder="10-Daily",
        daily_note_format="%Y-%m-%d",
    )


@pytest.fixture(scope="module")
def api(config: Config) -> ObsidianAPI:
    """Create API client for integration tests."""
    return ObsidianAPI(config.api_key, config.api_port)


@pytest.fixture(scope="module")
def capture(api: ObsidianAPI, config: Config) -> Capture:
    """Create Capture instance for integration tests."""
    return Capture(api, config)


class TestAPIConnection:
    """Test basic API connectivity."""

    def test_api_is_connected(self, api: ObsidianAPI):
        """Verify we can connect to the Obsidian API."""
        assert api.is_connected(), (
            "Cannot connect to Obsidian API. "
            "Is Obsidian running with the test vault open?"
        )


class TestDailyNoteOperations:
    """Test daily note creation and retrieval."""

    def test_get_or_create_daily_note(self, api: ObsidianAPI, capture: Capture):
        """Test that we can get or create today's daily note."""
        # Ensure daily note exists
        capture.ensure_daily_note()

        # Verify we can retrieve it
        content = api.get_daily_note()
        assert content is not None, "Daily note should exist after ensure_daily_note()"

    def test_daily_note_has_expected_headings(self, api: ObsidianAPI, capture: Capture):
        """Verify the daily note has the expected headings from the template."""
        capture.ensure_daily_note()
        content = api.get_daily_note()

        expected_headings = ["## Todo", "## Ideas", "## Journal", "## Bookmarks"]
        for heading in expected_headings:
            assert heading in content, f"Daily note should contain '{heading}'"


class TestCaptureOperations:
    """Test capture functionality against real API."""

    def test_capture_task(self, capture: Capture, api: ObsidianAPI):
        """Test capturing a task to the daily note."""
        test_text = f"[TEST] Integration test task - {datetime.now().isoformat()}"

        result = capture.task(test_text)
        assert result is True

        # Verify task was added
        content = api.get_daily_note()
        assert f"- [ ] {test_text}" in content

    def test_capture_idea(self, capture: Capture, api: ObsidianAPI):
        """Test capturing an idea to the daily note."""
        test_text = f"[TEST] Integration test idea - {datetime.now().isoformat()}"

        result = capture.idea(test_text)
        assert result is True

        # Verify idea was added
        content = api.get_daily_note()
        assert f"- {test_text}" in content

    def test_capture_journal(self, capture: Capture, api: ObsidianAPI):
        """Test capturing a journal entry with timestamp."""
        test_text = f"[TEST] Integration test journal - {datetime.now().isoformat()}"

        result = capture.journal(test_text)
        assert result is True

        # Verify journal entry was added (with some timestamp prefix)
        content = api.get_daily_note()
        assert test_text in content
        # Check that it has a timestamp format (HH:MM)
        assert any(
            f"- {h:02d}:" in content for h in range(24)
        ), "Journal entry should have timestamp"

    def test_capture_bookmark(self, capture: Capture, api: ObsidianAPI):
        """Test capturing a bookmark to the daily note."""
        test_title = f"[TEST] Test Site - {datetime.now().isoformat()}"
        test_url = "https://example.com/test"

        result = capture.bookmark(test_title, test_url)
        assert result is True

        # Verify bookmark was added
        content = api.get_daily_note()
        assert test_url in content


class TestErrorHandling:
    """Test error handling with real API."""

    def test_append_to_nonexistent_heading(self, api: ObsidianAPI, capture: Capture):
        """Test behavior when appending to a heading that doesn't exist."""
        capture.ensure_daily_note()

        # This should raise an error or handle gracefully
        with pytest.raises(ObsidianAPIError):
            api.append_to_heading("NonExistentHeading12345", "test content")


class TestTemplateRendering:
    """Test that templates are rendered correctly."""

    def test_daily_note_has_correct_date(self, api: ObsidianAPI, capture: Capture):
        """Verify the daily note has today's date in expected places."""
        capture.ensure_daily_note()
        content = api.get_daily_note()

        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")

        # The template uses {date} placeholder which should be replaced
        assert date_str in content, f"Daily note should contain today's date: {date_str}"
