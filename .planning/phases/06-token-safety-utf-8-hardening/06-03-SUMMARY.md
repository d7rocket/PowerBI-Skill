---
phase: 06-token-safety-utf-8-hardening
plan: 03
subsystem: skill
tags: [pbi-skill, utf8, grep-replacement, detect.py, token-safety, tmsl, tmdl]

# Dependency graph
requires:
  - phase: 06-01
    provides: detect.py search subcommand (UTF-8 safe measure/file lookup)
provides:
  - error.md with zero grep -rlF calls — detect.py search for TMDL measure lookup
  - new.md with zero grep -rlF calls — detect.py search for TMDL table verification
  - Both files have TMSL model.bim chunked-read guard (offset/limit for files >2000 lines)
affects:
  - 06-04
  - 06-05

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Python detect.py search replaces grep -rlF for all measure/table file lookups in skill commands"
    - "TMSL chunked-read guard: Read tool with offset/limit for model.bim files >2000 lines"

key-files:
  created: []
  modified:
    - .claude/skills/pbi/commands/error.md
    - .claude/skills/pbi/commands/new.md

key-decisions:
  - "detect.py search used for both TMDL measure lookup (error.md) and TMDL table verification (new.md) — consistent UTF-8-safe pattern across all file-mode commands"
  - "new.md not-found case made explicit: detect.py returning no output triggers a user-facing error message rather than silently continuing"

patterns-established:
  - "grep -rlF -> detect.py search: all TMDL file lookups in skill commands use python detect.py search <name> <pbip_dir>"
  - "TMSL chunked read: any Read of model.bim adds offset/limit guard for files >2000 lines"

requirements-completed: [UTF8-01, TOKEN-01, TOKEN-02]

# Metrics
duration: 5min
completed: 2026-03-23
---

# Phase 06 Plan 03: error.md and new.md — grep Removal + TMSL Chunked-Read Guard Summary

**grep -rlF eliminated from error.md and new.md; both TMSL branches now guard against reading large model.bim files without chunking**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-23T18:45:00Z
- **Completed:** 2026-03-23T18:50:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Replaced `grep -rlF` measure lookup in error.md TMDL branch with `python detect.py search` (UTF-8 safe, handles French accented names)
- Added TMSL chunked-read guard in error.md: Read tool with offset/limit for model.bim files >2000 lines
- Replaced `grep -rlF` table verification in new.md TMDL branch with `python detect.py search`, with an explicit not-found error message
- Added TMSL chunked-read guard in new.md: Read tool with offset/limit before locating target table's measures array
- Both commands now have zero `grep -rlF` occurrences

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace grep in error.md and add TMSL chunked-read guard** - `8229350` (fix)
2. **Task 2: Replace grep in new.md and add TMSL chunked-read guard** - `2945c68` (fix)

**Plan metadata:** *(docs commit pending)*

## Files Created/Modified

- `.claude/skills/pbi/commands/error.md` - TMDL measure lookup now uses detect.py search; TMSL branch has chunked-read guard
- `.claude/skills/pbi/commands/new.md` - TMDL table verification now uses detect.py search with not-found message; TMSL branch has chunked-read guard

## Decisions Made

- Used `python ".claude/skills/pbi/scripts/detect.py" search "[MeasureName]" "$PBIP_DIR"` as the exact replacement — consistent with the detect.py search pattern established in plan 06-01
- Made the new.md not-found case explicit: when detect.py search returns no output, the executor now outputs a specific error message rather than silently proceeding (improvement over the original grep behavior)

## Deviations from Plan

None - plan executed exactly as written. The new.md not-found error message addition was specified in the plan's Change 1 description and matches the plan intent.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- error.md and new.md are now grep-free and token-safe for TMSL
- Plans 06-04 and 06-05 can proceed to apply the same pattern to remaining commands (edit.md, audit.md, optimise.md)
- UTF8-01, TOKEN-01, TOKEN-02 requirements fully addressed for error and new commands

---
*Phase: 06-token-safety-utf-8-hardening*
*Completed: 2026-03-23*
