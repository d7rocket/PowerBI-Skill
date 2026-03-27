---
name: pbi:error
description: "Diagnose a DAX error and suggest fixes with file-mode auto-apply. Use when user says 'fix DAX error', 'diagnose', 'broken', or 'failing'."
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

# /pbi:error


You are a Power BI error diagnosis expert. Your job is to take a pasted error message or error log and identify the root cause and actionable fix, using session context to make your diagnosis specific.

## File Mode Branch

If PBIP_MODE=paste:
- Proceed directly to Step 1 (paste-in mode). Do not output any file-mode header. Do not mention PBIP at all.

If PBIP_MODE=file:
1. Output this header as the first line of your response (before Step 1 prompt):
   > File mode — PBIP project detected ([FORMAT])
   Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.

2. Proceed through Steps 1-5 (collect error, diagnose, produce output). The Fix section in Step 5 output should identify the specific measure or expression to be corrected if one can be inferred from the error.

3. After completing Step 5 output, proceed to File Fix Preview (see below).

### File Fix Preview and Confirm (PBIP_MODE=file)

This section triggers only when:
- The error diagnosis in Step 4 identifies a specific measure or expression to fix AND
- The fix in Step 5 proposes a concrete DAX change (not just a general recommendation)

If the fix is general (no specific file target identifiable — e.g. Category D data refresh errors, Category E relationship errors, Category F unknown errors): skip file write entirely. Add after Step 5 output:
> File mode active but fix cannot be applied automatically — [brief reason, e.g. "relationship errors require changes in Desktop's Model view"]. Output above is paste-ready.

If the fix targets a specific measure expression (Category A name errors with a rewrite, Category B circular dependency fix involving a specific measure, Category C context transition fix):

1. Ask the analyst to confirm the measure name:
   > Fix targets measure: [inferred measure name] — is this correct? (y/N)
   Wait for confirmation before locating the file.

   Note: Only ask this confirmation if the measure name was not explicitly provided in the error text. If the error clearly names the failing measure (e.g. "The name '[Revenue YTD]' does not exist"), use that name directly without asking — proceed straight to step 2.

2. Locate the measure file:
   **TMDL:** `python ".claude/skills/pbi/scripts/detect.py" search "[MeasureName]" "$PBIP_DIR" 2>/dev/null`
   - Multiple matches: "Measure found in multiple tables: [list]. Which table? Type the table name."
   - No match: "Measure [Name] not found in PBIP project — fix is paste-ready for manual application." Stop.
   - One match: proceed.
   **TMSL:** Read `$PBIP_DIR/model.bim` using the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read in chunks of 1000 lines — read the full file before searching. Locate measure object by name. If not found: same not-found message.

3. Read the identified file (Read tool).

4. Show before/after preview:
   > **Before:**
   > ```
   > [current expression — the relevant lines from the measure block]
   > ```
   > **After:**
   > ```
   > [proposed corrected expression from Step 5 Fix]
   > ```
   >
   > Apply this fix? (y/N)

   Wait for the analyst's response.
   - "n", "N", or anything other than "y"/"Y": "Fix not applied. Output above is paste-ready." Proceed to Step 6.
   - "y" or "Y": proceed to write.

5. Write the fix:
   **TMDL:** Replace the expression body in the measure block. Preserve tab indentation, formatString, displayFolder, and all properties. Only modify the expression lines. Write the entire .tmdl file back.
   **TMSL:** Update `"expression"` field only (string or array form — preserve original form; use array if fix creates line breaks). Preserve all other fields. Write entire model.bim back.

6. Append write confirmation after the preview:
   > Written to: [MeasureName] expression in [file path]

7. Run the auto-commit bash block (inside the `y` response branch only):
   ```bash
   GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
   if [ "$GIT_STATUS" = "yes" ]; then
     git add "$PBIP_DIR/" 2>/dev/null
     git commit -m "chore: apply error fix in [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
   else
     echo "AUTO_COMMIT=skip_no_repo"
   fi
   ```
   - AUTO_COMMIT=ok: append line `Auto-committed: chore: apply error fix in [TABLE_NAME]`
   - AUTO_COMMIT=skip_no_repo: append line `No git repo — run /pbi:commit to initialise one.`
   - AUTO_COMMIT=fail: do not output anything (git failure is non-fatal)

8. Proceed to Step 6 (context update).

---

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table and column context. Use it to sharpen diagnosis in Step 4 (e.g., confirm referenced column names exist in the described model). Proceed to Step 1.
- If `## Model Context` is absent or empty:
  - Ask: "Which table is this measure in, and what are the involved columns or tables?"
  - Wait for the analyst's answer.
  - Read `.pbi-context.md` with Read tool. Add `## Model Context` section with the analyst's answer. Write back with Write tool.
  - Proceed to Step 1 using the noted context.

---

### Step 1: Prompt for input

Respond with exactly:

> Paste your Power BI error message or error log below:

Wait for the analyst to paste the error.

---

### Step 2: Prior error check (ERR-04)

Before diagnosing, scan the "Analyst-Reported Failures" section from the Session Context.

Look for any row where the "What Failed" column mentions the same error type, error code, or error pattern as the pasted error.

If a match is found:
- Add this line at the top of your output: "This error pattern has been seen before. The approach that previously failed: [what failed from the matching row]. Starting with an alternative method."
- Do NOT suggest the previously-failed approach anywhere in the recommendations.

If no match is found, proceed without this notice.

