---
name: pbi-format
description: "Reformat DAX expressions for maximum readability using the DAX Formatter API (daxformatter.com). Handles long expressions, nested functions, and multi-line VAR/RETURN blocks. Preserves semantic meaning while applying consistent indentation and spacing. Auto-applies to PBIP files when detected."
model: haiku
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

# /pbi-format

<purpose>
Consistent formatting makes DAX scannable and reviewable. Unformatted DAX hides logic in walls of text — formatted DAX reveals structure at a glance.
</purpose>

<core_principle>
Use the external DAX Formatter API for consistent, community-standard formatting. Never invent formatting rules — defer to the API. If the API is unavailable, format manually following DAX Formatter conventions.
</core_principle>

> DAX Formatter API reference is in `shared/api-notes.md` (read if needed).

## Format API Status
!`TMPCHECK=$(mktemp); curl -s -L -X POST "https://www.daxformatter.com" -d "fx=1%2B1&r=US&embed=1" --max-time 5 -o "$TMPCHECK" 2>/dev/null; CURL_EXIT=$?; if [ "$CURL_EXIT" -eq 28 ]; then echo "API_TIMEOUT"; elif python3 -c "import sys; d=open('$TMPCHECK','r',errors='replace').read(); sys.exit(0 if 'formatted' in d else 1)" 2>/dev/null; then echo "API_OK"; else echo "API_FAIL"; fi; rm -f "$TMPCHECK"`

## Instructions

Respond to the analyst with exactly: "Paste your DAX measure below:"

Once the analyst pastes a DAX measure, follow these steps in order.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text, output: "Please paste a DAX measure to format." and stop.

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table context. Use it when inferring display folder in Step 5 output. Proceed to Step 1.
- If `## Model Context` is absent or empty:
  - Ask: "Which table does this measure belong to? (optional — skip if you just want formatting)"
  - If the analyst answers: Read `.pbi/context.md` with Read tool. Add `## Model Context` section with the answer. Write back with Write tool. Use the table context in output.
  - If the analyst skips or says "skip": note "Table context not available — formatting pasted measure as-is." Proceed to Step 1 without blocking.

### Step 1 — Measure Extraction

Extract the measure name from the pasted content:
- The measure name is everything before the first `=` sign, trimmed of whitespace
- If no `=` is found, use `[Measure]` as the placeholder name and include the note: "Note: No measure name detected — treating entire input as the expression."
- If `$ARGUMENTS` contains `--table TableName`, record the table name and include a table context note in the output: "Table context: TableName"

Store the full pasted measure text as the input for formatting.

### Step 2 — Check for Prior Failures

Review the Session Context. If the context file contains a record in the Analyst-Reported Failures table for this measure name, add a warning at the very top of the output (before everything else):
> Warning: Previous attempt at this measure used [approach from failure record] and failed. Using [alternative approach] instead.

### Step 3 — Format the Measure

Check the "Format API Status" section above:

**If API_TIMEOUT:**

Add exactly this one line at the top of the output (or after the prior-failure warning if one is present):
`_DAX Formatter API timed out (5 s) — formatted inline by Claude_`

Then format using the Claude inline SQLBI rules in Step 4.

**If API_OK:**

Use the Bash tool to call the DAX Formatter API. To avoid shell injection from DAX metacharacters (`$`, backticks, etc.), write the measure to a temp file first using a single-quoted heredoc delimiter:

```bash
TMPFILE=$(mktemp)
TMPHTML=$(mktemp)
cat > "$TMPFILE" <<'ENDDAX'
PASTE_MEASURE_HERE
ENDDAX
curl -s -L -X POST "https://www.daxformatter.com" \
  --data-urlencode "fx@$TMPFILE" \
  -d "r=US&embed=1" \
  --max-time 5 -o "$TMPHTML" 2>/dev/null
python .claude/skills/pbi/scripts/detect.py html-parse "$TMPHTML"
rm -f "$TMPFILE" "$TMPHTML"
```

Replace `PASTE_MEASURE_HERE` with the actual measure text the analyst pasted (between the `<<'ENDDAX'` and `ENDDAX` lines — the single-quoted delimiter prevents shell expansion). The output of this command is the formatted DAX string. Present it in a fenced `dax` code block.

If the API call succeeds but returns empty output or garbled text, treat it as API_FAIL and use the inline fallback below.

