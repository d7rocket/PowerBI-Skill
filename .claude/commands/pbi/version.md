---
name: pbi:version
description: "Display installed version and full changelog history (offline-only)"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

## Detection

Run ALL of the following detection commands using the Bash tool before proceeding. Save the output — subsequent steps reference these values.

Ensure .pbi/ directory exists and migrate legacy root-level files.
```bash
python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null
python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."
```

Save the PBI_CONFIRM value — use it to decide whether to ask before writing files.
```bash
python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"
```

### Auto-Resume (session-aware)

After detection, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null
   ```
   - If output is `SESSION=active` — context was already loaded this session: skip any reload.
   - If output is `SESSION=new` — first command this session: write `**Session-Start:** [current UTC time in ISO 8601]` to `.pbi/context.md` if a PBIP project is active. Proceed normally.

2. **PBIP_MODE=paste — nearby folder check**: skip silently for version command.

After auto-resume completes, proceed to the command instructions below.

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
