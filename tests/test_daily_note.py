"""Tests for daily note creation and template handling."""

from datetime import datetime
from unittest import mock

import pytest

from src.daily_note import load_template, render_template, get_template_path


class TestDailyNote:
    """Tests for daily note functions."""

    def test_get_template_path(self):
        """Test that template path is correctly constructed."""
        path = get_template_path()
        assert path.name == "daily_note_template.md"
        assert "templates" in str(path)

    def test_load_template_success(self):
        """Test loading template file."""
        template = load_template()
        assert "## Todo" in template
        assert "## Ideas" in template
        assert "## Journal" in template
        assert "## Bookmarks" in template

    def test_render_template_date_placeholder(self):
        """Test rendering date placeholder."""
        template = "Date: {date}"
        date = datetime(2024, 12, 15)

        result = render_template(template, date)

        assert result == "Date: 2024-12-15"

    def test_render_template_year_placeholder(self):
        """Test rendering year placeholder."""
        template = "Year: {year}"
        date = datetime(2024, 12, 15)

        result = render_template(template, date)

        assert result == "Year: 2024"

    def test_render_template_month_placeholder(self):
        """Test rendering month placeholder."""
        template = "Month: {month}"
        date = datetime(2024, 12, 15)

        result = render_template(template, date)

        assert result == "Month: December"

    def test_render_template_day_placeholder(self):
        """Test rendering day placeholder."""
        template = "Day: {day}"
        date = datetime(2024, 12, 5)

        result = render_template(template, date)

        assert result == "Day: 5"  # No leading zero

    def test_render_template_weekday_placeholder(self):
        """Test rendering weekday placeholder."""
        template = "Weekday: {weekday}"
        date = datetime(2024, 12, 15)  # Sunday

        result = render_template(template, date)

        assert result == "Weekday: Sunday"

    def test_render_template_filename_placeholder(self):
        """Test rendering filename placeholder."""
        template = "File: {filename}"
        date = datetime(2024, 12, 15)

        result = render_template(template, date)

        assert result == "File: 2024-12-15"

    def test_render_template_all_placeholders(self):
        """Test rendering template with all placeholders."""
        template = """---
created: {date}
---

# {weekday}, {month} {day}, {year}

{filename}
"""
        date = datetime(2024, 12, 15)

        result = render_template(template, date)

        expected = """---
created: 2024-12-15
---

# Sunday, December 15, 2024

2024-12-15
"""
        assert result == expected

    def test_render_template_default_date(self):
        """Test that render_template uses today's date by default."""
        template = "{date}"

        with mock.patch("src.daily_note.datetime") as mock_dt:
            mock_now = datetime(2024, 12, 15)
            mock_dt.now.return_value = mock_now

            result = render_template(template)

        assert result == "2024-12-15"
