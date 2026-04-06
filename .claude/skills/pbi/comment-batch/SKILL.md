---
name: pbi:comment-batch
description: "Scan the entire semantic model and add description properties to every measure that lacks one. Generates contextually accurate descriptions by analyzing each measure's expression, format string, and relationships. Processes table-by-table with progress tracking. Auto-commits."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.1.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection (run once)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report`. Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

### PBI Directory Setup
!`python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null && python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null`

### PBIP Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"`

Save the `PBIP_DIR` value from the output — all subsequent steps must use it instead of a hardcoded `.SemanticModel`.

### File Index
!`python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null`

### PBIR Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"`

### Git State
!`python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")`

### Session Context
!`python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."`

### Settings
!`python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"`

Save the `PBI_CONFIRM` value — commands use it to decide whether to ask before writing files.

### Auto-Resume (session-aware)

After detection blocks run, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null`
   - If output is `SESSION=active` — context was already loaded this session:
     - Output on a single line: `Context resumed — [N] tables loaded` (count from Session Context)
     - Skip any "Model Context Check" (Step 0.5) below — context is already available.
   - If output is `SESSION=new` — first command this session:
     - Output: `Loading model context (first command this session)...`
     - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi/context.md`.
     - Write `**Session-Start:** [current UTC time in ISO 8601]` immediately after the `## Model Context` heading line in `.pbi/context.md`.
     - Output the summary table and: `Context loaded — [N] tables. Ready.`

2. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.


---

# /pbi:comment-batch

<purpose>
Undocumented measures are invisible to report consumers — Power BI Desktop shows blank tooltips. Batch commenting brings the entire model to documentation parity in one pass.
</purpose>

<core_principle>
Generate descriptions for report CONSUMERS, not DAX developers. "Shows total revenue for the current fiscal year" is useful. "Uses CALCULATE with DATESYTD to sum the Amount column" is not.
</core_principle>

## Instructions

### Step 0 — PBIP-Only Guard

If PBIP_MODE=paste:
- Output: "Batch commenting requires a PBIP project. Run /pbi:comment-batch from a directory containing a *.SemanticModel/ folder. For a single measure, use /pbi:comment instead."
- Stop.

If PBIP_MODE=file: output header:
> File mode — PBIP project detected ([FORMAT])

---

### Step 1 — Scope Selection

If `$ARGUMENTS` contains a table name (e.g., `--table Sales` or just `Sales`):
- Set SCOPE=table, TARGET_TABLE=[table name]

If `$ARGUMENTS` contains `--all` or `all`:
- Set SCOPE=all

Otherwise output: "Comment all measures in one table, or the entire model?"
- "**One table** — type the table name"
- "**All** — type `all`"

Wait for response and set SCOPE accordingly.

---

### Step 2 — Discover Measures

**If PBIP_FORMAT=tmdl:**

Read each `.tmdl` file (from File Index) that matches the scope:
- SCOPE=table: read only `[TARGET_TABLE].tmdl`
- SCOPE=all: read all `.tmdl` files

For each file, extract all measure blocks:
- Measure name: text after `measure ` up to ` =`, stripping single quotes
- Expression: lines from the `=` through the next property line (`formatString:`, `displayFolder:`) or next entity block
- Existing description: `///` lines immediately above the measure keyword (may be absent)

**If PBIP_FORMAT=tmsl:**

Read `$PBIP_DIR/model.bim`. For each table matching the scope, extract:
- Measure name, expression, existing description

Build the measure list. Output progress:
> Found [N] measures in [scope description]. Processing...

If N=0: Output "No measures found in [scope]. Nothing to comment." Stop.

---

### Step 3 — Generate Comments for Each Measure

For each measure in the list, generate:

**Inline comments** (following the same rules as /pbi:comment):
- One comment above the measure name line describing overall business purpose
- Comments above CALCULATE arguments explaining filter logic in business terms
- Comments above VAR declarations explaining what each variable holds
- Comment above RETURN statement
- Do NOT comment every line — only non-obvious business logic
- Do NOT translate DAX syntax word-for-word

**Description field** (following /pbi:comment rules):
- 1–3 sentences, plain business English
- Max 300 characters, no DAX function names, no markdown
- Ends with a period

**Skip rule:** Skip only if a measure has BOTH a `///` description AND `//` comments in the expression body. If only one is present (e.g., description exists but no inline comments, or inline comments exist but no description), update the missing part. Include skipped measures in the summary with status "Skipped (already commented)".

---

### Step 4 — Preview and Confirmation

Output a summary table:

```
**Batch Comment Preview**

| # | Measure | Table | Status |
|---|---------|-------|--------|
| 1 | [Name] | [Table] | New comments |
| 2 | [Name] | [Table] | Updated comments |
| 3 | [Name] | [Table] | Skipped (already commented) |

[N] measures will be commented, [M] skipped.

**If PBI_CONFIRM=false:** skip the confirmation prompt below — proceed directly to Step 5 (write).

Apply all comments? (y/N)
```

- y or Y: proceed to Step 5.
- n, N, Enter, or anything else: Output "Batch cancelled. No files modified." Stop.

---

### Step 5 — Write Back

**TMDL path:**
For each table file that contains measures to update:
1. Read the .tmdl file (Read tool)
2. For each measure in that file:
   - Replace or insert `///` description line directly above the measure declaration (no blank line between `///` and `measure`)
   - Replace the expression body with the commented DAX
   - Preserve tab indentation, formatString, displayFolder, and all other properties
3. Write the entire modified file back (Write tool) — one write per table file

**TMSL path:**
1. Read `$PBIP_DIR/model.bim` (Read tool)
2. For each measure to update:
   - Set `"description"` to the generated description
   - Update `"expression"` with commented DAX (use array form if multiline)
   - Preserve all other fields
3. Write the entire model.bim back (Write tool) — single write

Output for each file written:
> Written: [N] measures in [file path]

**Auto-commit (single commit for all changes):**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add "$PBIP_DIR/" 2>/dev/null
  git commit -m "chore: batch comment [N] measures in [scope]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: chore: batch comment [N] measures in [scope]"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
- AUTO_COMMIT=fail: Output "⚠ File written but git commit failed — run /pbi:commit to save a snapshot."

---

### Step 6 — Update Session Context

Read `.pbi/context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:comment-batch`, Timestamp = current UTC ISO 8601, Measure = `[N] measures in [scope]`, Outcome = `Batch commented` (or `Batch commented (git commit failed)` if AUTO_COMMIT=fail)
- `## Command History`: Append one row; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

---

### Anti-Patterns
- NEVER write one file per measure — batch all changes for a table file into a single Write
- NEVER skip the confirmation prompt
- NEVER modify measures marked as "already commented" unless the analyst explicitly requests overwrite
- NEVER convert tabs to spaces in TMDL files

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
