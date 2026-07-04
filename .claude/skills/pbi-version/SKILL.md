---
name: pbi-version
description: "Display the installed PBI skill version and full changelog history from the bundled CHANGELOG.md. Offline-only — never makes network calls. Shows complete release history with dates, features, and changes."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 7.1.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

# /pbi-version

<purpose>
Know what version is installed and what changed in each release. Useful for troubleshooting and understanding when a feature was added.
</purpose>

<core_principle>
Offline-only. Read from the bundled CHANGELOG.md — never make network calls. The /pbi-help command handles update checking separately.
</core_principle>

## Instructions

### Step 1 - Read current version

Run the Python version check against the base skill file (no shell text-processing — Python-first):

```bash
python ".claude/skills/pbi/scripts/detect.py" version-check ".claude/skills/pbi/SKILL.md" 2>/dev/null || echo "LOCAL=unknown"
```

If the output is `LOCAL=unknown`, retry against the user-level install path:

```bash
python "$HOME/.claude/skills/pbi/scripts/detect.py" version-check "$HOME/.claude/skills/pbi/SKILL.md" 2>/dev/null || echo "LOCAL=unknown"
```

Parse the output: LOCAL = installed version (e.g., 7.0.0).

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
