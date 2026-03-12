# Requirements: PBI Skill

**Defined:** 2026-03-12
**Core Value:** A BI analyst can drop into `/pbi` at any point in their workflow and get expert-level help — DAX, model auditing, error recovery, version control — without leaving Claude.

## v1 Requirements

### Skill Infrastructure

- [x] **INFRA-01**: Skill suite is invocable via `/pbi` prefix commands (e.g. `/pbi:optimize`, `/pbi:audit`)
- [ ] **INFRA-02**: Bare `/pbi` command asks what the analyst needs and routes to the appropriate subcommand
- [ ] **INFRA-03**: All commands support two modes: paste-in (DAX/SQL pasted directly) and PBIP file mode (reads from disk when Desktop is closed)
- [ ] **INFRA-04**: Context detection — commands detect whether a `.SemanticModel/` PBIP project exists in the working directory
- [ ] **INFRA-05**: PBIP format detection — read `definition.pbism` version field to distinguish TMSL (`model.bim`) from TMDL (`definition/` folder) before any file operation
- [ ] **INFRA-06**: Desktop-open safety guard — before any file write, check for running `PBIDesktop.exe` process or require explicit analyst confirmation; default to paste-in output otherwise

### Session Context

- [x] **CTX-01**: A `.pbi-context.md` session file is maintained in the project root, tracking: last command run, what was changed, what was tried and failed, and open issues
- [x] **CTX-02**: Each command reads `.pbi-context.md` at startup and uses it to avoid repeating failed approaches
- [x] **CTX-03**: Each command updates `.pbi-context.md` after execution with a summary of what was done and the outcome
- [x] **CTX-04**: If a previous approach failed (logged in context), the command flags this to the analyst and suggests an alternative rather than retrying the same method

### DAX — Explain

- [x] **DAX-01**: User can paste a DAX measure expression and receive a plain-English explanation of what it calculates
- [x] **DAX-02**: Explanation identifies filter context, row context, and any context transitions present
- [x] **DAX-03**: Explanation adapts register to inferred analyst skill level (simpler for straightforward measures, technical depth for complex ones)

### DAX — Format

- [ ] **DAX-04**: User can paste a DAX measure and receive SQLBI-style formatted output (consistent indentation, keyword capitalisation, line breaks)
- [ ] **DAX-05**: Formatted output is returned as a copy-paste ready code block
- [ ] **DAX-06**: Format command attempts DAX Formatter API first; falls back to Claude inline formatting if API is unreachable

### DAX — Optimise

- [ ] **DAX-07**: User can paste a DAX measure and receive a performance-optimised rewrite with rationale explaining each change
- [ ] **DAX-08**: Optimiser detects and rewrites common slow patterns: unnecessary `FILTER` on a table, `SUMX` over a single column where `SUM` suffices, redundant `CALCULATE` wrappers
- [ ] **DAX-09**: Any measure containing iterators over measure references is flagged as "requires manual verification — context transition present" rather than auto-rewritten
- [ ] **DAX-10**: Optimiser suggests alternatives with trade-off explanations where multiple valid rewrites exist

### DAX — Comment

- [x] **DAX-11**: User can paste a DAX measure and receive a version with `//` inline comments explaining the business logic
- [x] **DAX-12**: Command also outputs a populated `description` field value suitable for pasting into the Power BI measure Description property
- [ ] **DAX-13**: When in PBIP file mode, command writes inline comments and description back to the target table's `.tmdl` or `model.bim` file directly (Desktop must be confirmed closed)

### Error Recovery

- [ ] **ERR-01**: User can paste a Power BI error log or error message and receive a diagnosis of the root cause
- [ ] **ERR-02**: Error recovery reads `.pbi-context.md` to understand what was last changed and correlates the error to recent edits
- [ ] **ERR-03**: Error recovery proposes a specific fix (not just an explanation) and, when in PBIP file mode with Desktop closed, can apply the fix directly
- [ ] **ERR-04**: If the same error has been seen before (logged in `.pbi-context.md`), the command skips failed prior approaches and leads with the correct method

### Model Audit

- [ ] **AUD-01**: User can run `/pbi:audit` against a PBIP project and receive a structured severity-graded report (CRITICAL / WARN / INFO)
- [ ] **AUD-02**: Audit checks naming conventions: table, column, and measure names follow a consistent pattern (e.g. measure prefixes, dim/fact table naming)
- [ ] **AUD-03**: Audit checks relationship health: flags bidirectional relationships, missing relationships between fact and dimension tables
- [ ] **AUD-04**: Audit checks date table presence and correct configuration (marked as date table, continuous date range, no gaps)
- [ ] **AUD-05**: Audit checks measure quality: blank `formatString`, empty `description`, measures with no display folder
- [ ] **AUD-06**: Audit is chunked by domain (one pass per category) to avoid context window saturation on large models
- [ ] **AUD-07**: Audit report includes specific location (table/measure name) and a concrete recommendation for each finding

### Version Control — Diff

- [ ] **GIT-01**: User can run `/pbi:diff` to get a human-readable summary of what changed since the last commit (measures added/modified/removed, relationships changed) — not raw JSON diff
- [ ] **GIT-02**: Diff summary uses business language (table and measure names, not JSON key paths)
- [ ] **GIT-03**: Diff command verifies `.gitignore` is guarding noise files (`cache.abf`, `localSettings.json`) before presenting output

### Version Control — Commit

