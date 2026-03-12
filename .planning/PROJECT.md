# PBI Skill

## What This Is

A Claude skill system for Power BI analysts working with PBIP (Power BI Projects) files. Invoked via `/pbi` slash commands, it acts as an intelligent assistant for DAX optimisation, model auditing, best practice enforcement, version control, and commenting — covering both direct PBIP file editing and paste-in workflows (measures, queries, SQL) for analysts with the report open in Power BI Desktop.

## Core Value

A BI analyst can drop into `/pbi` at any point in their workflow — whether staring at a broken measure, auditing a model, or committing changes — and get expert-level help without leaving Claude.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] `/pbi` entry point: asks what the analyst wants to do and routes to the right command/agent
- [ ] `/pbi:optimize` — DAX rewrite for performance (detect slow patterns: FILTER misuse, row context issues, iterator overuse)
- [ ] `/pbi:explain` — plain English explanation of a DAX measure
- [ ] `/pbi:format` — format/prettify DAX (indentation, line breaks, keyword capitalisation)
- [ ] `/pbi:comment` — add inline `//` comments to DAX + populate the measure Description field
- [ ] `/pbi:audit` — full model audit: naming conventions, bi-directional relationships, missing date tables, hidden column hygiene, measure quality
- [ ] `/pbi:commit` — Git workflow for PBIP: stage, write a human-readable commit message summarising model changes
- [ ] `/pbi:diff` — human-readable summary of what changed between commits (measures added/removed/changed, model changes in plain English)
- [ ] `/pbi:edit` — read and write PBIP JSON files directly (for when the report is closed)
- [ ] Paste-in workflow: analyst pastes raw DAX/M/SQL directly — commands work without needing file access
- [ ] Context awareness: detect if working from PBIP files or paste-in context and adapt accordingly

### Out of Scope

- Full report creation — this is a helper, not a report builder
- Data source / gateway configuration — too environment-specific
- Power BI Service API integration (publishing, datasets) — desktop/file-first focus for v1
- Visual formatting / report layout — DAX and model layer only

## Context

- PBIP format stores report definitions as JSON files on disk (`.Dataset/model.bim`, `.Report/report.json`, measure files etc.) — fully readable/writable by Claude
- **Key pain point**: Power BI Desktop must be closed for file edits to take effect — the tool must handle both modes gracefully (edit-on-disk when closed, paste-ready output when open)
- Target user is a BI analyst who already knows Power BI — this tool makes them faster, not teaches them basics
- DAX skill level varies — some analysts are intermediate, some advanced — explanations and suggestions should adapt
- Like GSD: specific commands go straight to work; bare `/pbi` asks a routing question first

## Constraints

- **Tech stack**: Claude skill system (`.claude/commands/` or equivalent), Bash for git operations, JSON parsing for PBIP files
- **File format**: PBIP is JSON-based — no proprietary binary formats for the model layer
- **Scope**: Single PBIP project at a time (one working directory)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Slash command architecture (like GSD) | Analyst knows exactly what command to reach for; smart routing for bare `/pbi` | — Pending |
| Support both file-edit and paste-in modes | PBIP reload pain point means paste-ready output is often more practical | — Pending |
| v1 focuses on DAX + model layer, not visuals | Highest-value pain points are measure quality and model health | — Pending |

---
*Last updated: 2026-03-12 after initialization*
