"""Obsidian app utilities."""

import subprocess
import time
from urllib.parse import quote

import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def is_obsidian_running() -> bool:
    """Check if Obsidian is currently running."""
    result = subprocess.run(
        ["pgrep", "-x", "Obsidian"],
        capture_output=True,
    )
    return result.returncode == 0


def is_api_available(api_key: str, port: int) -> bool:
    """Check if the Obsidian REST API is responding.

    This implicitly checks that:
    - Obsidian is running
    - The vault with REST API plugin is open
    - The REST API is enabled and responding

    Args:
        api_key: The API key for authentication.
        port: The API port number.

    Returns:
        True if the API is available, False otherwise.
    """
    try:
        response = requests.get(
            f"https://127.0.0.1:{port}/",
            headers={"Authorization": f"Bearer {api_key}"},
            verify=False,
            timeout=2,
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def open_vault(vault_path: str) -> None:
    """Open a vault in Obsidian using the obsidian:// URL scheme.

    Args:
        vault_path: Path to the Obsidian vault.
    """
    encoded_path = quote(vault_path, safe="")
    subprocess.run(
        ["open", f"obsidian://open?path={encoded_path}"],
        capture_output=True,
    )


def ensure_obsidian_ready(
    vault_path: str,
    api_key: str,
    port: int,
    max_retries: int = 5,
    retry_delay: float = 1.0,
) -> bool:
    """Ensure Obsidian is running with the vault open and API available.

    If the API is not available, attempts to open the vault and waits
    for the API to become ready.

    Args:
        vault_path: Path to the Obsidian vault.
        api_key: The API key for authentication.
        port: The API port number.
        max_retries: Maximum number of retries to wait for API.
        retry_delay: Seconds to wait between retries.

    Returns:
        True if the API is available, False if it couldn't be reached.
    """
    # First check if API is already available
    if is_api_available(api_key, port):
        return True

    # API not available - try to open the vault
    if not vault_path:
        return False

    open_vault(vault_path)

    # Wait for API to become available
    for _ in range(max_retries):
        time.sleep(retry_delay)
        if is_api_available(api_key, port):
            return True

    return False