- [ ] **GIT-04**: User can run `/pbi:commit` to stage PBIP changes and commit locally with an auto-generated business-language commit message
- [ ] **GIT-05**: Commit message summarises the actual model changes (e.g. "feat: add [Revenue YTD] measure to Sales table; fix bidirectional relationship on Customer[CustomerKey]")
- [ ] **GIT-06**: After every successful PBIP file write (from any command), an automatic local git commit is created without requiring the analyst to run `/pbi:commit` manually
- [ ] **GIT-07**: Push to remote (GitHub) is always manual — no command auto-pushes
- [ ] **GIT-08**: If no git repo exists in the project, `/pbi:commit` initialises one and creates an initial commit

### Direct PBIP Editing

- [ ] **EDIT-01**: User can run `/pbi:edit` with a description of what to change and Claude reads the relevant PBIP files, applies the change, and writes back to disk
- [ ] **EDIT-02**: Edit command performs pre-write checklist: Desktop-closed confirmation, `unappliedChanges.json` check, TMDL indentation preservation
- [ ] **EDIT-03**: Edit command shows a preview of the change before writing (diff of before/after) and requires confirmation
- [ ] **EDIT-04**: After a successful edit, an automatic local git commit is created (satisfies GIT-06)

## v2 Requirements

### Extended DAX

- **DAX-V2-01**: `/pbi:new` — scaffold a new measure with correct naming, format string, display folder, and description from a plain-English description
- **DAX-V2-02**: Batch commenting — apply `/pbi:comment` across all measures in a table or the entire model at once

### Extended Audit

- **AUD-V2-01**: Hidden column hygiene check — columns that are visible but should be hidden (foreign keys, internal IDs)
- **AUD-V2-02**: Audit auto-fix mode — apply CRITICAL and WARN fixes directly after audit with one confirmation

### Extended Version Control

- **GIT-V2-01**: `/pbi:branch` — create a feature branch for a set of model changes, merge back when done
- **GIT-V2-02**: Changelog generation — produce a human-readable CHANGELOG.md from git history

### Report Layer

- **RPT-V2-01**: PBIR visual layer audit — check which measures are used in which visuals (requires PBIR format)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full report creation | Different product category; this is a helper not a builder |
| Power BI Service / REST API | Requires Azure AD auth; desktop/file-first for v1 |
| VertiPaq viewer / query runner | DAX Studio does this better; requires live connection |
| M query optimisation | Different language/engine; separate domain from DAX+model |
| Visual formatting / layout | Report visual layer uses immature PBIR JSON in v1 timeframe |
| Real-time model monitoring | Requires persistent process; not a slash-command pattern |
| Auto-push to remote | Always manual — analyst controls when changes go to GitHub |

## Traceability

| Requirement | Phase | Phase Name | Status |
|-------------|-------|------------|--------|
| INFRA-01 | Phase 1 | Paste-in DAX Commands | Pending |
| INFRA-02 | Phase 5 | Direct Editing and Router | Pending |
| INFRA-03 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| INFRA-04 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| INFRA-05 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| INFRA-06 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| CTX-01 | Phase 1 | Paste-in DAX Commands | Pending |
| CTX-02 | Phase 1 | Paste-in DAX Commands | Pending |
| CTX-03 | Phase 1 | Paste-in DAX Commands | Pending |
| CTX-04 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-01 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-02 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-03 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-04 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-05 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-06 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-07 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-08 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-09 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-10 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-11 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-12 | Phase 1 | Paste-in DAX Commands | Pending |
| DAX-13 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| ERR-01 | Phase 1 | Paste-in DAX Commands | Pending |
| ERR-02 | Phase 1 | Paste-in DAX Commands | Pending |
| ERR-03 | Phase 2 | Context Detection and PBIP File I/O | Pending |
| ERR-04 | Phase 1 | Paste-in DAX Commands | Pending |
| AUD-01 | Phase 3 | Model-Wide Audit | Pending |
| AUD-02 | Phase 3 | Model-Wide Audit | Pending |
| AUD-03 | Phase 3 | Model-Wide Audit | Pending |
| AUD-04 | Phase 3 | Model-Wide Audit | Pending |
| AUD-05 | Phase 3 | Model-Wide Audit | Pending |
| AUD-06 | Phase 3 | Model-Wide Audit | Pending |
| AUD-07 | Phase 3 | Model-Wide Audit | Pending |
| GIT-01 | Phase 4 | Git Workflow | Pending |
| GIT-02 | Phase 4 | Git Workflow | Pending |
| GIT-03 | Phase 4 | Git Workflow | Pending |
| GIT-04 | Phase 4 | Git Workflow | Pending |
| GIT-05 | Phase 4 | Git Workflow | Pending |
| GIT-06 | Phase 4 | Git Workflow | Pending |
| GIT-07 | Phase 4 | Git Workflow | Pending |
| GIT-08 | Phase 4 | Git Workflow | Pending |
| EDIT-01 | Phase 5 | Direct Editing and Router | Pending |
| EDIT-02 | Phase 5 | Direct Editing and Router | Pending |
| EDIT-03 | Phase 5 | Direct Editing and Router | Pending |
| EDIT-04 | Phase 5 | Direct Editing and Router | Pending |

**Coverage:**
- v1 requirements: 43 total
- Mapped to phases: 43
- Unmapped: 0

---
*Requirements defined: 2026-03-12*
*Last updated: 2026-03-12 after roadmap creation — phase names added to traceability*
