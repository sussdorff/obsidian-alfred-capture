# Obsidian Alfred Capture - Implementation Plan

## Overview

An Alfred workflow for quick capture to Obsidian daily notes using the Local REST API plugin. Designed for frictionless task, idea, journal, and bookmark capture without switching focus from current work.

---

## Goals

1. **Quick capture from anywhere** - No need to open Obsidian
2. **Proper formatting** - Tasks as `- [ ]`, journal with timestamps, ideas as bullets
3. **Heading-aware insertion** - Content goes under specific H2 headings
4. **Auto-create daily note** - If it doesn't exist, create from template
5. **Browser integration** - Capture current tab as bookmark
6. **Zero friction** - Single keystroke + type + enter

---

## Dependencies

### Required Obsidian Plugins
- **Local REST API** - Provides the REST endpoints
- **Periodic Notes** (optional) - For daily note template support

### System Requirements
- macOS
- Alfred 5 (with Powerpack)
- Python 3.9+
- Obsidian with Local REST API plugin enabled

---

## Architecture

```
obsidian-alfred-capture/
├── README.md                    # Setup instructions
├── IMPLEMENTATION_PLAN.md       # This file
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration handling
│   ├── api.py                  # Obsidian REST API client
│   ├── capture.py              # Capture logic (task, idea, journal, bookmark)
│   └── daily_note.py           # Daily note creation/template handling
├── scripts/
│   ├── capture_task.py         # Entry point: jt
│   ├── capture_idea.py         # Entry point: ji
│   ├── capture_journal.py      # Entry point: jj
│   ├── capture_bookmark.py     # Entry point: browser hotkey
│   └── create_daily.py         # Entry point: create daily note
├── alfred/
│   └── Obsidian Capture.alfredworkflow  # Packaged workflow
├── templates/
│   └── daily_note_template.md  # Default daily note template
├── tests/
│   ├── test_api.py
│   ├── test_capture.py
│   └── test_daily_note.py
├── pyproject.toml              # Python project config
└── .env.example                # Example configuration
```

---

## Configuration

### Environment Variables (stored in Alfred workflow)

| Variable | Description | Example |
|----------|-------------|---------|
| `OBSIDIAN_API_KEY` | Local REST API key | `abc123...` |
| `OBSIDIAN_API_PORT` | API port (default 27124) | `27124` |
| `VAULT_PATH` | Path to vault | `/Users/malte/Library/Mobile Documents/iCloud~md~obsidian/Documents/Orbis Sapiens` |
| `DAILY_NOTE_FOLDER` | Daily note location | `10-Daily` |
| `DAILY_NOTE_FORMAT` | Date format | `%Y-%m-%d` |

### Heading Configuration

| Capture Type | Target Heading | Format |
|--------------|----------------|--------|
| Task | `## Todo` | `- [ ] {text}` |
| Idea | `## Ideas` | `- {text}` |
| Journal | `## Journal` | `- {HH:MM} {text}` |
| Bookmark | `## Bookmarks` | `- [{title}]({url})` |

---

## API Integration

### Endpoints Used

1. **Check if daily note exists**
   ```
   GET /periodic/daily/
   ```

2. **Create daily note**
   ```
   PUT /periodic/daily/
   Content-Type: text/markdown
   Body: {template content}
   ```

3. **Append under heading**
   ```
   PATCH /periodic/daily/
   Headers:
     Operation: append
     Target-Type: heading
     Target: {heading name}
   Body: {formatted content}
   ```

### API Client (src/api.py)

```python
class ObsidianAPI:
    def __init__(self, api_key: str, port: int = 27124):
        self.base_url = f"https://127.0.0.1:{port}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_daily_note(self) -> Optional[str]:
        """Get today's daily note content, or None if doesn't exist."""

    def create_daily_note(self, content: str) -> bool:
        """Create today's daily note with given content."""

    def append_to_heading(self, heading: str, content: str) -> bool:
        """Append content under specified heading in daily note."""
```

---

## Capture Logic (src/capture.py)

```python
class Capture:
    def __init__(self, api: ObsidianAPI, config: Config):
        self.api = api
        self.config = config

    def ensure_daily_note(self) -> bool:
        """Create daily note from template if it doesn't exist."""

    def task(self, text: str) -> bool:
        """Capture as task: - [ ] {text}"""
        self.ensure_daily_note()
        return self.api.append_to_heading("Todo", f"- [ ] {text}")

    def idea(self, text: str) -> bool:
        """Capture as idea: - {text}"""
        self.ensure_daily_note()
        return self.api.append_to_heading("Ideas", f"- {text}")

    def journal(self, text: str) -> bool:
        """Capture as journal: - {HH:MM} {text}"""
        self.ensure_daily_note()
        timestamp = datetime.now().strftime("%H:%M")
        return self.api.append_to_heading("Journal", f"- {timestamp} {text}")

    def bookmark(self, title: str, url: str) -> bool:
        """Capture as bookmark: - [{title}]({url})"""
        self.ensure_daily_note()
        return self.api.append_to_heading("Bookmarks", f"- [{title}]({url})")
```

