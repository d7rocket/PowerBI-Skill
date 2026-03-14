# Requirements: PBI Skill v2

**Defined:** 2026-03-14
**Milestone:** v1.1 Complete
**Core Value:** Never block a data analyst — solve immediately, interrogate only when stuck or asked.

## v1.1 Requirements

### Tech Debt

Context-field consistency bugs in `.pbi-context.md` writes that cause cross-command ERR-02 correlation failures.

- [x] **DEBT-01**: User running pbi-edit sees `Measure:` (not `Entity:`) written to `## Last Command` in `.pbi-context.md`, so pbi-error can correctly correlate the last-edited measure
- [ ] **DEBT-02**: User running pbi-diff or pbi-commit sees `Measure:` field written to `## Last Command`, so pbi-error correlates the correct measure after diff/commit workflows
- [x] **DEBT-03**: User running pbi-optimise sees Command History rows written in correct column order (`timestamp | command | measure | outcome`) matching the `.pbi-context.md` schema

### Deep Mode

On-demand structured workflow with model review, phase discipline, and context carry-forward.

- [ ] **PHASE-01**: User entering deep mode sees a model review phase that analyzes their described model and surfaces health issues (M:M relationships, missing date table, bidirectional filters) before any DAX is written
- [ ] **VERF-01**: User in deep mode must confirm at each phase boundary before the session advances to the next phase (hard gate — no auto-advance)
- [ ] **VERF-02**: User completing deep mode sees a final gate that checks the output answers the business question stated at the start of the session
- [ ] **VERF-03**: User at the start of each deep-mode phase sees an explicit context summary (tables, relationships, existing measures, business question) restated to prevent drift

## v2 Requirements

None — all known requirements are captured in v1.1.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Automated Power BI API integration | Conversational skill, not a service connector |
| Generic DAX tutorials | Context-driven assistance, not educational content |
| Free-form Q&A mode without structure | Destroys phase discipline in deep mode |
| OAuth / Power BI Service integration | Works from described context only |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEBT-01 | Phase 3 | Complete |
| DEBT-02 | Phase 3 | Pending |
| DEBT-03 | Phase 3 | Complete |
| PHASE-01 | Phase 4 | Pending |
| VERF-01 | Phase 4 | Pending |
| VERF-02 | Phase 4 | Pending |
| VERF-03 | Phase 4 | Pending |

**Coverage:**
- v1.1 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-14*
*Last updated: 2026-03-14 after v1.1 roadmap creation*
