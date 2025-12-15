"""Tests for Obsidian API client."""

from unittest import mock

import pytest
import requests

from src.api import ObsidianAPI, ObsidianAPIError


class TestObsidianAPI:
    """Tests for ObsidianAPI class."""

    @pytest.fixture
    def api(self):
        """Create an API client for testing."""
        return ObsidianAPI("test-api-key", port=27124)

    def test_init_sets_base_url_and_headers(self, api):
        """Test that initialization sets up base URL and headers."""
        assert api.base_url == "https://127.0.0.1:27124"
        assert api.headers["Authorization"] == "Bearer test-api-key"
        assert api.headers["Content-Type"] == "text/markdown"

    def test_get_daily_note_success(self, api):
        """Test getting daily note content."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = "# Daily Note\n\nContent here"

        with mock.patch("requests.request", return_value=mock_response):
            result = api.get_daily_note()

        assert result == "# Daily Note\n\nContent here"

    def test_get_daily_note_not_found(self, api):
        """Test getting daily note when it doesn't exist."""
        mock_response = mock.Mock()
        mock_response.status_code = 404

        with mock.patch("requests.request", return_value=mock_response):
            result = api.get_daily_note()

        assert result is None

    def test_get_daily_note_error(self, api):
        """Test getting daily note with API error."""
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with mock.patch("requests.request", return_value=mock_response):
            with pytest.raises(ObsidianAPIError, match="Failed to get daily note"):
                api.get_daily_note()

    def test_create_daily_note_success(self, api):
        """Test creating daily note."""
        mock_response = mock.Mock()
        mock_response.status_code = 201

        with mock.patch("requests.request", return_value=mock_response) as mock_req:
            result = api.create_daily_note("# New Note")

        assert result is True
        mock_req.assert_called_once()
        call_kwargs = mock_req.call_args[1]
        assert call_kwargs["method"] == "PUT"
        assert call_kwargs["data"] == b"# New Note"

    def test_create_daily_note_error(self, api):
        """Test creating daily note with error."""
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.text = "Failed"

        with mock.patch("requests.request", return_value=mock_response):
            with pytest.raises(ObsidianAPIError, match="Failed to create daily note"):
                api.create_daily_note("content")

    def test_append_to_heading_success(self, api):
        """Test appending content to heading."""
        mock_response = mock.Mock()
        mock_response.status_code = 200

        with mock.patch("requests.request", return_value=mock_response) as mock_req:
            result = api.append_to_heading("Todo", "- [ ] New task")

        assert result is True
        mock_req.assert_called_once()
        call_kwargs = mock_req.call_args[1]
        assert call_kwargs["method"] == "PATCH"
        assert call_kwargs["headers"]["Heading"] == "Todo"
        assert call_kwargs["headers"]["Content-Insertion-Position"] == "end"
        assert call_kwargs["data"] == b"- [ ] New task"

    def test_append_to_heading_error(self, api):
        """Test appending to heading with error."""
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.text = "Heading not found"

        with mock.patch("requests.request", return_value=mock_response):
            with pytest.raises(ObsidianAPIError, match="Failed to append"):
                api.append_to_heading("NonExistent", "content")

    def test_connection_error(self, api):
        """Test handling connection errors."""
        with mock.patch(
            "requests.request",
            side_effect=requests.exceptions.ConnectionError(),
        ):
            with pytest.raises(ObsidianAPIError, match="Cannot connect"):
                api.get_daily_note()

    def test_timeout_error(self, api):
        """Test handling timeout errors."""
        with mock.patch(
            "requests.request",
            side_effect=requests.exceptions.Timeout(),
        ):
            with pytest.raises(ObsidianAPIError, match="timed out"):
                api.get_daily_note()

    def test_is_connected_success(self, api):
        """Test connection check success."""
        mock_response = mock.Mock()
        mock_response.status_code = 200

        with mock.patch("requests.request", return_value=mock_response):
            assert api.is_connected() is True

    def test_is_connected_failure(self, api):
        """Test connection check failure."""
        with mock.patch(
            "requests.request",
            side_effect=requests.exceptions.ConnectionError(),
        ):
            assert api.is_connected() is False