---

## Alfred Workflow Structure

### Keywords

| Keyword | Script | Description |
|---------|--------|-------------|
| `jt` | `capture_task.py` | Quick task |
| `ji` | `capture_idea.py` | Quick idea |
| `jj` | `capture_journal.py` | Quick journal |
| `jd` | `create_daily.py` | Create/open daily note |

### Hotkeys

| Hotkey | Action | Description |
|--------|--------|-------------|
| `Cmd+Shift+T` | Run `capture_task.py` with clipboard | Task from clipboard |
| `Cmd+Shift+B` | Run `capture_bookmark.py` | Capture browser tab |

### Browser Bookmark Capture

Uses AppleScript/JXA to get current browser tab (Safari, Chrome, Arc, Zen):

```applescript
tell application "System Events"
    set frontApp to name of first process whose frontmost is true
end tell

if frontApp is "Safari" then
    tell application "Safari"
        set tabTitle to name of current tab of window 1
        set tabURL to URL of current tab of window 1
    end tell
else if frontApp is "Google Chrome" then
    -- Chrome handling
else if frontApp is "Arc" then
    -- Arc handling
else if frontApp is "Zen Browser" then
    -- Zen handling (Firefox-based)
end if
```

---

## Daily Note Template

```markdown
---
created: {date}
type: daily
---

# {weekday}, {month} {day}, {year}

## Today's Tasks
\```tasks
not done
(due on {date}) OR (scheduled on {date})
\```

## Todo
<!-- Quick tasks captured here -->


## Ideas
<!-- Quick ideas captured here -->


## Journal
<!-- Timestamped entries captured here -->


## Bookmarks
<!-- Browser captures here -->


## Other Tasks Created Today
\```tasks
created on {date}
not done
path does not include {filename}
\```

## Completed Today
\```tasks
done on {date}
\```

---
## End of Day
- [ ] Process Inbox items
- [ ] Review tomorrow's calendar
```

---

## Implementation Phases

### Phase 1: Core API Client
- [ ] Set up Python project structure
- [ ] Implement `ObsidianAPI` class
- [ ] Test connection and authentication
- [ ] Implement `get_daily_note()`, `create_daily_note()`, `append_to_heading()`

### Phase 2: Capture Logic
- [ ] Implement `Capture` class
- [ ] Add task, idea, journal, bookmark methods
- [ ] Implement `ensure_daily_note()` with template support
- [ ] Add error handling and user feedback

### Phase 3: Alfred Integration
- [ ] Create entry point scripts (`capture_task.py`, etc.)
- [ ] Build Alfred workflow with keywords
- [ ] Configure environment variables in workflow
- [ ] Test all capture types

### Phase 4: Browser Integration
- [ ] Implement browser tab capture (Safari, Chrome, Arc, Zen)
- [ ] Add hotkey for bookmark capture
- [ ] Test with different browsers

### Phase 5: Polish
- [ ] Add Alfred notifications for success/failure
- [ ] Write README with setup instructions
- [ ] Package as `.alfredworkflow` file
- [ ] Create GitHub release

---

## Testing

### Manual Test Cases

1. **Daily note doesn't exist**
   - Run `jt test task`
   - Verify daily note created with template
   - Verify task appears under `## Todo`

2. **Daily note exists**
   - Run `ji test idea`
   - Verify idea appended under `## Ideas`
   - Verify no duplicate daily note created

3. **Journal with timestamp**
   - Run `jj something happened`
   - Verify entry has correct timestamp format

4. **Bookmark capture**
   - Open Safari/Chrome/Zen to a page
   - Press bookmark hotkey
   - Verify link appears under `## Bookmarks`

5. **Error handling**
   - Stop Obsidian
   - Run capture command
   - Verify user-friendly error notification

---

## Future Enhancements

- [ ] Quick capture to specific project notes (not just daily)
- [ ] Capture with tags (`jt #work call client`)
- [ ] Due date parsing (`jt call client tomorrow`)
- [ ] Integration with Shimmering Obsidian for search
- [ ] iOS Shortcuts integration via REST API
- [ ] Raycast extension port

---

## Resources

- [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Alfred Workflow Documentation](https://www.alfredapp.com/help/workflows/)
- [Shimmering Obsidian](https://github.com/chrisgrieser/shimmering-obsidian) (for search integration)

---

## Notes

- SSL verification disabled for localhost (`--insecure` / `verify=False`) as Local REST API uses self-signed cert
- Daily note path: `{DAILY_NOTE_FOLDER}/{DAILY_NOTE_FORMAT}.md`
- All timestamps in 24-hour format

---

*Created: 2024-12-14*
*Status: Ready for Implementation*
