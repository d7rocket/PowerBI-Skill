---
name: pbi:comment
description: "Add inline comments to a single DAX measure. Use when user says 'comment DAX', 'annotate', 'document measure', or 'describe measure'."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 4.4.0
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

# /pbi:comment


## File Mode Branch

If PBIP_MODE=paste:
- Proceed directly to Step 1 (paste-in mode). Do not output any file-mode header. Do not mention PBIP at all.

If PBIP_MODE=file:
1. Output this header as the first line of your response (before Step 1 prompt):
   > File mode — PBIP project detected ([FORMAT])
   Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.

2. Proceed to Step 1 (paste-in flow) to collect the measure and generate commented output. The measure name extracted in Step 2 and the output from Steps 4-5 will be used for write-back.

3. After completing Steps 2-6 (output generated), proceed to File Write-Back (see below).

### File Write-Back (PBIP_MODE=file)

Use the measure name extracted in Step 2 as the search key.

**If PBIP_FORMAT=tmdl:**
1. Run bash:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" search "[MeasureName]" "$PBIP_DIR" 2>/dev/null
   ```
   - Replace [MeasureName] with the actual extracted measure name.
   - If multiple files returned: output "Measure [Name] found in multiple tables: [list]. Use --table TableName to specify which one." Deliver paste-ready output only. Stop write-back.
   - If no file returned: output "Measure [Name] not found in PBIP project — output is paste-ready for manual addition." Stop write-back.
   - If exactly one file returned: proceed.
2. Read the identified .tmdl file using the Read tool.
3. Locate the measure block:
   - Find the line matching `measure.*[MeasureName]` (the measure declaration line)
   - The line(s) immediately above starting with `///` are the existing description (may be absent)
   - The lines following the measure declaration through the blank line or next `measure`/`column`/`table` keyword are the expression and properties
4. Modify the block:
   - Replace or insert `///` description line directly above the measure declaration line (no blank line between `///` and `measure`). Use the Description Field value from Step 5 as the description text.
   - Replace the expression body with the commented DAX from Step 4. Preserve tab indentation (TMDL uses tabs — do NOT convert to spaces). Preserve formatString, displayFolder, and any other property lines that follow the expression.
5. Write the entire modified .tmdl file back using the Write tool.
6. Append the write confirmation line after the Description Field in the output:
   > Written to: [MeasureName] in [file path]
7. Run the auto-commit bash block:
   ```bash
   GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
   if [ "$GIT_STATUS" = "yes" ]; then
     git add "$PBIP_DIR/" 2>/dev/null
     git commit -m "chore: update [MEASURE_NAME] comment in [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
   else
     echo "AUTO_COMMIT=skip_no_repo"
   fi
   ```
   Where [MEASURE_NAME] is the actual measure name from Step 2 and [TABLE_NAME] is the table name extracted from the .tmdl file path.
   - AUTO_COMMIT=ok: append line `Auto-committed: chore: update [MEASURE_NAME] comment in [TABLE_NAME]`
   - AUTO_COMMIT=skip_no_repo: append line `No git repo — run /pbi:commit to initialise one.`
   - AUTO_COMMIT=fail: do not output anything (git failure is non-fatal; file write succeeded)

**If PBIP_FORMAT=tmsl:**
1. Read `$PBIP_DIR/model.bim` using the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read in chunks of 1000 lines — read the full file across multiple reads before locating the measure.
2. Locate the measure JSON object where `"name"` equals the extracted measure name.
   - If not found: output "Measure [Name] not found in PBIP project — output is paste-ready for manual addition." Stop write-back.
