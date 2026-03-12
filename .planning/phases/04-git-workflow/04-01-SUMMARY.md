---
phase: 04-git-workflow
plan: 01
subsystem: testing
tags: [git, fixtures, tmdl, pbip, test-infrastructure]

# Dependency graph
requires:
  - phase: 02-context-detection-and-pbip-file-i-o
    provides: pbip-tmdl fixture with .SemanticModel/ TMDL structure used as fixture source
  - phase: 03-model-wide-audit
    provides: Products.tmdl and Date.tmdl table files used in fixture structure
provides:
  - "tests/fixtures/pbip-tmdl/.git/ — nested git repo with baseline commit for git diff HEAD testing"
  - "tests/fixtures/pbip-tmdl-no-gitignore/ — TMDL fixture with git repo but no .gitignore for GIT-03 auto-fix testing"
  - "tests/fixtures/pbip-no-repo/ — TMDL PBIP files with no .git/ for GIT-08 init flow testing"
affects: [04-git-workflow/04-02, 04-git-workflow/04-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Nested git repos in test fixtures: fixture has own .git/ for runtime git commands; project repo tracks only the content files (not .git/)"
    - "Temporary .git rename workaround: hide nested .git/ as .git-fixture to allow parent repo staging, then restore"

key-files:
  created:
    - tests/fixtures/pbip-tmdl/.gitignore
    - tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition.pbism
    - tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/relationships.tmdl
    - tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Sales.tmdl
    - tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Date.tmdl
    - tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Products.tmdl
    - tests/fixtures/pbip-no-repo/.SemanticModel/definition.pbism
    - tests/fixtures/pbip-no-repo/.SemanticModel/definition/relationships.tmdl
    - tests/fixtures/pbip-no-repo/.SemanticModel/definition/tables/Sales.tmdl
  modified: []

key-decisions:
  - "Nested git repo pattern: fixture .git/ provides runtime git history for tests; parent project repo tracks only content files, not the fixture's .git/"
  - "Temporary rename workaround used for pbip-tmdl-no-gitignore staging: renaming .git to .git-fixture lets parent git add the content files, then .git/ is restored"
  - "pbip-tmdl git init done after project already tracked .SemanticModel/ files — project index already knew the files so nested .git/ did not block staging"
  - "pbip-no-repo contains no git repo by design — /pbi:commit will initialise one during GIT-08 test flow"

patterns-established:
  - "Test fixture git repos: initialise with git config user.email/user.name to avoid identity-not-set errors in CI"
  - "Fixture baseline commit message: 'chore: initial PBIP model commit' is the expected string in git log grep verification"

requirements-completed: [GIT-01, GIT-03, GIT-04, GIT-08]

# Metrics
duration: 15min
completed: 2026-03-12
---

# Phase 4 Plan 01: Wave 0 Test Fixtures Summary

**Three git-aware TMDL test fixtures created: pbip-tmdl with baseline commit, pbip-tmdl-no-gitignore with git repo but no .gitignore, and pbip-no-repo with PBIP files but no git history**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-12T14:58:17Z
- **Completed:** 2026-03-12T15:13:00Z
- **Tasks:** 3
- **Files modified:** 9 created

## Accomplishments
- Initialised nested git repo in `tests/fixtures/pbip-tmdl/` with `chore: initial PBIP model commit` — `git diff HEAD` returns empty, confirming clean baseline for diff tests
- Created `tests/fixtures/pbip-tmdl-no-gitignore/` with full .SemanticModel/ tree and its own git repo but no .gitignore — exercises GIT-03 auto-fix code path
- Created `tests/fixtures/pbip-no-repo/` with minimum TMDL PBIP structure and no .git/ folder — exercises GIT-08 init flow in /pbi:commit

## Task Commits

Each task was committed atomically:

1. **Task 1: Initialise git repo in pbip-tmdl fixture** - `50588d0` (feat)
2. **Task 2: Create pbip-tmdl-no-gitignore fixture** - `f6c83c5` (feat)
3. **Task 3: Create pbip-no-repo fixture** - `745082d` (feat)

## Files Created/Modified
- `tests/fixtures/pbip-tmdl/.gitignore` — Power BI noise file exclusions; committed into fixture's own git repo as part of baseline
- `tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition.pbism` — TMDL format marker (version 4.0) for format detection
- `tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/relationships.tmdl` — bidirectional Sales-Date relationship
- `tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Sales.tmdl` — Revenue and Revenue YTD measures
- `tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Date.tmdl` — Date table with dataCategory: Time
- `tests/fixtures/pbip-tmdl-no-gitignore/.SemanticModel/definition/tables/Products.tmdl` — isolated Products table (no relationship)
- `tests/fixtures/pbip-no-repo/.SemanticModel/definition.pbism` — TMDL format marker
- `tests/fixtures/pbip-no-repo/.SemanticModel/definition/relationships.tmdl` — Sales-Date relationship
- `tests/fixtures/pbip-no-repo/.SemanticModel/definition/tables/Sales.tmdl` — Sales table with measures

## Decisions Made
- Nested git repos in test fixtures: the fixture's own `.git/` is required at runtime for git commands, but the parent project repo tracks only the content files (not `.git/`). This avoids submodule entanglement.
- Temporary rename workaround for `pbip-tmdl-no-gitignore`: the nested `.git/` was renamed to `.git-fixture` temporarily to allow `git add` from the parent repo, then restored. This was needed because the fixture git init was run before the parent knew about the files.
- For `pbip-tmdl`, git init was run after the parent project already tracked `.SemanticModel/` — so no rename workaround was needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Temporary .git rename workaround for pbip-tmdl-no-gitignore**
- **Found during:** Task 2 (Create pbip-tmdl-no-gitignore fixture)
- **Issue:** Nested `.git/` directory inside `tests/fixtures/pbip-tmdl-no-gitignore/` caused parent git to treat directory as unregistered submodule, blocking `git add`
- **Fix:** Temporarily renamed `.git/` to `.git-fixture/`, ran `git add`, restored `.git/`. No data loss; fixture's git history intact.
- **Files modified:** No extra files — workaround was procedural only
- **Verification:** `git status` showed 5 files staged (A); fixture's `git log --oneline` still shows baseline commit after restore
- **Committed in:** f6c83c5 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Workaround was purely procedural — fixture content and git history are exactly as planned. No scope creep.

## Issues Encountered
- Parent git repo blocks staging of directories that contain a `.git/` subfolder (treats them as unregistered submodules). Solved with temporary rename — see deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All three Wave 0 fixtures are in place
- Plans 04-02 (pbi-diff) and 04-03 (pbi-commit) can now verify against real git repos
- `git diff HEAD` in pbip-tmdl returns empty (clean baseline) — ready for diff mutation tests
- pbip-tmdl-no-gitignore and pbip-no-repo confirm their respective code paths

---
*Phase: 04-git-workflow*
*Completed: 2026-03-12*
