# PBI Skill v2

## What This Is

A redesigned Claude Code skill for Power BI development that brings GSD-style structure to report work. Instead of jumping straight to DAX, it interrogates the problem first, breaks the work into phases, and verifies the output actually answers the business question before moving on.

## Core Value

Never write a line of DAX until the business question, data model state, and existing measures are understood.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Skill opens with deep questioning: extract data model state, existing measures, and intended business question before any code
- [ ] Phase-based workflow: model review → measures → visuals → polish
- [ ] Verification gate after each phase: confirm output answers the business question
- [ ] Context-aware DAX: generated measures account for existing model structure and don't duplicate existing calculations
- [ ] Full report workflow coverage: model advice, measure writing, visual recommendations, output polish

### Out of Scope

- Automated Power BI API integration — this is a conversational skill, not a service connector
- Generic DAX tutorials — skill should be context-driven, not educational content

## Context

Current skill exists but lacks structure. It accepts vague requests and jumps to DAX without:
1. Understanding the data model (tables, relationships, existing calculated columns/measures)
2. Clarifying the business question the report needs to answer
3. Establishing a workflow with checkpoints

GSD (Get Shit Done) is the reference model: deep questioning first, phased execution, verification gates between phases.

## Constraints

- **Scope**: Claude Code skill file — a `.md` prompt file that Claude reads and executes
- **Interaction**: Conversational only — no file system access to .pbix files, works from user-described context
- **Audience**: Devesh (Power BI / DAX developer using Claude Code daily)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Model after GSD structure | User explicitly identified GSD as the reference for quality | — Pending |
| Data model state + existing measures as mandatory pre-flight | All three failure modes (jumps to DAX, misses business Q, no clarification) stem from skipping this | — Pending |

---
*Last updated: 2026-03-13 after initialization*
