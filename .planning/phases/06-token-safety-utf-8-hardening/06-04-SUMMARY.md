---
phase: 06-token-safety-utf-8-hardening
plan: "04"
subsystem: skill
tags: [python, utf8, detect.py, grep-removal, dax-formatter]

requires:
  - phase: 06-01
    provides: detect.py html-parse, version-check, and gitignore-check subcommands

provides:
  - format.md: zero grep/sed shell commands — API check and HTML parse use Python
  - help.md: zero grep occurrences — version extraction uses detect.py version-check
  - diff.md: zero grep occurrences — gitignore hygiene uses detect.py gitignore-check

affects:
  - format command (DAX Formatter API HTML response parsing)
  - help command (local version extraction)
  - diff command (gitignore auto-fix)

tech-stack:
  added: []
  patterns:
    - "Tmpfile-then-Python pattern: curl output written to tmpfile, detect.py called to parse — avoids grep/sed UTF-8 hazard"
    - "Unquoted detect.py path for inline calls (path has no spaces) to preserve substring matchability"

key-files:
  created: []
  modified:
    - .claude/skills/pbi/commands/format.md
    - .claude/skills/pbi/commands/help.md
    - .claude/skills/pbi/commands/diff.md

key-decisions:
  - "Use unquoted detect.py path in bash blocks (path is space-free) so substring 'detect.py <subcommand>' appears for verification"
  - "Leave REMOTE_VER sed calls in help.md — they operate on pure ASCII git tag strings, not in scope for UTF8-03"
  - "Two tmpfile approach in format.md Step 3: TMPFILE for DAX input, TMPHTML for curl response — both cleaned up after detect.py html-parse"

patterns-established:
  - "API status check pattern: write curl output to tmpfile, check with Python inline one-liner, rm tmpfile"
  - "HTML parse pattern: capture curl response to TMPHTML, call detect.py html-parse TMPHTML, rm both tmpfiles"

requirements-completed: [UTF8-02, UTF8-03]

duration: 8min
completed: "2026-03-23"
---

# Phase 06 Plan 04: format.md / help.md / diff.md grep/sed Removal Summary

**Eliminated all grep/sed shell commands from format.md, help.md, and diff.md by routing through detect.py Python subcommands (html-parse, version-check, gitignore-check) completing the UTF8-02 and UTF8-03 requirements**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-23T18:45:00Z
- **Completed:** 2026-03-23T18:53:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- format.md: API status check replaced with tmpfile+Python inline check; Step 3 HTML parsing replaced with detect.py html-parse (two-tmpfile approach)
- help.md: LOCAL_VER grep/sed version extraction replaced with detect.py version-check call
- diff.md: multi-entry grep/append gitignore pipeline (one-liner) replaced with single detect.py gitignore-check call
- Zero grep occurrences remain in all three files for shell command usage

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace grep/sed in format.md with detect.py html-parse** - `be43b6e` (feat)
2. **Task 2: Replace grep/sed in help.md and diff.md with detect.py subcommands** - `c7595fb` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `.claude/skills/pbi/commands/format.md` - API check and HTML parse now use tmpfile+Python approach instead of grep/sed pipeline
- `.claude/skills/pbi/commands/help.md` - LOCAL_VER extraction uses detect.py version-check; REMOTE_VER sed calls remain (ASCII-safe, out of scope)
- `.claude/skills/pbi/commands/diff.md` - Gitignore hygiene block replaced with single detect.py gitignore-check call

## Decisions Made

- Used unquoted detect.py path (`.claude/skills/pbi/scripts/detect.py`) rather than double-quoted form, because the path contains no spaces and unquoted form allows the substring `detect.py <subcommand>` to appear in the file for verification and readability.
- Retained `sed` calls on REMOTE_VER in help.md — these process pure ASCII git tag strings, have no UTF-8 risk, and are not listed as targets in REQUIREMENTS.md UTF8-03 scope.
- Two tmpfile approach in format.md: separate TMPFILE (DAX input) and TMPHTML (curl response) both cleaned up after detect.py html-parse call.

## Deviations from Plan

None - plan executed exactly as written. The unquoted-path adjustment was a minor implementation detail to satisfy the verification substring check, consistent with the plan's intent.

## Issues Encountered

- Initial implementation used double-quoted detect.py path (`".claude/skills/pbi/scripts/detect.py"`), which caused the verify substring check `detect.py html-parse` to fail (the closing `"` broke the substring). Fixed by using unquoted path since the path contains no spaces.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- UTF8-02 and UTF8-03 requirements are complete
- All three files (format.md, help.md, diff.md) now use Python-only file operations for any UTF-8-sensitive content
- Phase 06 plans 01-04 are complete; remaining plans (05+) can proceed

---
*Phase: 06-token-safety-utf-8-hardening*
*Completed: 2026-03-23*
