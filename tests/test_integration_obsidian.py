"""Integration tests for Obsidian auto-start functionality.

These tests require manual intervention or specific system state.
Run with: pytest tests/test_integration_obsidian.py -v
"""

import os
import subprocess
import time
import pytest

from src.config import Config
from src.obsidian import ensure_obsidian_ready, is_obsidian_running, is_api_available


# Test configuration - uses test vault
TEST_VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "test-vault")
TEST_API_KEY = "2c2c85621cfea93661c1dcf59f880954f3d6c824e5c67808eb77d92d7c7de728"
TEST_API_PORT = 27125


def quit_obsidian() -> None:
    """Quit Obsidian if running."""
    if is_obsidian_running():
        subprocess.run(
            ["osascript", "-e", 'tell application "Obsidian" to quit'],
            capture_output=True,
        )
        # Wait for Obsidian to fully quit
        for _ in range(10):
            time.sleep(0.5)
            if not is_obsidian_running():
                break


def start_obsidian_without_vault() -> None:
    """Start Obsidian without opening a specific vault."""
    subprocess.run(
        ["open", "-a", "Obsidian"],
        capture_output=True,
    )
    # Wait for Obsidian to start
    for _ in range(10):
        time.sleep(0.5)
        if is_obsidian_running():
            break


def close_all_vaults() -> None:
    """Close all open vaults in Obsidian by closing all windows."""
    # Use AppleScript to close all Obsidian windows
    subprocess.run(
        ["osascript", "-e", '''
            tell application "Obsidian"
                close every window
            end tell
        '''],
        capture_output=True,
    )
    time.sleep(2)

    # Double-check by also using System Events to close any remaining windows
    subprocess.run(
        ["osascript", "-e", '''
            tell application "System Events"
                tell process "Obsidian"
                    repeat while (count of windows) > 0
                        click button 1 of window 1
                        delay 0.5
                    end repeat
                end tell
            end tell
        '''],
        capture_output=True,
    )
    time.sleep(1)


@pytest.fixture
def ensure_obsidian_quit():
    """Fixture to ensure Obsidian is quit before test."""
    quit_obsidian()
    assert not is_obsidian_running(), "Obsidian should not be running"
    yield
    # Cleanup: leave Obsidian in whatever state the test left it


@pytest.fixture
def ensure_obsidian_running_without_vault():
    """Fixture to ensure Obsidian is running but vault is closed."""
    # First quit Obsidian completely
    quit_obsidian()
    time.sleep(1)

    # Start Obsidian without a vault
    start_obsidian_without_vault()
    time.sleep(2)

    # Close any auto-opened vaults
    close_all_vaults()
    time.sleep(1)

    assert is_obsidian_running(), "Obsidian should be running"
    assert not is_api_available(TEST_API_KEY, TEST_API_PORT), "API should not be available (vault closed)"
    yield
    # Cleanup: leave Obsidian in whatever state the test left it


@pytest.mark.integration
class TestObsidianAutoStart:
    """Integration tests for Obsidian auto-start."""

    def test_obsidian_not_running_starts_and_captures(self, ensure_obsidian_quit):
        """Test: Obsidian not running => starts Obsidian, opens vault, API available."""
        # Precondition: Obsidian is not running
        assert not is_obsidian_running()
        assert not is_api_available(TEST_API_KEY, TEST_API_PORT)

        # Act: ensure_obsidian_ready should start Obsidian and open vault
        result = ensure_obsidian_ready(
            TEST_VAULT_PATH,
            TEST_API_KEY,
            TEST_API_PORT,
            max_retries=10,
            retry_delay=1.0,
        )

        # Assert: Obsidian is running and API is available
        assert result is True, "ensure_obsidian_ready should return True"
        assert is_obsidian_running(), "Obsidian should be running"
        assert is_api_available(TEST_API_KEY, TEST_API_PORT), "API should be available"

    def test_obsidian_running_vault_closed_opens_and_captures(self, ensure_obsidian_running_without_vault):
        """Test: Obsidian running but vault closed => opens vault, API available."""
        # Precondition: Obsidian is running but API not available
        assert is_obsidian_running()
        assert not is_api_available(TEST_API_KEY, TEST_API_PORT)

        # Act: ensure_obsidian_ready should open the vault
        result = ensure_obsidian_ready(
            TEST_VAULT_PATH,
            TEST_API_KEY,
            TEST_API_PORT,
            max_retries=10,
            retry_delay=1.0,
        )

        # Assert: API is now available
        assert result is True, "ensure_obsidian_ready should return True"
        assert is_api_available(TEST_API_KEY, TEST_API_PORT), "API should be available"
