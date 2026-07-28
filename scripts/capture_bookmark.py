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
from src.obsidian import ensure_obsidian_ready

# AppleScript templates for each browser
BROWSER_SCRIPTS = {
    "Arc": '''
        tell application "Arc"
            if (count of windows) > 0 then
                set tabTitle to title of active tab of window 1
                set tabURL to URL of active tab of window 1
                return tabTitle & "\n" & tabURL
            end if
        end tell
        return ""
    ''',
    "Google Chrome": '''
        tell application "Google Chrome"
            if (count of windows) > 0 then
                set tabTitle to title of active tab of window 1
                set tabURL to URL of active tab of window 1
                return tabTitle & "\n" & tabURL
            end if
        end tell
        return ""
    ''',
    "Safari": '''
        tell application "Safari"
            if (count of windows) > 0 then
                set tabTitle to name of current tab of window 1
                set tabURL to URL of current tab of window 1
                return tabTitle & "\n" & tabURL
            end if
        end tell
        return ""
    ''',
    "Zen Browser": '''
        tell application "Zen Browser"
            if (count of windows) > 0 then
                set tabTitle to name of front window
                set tabURL to URL of front document
                return tabTitle & "\n" & tabURL
            end if
        end tell
        return ""
    ''',
    "Firefox": '''
        tell application "Firefox"
            if (count of windows) > 0 then
                set tabTitle to name of front window
                set tabURL to URL of front document
                return tabTitle & "\n" & tabURL
            end if
        end tell
        return ""
    ''',
}

# Check which browsers are running
CHECK_RUNNING_SCRIPT = '''
tell application "System Events"
    set runningApps to name of every process
end tell
return runningApps
'''


def get_running_browsers() -> list[str]:
    """Get list of running browser apps."""
    try:
        result = subprocess.run(
            ["osascript", "-e", CHECK_RUNNING_SCRIPT],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            running = result.stdout.strip()
            return [b for b in BROWSER_SCRIPTS.keys() if b in running]
    except Exception:
        pass
    return []


def get_browser_tab() -> tuple[str, str] | None:
    """Get the current browser tab title and URL.

    Tries each running browser until one returns a valid URL.

    Returns:
        Tuple of (title, url) or None if failed.
    """
    running_browsers = get_running_browsers()

    if not running_browsers:
        print("Error: No supported browser is running")
        return None

    for browser in running_browsers:
        try:
            script = BROWSER_SCRIPTS[browser]
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    lines = output.split("\n")
                    if len(lines) >= 2 and lines[1]:
                        return lines[0], lines[1]
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue

    print("Error: Could not get URL from any running browser")
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
        if not ensure_obsidian_ready(config.vault_path, config.api_key, config.api_port):
            print("Error: Could not connect to Obsidian API")
            return 1
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
