# Requirements: PBI Skill v2

**Defined:** 2026-03-13
**Core Value:** Never block a data analyst — solve immediately, interrogate only when stuck or asked

## v1 Requirements

### Progressive Friction

- [ ] **PROG-01**: Skill defaults to solving the immediate request without interrogation or phase gates
- [ ] **PROG-02**: Skill escalates to structured questioning after 2-3 unresolved attempts, not upfront
- [ ] **PROG-03**: Escalation surfaces targeted questions (only what's blocking the solution), not a full pre-flight checklist
- [ ] **PROG-04**: Deep workflow mode (full phase breakdown + gates) only activates when user explicitly requests it

### Interrogation

- [ ] **INTR-01**: When escalating, skill extracts the business question the report needs to answer
- [ ] **INTR-02**: When escalating, skill gathers data model state (tables, relationships, calculated columns)
- [ ] **INTR-03**: When escalating, skill audits existing measures to prevent duplication or conflicts
- [ ] **INTR-04**: Before writing filter-sensitive DAX (ratios, time intelligence, ranking), skill asks about visual consumption context (where the measure will be placed, active slicers)

### DAX / Measures

- [ ] **DAX-01**: Generated measures reference actual tables/columns described by user, not assumed generic schema
- [ ] **DAX-02**: Duplication check — skill asks if a similar measure already exists before writing a new one
- [ ] **DAX-03**: Filter context warning surfaced when generating CALCULATE-heavy patterns without knowing visual placement

### Workflow Phases (deep mode)

- [ ] **PHASE-01**: Model review phase — analyze described model, flag health issues (M:M relationships, missing date table, bidirectional filters), outputs findings before any DAX
- [ ] **PHASE-02**: Measures phase — context-aware DAX generation, explicit gate before advancing to next phase

### Verification

- [ ] **VERF-01**: Phase gates — hard checkpoints between phases in deep mode, user must confirm before advancing
- [ ] **VERF-02**: Business question gate — final check that output answers the question stated at the start of the session
- [ ] **VERF-03**: Context re-injection — explicit context summary restated at start of each phase to prevent drift in long sessions

## v2 Requirements

### Visuals & Polish

- **VIS-01**: Visual type recommendations based on the data and business question
- **VIS-02**: Anti-pattern warnings (pie charts for >5 categories, excessive KPI cards, unlabeled axes)
- **POL-01**: Report-level polish review: layout, color consistency, accessibility high-signal items

### Advanced DAX

- **DAX-04**: Pattern-first generation — select from curated SQLBI patterns (15-20 core patterns) when writing complex measures
- **DAX-05**: Fabric/DirectLake-specific guidance (composite models, DirectLake mode gotchas)

### Session Persistence

- **SESS-01**: Persist interrogation context to a file to survive context compaction in long sessions

## Out of Scope

| Feature | Reason |
|---------|--------|
| DAX tutorials / educational content | Scope creep — skill is context-driven assistance, not a learning tool |
| Power BI API / .pbix file access | Conversational only — no file system access to Power BI files |
| Generic templates without model context | Anti-feature — false productivity that reproduces the exact failure mode we're fixing |
| Free-form Q&A mode (no structure) | Destroys phase discipline in deep mode |
| OAuth / Power BI Service integration | Infrastructure dependency; this skill works from described context only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROG-01 | Phase 1 | Pending |
| PROG-02 | Phase 1 | Pending |
| PROG-03 | Phase 1 | Pending |
| PROG-04 | Phase 1 | Pending |
| INTR-01 | Phase 1 | Pending |
| INTR-02 | Phase 1 | Pending |
| INTR-03 | Phase 1 | Pending |
| INTR-04 | Phase 2 | Pending |
| DAX-01 | Phase 2 | Pending |
| DAX-02 | Phase 2 | Pending |
| DAX-03 | Phase 2 | Pending |
| PHASE-01 | Phase 3 | Pending |
| PHASE-02 | Phase 2 | Pending |
| VERF-01 | Phase 3 | Pending |
| VERF-02 | Phase 3 | Pending |
| VERF-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 after roadmap creation*
