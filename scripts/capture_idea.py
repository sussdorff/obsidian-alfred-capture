#!/usr/bin/env python3
"""Entry point for capturing ideas via Alfred.

Usage: python capture_idea.py "idea text"
       or: echo "idea text" | python capture_idea.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import ObsidianAPI, ObsidianAPIError
from src.capture import Capture
from src.config import Config


def main() -> int:
    """Capture an idea to the daily note.

    Returns:
        0 on success, 1 on error.
    """
    # Get idea text from args or stdin
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read().strip()

    if not text:
        print("Error: No idea text provided")
        return 1

    try:
        config = Config.from_env()
        api = ObsidianAPI(config.api_key, config.api_port)
        capture = Capture(api, config)
        capture.idea(text)
        print(f"Idea captured: {text}")
        return 0
    except ObsidianAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
