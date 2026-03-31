---
name: pbi:load
description: "Parse the full PBIP semantic model (TMDL or TMSL format) and build structured session context. Extracts all tables, measures, columns, relationships, data categories, and hidden state. Writes to .pbi/context.md for reuse across all subsequent commands."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.0.0
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

# /pbi:load

<purpose>
Every PBIP command needs model awareness — which tables exist, how they relate, what measures are defined. Loading once and caching in .pbi/context.md prevents re-reading dozens of files on every command invocation.
</purpose>

<core_principle>
Extract structure, not content. The context cache stores table names, column lists, and relationship topology — not full measure expressions. Keep the context file small enough to fit in any command's context window.
</core_principle>

## Instructions

### Step 0 — Check detection output

**If PBIP_MODE=paste:**

Respond with exactly this message and stop — do not read any files, do not update `.pbi/context.md`:

> No PBIP project found in this directory. All commands work with pasted DAX — paste a measure into any /pbi command to get started.

---

**If PBIP_MODE=file:** proceed to Step 1 below.

---

### Step 1 — Output the file mode header immediately

Determine the format from the detection output:
- `PBIP_FORMAT=tmdl` → format label is **TMDL**
- `PBIP_FORMAT=tmsl` → format label is **TMSL (model.bim)**

Output immediately:

```
File mode — PBIP project detected ([FORMAT]) | Loading model context...
```

---

### Step 2 — Read model files and extract structure

**For TMDL (`PBIP_FORMAT=tmdl`):**

The File Index has already listed all `.tmdl` file paths under `$PBIP_DIR/definition/tables/`.

Use the Read tool to read each `.tmdl` file from that list.

**Malformed file guard:** If a `.tmdl` file cannot be read or does not contain a `table` keyword on any line, output: `Warning: [filename] could not be parsed — skipping.` and continue with the next file. Do not fail the entire load.

From each file, extract:
- **Table name:** from the `table TableName` declaration at the top of the file
- **Measure names:** lines matching `measure 'Name'` or `measure Name` (single-word). Extract the text after `measure ` up to ` =` or end of line, stripping any single quotes.
- **Column names:** lines matching `column 'Name'` or `column Name`. Same extraction rule — strip single quotes if present.

Also check for `$PBIP_DIR/definition/relationships.tmdl` using the Read tool (if it exists). Extract relationship pairs from lines containing `fromTable:`, `fromColumn:`, `toTable:`, `toColumn:`. Build pairs: `[FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one)`.

**Disambiguation rule (TMDL only):** If the same measure name appears in multiple table files, log it as `[MeasureName] (found in: Table1, Table2)` in the Measures column of the summary table. Do not fail — report all locations.

---

**For TMSL (`PBIP_FORMAT=tmsl`):**

Read `$PBIP_DIR/model.bim` with the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read it in chunks of 1000 lines — read the full file across multiple reads before navigating the JSON structure.

Navigate the JSON structure:
- `model.tables[]` → for each table extract: `name`, `measures[].name`, `columns[].name`
- `model.relationships[]` → for each relationship extract: `fromTable`, `fromColumn`, `toTable`, `toColumn`

Build relationship pairs: `[FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one)`.

---

### Step 3 — Format the Model Context section

Build the following markdown block:

```markdown
## Model Context
**Loaded:** [current UTC time in ISO 8601 format]
**Format:** [TMDL or TMSL (model.bim)]
**Project:** $PBIP_DIR

| Table | Measures | Columns |
|-------|----------|---------|
| [TableName] | [measure1, measure2] | [col1, col2] |
| [TableName] | (none) | [col1, col2] |

**Relationships summary:** [FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one) · [additional relationships separated by ·]
```

Rules:
- If no relationships file or data is found: omit the **Relationships summary** line entirely.
- If a table has no measures: write `(none)` in the Measures column.

---

### Step 4 — Write `.pbi/context.md` (Read-then-Write, single pass)

Perform a single Read-then-Write pass to update `.pbi/context.md`:

1. **Read** `.pbi/context.md` using the Read tool.

2. **Build the updated file content** — in one pass, update four things:
   a. **`## Model Context` section:** If it already exists, replace everything from `## Model Context` through the end of that section (up to the next `##` heading or end of file) with the new Model Context block. If it does not exist, append the new Model Context block after the last existing section.
   b. **`## Session Start` line:** Add or replace `**Session-Start:** [current UTC time in ISO 8601]` immediately after the `## Model Context` section heading line. This marks the session as active so subsequent commands skip re-loading.
   c. **`## Last Command` section:** Update with:
      - Command: `/pbi:load`
      - Timestamp: current UTC time
      - Measure: `[N tables loaded]` where N is the count of tables found
      - Outcome: `Model context loaded ([FORMAT])`
   d. **`## Command History` section:** Append a row with the same values. Keep history to 20 rows max — remove the oldest row if the count exceeds 20.

3. **CRITICAL:** Do not remove or modify `## Analyst-Reported Failures` or any other sections not listed above. Only `## Model Context`, `## Last Command`, and `## Command History` are updated.

4. **Write** the entire updated file back using the Write tool.

---

### Step 5 — Output the summary table to the analyst

After writing `.pbi/context.md`, output:

```
File mode — PBIP project detected ([FORMAT]) | Context loaded.

| Table | Measures | Columns |
|-------|----------|---------|
[same table as written to .pbi/context.md]

**Relationships summary:** [same as written, if present]

Context loaded — all DAX commands will now use model-aware analysis.
```

### Anti-Patterns
- NEVER overwrite existing Model Context without re-reading .pbi/context.md first
- NEVER output raw file contents to the analyst — only the summary table
- NEVER fail silently on unreadable files — log a warning and skip the file
- NEVER modify Analyst-Reported Failures section

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
