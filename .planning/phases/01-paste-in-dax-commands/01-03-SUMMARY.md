---
phase: 01-paste-in-dax-commands
plan: "03"
subsystem: dax
tags: [claude-skills, dax, power-bi, dax-formatter, api-integration]

requires:
  - phase: 01-paste-in-dax-commands/01-01
    provides: .claude/skills/pbi-format/ directory and stub SKILL.md

provides:
  - /pbi:format command — full implementation with DAX Formatter API call and Claude inline fallback
  - Empirically verified DAX Formatter endpoint documented in api-notes.md
  - API_OK/API_FAIL probe pattern for skill-startup API health check

affects:
  - 01-04-PLAN (pbi-optimise — same context-update pattern)
  - 01-05-PLAN (pbi-comment — same context-update pattern)

tech-stack:
  added: []
  patterns:
    - "DAX Formatter legacy form-POST endpoint: POST https://www.daxformatter.com with fx=, r=US, embed=1 params"
    - "API probe at skill startup via ! bash injection — API_OK/API_FAIL branch in instructions"
    - "HTML stripping pipeline: grep formatted div → sed br to newline → strip spans → convert &nbsp;"
    - "Claude inline SQLBI formatting rules as fallback: keyword caps, CALCULATE arg per line, VAR/RETURN lines"

key-files:
  created:
    - .claude/skills/pbi-format/api-notes.md
  modified:
    - .claude/skills/pbi-format/SKILL.md

key-decisions:
  - "DAX Formatter JSON endpoint /api/daxformatter/dax returns 404 — not available; legacy form-POST confirmed working as of 2026-03-12"
  - "Skill uses legacy form-POST with embed=1 and HTML stripping (sed pipeline) to extract clean DAX text"
  - "API probe in ! bash injection checks for 'formatted' div in response to determine API_OK vs API_FAIL"
  - "Fallback one-line acknowledgement text is locked: '_DAX Formatter API unavailable — formatted inline by Claude_'"

patterns-established:
  - "API-probe-then-fallback: probe runs at startup via ! bash injection, instructions branch on API_OK/API_FAIL"
  - "HTML stripping pipeline documented in api-notes.md for reuse if other skills need external HTML APIs"

requirements-completed: [DAX-04, DAX-05, DAX-06, CTX-02, CTX-03, CTX-04]

duration: 2min
completed: 2026-03-12
---

# Phase 1 Plan 03: /pbi:format Summary

**DAX Formatter legacy form-POST endpoint confirmed working (JSON endpoint 404); /pbi:format skill implemented with live API probe, HTML-strip pipeline, and Claude SQLBI inline formatting fallback**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-12T10:24:00Z
- **Completed:** 2026-03-12T10:26:17Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments

- Empirically verified both DAX Formatter endpoints: JSON endpoint returns 404 after redirect; legacy form-POST (`POST https://www.daxformatter.com` with `fx=`, `r=US`, `embed=1`) returns HTTP 200 with formatted DAX in HTML div
- Implemented HTML stripping pipeline to extract clean DAX from the legacy endpoint response (grep formatted div, convert `<br>` to newlines, strip `<span>` tags, convert `&nbsp;`)
- Full `SKILL.md` written with API probe at startup, API_OK path using the confirmed endpoint, API_FAIL path with exact locked fallback line and Claude inline SQLBI formatting rules
- `api-notes.md` documents both probe results, confirmed endpoint, request schema, response format, and HTML stripping steps

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify DAX Formatter API endpoint and implement /pbi:format SKILL.md** — `4c76b7a` (feat)

**Plan metadata:** (docs commit pending)

## Files Created/Modified

- `.claude/skills/pbi-format/SKILL.md` — Full /pbi:format skill: API probe injection, API_OK branch with curl+HTML-strip, API_FAIL branch with Claude inline SQLBI rules, context update, --table flag, prior-failure detection
- `.claude/skills/pbi-format/api-notes.md` — Documents verified endpoint (legacy form-POST confirmed), failed endpoint (JSON 404), request parameters, response format, HTML stripping pipeline

## Decisions Made

- **Legacy form-POST is the confirmed endpoint:** JSON endpoint `/api/daxformatter/dax` returns 404; the 2014 legacy `POST https://www.daxformatter.com` with `fx=` and `embed=1` is confirmed working as of 2026-03-12
- **HTML stripping via sed pipeline:** The `embed=1` parameter reduces the HTML but doesn't eliminate it; a sed pipeline extracts clean DAX text reliably from the `<div class="formatted">` element
- **API probe checks for `formatted` keyword:** The startup `!` bash injection probes with a trivial expression (`1+1`) and checks if the word "formatted" appears in the response — simple and robust against minor HTML structure changes
- **Fallback acknowledgement text locked:** Exactly `_DAX Formatter API unavailable — formatted inline by Claude_` as specified in CONTEXT.md

## Deviations from Plan

None — plan executed exactly as written. The API verification step was required before writing the skill, and the JSON endpoint failure was anticipated (RESEARCH.md flagged it as LOW confidence); the fallback to the legacy endpoint was the documented decision logic.

## Issues Encountered

The JSON endpoint (`/api/daxformatter/dax`) returned HTTP 301 then HTTP 404 — it does not exist at this path. This was anticipated in the plan's decision logic ("If Probe A fails → use Probe B"). Probe B worked correctly on the first attempt.

## User Setup Required

None — no external service configuration required. The DAX Formatter API is a free public service with no authentication.

## Next Phase Readiness

- `/pbi:format` is fully operational: analysts can paste a DAX measure and receive SQLBI-formatted output
- DAX Formatter endpoint verified and documented; api-notes.md provides reference for future maintenance
- The API_FAIL fallback ensures the skill degrades gracefully if the external service becomes unavailable
- Plans 04-06 (optimise, comment, error) can proceed; they use the same context-update pattern established here

---
*Phase: 01-paste-in-dax-commands*
*Completed: 2026-03-12*
