# Phase 5: Installer Overhaul - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-23
**Phase:** 05-installer-overhaul
**Areas discussed:** Default scope, File manifest, Update behavior, GitHub source URL

---

## Default Scope

| Option | Description | Selected |
|--------|-------------|----------|
| user (Recommended) | Installs to ~/.claude/skills/pbi/ — one install, all projects get it | ✓ |
| project | Installs to ./.claude/skills/pbi/ — per-repo copy | |
| Ask during install | Prompt interactively if no -Scope passed | |

**User's choice:** user (Recommended)
**Notes:** User asked for clarification on what "per-project versions" means. Clarified that skill output (.pbi-context.md, diffs, etc.) always writes to the current project regardless of scope — scope only affects where skill source files live.

---

## File Manifest

| Option | Description | Selected |
|--------|-------------|----------|
| manifest.json in repo | JSON file lists all skill files, installer reads it first | |
| Hardcoded but complete | Keep list in install.ps1, ensure everything included | |
| You decide | Claude picks most maintainable approach | ✓ |

**User's choice:** You decide
**Notes:** None

---

## Update Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Overwrite all | Always replace every file, local edits lost | ✓ |
| Backup then overwrite | Create .bak copies before overwriting | |
| You decide | Claude picks safest approach | |

**User's choice:** Overwrite all
**Notes:** None

---

## GitHub Source URL

| Option | Description | Selected |
|--------|-------------|----------|
| Correct as-is | deveshd7/PowerBI-Skill on main branch | |
| Different repo/branch | User provides correct URL | |
| d7rocket/PBI-SKILL | Use d7rocket username and PBI-SKILL repo name | ✓ |

**User's choice:** d7rocket/PBI-SKILL
**Notes:** None

---

## Claude's Discretion

- Manifest approach (hardcoded vs manifest.json)
- Progress bar implementation
- Error messaging and retry logic
- Banner formatting

## Deferred Ideas

None
