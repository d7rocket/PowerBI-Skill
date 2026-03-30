# Project: PowerBI DAX Skills for Claude Code

## Overview

This repo contains a Claude Code skill namespace (`/pbi`) that turns Claude into a Power BI DAX co-pilot. Each command is an individual skill invoked as `/pbi:<command>` (e.g., `/pbi:explain`, `/pbi:audit`). The base `/pbi` provides a menu, catch-all solver, and backward-compatible routing.

## Skill Architecture (v6.0)

### Individual sub-skills

Each command is a self-contained skill at `.claude/skills/pbi/<cmd>/SKILL.md`, directly invocable as `/pbi:<cmd>`. Each sub-skill includes its own detection blocks, auto-resume logic, command instructions, and shared rules.

The base `/pbi` (at `.claude/skills/pbi/SKILL.md`) serves as:
- **Menu** — shows categories when invoked with no arguments
- **Catch-all solver** — handles free-text DAX questions directly
- **Backward-compatible router** — `/pbi explain` still works, routing to `/pbi:explain`

### Command types

- **Paste-in** (work anywhere): `/pbi:explain`, `/pbi:format`, `/pbi:optimise`, `/pbi:comment`, `/pbi:error`, `/pbi:new`
- **PBIP** (require `*.SemanticModel/` directory): `/pbi:load`, `/pbi:audit`, `/pbi:diff`, `/pbi:commit`, `/pbi:edit`, `/pbi:undo`, `/pbi:comment-batch`, `/pbi:changelog`, `/pbi:extract`, `/pbi:docs`
- **Workflow**: `/pbi:deep`
- **Session**: `/pbi:resume`
- **Utility** (work anywhere): `/pbi:help`, `/pbi:version`

### Model selection

- **Sonnet** (default): DAX reasoning commands — explain, format, optimise, comment, error, new, edit, comment-batch, audit, docs, deep, extract, help, version
- **Haiku** (set in frontmatter): file/git-heavy commands — load, diff, commit, undo, changelog, resume
- **Opus** (via Agent spawn): extract detailed tier (high token usage, deep analysis)

### Detection

Each sub-skill runs its own detection blocks on load via `!` backtick syntax:
- **PBIP detection**: globs for `*.SemanticModel` or `.SemanticModel` directories, outputs `PBIP_DIR=<actual folder name>`, then checks format (`model.bim` → TMSL, `definition/tables/` → TMDL)
- **File Index**: lists all `.tmdl` files or model.bim under `$PBIP_DIR`
- **PBIR detection**: globs for `*.Report` or `.Report` directories, outputs `PBIR_DIR=<actual folder name>`
- **Git state**: checks if inside a git repo with commits
- **Session context**: reads `.pbi-context.md`

### Conventions

- **Session context**: all commands read/write `.pbi-context.md` using Read-then-Write (never bash append). Keep Command History to 20 rows max. Never modify the Analyst-Reported Failures section.
- **Session-aware auto-load**: the first `/pbi` command in each session always runs a fresh load to ensure model data is current. Subsequent commands in the same session resume from cached context (2-hour session window). No explicit `/pbi:load` required.
- **Auto-commit**: edit, comment, error, and new auto-commit after successful writes. Use undo to revert. All commits are LOCAL only.
- **Post-command staging**: after every command that writes to `$PBIP_DIR/`, changes are auto-staged (`git add`) and the user is notified.
- **LOCAL-FIRST GIT POLICY (CRITICAL)**: NEVER `git pull`, `git fetch`, `git merge`, `git push`, or create PRs. Local files are always the source of truth. Pulling has previously overwritten PBIP changes and broken relationships. Git is used only for local version control (`init`, `add`, `commit`, `diff`, `log`, `status`, `revert`).
- **Path quoting**: all bash paths must be double-quoted to handle spaces in directory names.

### File format rules

- **TMDL files use tabs for indentation** — never convert tabs to spaces when writing back
- **TMSL expression format**: preserve original form (JSON string vs array). Use array form only if the expression contains line breaks
- **Python-first file operations**: always use Python with `encoding='utf-8'` for file read/write and text search. Use `detect.py search` instead of `grep -rlF` for measure name search. Shell/bash is only for git CLI commands.
- **UTF-8 encoding**: model files may contain French accented characters (é, è, ê, ç, à, ù). All file operations must handle UTF-8 correctly.

## Directory Structure

```
.claude/skills/pbi/
  SKILL.md              ← base /pbi (menu + catch-all + backward-compatible router)
  explain/SKILL.md      ← /pbi:explain (sonnet)
  format/SKILL.md       ← /pbi:format (sonnet)
  optimise/SKILL.md     ← /pbi:optimise (sonnet)
  comment/SKILL.md      ← /pbi:comment (sonnet)
  error/SKILL.md        ← /pbi:error (sonnet)
  new/SKILL.md          ← /pbi:new (sonnet)
  load/SKILL.md         ← /pbi:load (haiku)
  audit/SKILL.md        ← /pbi:audit (sonnet, parallel agents for 5+ table models)
  diff/SKILL.md         ← /pbi:diff (haiku)
  commit/SKILL.md       ← /pbi:commit (haiku)
  edit/SKILL.md         ← /pbi:edit (sonnet)
  undo/SKILL.md         ← /pbi:undo (haiku)
  comment-batch/SKILL.md ← /pbi:comment-batch (sonnet)
  changelog/SKILL.md    ← /pbi:changelog (haiku)
  deep/SKILL.md         ← /pbi:deep (sonnet)
  extract/SKILL.md      ← /pbi:extract (sonnet, agents for opus tier)
  docs/SKILL.md         ← /pbi:docs (sonnet)
  help/SKILL.md         ← /pbi:help (sonnet)
  version/SKILL.md      ← /pbi:version (sonnet)
  resume/SKILL.md       ← /pbi:resume (haiku)
  scripts/
    detect.py           ← Python detection, search, HTML parsing, version check, session check, gitignore (UTF-8 safe, 11 subcommands)
  shared/
    api-notes.md        ← DAX Formatter API reference
    CHANGELOG.md        ← version history (read by /pbi:version)
    ui-brand.md         ← visual output standards reference
```

## Testing

Test fixtures are in `tests/fixtures/`:
- `.dax` files: individual DAX measures for paste-in testing
- `pbip-tmdl/`: TMDL project with git repo, 3 tables, relationships, bidirectional filter (audit trigger)
- `pbip-tmsl/`: TMSL project (model.bim)
- `pbip-no-repo/`: TMDL project with no git repo (tests git init flow)
- `pbip-empty-model/`: project with tables but no measures
- `context-20-rows.md`: saturated command history (tests trim-to-20 logic)

## Known Limitations

- **Session context race condition**: simultaneous skill invocations can overwrite each other's `.pbi-context.md` updates. Not an issue in interactive use but worth noting.
- **Audit parallelism**: for models with 5+ tables, audit spawns 3 parallel agents for domain passes. For < 5 tables, runs sequentially to avoid agent overhead.

## Version

Current: 6.1.0 (set in `pbi/SKILL.md` frontmatter)
