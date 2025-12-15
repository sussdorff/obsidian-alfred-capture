# Obsidian Alfred Capture

Quick capture to Obsidian daily notes from anywhere on macOS using Alfred and the Local REST API.

## Features

- **Quick Task** (`jt`) - Capture tasks as `- [ ] text`
- **Quick Idea** (`ji`) - Capture ideas as bullets
- **Quick Journal** (`jj`) - Timestamped journal entries
- **Browser Bookmark** - Capture current tab as markdown link
- **Auto-create daily note** - Creates from template if missing

## Requirements

- macOS
- [Alfred 5](https://www.alfredapp.com/) with Powerpack
- [Obsidian](https://obsidian.md/) with [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin
- Python 3.11+

## Installation

1. Install the Local REST API plugin in Obsidian
2. Enable the plugin and copy your API key
3. Download the latest `.alfredworkflow` from releases
4. Double-click to install in Alfred
5. Configure the workflow variables (vault path, API key, etc.)

## Usage

| Command | Action |
|---------|--------|
| `jt buy milk` | Add task to daily note |
| `ji app idea` | Add idea to daily note |
| `jj met with client` | Add timestamped journal entry |
| `Cmd+Shift+B` | Capture current browser tab |

## Daily Note Template

The workflow expects these H2 headings in your daily note:

```markdown
## Todo
## Ideas
## Journal
## Bookmarks
```

See `templates/daily_note_template.md` for a complete example.

## Configuration

Set these variables in Alfred workflow configuration:

| Variable | Description |
|----------|-------------|
| `OBSIDIAN_API_KEY` | Your Local REST API key |
| `VAULT_PATH` | Full path to your Obsidian vault |
| `DAILY_NOTE_FOLDER` | Folder for daily notes (e.g., `10-Daily`) |
| `DAILY_NOTE_FORMAT` | Python strftime format (e.g., `%Y-%m-%d`) |

## License

MIT
