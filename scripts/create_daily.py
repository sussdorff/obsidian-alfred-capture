#!/usr/bin/env python3
"""Entry point for creating daily note via Alfred.

Usage: python create_daily.py
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
    """Create today's daily note if needed and open it in Obsidian.

    Returns:
        0 on success, 1 on error.
    """
    try:
        config = Config.from_env()
        if not ensure_obsidian_ready(config.vault_path, config.api_key, config.api_port):
            print("Error: Could not connect to Obsidian API")
            return 1
        api = ObsidianAPI(config.api_key, config.api_port)
        capture = Capture(api, config)

        # Ensure daily note exists
        capture.ensure_daily_note()

        # Open the daily note in Obsidian
        api.open_daily_note()
        print("Daily note opened")
        return 0
    except ObsidianAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
