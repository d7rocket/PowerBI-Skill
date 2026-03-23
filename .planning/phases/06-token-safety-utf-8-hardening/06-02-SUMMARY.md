---
phase: 06-token-safety-utf-8-hardening
plan: 02
subsystem: infra
tags: [python, detect.py, utf-8, grep-replacement, token-safety, tmdl, tmsl]

# Dependency graph
requires:
  - phase: 06-01
    provides: "detect.py search subcommand (already existed since v1.0, UTF-8 safe)"
provides:
  - "edit.md: grep-free TMDL measure lookup using detect.py search"
  - "edit.md: zero-results fallback uses detect.py search + reads returned files for measure list"
  - "edit.md: TMSL model.bim chunked-read guard (offset/limit for files >2000 lines)"
  - "comment.md: grep-free TMDL measure file lookup using detect.py search"
  - "comment.md: TMSL model.bim chunked-read guard (offset/limit for files >2000 lines)"
affects:
  - 06-03
  - 06-04

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Replace grep -rlF with python detect.py search for all TMDL measure file lookups"
    - "TMSL chunked-read guard: offset/limit on Read tool when model.bim >2000 lines"

key-files:
  created: []
  modified:
    - .claude/skills/pbi/commands/edit.md
    - .claude/skills/pbi/commands/comment.md

key-decisions:
  - "Zero-results fallback in edit.md now reads returned files to list measure names (detect.py search returns files, not line:content pairs)"
  - "TMSL chunked-read guard threshold set at 2000 lines, chunk size 1000 lines — consistent with pattern from plan spec"

patterns-established:
  - "All TMDL measure lookups in command files use detect.py search, never grep -rlF"
  - "TMSL model.bim reads always include chunked-read guard for token overflow prevention"

requirements-completed: [UTF8-01, TOKEN-01, TOKEN-02]

# Metrics
duration: 5min
completed: 2026-03-23
---

# Phase 06 Plan 02: edit.md + comment.md grep Replacement Summary

**grep -rlF eliminated from edit.md and comment.md (replaced with detect.py search), plus TMSL offset/limit chunked-read guards added to both files for token overflow prevention**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-23T18:41:30Z
- **Completed:** 2026-03-23T18:46:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- edit.md: two grep calls replaced with `python detect.py search` (primary TMDL lookup and zero-results fallback); fallback instruction updated to "Read each returned file to list measure names" to match detect.py output format (filenames, not line content)
- edit.md: TMSL branch Step 2 now instructs "use offset/limit parameters to read in chunks of 1000 lines" when model.bim >2000 lines
- comment.md: one grep call replaced with `python detect.py search` in TMDL File Write-Back section
- comment.md: TMSL branch File Write-Back step 1 now includes offset/limit chunked-read guard

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace grep in edit.md and add TMSL chunked-read guard** - `aaa6c4b` (fix)
2. **Task 2: Replace grep in comment.md and add TMSL chunked-read guard** - `8524801` (fix)

## Files Created/Modified

- `.claude/skills/pbi/commands/edit.md` - Two grep calls replaced with detect.py search; TMSL branch gets offset/limit chunked-read guard in entity resolution step
- `.claude/skills/pbi/commands/comment.md` - One grep call replaced with detect.py search; TMSL branch gets offset/limit chunked-read guard in file write-back step

## Decisions Made

- Zero-results fallback text in edit.md updated from "list all measure names" to "Read each returned file to list measure names" because detect.py search returns file paths, not line content — the executor must read those files to extract measure names. This keeps the instruction accurate with the new tool's output format.
- No change to the surrounding logic or branch structure in either file — only the bash command inside code blocks and the TMSL read instruction were modified.

## Deviations from Plan

None - plan executed exactly as written. All three changes in edit.md and both changes in comment.md applied as specified.

## Issues Encountered

None.

## Known Stubs

None — both files are fully functional with the replacements applied.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 06-03 and 06-04 can continue the grep-replacement sweep in remaining command files
- edit.md and comment.md are now fully grep-free and have TMSL token-overflow protection
- Pattern established: detect.py search replaces grep -rlF; TMSL branches include offset/limit guard

---
*Phase: 06-token-safety-utf-8-hardening*
*Completed: 2026-03-23*

## Self-Check: PASSED

- FOUND: .claude/skills/pbi/commands/edit.md
- FOUND: .claude/skills/pbi/commands/comment.md
- FOUND: .planning/phases/06-token-safety-utf-8-hardening/06-02-SUMMARY.md
- FOUND commit: aaa6c4b (Task 1)
- FOUND commit: 8524801 (Task 2)
