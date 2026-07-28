# Alfred Workflow Development - Learnings

## Workflow Structure

An `.alfredworkflow` file is just a ZIP archive containing:
- `info.plist` - The workflow configuration (XML plist format)
- Optional: `icon.png`, scripts, and other assets

The `info.plist` is the source file that should be version controlled. The `.alfredworkflow` is a build artifact.

## Variables: Two Systems

Alfred has **two separate systems** for variables:

### 1. `variables` dict - Runtime Values
```xml
<key>variables</key>
<dict>
    <key>MY_VAR</key>
    <string>value</string>
</dict>
```
- These are the **actual values** passed to scripts as environment variables
- Scripts access them as `$MY_VAR` (shell) or `os.environ["MY_VAR"]` (Python)

### 2. `userconfigurationconfig` - UI Configuration
```xml
<key>userconfigurationconfig</key>
<array>
    <dict>
        <key>config</key>
        <dict>
            <key>default</key>
            <string>default value</string>
            <key>placeholder</key>
            <string>hint text</string>
        </dict>
        <key>label</key>
        <string>My Variable</string>
        <key>variable</key>
        <string>MY_VAR</string>
    </dict>
</array>
```
- Defines the **configuration UI** shown to users
- The `default` field pre-fills the UI, but **does not automatically set the runtime variable**
- When user saves configuration, values are written to `variables` dict

**Key insight:** You need BOTH for a complete workflow:
- `variables` for runtime defaults
- `userconfigurationconfig` for the UI with matching defaults

## Variable Expansion in Scripts

### What DOES NOT work: `{var:...}` placeholders in shell scripts
```bash
# WRONG - {var:...} is NOT expanded in shell scripts
cd "{var:workflow_dir}"  # Results in literal "{var:workflow_dir}"
```

### What WORKS: Environment variables
```bash
# CORRECT - Alfred passes variables as environment variables
cd "$workflow_dir"
```

### `{query}` is special
The `{query}` placeholder IS expanded by Alfred before the script runs:
```bash
# This works - Alfred replaces {query} with the user input
python script.py "{query}"
```

## Script Configuration in plist

```xml
<dict>
    <key>config</key>
    <dict>
        <key>script</key>
        <string>#!/bin/bash
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
cd "$workflow_dir"
.venv/bin/python scripts/capture.py "{query}"</string>
        <key>type</key>
        <integer>0</integer>  <!-- 0 = /bin/bash -->
    </dict>
    <key>type</key>
    <string>alfred.workflow.action.script</string>
</dict>
```

## Python Script Integration

### Environment Variables
Alfred workflow variables are passed as environment variables:
```python
import os

workflow_dir = os.environ.get("workflow_dir")
api_key = os.environ.get("OBSIDIAN_API_KEY")
```

### Working Directory
Scripts run from Alfred's cache directory, NOT the workflow directory:
```
/Users/xxx/Library/Caches/com.runningwithcrayons.Alfred/Workflow Scripts/
```

Always `cd` to the workflow directory before running Python scripts that have relative imports.

### Path Setup
System Python paths may not include homebrew. Always set PATH:
```bash
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
```

## Debugging

Add logging to diagnose issues:
```bash
#!/bin/bash
echo "=== Debug ===" >> /tmp/workflow-debug.log
echo "workflow_dir: $workflow_dir" >> /tmp/workflow-debug.log
echo "pwd: $(pwd)" >> /tmp/workflow-debug.log
cd "$workflow_dir" 2>> /tmp/workflow-debug.log
.venv/bin/python script.py "{query}" >> /tmp/workflow-debug.log 2>&1
echo "exit: $?" >> /tmp/workflow-debug.log
```

## Validating plist Files

```bash
# Syntax validation
plutil -lint info.plist

# View as readable format
plutil -p info.plist

# Modify values
plutil -replace variables.MY_VAR -string "value" info.plist
```

## Build Process

For a workflow with pre-configured defaults:

```bash
# 1. Copy source plist
cp alfred/workflow/info.plist /tmp/build/info.plist

# 2. Set runtime variables
plutil -replace variables.workflow_dir -string "/path/to/project" /tmp/build/info.plist

# 3. Set UI defaults (so they show in configuration)
plutil -replace userconfigurationconfig.0.config.default -string "/path/to/project" /tmp/build/info.plist

# 4. Package
cd /tmp/build && zip -r "MyWorkflow.alfredworkflow" info.plist
```

## Common Pitfalls

1. **Empty variables:** Setting only `userconfigurationconfig` defaults without `variables` dict
2. **Wrong placeholder syntax:** Using `{var:name}` instead of `$name` in shell scripts
3. **Missing PATH:** Python/homebrew commands not found
4. **Wrong working directory:** Relative paths fail because scripts run from Alfred's cache
5. **Forgetting to rebuild:** Testing old workflow after making plist changes
