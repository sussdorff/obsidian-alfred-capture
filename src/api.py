"""Obsidian Local REST API client."""

import urllib3
from typing import Optional

import requests

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ObsidianAPIError(Exception):
    """Exception raised for Obsidian API errors."""

    pass


class ObsidianAPI:
    """Client for Obsidian Local REST API.

    The Local REST API uses HTTPS with a self-signed certificate,
    so SSL verification is disabled.
    """

    def __init__(self, api_key: str, port: int = 27124):
        """Initialize the API client.

        Args:
            api_key: The API key from Local REST API settings.
            port: The port number (default 27124).
        """
        self.base_url = f"https://127.0.0.1:{port}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "text/markdown",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        content: str | None = None,
        extra_headers: dict | None = None,
    ) -> requests.Response:
        """Make a request to the API.

        Args:
            method: HTTP method (GET, PUT, PATCH, etc.)
            endpoint: API endpoint path.
            content: Optional request body content.
            extra_headers: Optional additional headers.

        Returns:
            The response object.

        Raises:
            ObsidianAPIError: If the request fails.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=content.encode("utf-8") if content else None,
                verify=False,  # Self-signed certificate
                timeout=10,
            )
            return response
        except requests.exceptions.ConnectionError as e:
            raise ObsidianAPIError(
                "Cannot connect to Obsidian. Is Obsidian running with Local REST API enabled?"
            ) from e
        except requests.exceptions.Timeout as e:
            raise ObsidianAPIError("Request to Obsidian timed out.") from e

    def get_daily_note(self) -> Optional[str]:
        """Get today's daily note content.

        Returns:
            The note content as string, or None if it doesn't exist.

        Raises:
            ObsidianAPIError: If the request fails (other than 404).
        """
        response = self._request("GET", "/periodic/daily/")

        if response.status_code == 404:
            return None
        if response.status_code == 200:
            return response.text
        raise ObsidianAPIError(
            f"Failed to get daily note: {response.status_code} - {response.text}"
        )

    def create_daily_note(self, content: str) -> bool:
        """Create today's daily note with given content.

        Args:
            content: The markdown content for the note.

        Returns:
            True if successful.

        Raises:
            ObsidianAPIError: If creation fails.
        """
        response = self._request("PUT", "/periodic/daily/", content=content)

        if response.status_code in (200, 201, 204):
            return True
        raise ObsidianAPIError(
            f"Failed to create daily note: {response.status_code} - {response.text}"
        )

    def append_to_heading(self, heading: str, content: str) -> bool:
        """Append content under specified heading in daily note.

        Uses PATCH with Heading-Target header to append content
        under a specific H2 heading.

        Args:
            heading: The heading name (without ##).
            content: The content to append.

        Returns:
            True if successful.

        Raises:
            ObsidianAPIError: If append fails.
        """
        extra_headers = {
            "Heading": heading,
            "Content-Insertion-Position": "end",
        }

        response = self._request(
            "PATCH",
            "/periodic/daily/",
            content=content,
            extra_headers=extra_headers,
        )

        if response.status_code in (200, 201, 204):
            return True
        raise ObsidianAPIError(
            f"Failed to append to heading '{heading}': {response.status_code} - {response.text}"
        )

    def is_connected(self) -> bool:
        """Check if we can connect to the Obsidian API.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            response = self._request("GET", "/")
            return response.status_code == 200
        except ObsidianAPIError:
            return False

    def open_daily_note(self) -> bool:
        """Open today's daily note in Obsidian.

        Returns:
            True if successful.

        Raises:
            ObsidianAPIError: If opening fails.
        """
        response = self._request("POST", "/open/periodic/daily/")

        if response.status_code in (200, 201, 204):
            return True
        raise ObsidianAPIError(
            f"Failed to open daily note: {response.status_code} - {response.text}"
        )
