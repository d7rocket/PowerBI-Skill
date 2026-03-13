# Roadmap: PBI Skill v2

## Overview

The skill is built in three delivery phases. Phase 1 ships the working skill with the progressive friction model: default immediate solve, targeted escalation after failure, no upfront interrogation theater. Phase 2 makes DAX output context-aware: visual placement intake, duplication check, filter context warnings, actual table/column names. Phase 3 adds the on-demand deep workflow: model review phase, phase gates, business question verification, and context re-injection to prevent drift across long sessions.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Skill Core + Escalation** - Working skill file with solve-first default and targeted escalation after 2-3 failed attempts
- [ ] **Phase 2: Context-Aware DAX** - Measures output uses actual model context, checks for duplicates, warns on filter exposure
- [ ] **Phase 3: Deep Mode + Verification** - On-demand structured workflow with model review phase, phase gates, and context re-injection

## Phase Details

### Phase 1: Skill Core + Escalation
**Goal**: Users get immediate DAX help by default; targeted interrogation fires only after attempts stall
**Depends on**: Nothing (first phase)
**Requirements**: PROG-01, PROG-02, PROG-03, PROG-04, INTR-01, INTR-02, INTR-03
**Success Criteria** (what must be TRUE):
  1. User submits a DAX request and the skill attempts a solution immediately, without asking any upfront questions
  2. After 2-3 failed or unresolved attempts, the skill escalates and asks only the questions blocking the solution — not a full pre-flight checklist
  3. Escalation surfaces exactly the blocking gaps: business question, data model state, or existing measures — as targeted questions, not a form
  4. User can invoke deep workflow mode explicitly and the skill does not enter that mode otherwise
**Plans**: TBD

### Phase 2: Context-Aware DAX
**Goal**: Generated DAX is grounded in the user's actual model, avoids duplicates, and flags filter context risks
**Depends on**: Phase 1
**Requirements**: INTR-04, DAX-01, DAX-02, DAX-03, PHASE-02
**Success Criteria** (what must be TRUE):
  1. Generated measures reference the exact table and column names the user described — no placeholder names like [Sales] or [Date]
  2. Before writing a new measure, the skill asks whether a similar measure already exists
  3. When generating CALCULATE-heavy or filter-sensitive DAX (time intelligence, ratios, ranking) without knowing the visual placement, the skill surfaces a filter context warning
  4. Before writing filter-sensitive DAX, the skill asks where the measure will be placed and what slicers are active
  5. The measures phase in deep mode has an explicit gate: user must confirm before the session advances
**Plans**: TBD

### Phase 3: Deep Mode + Verification
**Goal**: On-demand structured workflow is available with model review, hard phase gates, and context carry-forward
**Depends on**: Phase 2
**Requirements**: PHASE-01, VERF-01, VERF-02, VERF-03
**Success Criteria** (what must be TRUE):
  1. In deep mode, model review runs before any DAX: the skill produces a structured summary of tables, relationships, and health flags (M:M, missing date table, bidirectional filters) with no measures written
  2. Each phase boundary in deep mode is a hard gate: user must confirm before the skill advances, not a "looks good?" rubber stamp
  3. At the end of a deep mode session, the skill checks that the final output answers the business question stated at the start
  4. At the start of each phase in deep mode, the skill restates the confirmed context (tables, relationships, existing measures, business question) to prevent drift
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Skill Core + Escalation | 0/TBD | Not started | - |
| 2. Context-Aware DAX | 0/TBD | Not started | - |
| 3. Deep Mode + Verification | 0/TBD | Not started | - |
