# Project: PowerBI DAX Skills for Claude Code

## Overview

This repo contains a single Claude Code skill (`/pbi`) that turns Claude into a Power BI DAX co-pilot. The skill is a markdown file in `.claude/skills/pbi/` with subcommand files in `commands/`. Claude Code discovers the skill automatically.

## Skill Architecture (v3.0)

### Single-skill router

All commands are accessed via `/pbi [subcommand]` (e.g., `/pbi explain`, `/pbi audit`). The router in `SKILL.md` runs detection blocks once, then loads the appropriate command file from `commands/`.

### Subcommand types

- **Paste-in** (work anywhere): explain, format, optimise, comment, error, new
- **PBIP** (require `*.SemanticModel/` directory): load, audit, diff, commit, edit, undo, comment-batch, changelog, extract
- **Utility** (work anywhere): help

### Model selection

- **Sonnet** (default): DAX reasoning subcommands — explain, format, optimise, comment, error, new, edit, comment-batch, audit, help
- **Haiku** (via Agent spawn): file/git-heavy subcommands — load, diff, commit, undo, changelog; also extract simple tier
- **Opus** (via Agent spawn): extract detailed tier (high token usage, deep analysis)

### Detection

Detection blocks run once in `SKILL.md` and are shared by all subcommands:
- **PBIP detection**: globs for `*.SemanticModel` or `.SemanticModel` directories, outputs `PBIP_DIR=<actual folder name>`, then checks format (`model.bim` → TMSL, `definition/tables/` → TMDL)
- **File Index**: lists all `.tmdl` files or model.bim under `$PBIP_DIR`
- **PBIR detection**: globs for `*.Report` or `.Report` directories, outputs `PBIR_DIR=<actual folder name>`
- **Git state**: checks if inside a git repo with commits
- **Session context**: reads `.pbi-context.md`

Desktop detection (`tasklist`) has been removed — file-mode commands always write to disk.

### Conventions

- **Session context**: all commands read/write `.pbi-context.md` using Read-then-Write (never bash append). Keep Command History to 20 rows max. Never modify the Analyst-Reported Failures section.
- **Auto-commit**: edit, comment, error, and new auto-commit after successful writes. Use undo to revert.
- **Path quoting**: all bash paths must be double-quoted to handle spaces in directory names.

### File format rules

- **TMDL files use tabs for indentation** — never convert tabs to spaces when writing back
- **TMSL expression format**: preserve original form (JSON string vs array). Use array form only if the expression contains line breaks
- **grep for measure names**: always use `grep -rlF` (fixed-string) to avoid regex metacharacters in measure names breaking the search
- **DAX in shell commands**: write to a temp file using a single-quoted heredoc delimiter to prevent shell expansion of `$`, backticks, etc.

## Directory Structure

```
.claude/skills/pbi/
  SKILL.md              ← router + detection blocks (v3.0)
  commands/
    explain.md          ← DAX explanation (sonnet)
    format.md           ← DAX formatting (sonnet)
    optimise.md         ← DAX optimisation (sonnet)
    comment.md          ← DAX commenting (sonnet)
    error.md            ← error diagnosis (sonnet)
    new.md              ← measure scaffolding (sonnet)
    load.md             ← PBIP context loader (haiku)
    audit.md            ← model audit + auto-fix (sonnet, parallel agents)
    diff.md             ← model change summary (haiku)
    commit.md           ← git commit (haiku)
    edit.md             ← plain-language model editing (sonnet)
    undo.md             ← revert last auto-commit (haiku)
    comment-batch.md    ← batch commenting (sonnet)
    changelog.md        ← changelog generation (haiku)
    extract.md          ← project extraction (haiku/sonnet/opus by tier)
    help.md             ← command reference (sonnet)
  shared/
    api-notes.md        ← DAX Formatter API reference
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

Current: 4.0.0 (set in `pbi/SKILL.md` frontmatter)
