#!/usr/bin/env python3
"""Entry point for capturing browser bookmarks via Alfred hotkey.

This script gets the current browser tab (Safari, Chrome, Arc, or Zen)
and captures it as a bookmark to the daily note.

Usage: python capture_bookmark.py
"""

import subprocess
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import ObsidianAPI, ObsidianAPIError
from src.capture import Capture
from src.config import Config

# AppleScript to get the frontmost browser's current tab
APPLESCRIPT = '''
tell application "System Events"
    set frontApp to name of first process whose frontmost is true
end tell

if frontApp is "Safari" then
    tell application "Safari"
        set tabTitle to name of current tab of window 1
        set tabURL to URL of current tab of window 1
    end tell
else if frontApp is "Google Chrome" then
    tell application "Google Chrome"
        set tabTitle to title of active tab of window 1
        set tabURL to URL of active tab of window 1
    end tell
else if frontApp is "Arc" then
    tell application "Arc"
        set tabTitle to title of active tab of window 1
        set tabURL to URL of active tab of window 1
    end tell
else if frontApp is "Zen Browser" then
    -- Zen Browser is Firefox-based, uses similar AppleScript interface
    tell application "Zen Browser"
        set tabTitle to name of front window
        set tabURL to URL of front document
    end tell
else if frontApp is "Firefox" then
    tell application "Firefox"
        set tabTitle to name of front window
        set tabURL to URL of front document
    end tell
else
    error "Unsupported browser: " & frontApp
end if

return tabTitle & "\n" & tabURL
'''


def get_browser_tab() -> tuple[str, str] | None:
    """Get the current browser tab title and URL.

    Returns:
        Tuple of (title, url) or None if failed.
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", APPLESCRIPT],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            error = result.stderr.strip()
            if "Unsupported browser" in error:
                print(f"Error: {error}")
            else:
                print(f"Error getting browser tab: {error}")
            return None

        output = result.stdout.strip()
        lines = output.split("\n")
        if len(lines) >= 2:
            title = lines[0]
            url = lines[1]
            return title, url

        return None
    except subprocess.TimeoutExpired:
        print("Error: Timeout getting browser tab")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main() -> int:
    """Capture the current browser tab as a bookmark.

    Returns:
        0 on success, 1 on error.
    """
    tab_info = get_browser_tab()
    if tab_info is None:
        return 1

    title, url = tab_info

    if not url:
        print("Error: Could not get URL from browser")
        return 1

    try:
        config = Config.from_env()
        api = ObsidianAPI(config.api_key, config.api_port)
        capture = Capture(api, config)
        capture.bookmark(title or url, url)
        print(f"Bookmark captured: {title}")
        return 0
    except ObsidianAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
