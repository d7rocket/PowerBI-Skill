# Project: pbi - Power BI DAX co-pilot plugin for Claude Code

## Overview

This repo is a Claude Code plugin marketplace with one plugin, `pbi`, in `plugins/pbi/`.
The plugin turns Claude into a Power BI DAX co-pilot.
Each command is a skill invoked as `/pbi:<command>` (for example `/pbi:explain`, `/pbi:audit`).
`/pbi:menu` is the menu and the free-text solver.

## Architecture (v8)

### One preflight, shared rules

Every command file starts with a single dynamic block:

```
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight ...`
```

`preflight` prints, in under a second:

- project detection: `PBIP_MODE` (`file` or `paste`), `PBIP_FORMAT` (`tmdl`, `tmsl`, `unknown`), `PBIP_DIR`, `PBIR_DIR`, git state, `UNAPPLIED_CHANGES`
- hints: `DESKTOP` (running or not), `LIVE_MCP_CONFIG`, `PENDING_LIVE_CHANGES`
- the model index, parsed from disk: tables, column and measure counts, measure names, relationships
- recent commands, saved notes and analyst-reported failures from `.pbi/context.md`
- the full text of `shared/core.md`, the rules every command follows

Command files therefore contain only what is specific to the command.
Shared behaviour is changed in `shared/core.md` or `shared/live-mode.md`, never copied into command files.

### Edit tiers

- **LIVE**: Microsoft's Power BI Modeling MCP tools are available in the session. Commands read and write the model open in Power BI Desktop, and execute measures to verify them. Procedure: `shared/live-mode.md`.
- **FILE**: otherwise. Commands edit TMDL or TMSL files. Procedure: `shared/core.md` section 5.
- **Paste mode**: no project. DAX in, DAX out, nothing written.

The MCP server is never bundled or auto-registered.
`/pbi:setup` registers it only after explaining Microsoft's EULA and data collection and getting an explicit yes.

### Command groups

- **Measure** (paste DAX or name a project measure): `explain`, `format`, `optimise`, `comment`, `error`, `new`
- **Model** (need a `*.SemanticModel/` folder): `load`, `edit`, `audit`, `extract`, `docs`, `deep`
- **History**: `diff`, `commit`, `undo`, `changelog`, `resume`
- **Live**: `query`, `setup`
- **Utility**: `menu`, `help`, `version`

### Model selection

- **Sonnet**: DAX reasoning and anything that writes: explain, format, optimise, comment, error, new, edit, audit, docs, deep, extract, undo, query, setup, menu
- **Haiku**: mechanical and read-only: load, diff, commit, changelog, resume, help, version
- **Opus** (via Agent spawn): extract deep-dive tier

### Conventions

- **Preview and confirm**: every model change shows Before and After and needs an explicit `y`. There is no auto mode and no settings file. Generated reports under `.pbi/` are written directly.
- **Verify**: after a write, re-read the object (and execute it when live). State which checks ran. Never claim a change works when it was only written.
- **Record**: after a confirmed change, the command writes `.pbi/change.json` and calls `detect.py record`. For file-tier changes that one call commits the model folder and journals the change with the commit it made. Commands do not run `git add` or `git commit` themselves, except `/pbi:commit`.
- **Live changes commit on save**: a live change reaches the files when the analyst saves in Desktop. `detect.py snapshot` then commits it with the journaled message.
- **Undo** reads the journal (`.pbi/journal.jsonl`): reverse through the MCP for live changes, `git revert` for file changes. Never `git reset`.
- **Session log**: `detect.py log` and `detect.py note` write `.pbi/context.md` with a lock and an atomic rename. Commands never rewrite that file by hand. The Analyst-Reported Failures section is never modified.
- **No bulk rewrites**: one object per change. The batch and auto-fix commands were removed in v8 on purpose.
- **LOCAL ONLY (CRITICAL)**: never `git pull`, `fetch`, `merge`, `rebase`, `push`, or open PRs from a command. Never connect to a Fabric or Power BI service workspace, never deploy or publish.
- **Output**: lead with the result. No banners, mode headers or loading lines. At most one `Next:` line.
- **Path quoting**: all shell paths are double-quoted.
- **No em dashes** in anything new. Use a plain dash.

### File format rules

- **TMDL files use tabs for indentation**. Never convert tabs to spaces.
- **TMSL expression format**: preserve the original form (string or array). Use the array form only if the expression has line breaks.
- **Python-first file operations**: Python with `encoding='utf-8'`, or the Read, Write and Edit tools. `detect.py search` and `detect.py measure` instead of `grep`. Shell is for git and for calling the scripts.
- **UTF-8**: model files may contain French accented characters (é, è, ê, ç, à, ù).

### DAX style

- **Simplicity-first**: the simplest expression that answers the business question. A plain `SUM`/`DIVIDE` beats a `CALCULATE` wrapper with no filter arguments. No `VAR/RETURN` for a single-use expression. No `IFERROR` or defensive BLANK handling unless the analyst asks.
- The full guides are `shared/dax-style.md`, `shared/modeling.md` and `shared/performance.md`. They are distilled from Microsoft's `skills-for-fabric` (MIT) and carry an attribution section. Keep it.
- Never suggest bidirectional cross-filtering as a first approach.

### Power BI Desktop

- When project files change on disk, Desktop offers to refresh. Commands tell the analyst to accept that prompt (or reopen the project). They do not try to reload Desktop.
- Report-side (PBIR) commands are not part of v8.

### Documentation generation

- Client-facing documentation uses French for headings and content unless told otherwise.
- When generating Word documents, test RGBColor imports and markdown-to-docx conversion before a full run.
- Verify stakeholder names and details with the user before finalizing onboarding or project docs.

### Python environment

- Several Python versions are installed on the dev machine. Verify which `python`/`pip` is active before installing packages.
- The scripts use the standard library only, except `gen_docx.py` (python-docx) and `gen_pdf.py` (reportlab).
- Command files call `python` and fall back to `python3`.

## Directory structure

```
.claude-plugin/marketplace.json     marketplace "powerbi-skill", lists the pbi plugin
plugins/pbi/
  .claude-plugin/plugin.json        manifest; "version" is the single source of truth
  skills/<command>/SKILL.md         22 commands
  scripts/
    detect.py                       preflight, model index, measure, search, log, note,
                                    record, journal-last, journal-undone, snapshot, env,
                                    version, gitignore-check, html-parse, rules
    validate-edit.py                PostToolUse hook: TMDL control characters and space indentation
    gen_docx.py, gen_pdf.py         /pbi:docs generators
  hooks/hooks.json                  registers validate-edit.py for Edit and Write
  shared/
    core.md                         rules every command follows (injected by preflight)
    live-mode.md                    LIVE tier procedure
    dax-style.md, modeling.md, performance.md   distilled guides
    api-notes.md                    DAX Formatter API reference
    ui-brand.md                     visual output standards
    pbi-docs-contract.md            docgen output contract for /pbi:docs
    CHANGELOG.md                    version history (read by /pbi:version)
