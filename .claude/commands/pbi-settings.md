---
name: pbi:settings
description: "Manage write mode — toggle between auto (no confirmation) and confirm (ask before every file write)"
allowed-tools:
  - Bash
---

## Detection

Run the following detection command using the Bash tool before proceeding:

```bash
python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"
```

Save the `PBI_CONFIRM` value — this is the current write mode.

---

# /pbi-settings

## Instructions

Parse the argument after `settings` (from `$ARGUMENTS`):

- `auto` → Run: `python ".claude/skills/pbi/scripts/detect.py" settings-set confirm_writes false 2>/dev/null`
  Output: `Write mode set to **auto** — changes will be applied without confirmation.`

- `confirm` → Run: `python ".claude/skills/pbi/scripts/detect.py" settings-set confirm_writes true 2>/dev/null`
  Output: `Write mode set to **confirm** — you'll be asked before every file write.`

- No argument → Read current PBI_CONFIRM value from the detection output above.
  Output:
  ```
  **Current settings**
  Write mode: [auto or confirm] (stored in .pbi/settings.json)

  `/pbi settings auto` — apply changes without asking
  `/pbi settings confirm` — ask before every file write
  ```

Stop. Do not proceed to any other handler.

### Anti-Patterns
- NEVER edit `.pbi/settings.json` directly — always use `detect.py settings-set`
- NEVER apply a setting without confirming the change in output
