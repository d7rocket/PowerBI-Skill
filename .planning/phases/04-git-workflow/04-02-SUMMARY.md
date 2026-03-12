---
phase: 04-git-workflow
plan: 02
subsystem: skills
tags: [pbi-diff, git, tmdl, tmsl, gitignore, diff-parsing, business-language]

# Dependency graph
requires:
  - phase: 04-01
    provides: "Phase 4 plan 1 foundation (pbi-commit or prior git skill)"
provides:
  - "/pbi:diff command skill — human-readable model change summary since last commit"
  - "TMDL and TMSL diff parsing rules with measure/table/relationship change detection"
  - "Silent .gitignore hygiene auto-fix before diff output"
  - "Empty repo fallback using git status --porcelain"
affects:
  - 04-03
  - pbi-commit

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Git state check bash block (GIT=yes/no + HAS_COMMITS=yes/no) as second startup block"
    - "Silent gitignore auto-fix using grep -qE with glob coverage check before append"
    - "Scoped git diff using -- path arguments restricted to .SemanticModel/ files only"
    - "TMDL diff parsing: filter to +/- prefix lines only, ignore context and hunk headers"
    - "TMSL diff parsing: track measure object boundaries by nearest 'name' field above changed lines"

key-files:
  created:
    - .claude/skills/pbi-diff/SKILL.md
  modified: []

key-decisions:
  - "Silent gitignore auto-fix: missing noise entries appended without analyst prompt, skill proceeds immediately"
  - "Git diff scoped to .SemanticModel/definition/tables/ and relationships.tmdl (TMDL) or model.bim (TMSL) only — no unscoped git diff"
  - "Empty repo fallback: HAS_COMMITS=no triggers git status --porcelain instead of git diff HEAD"
  - "Output omits zero-change categories; +/~/- prefixes used for added/modified/removed items"
  - "No git push in skill — push is always manual per GIT-07"

patterns-established:
  - "Git state check block: second startup block after PBIP detection, before session context"
  - "Gitignore check uses grep -qE '^(*.abf|cache.abf)' to handle glob coverage (Pitfall 5)"

requirements-completed: [GIT-01, GIT-02, GIT-03]

# Metrics
duration: 2min
completed: 2026-03-12
---

# Phase 4 Plan 02: pbi-diff Skill Summary

**pbi-diff SKILL.md delivering scoped git diff translated to business-language measure/table/relationship change counts with silent .gitignore hygiene auto-fix**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-12T15:18:08Z
- **Completed:** 2026-03-12T15:20:00Z
- **Tasks:** 1 of 1
- **Files modified:** 1

## Accomplishments

- Created `.claude/skills/pbi-diff/SKILL.md` with correct frontmatter (`model: sonnet`, `disable-model-invocation: true`, `allowed-tools: Read, Write, Bash`)
- Implemented silent `.gitignore` hygiene auto-fix (Step 1) that handles glob coverage edge case per Pitfall 5 from RESEARCH.md
- Implemented scoped `git diff HEAD` commands restricted to PBIP model files only — no unscoped diff
- Implemented TMDL and TMSL parsing rules covering Pitfall 3 (context line filtering) and Pitfall 4 (TMSL measure object boundary grouping)
- Implemented empty repo fallback using `git status --porcelain` when HAS_COMMITS=no
- Output format uses business names (TableName: +[MeasureName]) with zero-change category omission

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pbi-diff/SKILL.md** - `8f05d8a` (feat)

## Files Created/Modified

- `.claude/skills/pbi-diff/SKILL.md` - /pbi:diff command skill: PBIP detection, git state check, session context startup; 5-step flow for gitignore hygiene, diff retrieval, TMDL/TMSL parsing, business-language output, context update

## Decisions Made

- Git state check bash block positioned as second startup block (after PBIP detection, before session context) — follows established startup ordering pattern from pbi-audit
- Gitignore auto-fix uses `grep -qE '^(\*\.abf|cache\.abf)'` to handle both literal and glob forms, preventing duplicate entries on repeated runs (Pitfall 5)
- TMDL parsing instructions explicitly filter out context lines (space-prefix) and hunk headers (`@@`) before classification — mitigates Pitfall 3
- TMSL parsing groups all +/- lines between `"name":` boundaries into one measure — mitigates Pitfall 4
- Empty repo (HAS_COMMITS=no) is handled as a distinct state: `git status --porcelain` used instead of `git diff HEAD` to avoid "unknown revision" fatal error (Pitfall 1)

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `/pbi:diff` skill is complete and ready for manual validation against `tests/fixtures/pbip-tmdl/` and `tests/fixtures/pbip-tmsl/`
- Wave 0 test gaps from RESEARCH.md still open: `tests/fixtures/pbip-tmdl-no-gitignore/` and `tests/fixtures/pbip-no-repo/` directories need to be created for GIT-03 and GIT-08 testing
- No blockers for Phase 4 Plan 03 (pbi-commit skill)

---
*Phase: 04-git-workflow*
*Completed: 2026-03-12*
