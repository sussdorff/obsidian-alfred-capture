#!/usr/bin/env python3
"""Entry point for capturing tasks via Alfred.

Usage: python capture_task.py "task description"
       or: echo "task description" | python capture_task.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import ObsidianAPI, ObsidianAPIError
from src.capture import Capture
from src.config import Config
from src.obsidian import ensure_obsidian_ready


def main() -> int:
    """Capture a task to the daily note.

    Returns:
        0 on success, 1 on error.
    """
    # Get task text from args or stdin
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read().strip()

    if not text:
        print("Error: No task text provided")
        return 1

    try:
        config = Config.from_env()
        if not ensure_obsidian_ready(config.vault_path, config.api_key, config.api_port):
            print("Error: Could not connect to Obsidian API")
            return 1
        api = ObsidianAPI(config.api_key, config.api_port)
        capture = Capture(api, config)
        capture.task(text)
        print(f"Task captured: {text}")
        return 0
    except ObsidianAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
