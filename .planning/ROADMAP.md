# Roadmap: PBI Skill

## Overview

PBI Skill is built in five phases that follow a strict dependency order: paste-in DAX commands first (zero setup, immediate value), then PBIP file I/O and context detection (foundation for all subsequent file work), then model-wide audit (read-only, validates the file layer), then Git workflow (diff and commit against a proven model layer), then general-purpose editing and the bare router (built last because it routes to commands that must already exist). Each phase delivers a coherent, independently verifiable capability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Paste-in DAX Commands** - All four DAX commands (explain, format, optimise, comment) plus session context — zero PBIP setup required (completed 2026-03-12)
- [x] **Phase 2: Context Detection and PBIP File I/O** - Mode detection, TMSL/TMDL format detection, Desktop-open safety guard, comment write-back, error recovery write-back (completed 2026-03-12)
- [ ] **Phase 3: Model-Wide Audit** - Full `/pbi:audit` command with severity-graded output across all audit domains
- [ ] **Phase 4: Git Workflow** - `/pbi:diff` and `/pbi:commit` with business-language output and gitignore hygiene
- [ ] **Phase 5: Direct Editing and Router** - General-purpose `/pbi:edit` for any PBIP change, plus the bare `/pbi` routing command

## Phase Details

### Phase 1: Paste-in DAX Commands
**Goal**: Analysts can explain, format, optimise, and comment any DAX measure by pasting it into a command — no PBIP project or file access needed
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, CTX-01, CTX-02, CTX-03, CTX-04, DAX-01, DAX-02, DAX-03, DAX-04, DAX-05, DAX-06, DAX-07, DAX-08, DAX-09, DAX-10, DAX-11, DAX-12, ERR-01, ERR-02, ERR-04
**Success Criteria** (what must be TRUE):
  1. Analyst can paste any DAX measure and receive a plain-English explanation that identifies filter context, row context, and context transitions
  2. Analyst can paste a DAX measure and receive a copy-paste ready SQLBI-formatted code block (DAX Formatter API attempted first, Claude inline fallback on failure)
  3. Analyst can paste a DAX measure and receive a performance-optimised rewrite with per-change rationale; iterators over measure references are flagged for manual verification rather than auto-rewritten
  4. Analyst can paste a DAX measure and receive a version with inline `//` comments plus a populated description field value ready to paste into Power BI
  5. A `.pbi-context.md` session file is created and updated after each command; subsequent commands read it to avoid repeating failed approaches and flag prior failures to the analyst
**Plans**: 6 plans

Plans:
- [ ] 01-01-PLAN.md — Skill directory scaffolding, .pbi-context.md initial schema, test fixtures, /pbi:load stub
- [ ] 01-02-PLAN.md — /pbi:explain command with context read/write loop and complexity-adaptive output
- [ ] 01-03-PLAN.md — /pbi:format command with DAX Formatter API probe and Claude inline fallback
- [ ] 01-04-PLAN.md — /pbi:optimise command with five optimisation rules and iterator-over-measure-ref guard
- [ ] 01-05-PLAN.md — /pbi:comment command with inline // comments and Description Field block
- [ ] 01-06-PLAN.md — /pbi:error command with error diagnosis, context correlation, and prior-failure skip

### Phase 2: Context Detection and PBIP File I/O
**Goal**: Commands detect whether a PBIP project is present and which format it uses, and can safely write back to PBIP files when Desktop is confirmed closed
**Depends on**: Phase 1
**Requirements**: INFRA-03, INFRA-04, INFRA-05, INFRA-06, DAX-13, ERR-03
**Success Criteria** (what must be TRUE):
  1. Every command detects whether a `.SemanticModel/` PBIP project exists in the working directory and branches to file mode or paste-in mode accordingly
  2. Before any file operation, the command reads `definition.pbism` to distinguish TMSL (`model.bim`) from TMDL (`definition/` folder) and uses the correct read/write path
  3. Before any file write, the command either detects a running `PBIDesktop.exe` process or requires explicit analyst confirmation; if Desktop is open or confirmation is absent, output is paste-ready only
  4. In PBIP file mode with Desktop confirmed closed, `/pbi:comment` writes inline comments and the description field back to the correct TMDL or `model.bim` file
  5. In PBIP file mode, error recovery diagnoses an error using `.pbi-context.md` context and can apply the fix directly to the file
