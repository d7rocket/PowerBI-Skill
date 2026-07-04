# Changelog

All notable changes to the PBI skill are documented here.
Format: [Keep a Changelog](https://keepachangelog.com)

## [7.1.0] — 2026-07-04

### Added
- **Simplicity-first DAX principle** across all generation commands (`/pbi-new`, `/pbi-edit`, `/pbi-deep`, `/pbi-error`): prefer the simplest DAX that meets the requirement — no CALCULATE without filter arguments, no VAR/RETURN for single-use expressions, no IFERROR/defensive BLANK-handling unless requested.
- `/pbi-optimise` Rule 14 — flags gratuitous IFERROR (rewrite to DIVIDE or remove).
- `validate-edit.py` now registered as a PostToolUse hook in `.claude/settings.json` (previously never executed) and validates TMDL tab-only indentation in addition to control characters.
- `/pbi-audit-fix` fully packaged: command descriptor, installer entries (23 commands), README documentation.
- `tests/test_detect.py` — automated test suite for detect.py subcommands.
- Installers now download `validate-edit.py`, `gen_docx.py`, `gen_pdf.py`, and `pbi-docs-contract.md`, and clean up legacy pre-7.1 `pbi:<cmd>` command files and v5/v6 nested sub-skill directories.

### Fixed
- `/pbi-optimise` Rule 13 no longer rewrites all-time running totals to DATESYTD (semantics-changing); the case is now flag-only. Removed inaccurate "xmatch" and SWITCH-evaluation claims.
- `/pbi-format-batch` no longer instructs 4-space indentation inside TMDL expression blocks (tabs-only, applied relative to block depth); restored the full Shared Rules block and missing Session Context detection.
- `detect.py html-parse` now unescapes HTML entities — DAX containing `<`, `>`, `&&`, `&` is no longer written back HTML-escaped.
- `detect.py files` now includes `relationships.tmdl`, `model.tmdl`, and `expressions.tmdl` in the File Index.
- Base `/pbi` router updated to post-rename flat paths (`.claude/skills/pbi-<cmd>/SKILL.md`); menu/handler drift fixed (format-batch, H/S options, auto-commit list).
- `/pbi-help` no longer calls `git ls-remote` (LOCAL-FIRST violation) — version check is now offline; added Shared Rules and the missing `/pbi-settings` row.
- `/pbi-undo` handles empty and single-commit repos, only auto-reverts commits matching PBI auto-commit patterns, and invalidates stale session context after revert.
- `/pbi-commit` and `/pbi-diff` now diff the whole `definition/` folder (previously missed `expressions.tmdl` and `model.tmdl` changes).
- `/pbi-audit` parallel path now runs domains G and H; rule count corrected to 21; P-02 memory advice corrected; M-02/M-03 severities swapped; PBI_CONFIRM instruction moved out of the output template.
- `/pbi-changelog` writes to `.pbi/changelog.md` (never overwrites a root CHANGELOG.md) and respects scope arguments beyond 50 commits.
- `/pbi-extract` writes to `.pbi/project-extract.md` (was project root) and no longer spawns an agent for the overview tier.
- `/pbi-error` fixes no longer prescribe redundant `CALCULATE()` wrappers in iterators or blanket BLANK→0 wrapping; `/pbi-comment` no longer forces inline comments onto trivial measures.
- `gen_docx.py`/`gen_pdf.py`: multi-line DAX and ERD content renders correctly; PDF table cells wrap; Word page-number field renders without manual refresh.
- `session_check` no longer crashes on timestamps without timezone; `gitignore_check` no longer corrupts a `.gitignore` lacking a trailing newline.

### Changed
- `pbi:<cmd>` → `/pbi-<cmd>` flat skill structure (rename from commit b95a530, now documented); all command descriptor `name:` fields updated.
- Model assignments: `format`/`format-batch` → sonnet (reasoning); `help`/`version`/`settings` → haiku (mechanical).
- `.pbi/settings.json` is no longer git-tracked (per-user preference).
- `pbi-docs-contract.md` moved to `.claude/skills/pbi/shared/` and referenced from `/pbi-docs`.

## [7.0.1] — 2026-04-07

### Fixed
- `/pbi-docs` Markdown output now fully compliant with `pbi-docgen` pipeline contract:
  - Section headings use explicit `##` H2 with keyword-matched heading text (`## Overview`, `## Data Model`, `## Measures & KPIs`, `## Business Logic`, `## Columns`, `## Data Sources`, `## Report Pages`, `## Model Health`)
  - DAX expressions wrapped in ` ```dax ` fenced blocks; M/Power Query in ` ```m `; SQL in ` ```sql `
  - Tabular data uses pipe table format throughout
  - Anti-patterns extended to explicitly prohibit `CODE_BLOCK:`/`END_CODE_BLOCK` and `TABLE:`/`END_TABLE` markers
- Added `pbi-docs-contract.md` — reference spec defining docgen output requirements

## [7.0.0] — 2026-04-01

### Added
- `/pbi-format-batch` — bulk-format every measure in the model in one pass (SQLBI-standard structure, VAR/RETURN blocks, CALCULATE arguments, keyword capitalisation). No DAX Formatter API dependency. Auto-commits.
- `/pbi-settings` — dedicated slash command for toggling write mode: `auto` (silent writes) vs `confirm` (preview before every write). Replaces keyword-only access via `/pbi settings`.
- `format-batch` and `settings` added to both `install.ps1` and `install.sh` installers (22 sub-skills total).

### Changed
- Version bumped to 7.0.0 — marks completion of the full sub-skill architecture: all 22 commands are independently invocable as `/pbi-<cmd>`.
- README updated with new ASCII art banner, v7 What's New section, and complete 22-command table.
- `install.sh` updated to include `settings` and `format-batch` in the commands array.

## [6.2.0] — 2026-03-31

### Added
- `/pbi-settings` is now a dedicated slash command — directly invocable as `/pbi-settings` (previously only accessible as a keyword via `/pbi settings`)
- `settings/SKILL.md` sub-skill with proper frontmatter (model: sonnet, version: 6.1.0)
- `.claude/commands/pbi-settings.md` command stub added to installer

### Fixed
- All 20 `.claude/commands/*.md` files updated to v6.1: now write context to `.pbi/context.md` (previously wrote to stale `.pbi-context.md` path)
- All 20 commands files now include `ensure-dir`, `migrate`, and `settings` detection steps
- All 20 commands files now use `detect.py session-check` auto-resume logic (SESSION=active/new) instead of checking `## Model Context` presence
- Session-start format standardised across all sub-skills: auto-resume blocks now write `**Session-Start:** [ISO timestamp]` (the format `detect.py session_check()` expects), replacing the ambiguous `## Session Start` heading that could produce a two-line write
- All 20 sub-skill `version:` metadata updated from `6.0.0` to `6.1.0`

## [6.1.0] — 2026-03-30

### Added

- Session-aware auto-load — first `/pbi` command in each session runs a fresh model load to ensure data is current; subsequent commands resume from cache (2-hour session window)
- `detect.py session-check` subcommand — reads `**Session-Start:**` timestamp from `.pbi-context.md` and outputs `SESSION=active` or `SESSION=new`

### Removed

- Context usage bar (`detect.py context-bar`) — removed from all 20 commands and the Post-Command Epilogue
- `## Post-Command Footer` sections removed from all sub-skill and command files
- Context bar references removed from `ui-brand.md`

### Changed

- Auto-Resume logic across all sub-skills now checks session state before deciding whether to load or resume
- `/pbi-load` now writes `**Session-Start:**` timestamp to `.pbi-context.md` to mark the session as active

## [6.0.0] — 2026-03-28

### Added

- `/pbi-resume` command — restore session context across sessions with model state, command history, workflow progress, and git state summary
- `<purpose>` and `<core_principle>` blocks on all 20 commands — explains WHY each command exists and HOW it makes decisions
- `shared/ui-brand.md` — visual output standards reference (stage banners, status symbols, severity tags, progress bars)
- Context freshness tracking — resume command shows whether cached context is Current, Recent, or Stale
- Conditional workflow state display — resume shows active deep-mode phase and pending escalation questions

### Changed

- All 20 sub-skill descriptions rewritten with specific capabilities, not just trigger phrases
- Help command updated with resume, version, and docs in the command table
- Base router menu expanded with category H (Resume session)
- Installers updated to download resume skill and ui-brand.md shared resource

## [4.4.0] — 2026-03-24

### Added

- Context tracker progress bar — every command now outputs a visual context usage indicator as its final line
- `detect.py context-bar` subcommand — centralized progress bar logic (reads Command History rows from .pbi-context.md)
- Post-Command Footer added to all 17 command files for reliable context bar output

### Changed

- Post-Command Epilogue in SKILL.md updated to use `detect.py context-bar` instead of inline prose instructions

## [4.3.0] — 2026-03-23

### Changed

- Python-first UTF-8 file operations: all measure search now uses `detect.py search` instead of `grep -rlF` in edit.md, comment.md, error.md, and new.md
- `format.md` HTML response parsing migrated to `detect.py html-parse` Python subcommand
- `help.md` version check migrated to `detect.py version-check` Python subcommand
- `detect.py` expanded with three new subcommands: `html-parse`, `version-check`, `gitignore-check`
- TMSL large-file guard added: commands reading model.bim use offset/limit chunked-read at 2000-line threshold (edit.md, comment.md, error.md, new.md, load.md)

## [4.1.0] — 2026-03-23

### Added

- Auto-resume — every `/pbi` invocation auto-loads project context from `.pbi-context.md` without requiring explicit `/pbi load`
- LOCAL-FIRST GIT POLICY enforced in all commands — `git pull`, `git fetch`, `git push` are never used; local files are always the source of truth

### Changed

- Installer (`install.ps1`) rewritten with `-Scope project|user` parameter, full file manifest including `detect.py` and `docs.md`, dynamic version banner read from downloaded SKILL.md
- `scripts/` directory created automatically by installer; `detect.py` placed inside it

## [4.0.0] — 2026-03-14

### Added

- `/pbi docs` command — generates polished, stakeholder-ready model documentation from PBIP project
- `/pbi extract` command with three tiers (overview, standard, deep-dive) for structured project summaries
- `/pbi deep` command — guided multi-phase workflow with upfront context gathering, model review, DAX development, and verification phases

### Changed

- Routing table extended to cover `docs`, `extract`, and `deep` keywords
- Model selection is now automatic — Haiku for file/git operations, Sonnet for DAX reasoning, Opus for deep-dive extraction

## [3.0.0] — 2026-03-14

### Added

- `/pbi audit` command — full model health check with auto-fix for critical issues (bidirectional filters, unhidden key columns, naming violations)
- `/pbi comment-batch` command — adds descriptions to all undocumented measures in a single pass
- `/pbi changelog` command — generates release notes from recent local git commits
- Parallel agent execution for audit on models with 5+ tables (3 domain-pass agents)
- `/pbi edit` command — modify model entities from plain-English instructions with auto-commit

### Changed

- All PBIP commands now use the `PBIP_DIR` value from detection output — never a hardcoded `.SemanticModel`
- Auto-commit added after successful writes in edit, comment, error, and new; `/pbi undo` reverts the last auto-commit
- Post-command auto-stage — after every command that writes to `$PBIP_DIR/`, changes are staged with `git add`

## [2.0.0] — 2026-03-14

### Added

- PBIP context loading — `/pbi load` reads all TMDL/TMSL files, extracts table/measure/column/relationship structure into `.pbi-context.md`
- `/pbi diff` command — summarises uncommitted model changes using `git diff`
- `/pbi commit` command — stages and commits model changes with a generated commit message
- `/pbi undo` command — reverts the last auto-commit using `git revert`
- Session context tracking — every command reads and writes `.pbi-context.md`; Command History is trimmed to 20 rows max

### Changed

- Detection blocks run once in SKILL.md and are shared by all subcommands (PBIP detection, file index, PBIR detection, git state)
- Post-command epilogue added — auto-stage and context tracking (progress bar) after every subcommand

## [1.0.0] — 2026-03-13

### Added

- Initial release of `/pbi` skill for Claude Code
- Core subcommands: `explain`, `format`, `optimise`, `comment`, `error`, `new`, `load`, `help`
- DAX Formatter API integration: `format` uses `shared/api-notes.md` for API reference
- Solve-First Default handler: free-text questions route to an immediate DAX solution with a two-failure escalation flow
- Escalation logic: silent retry on first failure, one targeted question on second failure, escalation state written to `.pbi-context.md`
- `detect.py` utility script for UTF-8-safe PBIP/PBIR/git detection
