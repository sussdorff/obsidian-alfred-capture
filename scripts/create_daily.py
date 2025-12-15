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


def main() -> int:
    """Create today's daily note if it doesn't exist.

    Returns:
        0 on success, 1 on error.
    """
    try:
        config = Config.from_env()
        api = ObsidianAPI(config.api_key, config.api_port)
        capture = Capture(api, config)

        # Check if daily note already exists
        existing = api.get_daily_note()
        if existing is not None:
            print("Daily note already exists")
            return 0

        capture.ensure_daily_note()
        print("Daily note created")
        return 0
    except ObsidianAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