**Plans**: 4 plans

Plans:
- [ ] 02-01-PLAN.md — TMDL and TMSL test fixtures for verification of all file-mode paths
- [ ] 02-02-PLAN.md — /pbi:load rewrite: full PBIP context loading with format detection and model summary
- [ ] 02-03-PLAN.md — /pbi:comment file-mode branch: Desktop guard, TMDL/TMSL write-back
- [ ] 02-04-PLAN.md — /pbi:error file-mode branch: Desktop guard, before/after preview, confirm-before-write

### Phase 3: Model-Wide Audit
**Goal**: Analysts can run a single command against a PBIP project and receive a complete, severity-graded model health report with specific locations and actionable recommendations
**Depends on**: Phase 2
**Requirements**: AUD-01, AUD-02, AUD-03, AUD-04, AUD-05, AUD-06, AUD-07
**Success Criteria** (what must be TRUE):
  1. `/pbi:audit` produces a structured CRITICAL / WARN / INFO report that checks naming conventions, relationship health, date table configuration, and measure quality
  2. Every finding includes the specific table or measure name (not a JSON path) and a concrete recommendation for resolution
  3. Audit runs in chunked domain passes (one category per context window pass) so large models do not saturate context and degrade output quality
  4. Bidirectional relationships and missing fact-to-dimension relationships are explicitly flagged with severity CRITICAL or WARN
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Add Date.tmdl and Products.tmdl test fixtures for AUD-03/AUD-04 verification cases
- [ ] 03-02-PLAN.md — /pbi:audit skill: four-pass domain architecture, severity-sorted report, audit-report.md write

### Phase 4: Git Workflow
**Goal**: Analysts can get a human-readable summary of model changes since the last commit, and can commit PBIP changes with an auto-generated business-language commit message
**Depends on**: Phase 3
**Requirements**: GIT-01, GIT-02, GIT-03, GIT-04, GIT-05, GIT-06, GIT-07, GIT-08
**Success Criteria** (what must be TRUE):
  1. `/pbi:diff` outputs a human-readable changelog using measure and table names (e.g., "3 measures modified in Sales table, 1 relationship removed") — not raw JSON key paths
  2. Before presenting diff output, the command verifies that `.gitignore` guards noise files (`cache.abf`, `localSettings.json`); if not guarded, the analyst is warned before any staging
  3. `/pbi:commit` stages PBIP changes and commits locally with a generated message naming the actual model changes (tables, measures, relationships)
  4. After any successful PBIP file write by any command, an automatic local git commit is created without requiring the analyst to manually run `/pbi:commit`
  5. If no git repo exists, `/pbi:commit` initialises one and creates an initial commit; push to remote is always manual and never triggered automatically
**Plans**: TBD

### Phase 5: Direct Editing and Router
**Goal**: Analysts can describe any model change in plain language and have Claude apply it directly to PBIP files, and bare `/pbi` orients any analyst to the full command suite
**Depends on**: Phase 4
**Requirements**: INFRA-02, EDIT-01, EDIT-02, EDIT-03, EDIT-04
**Success Criteria** (what must be TRUE):
  1. Analyst can describe a model change (e.g., "rename measure [Revenue] to [Total Revenue] in Sales table") and `/pbi:edit` reads the relevant file, applies the change, and writes back to disk
  2. Before writing, `/pbi:edit` shows a before/after diff of the exact change and requires explicit analyst confirmation
  3. Pre-write checklist is enforced on every edit: Desktop-closed confirmation, `unappliedChanges.json` check, TMDL indentation preservation verified
  4. Bare `/pbi` presents all available commands with brief descriptions and asks what the analyst needs, then routes to the appropriate subcommand
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Paste-in DAX Commands | 6/6 | Complete   | 2026-03-12 |
| 2. Context Detection and PBIP File I/O | 4/4 | Complete   | 2026-03-12 |
| 3. Model-Wide Audit | 0/2 | Not started | - |
| 4. Git Workflow | 0/TBD | Not started | - |
| 5. Direct Editing and Router | 0/TBD | Not started | - |