tests/
  test_detect.py                    script, hook and plugin-integrity tests
  fixtures/                         .dax files and PBIP fixture projects
```

## Working on the plugin

- Run it locally: `claude --plugin-dir plugins/pbi`, then `/pbi:help`.
- Validate: `claude plugin validate .` and `claude plugin validate ./plugins/pbi`.
- Test: `python tests/test_detect.py` (or pytest). The integrity test fails on stale v7 references, missing shared files and unknown `/pbi:` command names.
- End-to-end check of a write command: run it with `claude --plugin-dir plugins/pbi -p "/pbi:edit ..."` in a copy of a fixture project, answer with `--continue -p "y"`, then inspect `git log`, the diff and `.pbi/journal.jsonl`.
- Live mode can only be tested with Power BI Desktop open on a real project and the MCP registered.

## Testing fixtures

- `.dax` files: individual DAX measures for paste-in testing
- `pbip-tmdl/`: TMDL project, relationships, bidirectional filter (audit trigger), `unappliedChanges.json`
- `pbip-tmsl/`: TMSL project (model.bim)
- `pbip-no-repo/`: TMDL project with no git repo (tests the git init flow)
- `pbip-empty-model/`: tables but no measures
- `pbip-tmdl-no-gitignore/`: TMDL project without .gitignore
- `context-20-rows.md`: saturated command history (tests trim-to-20)

## Known limitations

- **Live mode is untested in CI**: it needs Power BI Desktop. Changes to `shared/live-mode.md` must be checked by hand against a real model.
- **MCP operation names** are not hardcoded. Commands read the tool schema at run time, because Microsoft may rename operations between releases.
- **Audit parallelism**: for models with 5+ tables, audit spawns 3 parallel agents. Below that it runs sequentially.

## Version

Current: 8.0.1, set in `plugins/pbi/.claude-plugin/plugin.json`.
The top entry of `plugins/pbi/shared/CHANGELOG.md` must match (enforced by a test).