3. Update the measure object:
   - Set `"description"` to the Description Field value from Step 5 (plain string).
   - Update `"expression"` with the commented DAX from Step 4. CRITICAL: detect whether the original expression was a JSON string or a JSON array of strings. If the commented DAX has line breaks (which it will if // comments were added inline), use the array form. Preserve the exact array/string form of the original if the expression is unchanged; use array if adding comments creates new lines.
   - Preserve ALL other fields: formatString, displayFolder, annotations, etc.
4. Write the entire model.bim back using the Write tool.
5. Append the write confirmation line after the Description Field in the output:
   > Written to: [MeasureName] in $PBIP_DIR/model.bim
6. Run the auto-commit bash block:
   ```bash
   GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
   if [ "$GIT_STATUS" = "yes" ]; then
     git add "$PBIP_DIR/" 2>/dev/null
     git commit -m "chore: update [MEASURE_NAME] comment in [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
   else
     echo "AUTO_COMMIT=skip_no_repo"
   fi
   ```
   Where [MEASURE_NAME] is the actual measure name from Step 2 and [TABLE_NAME] is the table name of the measure's table context in model.bim.
   - AUTO_COMMIT=ok: append line `Auto-committed: chore: update [MEASURE_NAME] comment in [TABLE_NAME]`
   - AUTO_COMMIT=skip_no_repo: append line `No git repo — run /pbi:commit to initialise one.`
   - AUTO_COMMIT=fail: do not output anything (git failure is non-fatal; file write succeeded)

## Instructions

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table context. Use it to make inline comments more specific (e.g., reference actual column names when explaining filter logic). Proceed to Step 1.
- If `## Model Context` is absent or empty:
  - Ask: "Which table does this measure belong to?"
  - Wait for the analyst's answer.
  - Read `.pbi-context.md` with Read tool. Add `## Model Context` section with the analyst's answer. Write back with Write tool.
  - Proceed to Step 1 using the noted table context.

### Step 1 — Initial Response

Respond immediately with:

> Paste your DAX measure below:

Wait for the analyst to paste their DAX measure before proceeding.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text, output: "Please paste a DAX measure to comment." and stop.

### Step 2 — Measure Extraction

- Extract the measure name from the text before the first `=` sign (strip whitespace). Example: `Revenue YTD = CALCULATE(...)` → measure name is `Revenue YTD`.
- If there is no `=` in the pasted text, use `[Measure]` as the placeholder name and append a note: `_Note: No measure name found — treating full input as expression._`
- If `$ARGUMENTS` contains `--table TableName`, use that table name as additional business context when writing comments (e.g., "filters to rows in the TableName table where…").

### Step 3 — Prior Failure Check

Scan the Session Context for the extracted measure name under the `Analyst-Reported Failures` section. If a matching entry exists, prepend this flag at the very top of the output (before the measure name heading):

> Previous attempt at this measure was reported as failed. Review comments carefully before use.

### Step 4 — Comment Placement Rules

Add `//` inline comments to the DAX measure according to these rules:

**Where to comment:**
- Add one comment immediately **above the measure name line** (the `MeasureName =` line) describing the overall business purpose in one plain-English sentence. Example: `// Returns year-to-date revenue, filtered to the selected region`.
- Add comments **on or above CALCULATE arguments** explaining the filter logic in business terms — not DAX terms. Say `// Filter to current year only`, not `// DATESYTD applies a year-to-date time intelligence filter`.
- Add comments **above or on VAR declarations** explaining what each variable holds in business terms. Example: `// Total orders placed before the selected date`.
- Add a comment **above the RETURN statement** (when variables are used) stating plainly what is being returned. Example: `// Return the ratio of converted leads to total leads`.
- For **simple single-line measures** (e.g., `Revenue = SUM(Sales[Amount])`): add exactly one comment above the expression describing the business calculation in a full sentence. Example: `// Total sales revenue — sums the Amount column across all visible rows`.

**What not to do:**
- Do NOT add a comment on every line — only comment lines where the intent is non-obvious.
- Do NOT translate DAX syntax word-for-word into English. Explain the business logic, not the code mechanics.
- Do NOT comment on closing parentheses, indentation, or structural syntax.
- Do NOT repeat the measure name in the comment.

**Complexity scaling:**
- Infer complexity from patterns: simple measures (SUM, DIVIDE, basic CALCULATE with one filter) → fewer, shorter comments; complex measures (context transitions, EARLIER, ALLEXCEPT, nested iterators, multiple VARs) → more detailed comments on each key step.

### Step 5 — Description Field Generation Rules

Write a Description Field value (plain text, not inside a code block) that:

- Is **1–3 sentences** in plain business English.
- States: (1) what the measure calculates, (2) any key filter conditions or time intelligence behaviour, (3) any important caveats for interpretation (e.g., "Returns blank when no sales exist for the period.").
- Does **not** use DAX function names — write "year-to-date" not "DATESYTD"; write "filtered to" not "CALCULATE"; write "for each row" not "SUMX"; write "ignoring all filters" not "ALL".
- Is a **maximum of 300 characters** — Power BI's Description property is displayed in a tooltip and truncates at approximately 250–300 characters. Count characters and trim if needed.
- Uses **no markdown formatting** — no bold, no italics, no bullet points, no code formatting. Plain text only.
- Ends with a period.

### Step 6 — Output Structure

Produce the output using exactly this structure (locked decision — two labelled blocks):

```
**[Measure Name] — Commented**

### Commented DAX
```dax
// [overall purpose comment]
[MeasureName] =
// [comment if needed]
[expression with inline // comments as appropriate]
```

### Description Field
[Plain-text description, 1–3 sentences, max 300 characters, no markdown, ready to paste into Power BI measure Description property]

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:optimise` · `/pbi:error`
```

### Step 7 — Context Update

After producing the output, update `.pbi-context.md` using Read then Write:

1. **Read** `.pbi-context.md` using the Read tool to get the current contents.
2. **Write** the updated file back using the Write tool with these changes:
   - Update the `## Last Command` section: set Command to `/pbi:comment`, Timestamp to current UTC time (ISO 8601), Measure to the extracted measure name, Outcome to `Commented`.
   - Append a new row to the `## Command History` table with columns: Timestamp, Command (`/pbi:comment`), Measure Name (extracted name), Outcome (`Commented`).
   - Keep the Command History table to a maximum of 20 rows — if adding the new row would exceed 20, remove the oldest row first.
   - Do **not** modify the `## Analyst-Reported Failures` section.

### Anti-Patterns
- NEVER translate DAX syntax word-for-word into English — explain business logic
- NEVER remove existing comments — only add or update
- NEVER modify the DAX expression while adding comments
- NEVER exceed 300 characters in the Description Field

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
