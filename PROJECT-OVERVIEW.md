# PBI Skill — Project Overview

## The Problem

Power BI developers working with DAX live in two disconnected worlds. They write DAX in Power BI Desktop — a GUI tool with no CLI, no version control, and no programmatic access. When they need help, they context-switch to ChatGPT or documentation, paste fragments of code, lose model context, and start over every time.

Three specific pain points:

1. **DAX is write-only.** A six-month-old measure with nested `CALCULATE`, `SUMX`, and `ALLEXCEPT` is unreadable without significant effort. There is no "explain this measure" button in Power BI Desktop.

2. **PBIP projects are unmanaged.** Microsoft's Power BI Project format (PBIP) gives developers text files (TMDL/TMSL) instead of binary `.pbix` — but no tooling exists to audit, diff, commit, or document those files. Developers get version control without version control workflows.

3. **AI assistance forgets everything.** Every new Claude or ChatGPT conversation starts from zero. The AI doesn't know your tables, your relationships, your existing measures, or what you tried ten minutes ago. You re-explain the same model structure in every session.

## What This Skill Solves

PBI Skill turns Claude Code into a persistent, model-aware Power BI co-pilot that works directly with your project files.

### Solve immediately, interrogate never

The core design principle: **never block a data analyst.** When you ask a DAX question, the skill attempts a solution immediately — no intake forms, no "tell me about your model first." Structured questioning only fires after two consecutive failure signals, and even then, it asks exactly one targeted question per identified gap.

### Model awareness across commands

On first use, the skill reads your PBIP project files (TMDL or TMSL), extracts every table, measure, column, and relationship, and caches the structure in `.pbi-context.md`. Every subsequent command — explain, audit, edit, new — references your actual model. When the skill generates a measure, it uses your real table names and validates against your real relationships.

### Version control that speaks business

PBIP files are text, but `git diff` on a `.tmdl` file is noise. The skill translates file-level changes into model-level descriptions: "Added measure [Revenue YTD] to Sales table" instead of "Modified Sales.tmdl lines 45-52." Commits use conventional prefixes (`feat:`, `fix:`) with business-language messages. All commits are local-only — the skill never pushes, pulls, or touches remotes, because pulling has previously overwritten PBIP relationships.

### Session continuity

`.pbi-context.md` persists model context, command history (20 rows max), analyst-reported failures, escalation state, and in-progress workflow data. The `/pbi-resume` command reconstructs the full working state in a new session — what you were doing, what the model looks like, and what failed before.

## The 20 Commands

| Category | Commands | What they do |
|----------|----------|-------------|
| **Understand DAX** | explain, format, optimise | Break down, reformat, or performance-scan any measure |
| **Fix & Build DAX** | error, new, comment | Diagnose errors, scaffold new measures, add documentation |
| **Audit the Model** | audit, comment-batch | 19-rule health check with auto-fix, batch documentation |
| **Edit the Model** | edit, load | Plain-English model changes, context loading |
| **Version Control** | diff, commit, undo, changelog | Business-language diffs, commits, reverts, release notes |
| **Documentation** | docs, extract | Stakeholder-ready docs, 3-tier model summaries |
| **Workflow** | deep, resume | Guided multi-phase DAX dev, cross-session context restore |
| **Utility** | help, version | Command reference, installed version + changelog |

## Design Decisions That Matter

**Solve-first, not interrogation-first.** A daily-use co-pilot should feel like a colleague who tries to help immediately, not a form that demands context before doing anything. Escalation is progressive — silent retry on first failure, one targeted question on second.

**Local-first git.** The skill never runs `git pull`, `git fetch`, `git push`, or creates PRs. This exists because pulling remote changes has previously overwritten local PBIP files and broken table relationships. Git is used only as a local versioning tool.

**Python-first file operations.** All file reads, writes, and text searches use Python with `encoding='utf-8'`. Shell tools like `grep` and `sed` fail silently on French accented characters (é, è, ç, à). The `detect.py` script centralizes all file operations with 10 subcommands.

**Model selection by task.** Haiku handles file/git operations (load, diff, commit, undo, changelog, resume) — fast and cheap. Sonnet handles DAX reasoning (explain, audit, edit, new) — accurate and detailed. Opus handles deep-dive extraction — thorough but expensive.

**Hard gates in deep mode.** The `/pbi-deep` four-phase workflow (intake → model review → DAX development → verification) uses hard gates — no phase advances without explicit user confirmation. This prevents premature solutions that skip context gathering.

## Evolution

| Version | Date | Milestone |
|---------|------|-----------|
| 1.0 | 2026-03-13 | Initial release — 8 commands, solve-first handler, escalation logic |
| 2.0 | 2026-03-14 | PBIP context loading, session tracking, diff/commit/undo |
| 3.0 | 2026-03-14 | Audit (19 rules), parallel agents, edit, comment-batch, changelog |
| 4.0 | 2026-03-14 | Deep mode, extract (3 tiers), docs, model selection |
| 4.1 | 2026-03-23 | Auto-resume, local-first git policy, installer rewrite |
| 4.3 | 2026-03-23 | Python-first UTF-8, detect.py expansion, TMSL chunked reads |
| 4.4 | 2026-03-24 | Context tracker progress bar, post-command footer |
| 5.0 | 2026-03-28 | Sub-skill architecture — each command is its own `/pbi-<cmd>` skill |
| 6.0 | 2026-03-28 | Resume command, rich descriptions, visual branding, GSD-level quality |

## Who This Is For

Power BI developers who work with PBIP format projects and use Claude Code as their terminal. The skill assumes DAX fluency — it explains measures, it doesn't teach DAX. It assumes the analyst knows their model — it augments, it doesn't replace domain knowledge.

Built by [d7rocket](https://github.com/d7rocket). MIT licensed.
