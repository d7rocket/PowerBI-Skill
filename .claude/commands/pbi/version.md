---
name: pbi:version
description: "Display version history and changelog"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

# /pbi:version


## Instructions

### Step 1 - Read current version

Run the following bash command to locate the skill file and read the installed version:

```bash
SKILL_FILE=$(find . -path "*/.claude/skills/pbi/SKILL.md" -print -quit 2>/dev/null)
if [ -z "$SKILL_FILE" ]; then SKILL_FILE=$(find "$HOME" -maxdepth 5 -path "*/.claude/skills/pbi/SKILL.md" -print -quit 2>/dev/null); fi
python ".claude/skills/pbi/scripts/detect.py" version-check "$SKILL_FILE" 2>/dev/null || echo "LOCAL=unknown"
```

Parse the output: LOCAL = installed version (e.g., 4.3.0).

### Step 2 - Read CHANGELOG.md

Use the Read tool to load .claude/skills/pbi/shared/CHANGELOG.md

If the file is not found at that path, try ~/.claude/skills/pbi/shared/CHANGELOG.md

If neither path exists, output:
  PBI Skill - Version LOCAL
  Changelog not available - re-run the installer to download CHANGELOG.md.
Then stop.

### Step 3 - Output version header and changelog

Output the following, substituting LOCAL from Step 1 and the full CHANGELOG.md content from Step 2:

**PBI Skill - Version LOCAL**

[full content of CHANGELOG.md, printed verbatim]

Stop. Do not output anything else.

### Anti-Patterns
- NEVER make network calls or check for updates - this command is offline-only
- NEVER use cat or bash redirection to read CHANGELOG.md - always use the Read tool
- NEVER output anything after the changelog - stop immediately