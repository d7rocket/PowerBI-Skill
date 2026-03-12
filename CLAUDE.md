# Project: PowerBI DAX Skills for Claude Code

## Overview

This repo contains Claude Code skills (`/pbi:*`) that turn Claude into a Power BI DAX co-pilot. Skills are markdown files in `.claude/skills/` that Claude Code loads automatically.

## Skill Architecture

### Skill types

- **Paste-in skills** (work anywhere): `pbi-explain`, `pbi-format`, `pbi-optimise`, `pbi-comment`, `pbi-error`
- **PBIP skills** (require `.SemanticModel/` directory): `pbi-load`, `pbi-audit`, `pbi-diff`, `pbi-commit`, `pbi-edit`, `pbi-undo`
- **Router**: `pbi` — entry point that routes to subcommands

### Conventions

- **Frontmatter**: every skill has `name`, `description`, `disable-model-invocation: true` (for paste-in skills), `model`, and `allowed-tools`
- **PBIP detection**: skills that touch model files detect the project format using file-existence checks (`model.bim` → TMSL, `definition/tables/` → TMDL). Detection logic is inline in each skill's `!` block.
- **Desktop check**: write-capable skills check whether Power BI Desktop is running. If open, output is paste-ready; if closed, files are written to disk. The `tasklist` check is Windows-only — non-Windows environments default to DESKTOP=closed (safe).
- **Session context**: all skills read/write `.pbi-context.md` using Read-then-Write (never bash append). Keep Command History to 20 rows max. Never modify the Analyst-Reported Failures section.
- **Auto-commit**: `pbi-edit`, `pbi-comment`, and `pbi-error` auto-commit after successful writes. Use `pbi-undo` to revert.

### File format rules

- **TMDL files use tabs for indentation** — never convert tabs to spaces when writing back
- **TMSL expression format**: preserve original form (JSON string vs array). Use array form only if the expression contains line breaks
- **grep for measure names**: always use `grep -rlF` (fixed-string) to avoid regex metacharacters in measure names breaking the search
- **DAX in shell commands**: write to a temp file using a single-quoted heredoc delimiter to prevent shell expansion of `$`, backticks, etc.

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
- **Audit parallelism**: `pbi-audit` runs 4 domain passes sequentially. For large enterprise models (100+ tables), adding Agent-based parallelism per domain would improve latency. Currently acceptable for typical models.
- **Desktop detection**: Windows-only via `tasklist`. Non-Windows defaults to DESKTOP=closed safely.

## Version

Current: 2.0.0 (set in `pbi/SKILL.md` frontmatter)
