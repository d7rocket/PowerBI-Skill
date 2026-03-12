---
phase: 02-context-detection-and-pbip-file-i-o
plan: 01
subsystem: testing
tags: [pbip, tmdl, tmsl, fixtures, test-data]

# Dependency graph
requires: []
provides:
  - TMDL fixture project at tests/fixtures/pbip-tmdl/.SemanticModel/ (version 4.0, Sales table with two measures and two columns, one bidirectional relationship)
  - TMSL fixture project at tests/fixtures/pbip-tmsl/.SemanticModel/ (version 1.0, model.bim with Sales table, array and string expression forms, one measure with description and one without)
affects:
  - 02-context-detection-and-pbip-file-i-o (Plans 02-05 reference these fixtures for all manual verification steps)
  - 03-model-auditing (relationships fixture includes bidirectional relationship for Phase 3 audit rule testing)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - TMDL fixture uses tab indentation (not spaces) per TMDL spec — measure properties at one tab, expression content at two tabs
    - TMSL model.bim fixture exercises both expression forms (string for simple measures, array-of-strings for multi-line DAX)
    - Both fixture definition.pbism files use the "version" key confirmed by Microsoft Learn docs

key-files:
  created:
    - tests/fixtures/pbip-tmdl/.SemanticModel/definition.pbism
    - tests/fixtures/pbip-tmdl/.SemanticModel/definition/tables/Sales.tmdl
    - tests/fixtures/pbip-tmdl/.SemanticModel/definition/relationships.tmdl
    - tests/fixtures/pbip-tmsl/.SemanticModel/definition.pbism
    - tests/fixtures/pbip-tmsl/.SemanticModel/model.bim
  modified: []

key-decisions:
  - "TMDL fixture: measure 'Revenue YTD' has triple-slash description, measure 'Revenue' has none — exercises both add-description and update-description code paths"
  - "TMSL fixture: Revenue YTD expression is array-of-strings, Revenue expression is plain string — both forms must be preserved on write-back (Pitfall 3 from RESEARCH.md)"
  - "Both fixtures include a bidirectional relationship (crossFilteringBehavior: bothDirections) — intentionally included to support Phase 3 audit rule testing without extra fixture work"
  - "definition.pbism version key confirmed as 'version' (not 'pbismVersion') — grep pattern version.*4 and version.*1.0 are correct for format detection"

patterns-established:
  - "PBIP fixture structure: definition.pbism at .SemanticModel/ root, TMDL tables in definition/tables/, TMSL model.bim at .SemanticModel/ root"
  - "Tab indentation for TMDL files is structural — must not be converted to spaces on write-back"

requirements-completed: [INFRA-04, INFRA-05, INFRA-06, DAX-13, ERR-03]

# Metrics
duration: 2min
completed: 2026-03-12
---

# Phase 2 Plan 01: PBIP Test Fixtures Summary

**Minimal TMDL and TMSL fixture projects under tests/fixtures/ covering format detection, measure lookup, and write-back code paths for all Phase 2 skills**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-12T12:36:04Z
- **Completed:** 2026-03-12T12:37:44Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- TMDL fixture at tests/fixtures/pbip-tmdl/.SemanticModel/ with definition.pbism (v4.0), Sales.tmdl (2 measures with correct tab indentation, one with /// description), and relationships.tmdl
- TMSL fixture at tests/fixtures/pbip-tmsl/.SemanticModel/ with definition.pbism (v1.0) and model.bim (valid JSON, 2 measures — array expression + description, plain string expression without description)
- All wave 0 requirements from 02-VALIDATION.md satisfied — Phase 2 plans 02–05 are now unblocked for manual verification

## Task Commits

Each task was committed atomically:

1. **Task 1: Create TMDL fixture project** - `c147706` (feat)
2. **Task 2: Create TMSL fixture project** - `0b0f979` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `tests/fixtures/pbip-tmdl/.SemanticModel/definition.pbism` - TMDL format indicator, version 4.0
- `tests/fixtures/pbip-tmdl/.SemanticModel/definition/tables/Sales.tmdl` - Sales table with Date and Amount columns; Revenue YTD measure (with /// description) and Revenue measure (without description); correct tab indentation throughout
- `tests/fixtures/pbip-tmdl/.SemanticModel/definition/relationships.tmdl` - Single bidirectional relationship: Sales[Date] -> Date[Date]
- `tests/fixtures/pbip-tmsl/.SemanticModel/definition.pbism` - TMSL format indicator, version 1.0
- `tests/fixtures/pbip-tmsl/.SemanticModel/model.bim` - SalesModel JSON with Sales table (2 columns, 2 measures), Revenue YTD as array expression with description, Revenue as plain string expression without description

## Decisions Made
- Revenue YTD measure in both fixtures has a description populated; Revenue does not — this exercises both the update-description and add-description code paths in pbi-comment file mode
- Array expression form used for Revenue YTD in model.bim (multi-line DAX) and string form for Revenue — write-back must preserve the original form to avoid TMSL parse errors
- Bidirectional relationship included in both fixtures to support Phase 3 audit rule testing (bidirectionality is a known performance anti-pattern that pbi-audit will flag)
- definition.pbism "version" key confirmed as the correct field name per Microsoft Learn; no alternate key name needed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All Wave 0 fixture gaps from 02-VALIDATION.md are now resolved
- Plans 02-01 through 02-05 can proceed with manual smoke tests against these fixtures
- Phase 3 (model auditing) can reuse the bidirectional relationship in the fixtures without additional fixture work

---
*Phase: 02-context-detection-and-pbip-file-i-o*
*Completed: 2026-03-12*

## Self-Check: PASSED

- All 5 fixture files found on disk
- Both task commits (c147706, 0b0f979) confirmed in git log
- All smoke tests passed (version grep, measure grep, JSON validation)
