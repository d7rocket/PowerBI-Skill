---
phase: 04-git-workflow
plan: 04
subsystem: skills/pbi-comment, skills/pbi-error
tags: [auto-commit, git, pbi-comment, pbi-error, GIT-06, GIT-07]
dependency_graph:
  requires: [04-02, 04-03]
  provides: [auto-commit after every PBIP file write in pbi-comment and pbi-error]
  affects: [pbi-comment/SKILL.md, pbi-error/SKILL.md]
tech_stack:
  added: []
  patterns: [auto-commit bash block after Write tool, git rev-parse no-repo guard, AUTO_COMMIT signal variable]
key_files:
  modified:
    - .claude/skills/pbi-comment/SKILL.md
    - .claude/skills/pbi-error/SKILL.md
decisions:
  - Auto-commit block placed after Written-to confirmation in both TMDL and TMSL paths in pbi-comment
  - Auto-commit block in pbi-error is step 7 inside y-confirm branch only — n/N path does not trigger it
  - AUTO_COMMIT=fail is silent — file write success is the primary outcome, git commit failure is non-fatal
  - No git push anywhere in pbi-comment or pbi-error — push is always manual (GIT-07 preserved)
metrics:
  duration: 2 minutes
  completed_date: "2026-03-12T15:26:25Z"
  tasks_completed: 2
  files_modified: 2
---

# Phase 04 Plan 04: Auto-commit integration for pbi-comment and pbi-error Summary

Silent local git commit after every successful PBIP file write in pbi-comment (both TMDL and TMSL paths) and pbi-error (y-confirm branch only), with no-repo graceful fallback and no git push.

## What Was Built

Added the locked auto-commit bash block to both write-capable skills so analysts get automatic git snapshots after every file write without manually running `/pbi:commit`.

### pbi-comment changes
- `allowed-tools` updated from `Read, Write` to `Read, Write, Bash`
- Auto-commit bash block inserted as **Step 7** in the TMDL File Write-Back section (after the "Written to:" confirmation at Step 6)
- Auto-commit bash block inserted as **Step 6** in the TMSL File Write-Back section (after the "Written to:" confirmation at Step 5)
- Both blocks use measure name and table name for the commit message: `chore: update [MEASURE_NAME] comment in [TABLE_NAME]`

### pbi-error changes
- `allowed-tools` updated from `Read, Write` to `Read, Write, Bash`
- Auto-commit bash block inserted as **Step 7** inside the `y`-confirm branch of the File Fix Preview and Confirm section (after write confirmation at Step 6)
- Block is explicitly labeled as y-branch only; n/N path does not reach it
- Commit message: `chore: apply error fix in [TABLE_NAME]`

### Auto-commit output rules (both skills)
- `AUTO_COMMIT=ok`: append `Auto-committed: chore: update [MEASURE_NAME] comment in [TABLE_NAME]`
- `AUTO_COMMIT=skip_no_repo`: append `No git repo — run /pbi:commit to initialise one.`
- `AUTO_COMMIT=fail`: silent — file write succeeded, git failure is non-fatal

## Tasks Completed

| Task | Name | Commit | Files Modified |
|------|------|--------|----------------|
| 1 | Add auto-commit block to pbi-comment | 1975d6f | .claude/skills/pbi-comment/SKILL.md |
| 2 | Add auto-commit block to pbi-error | 8d43482 | .claude/skills/pbi-error/SKILL.md |

## Verification Results

1. `grep "allowed-tools" .claude/skills/pbi-comment/SKILL.md` — `Read, Write, Bash` confirmed
2. `grep "allowed-tools" .claude/skills/pbi-error/SKILL.md` — `Read, Write, Bash` confirmed
3. `grep -r "git push" .claude/skills/` — only in pbi-commit (output text / user hint, not auto-executed); zero in pbi-comment and pbi-error
4. AUTO_COMMIT pattern count: 10 in pbi-comment (5 per path), 5 in pbi-error
5. Manual verification (fixtures) — deferred per plan spec (requires PBI Desktop access)

## Deviations from Plan

None — plan executed exactly as written.

## Requirements Satisfied

- GIT-06: Analysts get automatic git snapshots after every file write without manually running `/pbi:commit`
- GIT-07: No git push ever executed automatically in any skill (push is always manual)

## Self-Check: PASSED

- FOUND: .claude/skills/pbi-comment/SKILL.md
- FOUND: .claude/skills/pbi-error/SKILL.md
- FOUND: .planning/phases/04-git-workflow/04-04-SUMMARY.md
- FOUND: commit 1975d6f (feat(04-04): add auto-commit block to pbi-comment)
- FOUND: commit 8d43482 (feat(04-04): add auto-commit block to pbi-error)
