"""Daily note creation and template handling."""

from datetime import datetime
from pathlib import Path

from .config import Config


def get_template_path() -> Path:
    """Get the path to the daily note template.

    Returns:
        Path to the template file.
    """
    # Look for template relative to the src directory
    src_dir = Path(__file__).parent
    project_root = src_dir.parent
    return project_root / "templates" / "daily_note_template.md"


def load_template() -> str:
    """Load the daily note template.

    Returns:
        The template content as string.

    Raises:
        FileNotFoundError: If template file doesn't exist.
    """
    template_path = get_template_path()
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")
    return template_path.read_text(encoding="utf-8")


def render_template(template: str, date: datetime | None = None) -> str:
    """Render the daily note template with date placeholders.

    Supported placeholders:
        - {date}: YYYY-MM-DD format
        - {year}: 4-digit year
        - {month}: Full month name
        - {day}: Day of month (no leading zero)
        - {weekday}: Full weekday name
        - {filename}: The filename (date format)

    Args:
        template: The template string with placeholders.
        date: The date to use. Defaults to today.

    Returns:
        The rendered template content.
    """
    if date is None:
        date = datetime.now()

    replacements = {
        "{date}": date.strftime("%Y-%m-%d"),
        "{year}": date.strftime("%Y"),
        "{month}": date.strftime("%B"),
        "{day}": str(date.day),
        "{weekday}": date.strftime("%A"),
        "{filename}": date.strftime("%Y-%m-%d"),
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def create_daily_note_content(config: Config, date: datetime | None = None) -> str:
    """Create daily note content from template.

    Args:
        config: Configuration object (for future custom template support).
        date: The date for the daily note. Defaults to today.

    Returns:
        The rendered daily note content.
    """
    template = load_template()
    return render_template(template, date)
