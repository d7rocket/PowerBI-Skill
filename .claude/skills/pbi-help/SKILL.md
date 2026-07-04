---
name: pbi-help
description: "Display the complete PBI skill command reference with version check, organized by category (paste-in, PBIP, workflow, utility). Shows model assignment for each command. Offline version check against the bundled changelog — never contacts a remote."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 7.1.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

# /pbi-help

<purpose>
Quick reference for all available commands with enough context to choose the right one. The version check ensures users know when updates are available.
</purpose>

<core_principle>
Show everything in one view. No pagination, no "type help <cmd> for details". The help output is a complete reference that fits on one screen.
</core_principle>

## Instructions

### Step 1 — Version check (offline)

Run the Python version check against the base skill file (no network calls — LOCAL-FIRST policy):

```bash
python ".claude/skills/pbi/scripts/detect.py" version-check ".claude/skills/pbi/SKILL.md" 2>/dev/null || echo "LOCAL=unknown"
```

If the output is `LOCAL=unknown`, retry against the user-level install path:

```bash
python "$HOME/.claude/skills/pbi/scripts/detect.py" version-check "$HOME/.claude/skills/pbi/SKILL.md" 2>/dev/null || echo "LOCAL=unknown"
```

Parse the output: `LOCAL` = installed version (e.g., `7.0.0`).

Then use the Read tool to read `.claude/skills/pbi/shared/CHANGELOG.md` (fall back to `~/.claude/skills/pbi/shared/CHANGELOG.md`). Take the version number from the topmost `## [X.Y.Z]` heading — call it `CHANGELOG_TOP`.

Build the version line for the header:

- If LOCAL is `unknown` OR the changelog could not be read: `**Version:** LOCAL (changelog not available)`
- If LOCAL matches CHANGELOG_TOP: `**Version:** LOCAL ✓ (matches changelog)`
- If they differ: `**Version:** LOCAL — changelog top entry is CHANGELOG_TOP (frontmatter and CHANGELOG.md are out of sync)`

Never run `git ls-remote`, `git fetch`, or any other network command — the version check is offline-only.

### Step 2 — Output help reference

Output the following, inserting the version line from Step 1:

---

```
# /pbi — Power BI DAX Co-Pilot
[version line from Step 1]

## DAX Commands (paste-in — work anywhere)

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi-explain` | Break down a DAX measure into plain English | Sonnet |
| `/pbi-format` | Reformat DAX for readability (uses DAX Formatter API) | Sonnet |
| `/pbi-optimise` | Analyse DAX for performance and suggest improvements | Sonnet |
| `/pbi-comment` | Add inline comments to a DAX measure | Sonnet |
| `/pbi-error` | Diagnose a DAX error and suggest fixes | Sonnet |
| `/pbi-new` | Scaffold a new measure from a plain-English description | Sonnet |

## PBIP Commands (require `*.SemanticModel/` directory)

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi-load` | Read project structure into session context | Haiku |
| `/pbi-audit` | Full model health check with auto-fix for critical issues | Sonnet |
| `/pbi-audit-fix` | Autonomous scan → fix → validate → commit pipeline | Sonnet |
| `/pbi-edit` | Modify model entities from plain-English instructions | Sonnet |
| `/pbi-comment-batch` | Add descriptions to all undocumented measures | Sonnet |
| `/pbi-format-batch` | Apply SQLBI-standard DAX formatting to all measures | Sonnet |
| `/pbi-extract` | Export a structured summary of your PBIP project | Varies |
| `/pbi-diff` | Summarise uncommitted model changes | Haiku |
| `/pbi-commit` | Stage and commit model changes with a generated message | Haiku |
| `/pbi-undo` | Revert the last auto-commit | Haiku |
| `/pbi-changelog` | Generate release notes from recent commits | Haiku |

## Workflow Commands

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi-deep` | Guided multi-phase workflow: intake → model review → DAX dev → verification | Sonnet |
| `/pbi-resume` | Restore session context and continue from where you left off | Haiku |
| `/pbi-version` | Display installed version and full changelog | Haiku |
| `/pbi-docs` | Generate polished, stakeholder-ready project documentation | Sonnet |
| `/pbi-settings` | Toggle write mode: auto (silent writes) vs confirm (ask first) | Haiku |
| `/pbi-help` | Show this reference with version check | Haiku |

## Quick Start

1. **No project?** Paste DAX directly: `/pbi-explain <your DAX>`
2. **Have a PBIP project?** Run `/pbi-load` first, then any command uses model context automatically.
3. **Full guided session?** Use `/pbi-deep` for complex multi-measure work.
4. **Project summary?** Use `/pbi-extract [overview|standard|deep-dive]` to generate a model overview.

## Tips

- All commands read `.pbi/context.md` for session state. Use `/pbi-resume` to see current state, or `/pbi-load` to refresh.
- `/pbi-audit` finds issues; `/pbi-audit-fix` finds AND fixes them autonomously.
- Free-text works too — just type `/pbi <your question>` and it will be solved directly.
- Model selection is automatic: Haiku for file/git ops, Sonnet for DAX reasoning, Opus for deep extraction.
```

---

Stop. Do not output anything else.

### Anti-Patterns
- NEVER suggest git pull or git push
- NEVER run `git ls-remote`, `git fetch`, or any network command — version check is offline-only
- NEVER output anything after the help reference — stop immediately

## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi/context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi/context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
- **Confirm mode (PBI_CONFIRM):** When `PBI_CONFIRM=true`: show preview and ask `(y/N)` before writing model files or output files. When `PBI_CONFIRM=false`: write directly without asking. Commands that already have a `(y/N)` prompt respect this — if PBI_CONFIRM=false, skip the prompt and proceed.
