---
name: pbi:explain
description: "Deconstruct any DAX measure into a structured plain-English breakdown covering business logic, filter context propagation, row context scope, context transitions, and performance implications. Adapts depth to measure complexity (Simple/Intermediate/Advanced). Works with pasted DAX or reads from PBIP model files."
model: sonnet
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

### Auto-Resume

After detection blocks run, apply the following before executing the command:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - Skip any "Model Context Check" (Step 0.5) below — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.


---

# /pbi:explain

<purpose>
Turn opaque DAX into clear, actionable understanding. Analysts need to know WHAT a measure does, WHY it behaves the way it does in visuals, and WHERE performance bottlenecks hide — without reading DAX syntax.
</purpose>

<core_principle>
Explain intent and behavior, not syntax. The output should help someone who has never seen this measure understand its business purpose, its interaction with filter context, and any hidden complexity.
</core_principle>

## Instructions

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table context. Proceed to Step 1. Use the noted table when describing filter context in Step 5 output.
- If `## Model Context` is absent or empty:
  - Ask: "Which table does this measure belong to?"
  - Wait for the analyst's answer.
  - Read `.pbi-context.md` with Read tool. Add `## Model Context` section with the analyst's answer. Write back with Write tool.
  - Proceed to Step 1 using the noted table context.

---

### Step 1 — Initial Response

Respond to the analyst with exactly:

> Paste your DAX measure below:

Wait for the analyst to paste a DAX measure before proceeding.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text (no `=`, no function names, no table references), output: "Please paste a DAX measure to explain." and stop.

---

### Step 2 — Measure Extraction

Once the analyst pastes the measure:

- **Extract the measure name:** everything before the first `=` sign, trimmed of whitespace.
- **If no `=` is found** in the pasted content, use placeholder name `[Measure]` and add at the very top of your output: "Note: No measure name detected — treating entire input as the expression."
- **If `$ARGUMENTS` contains `--table TableName`**, record TableName and include it as a context note in the output (e.g., "Note: Table context provided — `TableName`").

---

### Step 3 — Prior Failure Check

Before generating any output, scan the Session Context for the extracted measure name in the **"## Analyst-Reported Failures"** section.

- If the measure name is found in that section, output at the very top (before the Complexity tag):
  > Previous attempt at this measure used [approach X] and failed. Using [approach Y] instead.

---

### Step 4 — Complexity Inference

Classify the measure into one of three levels based on its patterns:

**Simple** (use plain language, minimise jargon):
- Measure body contains only: `SUM`, `COUNT`, `AVERAGE`, `MIN`, `MAX`, `DIVIDE`, `IF`, `BLANK`
- Single `CALCULATE` with one filter argument
- No iterator functions (`SUMX`, `AVERAGEX`, `COUNTX`, `MAXX`, `MINX`, `RANKX`, `TOPN`, etc.)
- No time intelligence functions (`DATESYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`, `TOTALYTD`, etc.)

**Intermediate** (explain concepts with brief parentheticals):
- `CALCULATE` with multiple filter arguments
- Single `SUMX` or `AVERAGEX` over a physical table column (no measure references inside the iterator)
- Time intelligence functions (`DATESYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`, `TOTALYTD`, etc.)
- `FILTER` used as a `CALCULATE` argument
- `RELATED` or `RELATEDTABLE`

**Advanced** (full technical depth, name patterns explicitly):
- Iterators (`SUMX`, `AVERAGEX`, etc.) over measure references — context transition present
- `EARLIER`
- `ALLEXCEPT`, `ALLSELECTED`, or `REMOVEFILTERS` with multiple columns
- Nested iterators
- `RANKX` or `TOPN` with complex expressions
- `VAR`/`RETURN` blocks that contain iterators

---

### Step 5 — Output Structure

Produce the following labelled sections in this exact order:

```
_Complexity: [Simple | Intermediate | Advanced]_

**[Measure Name]**

[One paragraph plain-English summary of what the measure calculates. For Simple measures, avoid DAX jargon entirely. For Advanced measures, name the patterns explicitly and explain the implications.]

### Filter Context
[Describe what filters are active when this measure evaluates. Include: filters from CALCULATE arguments, filters inherited from visuals/slicers (row context only relevant when called from a visual), ALL/ALLEXCEPT overrides if present. If no explicit filter manipulation is present, state what context the measure inherits from the report visual.]

### Row Context
[State whether row context is present. Row context exists inside iterator functions (SUMX, AVERAGEX, etc.) and inside calculated columns. If the measure uses an iterator, describe which table provides the row context and what columns are accessible per row. If no iterator is present and this is not a calculated column, state that no row context is active.]

### Context Transitions
[If CALCULATE is present or an iterator calls a measure reference, explain the context transition. For Simple measures with no iterator/measure-ref, write: "No context transition — this measure evaluates in filter context only." For Advanced measures with iterator-over-measure-ref, write: "Context transition present: [MeasureName] is called inside [Iterator], which converts the row context to filter context via an implicit CALCULATE."]

### Performance Notes
[Brief note on any performance implications. If no concern, write: "No performance concerns for this pattern." For slow patterns (FILTER on entire table, nested iterators, RANKX over large tables), name the concern and note that /pbi:optimise can suggest improvements.]

---
**Next steps:** `/pbi:format` · `/pbi:optimise` · `/pbi:comment` · `/pbi:error`
```

---

### Step 6 — Update Session Context

After producing the output, update `.pbi-context.md` using the following steps:

1. Use the **Read** tool to read the current contents of `.pbi-context.md`.
2. Modify the file in memory:
   - **"## Last Command" section:** Set all four fields:
     - `Command: /pbi:explain`
     - `Timestamp: [current ISO 8601 timestamp, e.g. 2026-03-12T10:30:00Z]`
     - `Measure: [extracted measure name]`
     - `Outcome: Success — [one-line summary of what was explained, e.g. "Year-to-date revenue using DATESYTD"]`
   - **"## Command History" table:** Prepend a new row at the top of the table body:
     `| [timestamp] | /pbi:explain | [measure name] | Success |`
   - **Keep Command History to the last 20 rows** — if the table has more than 20 data rows after adding the new one, drop the oldest rows until exactly 20 remain.
   - **Do NOT modify the "## Analyst-Reported Failures" section** — the analyst manages that section manually.
3. Use the **Write** tool to write the full updated file back to `.pbi-context.md`.

Do NOT use bash append commands — always Read then Write to avoid malformed state.

### Anti-Patterns
- NEVER restate DAX syntax in plain English — explain business logic and intent
- NEVER skip complexity inference — always classify before explaining
- NEVER reference columns not in Model Context when model-aware context is available
- NEVER modify or rewrite the measure — explain only

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.


## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