**If API_FAIL:**

Add exactly this one line at the top of the output (or after the prior-failure warning if one is present):
`_DAX Formatter API unavailable — formatted inline by Claude_`

Then format the measure using the Claude inline SQLBI formatting rules below.

### Step 4 — Claude Inline SQLBI Formatting Rules

Use these rules when API_FAIL, or when API_OK but the API returned unusable output:

**Keyword capitalisation:**
All DAX keywords must be UPPERCASE: CALCULATE, SUMX, AVERAGEX, MAXX, MINX, FILTER, ALL, ALLEXCEPT, ALLSELECTED, VALUES, RELATED, RELATEDTABLE, DIVIDE, IF, BLANK, VAR, RETURN, SUM, SUMX, COUNT, COUNTROWS, COUNTBLANK, AVERAGE, MIN, MAX, HASONEVALUE, SELECTEDVALUE, SWITCH, TRUE, FALSE, AND, OR, NOT, ISBLANK, IFERROR, DATESYTD, DATEADD, SAMEPERIODLASTYEAR, DATESBETWEEN, TOTALYTD, RANKX, TOPN, EARLIER, EARLIER, UNION, INTERSECT, EXCEPT, GENERATE, CROSSJOIN, NATURALINNERJOIN, NATURALLEFTOUTERJOIN, etc.

**Structure rules:**
- Measure name and `=` on the first line, then expression body on the next line indented 4 spaces
- Each CALCULATE argument on its own line, indented 4 spaces from the CALCULATE call
- Each VAR and RETURN on its own line
- Opening parenthesis stays on the same line as the function name (no line break before `(`)
- Closing parenthesis on its own line, aligned with the indent level of the function name
- Nested functions follow the same pattern recursively

**Example — simple measure:**
```dax
Revenue =
SUM ( Sales[Amount] )
```

**Example — CALCULATE with filters:**
```dax
Sales YTD =
CALCULATE(
    [Revenue],
    DATESYTD ( 'Date'[Date] )
)
```

**Example — VAR/RETURN:**
```dax
YoY Growth % =
VAR CurrentYear = [Revenue]
VAR PriorYear =
    CALCULATE(
        [Revenue],
        DATEADD ( 'Date'[Date], -1, YEAR )
    )
RETURN
DIVIDE ( CurrentYear - PriorYear, PriorYear, BLANK () )
```

### Step 5 — Output Structure

Present the output in this order:

1. (Only if prior failure warning applies): Warning line
2. (Only if API_FAIL): `_DAX Formatter API unavailable — formatted inline by Claude_`
3. (Only if --table flag was passed): `Table context: TableName`
4. The formatted measure in a fenced `dax` code block
5. Next steps line: `**Next steps:** /pbi-explain · /pbi-optimise · /pbi-comment · /pbi-error`

### Step 6 — Update .pbi/context.md

After producing the output, update the `.pbi/context.md` file:

1. Use the Read tool to read the current contents of `.pbi/context.md`
2. If the file does not exist or is empty, start with the full schema below
3. Update the `## Last Command` section with:
   - Command: /pbi-format
   - Timestamp: current UTC timestamp
   - Measure: the measure name extracted in Step 1
   - Outcome: "Success — formatted via API" or "Success — formatted inline by Claude (API timeout)" or "Success — formatted inline by Claude (API unavailable)"
4. Append a new row to the `## Command History` table with the same info
5. If the Command History table has more than 20 rows, remove the oldest rows to keep it at 20
6. Do NOT modify the `## Analyst-Reported Failures` section
7. Use the Write tool to write the complete updated file back to `.pbi/context.md`

**Full schema for new file creation:**
```markdown
# PBI Context

## Last Command
- Command: /pbi-format
- Timestamp: [current timestamp]
- Measure: [measure name]
- Outcome: [outcome]

## Command History
| Timestamp | Command | Measure Name | Outcome |
|-----------|---------|--------------|---------|
| [timestamp] | /pbi-format | [measure name] | [outcome] |

## Analyst-Reported Failures
| Timestamp | Command | Measure Name | What Failed | Notes |
|-----------|---------|--------------|-------------|-------|
```

### Anti-Patterns
- NEVER change DAX logic — formatting is cosmetic only
- NEVER remove comments from the original measure
- NEVER change the measure name
- NEVER skip the DAX Formatter API check — always try API first

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
