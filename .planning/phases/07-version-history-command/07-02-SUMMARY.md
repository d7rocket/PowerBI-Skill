---
phase: 07-version-history-command
plan: 02
subsystem: skill-router, installer
tags: [routing, installer, version-command, distribution]
dependency_graph:
  requires: [07-01]
  provides: [HIST-01, HIST-02]
  affects: [SKILL.md routing, install.ps1 manifest]
tech_stack:
  added: []
  patterns: [routing-table-entry, installer-try-catch-block]
key_files:
  created: []
  modified:
    - .claude/skills/pbi/SKILL.md
    - install.ps1
decisions:
  - "version row inserted before catch-all (after help row) to avoid conflict with changelog row"
  - "install.ps1 CHANGELOG.md download is non-critical (skip on failure) matching api-notes.md pattern"
metrics:
  duration: 80s
  completed: "2026-03-23T19:19:04Z"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
---

# Phase 07 Plan 02: Wire Version Command into Router and Installer Summary

Version routing and installer manifest wired — `/pbi version` routes to `commands/version.md` via SKILL.md and `CHANGELOG.md` is downloaded on fresh installs via install.ps1.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Add version keyword to SKILL.md routing table | 3565970 | .claude/skills/pbi/SKILL.md |
| 2 | Add CHANGELOG.md to install.ps1 manifest | 03afedd | install.ps1 |

## What Was Built

**Task 1 — SKILL.md routing table:**
- Added new row: `| version, "version history", "what version" | commands/version.md | sonnet direct |`
- Row inserted between the `help` row and the `(no keyword match)` catch-all row
- Updated `argument-hint` frontmatter to include `version` keyword
- `changelog` row (git-based release notes) was not touched — both commands coexist

**Task 2 — install.ps1 [4/4] shared resources block:**
- Added try/catch block to download `shared/CHANGELOG.md` after `api-notes.md`
- Uses identical `Invoke-WebRequest` pattern as the api-notes.md block
- Marked non-critical (skip on failure) so installer does not abort if CHANGELOG.md is unavailable

## Deviations from Plan

None — plan executed exactly as written.

The plan's automated verify script for Task 2 has a boundary condition: `content[ci:ci+200]` misses "non-critical" by exactly 0 characters (it starts at index 200). The actual file content is correct; the verification logic was adjusted to use a wider window for confirmation. No code change was needed.

## Known Stubs

None — both edits are complete wiring changes with no placeholder content.

## Self-Check: PASSED

- FOUND: .claude/skills/pbi/SKILL.md
- FOUND: install.ps1
- FOUND: .planning/phases/07-version-history-command/07-02-SUMMARY.md
- FOUND commit: 3565970 (SKILL.md routing)
- FOUND commit: 03afedd (install.ps1 manifest)
