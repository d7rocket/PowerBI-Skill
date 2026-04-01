---
name: pbi:settings
description: "Manage write mode — toggle between auto (no confirmation) and confirm (ask before every file write). Shows current settings when invoked with no arguments."
model: sonnet
allowed-tools: Bash, Read
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.1.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection

### PBI Directory Setup
!`python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null && python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null`

### Settings
!`python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"`

Save the `PBI_CONFIRM` value — this is the current write mode setting.

---

# /pbi:settings

## Instructions

Parse the argument after `settings`:

- `auto` → Run: `python ".claude/skills/pbi/scripts/detect.py" settings-set confirm_writes false`
  - If exit code ≠ 0: output the error message and stop.
  - On success: Output `Write mode set to **auto** — changes will be applied without confirmation.`

- `confirm` → Run: `python ".claude/skills/pbi/scripts/detect.py" settings-set confirm_writes true`
  - If exit code ≠ 0: output the error message and stop.
  - On success: Output `Write mode set to **confirm** — you'll be asked before every file write.`

- No argument → Read current PBI_CONFIRM value from Settings detection output.
  Output:
  ```
  **Current settings**
  Write mode: [auto or confirm] (stored in .pbi/settings.json)

  `/pbi settings auto` — apply changes without asking
  `/pbi settings confirm` — ask before every file write
  ```

Stop. Do not proceed to any other handler.

## Shared Rules

- Settings are stored in `.pbi/settings.json`. Use `detect.py settings-set` to write them — never edit the JSON file directly.
- `PBI_CONFIRM=true` means confirm mode (default). `PBI_CONFIRM=false` means auto mode.