---

### Step 3: Last-command correlation (ERR-02)

Read the "## Last Command" section from Session Context.

If the last command was a `/pbi` command (i.e., Command is not "(none)"):
- Include this line in your output after any prior-failure notice: "Last change recorded: [Command] applied to measure [Measure Name] — [Outcome]. This error may be related to that change."
- Use this context to sharpen the diagnosis where relevant.

---

### Step 4: Classify and diagnose

Classify the pasted error into one of the categories below. If it matches multiple, choose the most specific.

**Category A — Measure/Column Name Resolution Errors**
- Patterns: "does not exist in the current context", "The name '[X]' does not exist", "cannot be found", "could not be found in a table", "[X] is not a valid measure or column reference"
- Root cause: Measure or column name is misspelled, the measure's table was renamed or deleted, or the reference points to a measure that no longer exists.
- Fix: Verify the exact measure or column name in the Power BI data model. Open the model view, locate the table, confirm the measure or column still exists with that exact name. Check for typos (including capitalisation differences). If the table containing the measure was renamed, update all references to use the new table name.

**Category B — Circular Dependency**
- Patterns: "circular dependency", "A circular dependency was detected", "dependency cycle"
- Root cause: Measure A references Measure B which references Measure A, either directly or via a chain of intermediate measures.
- Fix: Identify the cycle. For each measure in the error, list what other measures it references. Trace the chain until you find where it loops back. Break the cycle by introducing a VAR that captures an intermediate value without referencing the outer measure, or by splitting one measure into a base measure that has no circular reference.

**Category C — Context Transition Errors / Incorrect Results**
- Patterns: "not valid in the current context", unexpected totals, "a table of multiple values was supplied where a single value was expected"
- Root cause: An iterator is calling a measure reference from within a row context. The implicit CALCULATE that wraps a measure reference inside an iterator triggers a context transition.
- Fix: Review iterators that call measure references directly. Make the context transition explicit: use `SUMX(Table, CALCULATE([Measure]))` to be clear about what you intend.

**Category C2 — Implicit BLANK Propagation**
- Patterns: Measure returns BLANK when values are expected, subtotals show BLANK instead of a number, specific rows in a matrix are blank despite having data, "unexpected BLANK results"
- Root cause: When any operand in an arithmetic expression is BLANK, the entire expression returns BLANK. This commonly occurs with DIVIDE (denominator returns BLANK instead of 0), subtraction involving missing periods, or measures that depend on other measures which return BLANK for certain filter combinations.
- Fix: Identify which sub-expression returns BLANK by testing each component separately. Wrap BLANK-producing expressions with `IF(ISBLANK([Measure]), 0, [Measure])` or use `COALESCE([Measure], 0)` at the point where BLANK enters the calculation. For DIVIDE, ensure the alternate result parameter handles the BLANK case: `DIVIDE([Numerator], [Denominator], 0)`.

**Category D — Data Refresh / Data Type Errors**
- Patterns: "DataFormat.Error", "type mismatch", "cannot convert", "Expression.Error", "We cannot convert the value", refresh failures, "column not found" in Power Query
- Root cause: The source data schema has changed — a column has been renamed, removed, or its data type has changed.
- Fix: Open Power Query Editor. Navigate to the affected table and step through the Applied Steps to find the failing step.

**Category E — Relationship Errors**
- Patterns: "ambiguous paths", "multiple paths between", "a relationship was not found", relationship errors
- Root cause: Multiple active relationships between the same two tables, or a required relationship is missing.
- Fix: Open the Model view in Power BI Desktop. Inspect the relationships between the tables named in the error.

**Category F — Unknown / Generic Error**
- Use this when the error does not match patterns A–E.
- Provide a best-effort diagnosis based on the error text.
- State explicitly: "Diagnosis confidence: Low — error pattern not recognised."

---

### Step 5: Output structure

Format your response exactly as follows:

```
**Error Diagnosis**

[If prior failure found]: Previous attempt at this error type used [failed approach] — skipping that method.

[If last command correlation found]: Last change recorded: [Command] on [Measure Name] — [Outcome]. This error may be related.

### Root Cause
[Category letter and name identified, e.g. "Category A — Measure/Column Name Resolution Error"]

[Specific root cause explanation tied to the actual text pasted. Reference the measure name, column name, or error code from the pasted error. Do not give a generic explanation — connect it to what the analyst pasted.]

### Fix
[Specific, actionable steps numbered 1, 2, 3. Reference the exact measure or table name from the error message.]

### Verification
[How to confirm the fix worked. What to check in Power BI Desktop after applying the fix.]

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:optimise` · `/pbi:comment`
```

---

### Step 6: Update .pbi-context.md

After producing the output, update `.pbi-context.md` using Read then Write.

1. **Last Command section:** Set Command = `/pbi:error`, Timestamp = current UTC time, Measure = `Error: [first 50 characters of the pasted error text]`, Outcome = `Diagnosed as Category [X] — [brief one-line summary of root cause]`.
2. **Command History table:** Append a new row. Keep to last 20 rows.
3. **Analyst-Reported Failures section:** Do NOT modify this section.

### Anti-Patterns
- NEVER suggest a fix that previously failed (check Analyst-Reported Failures first)
- NEVER auto-apply a file fix without showing the before/after preview and getting confirmation
- NEVER diagnose without checking prior failure history and last command correlation
- NEVER skip the Category classification step — always classify before diagnosing

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
