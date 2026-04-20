---
name: pbi:audit-fix
description: "Autonomous audit-then-fix pipeline — scan the TMDL/TMSL model, auto-fix WARN-level issues (missing descriptions, stray control characters, unhidden key columns, missing format strings), validate integrity, and commit only if clean. Eliminates iterative manual debugging."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 7.1.0
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

# /pbi:audit-fix

<purpose>
The audit command finds issues but leaves fixing to the user. This command closes the loop — scan, fix, validate, commit — in one autonomous pass. It targets WARN-level issues that are safe to auto-fix without changing business logic.
</purpose>

<core_principle>
Fix only what is safe to fix automatically. Never modify DAX expressions or business logic. Only touch structural properties (isHidden, descriptions, formatString defaults, stray characters). Validate after every fix batch. Revert any fix that breaks TMDL parsing. Commit only when the model is clean.
</core_principle>

## Instructions

### Step 0 — PBIP-Only Guard

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run `/pbi:audit-fix` from a directory containing a `*.SemanticModel/` folder.

**If PBIP_MODE=file:** output:

```
Audit-Fix Pipeline — scanning model...
```

Proceed to Step 1.

---

### Step 1 — Full Model Scan

Read every `.tmdl` file path from the File Index using the Read tool.

Also read:
- `$PBIP_DIR/definition/relationships.tmdl` (if it exists)

**For TMSL:** Read `$PBIP_DIR/model.bim`. If >2000 lines, use offset/limit parameters.

Extract the same metadata as `/pbi:audit`:
- Tables: name, columns (name, dataType, isHidden), measures (name, expression, description, formatString, displayFolder)
- Relationships: fromTable, fromColumn, toTable, toColumn, crossFilteringBehavior

---

### Step 2 — Identify Fixable Issues

Scan for these auto-fixable issue types:

| ID | Issue | Fix Action | Severity |
|----|-------|-----------|----------|
| AF-01 | Stray control characters in TMDL files | Remove characters with `ord(c) < 32` that are not `\n`, `\r`, `\t` | WARN |
| AF-02 | Relationship key column not hidden | Add `isHidden` property to column block | WARN |
| AF-03 | Foreign key / ID column not hidden | Add `isHidden` property to column block | WARN |
| AF-04 | Measure missing description | Generate 1-3 sentence business description (max 300 chars, no DAX names) | INFO |
| AF-05 | Measure missing displayFolder | Infer folder from measure type (Financial, Counts, KPIs, Time Intelligence) | WARN |

**Issues NOT auto-fixed (report only):**

| ID | Issue | Why not fixed |
|----|-------|--------------|
| R-01 | Bidirectional relationship | Requires user direction choice |
| M-01 | Missing formatString | Cannot reliably infer correct format without context |
| N-* | Naming inconsistencies | Renaming is destructive — breaks downstream references |

Build two lists:
- `fixable[]` — issues from the AF-* table above
- `report_only[]` — issues that cannot be safely auto-fixed

Output a summary:

```
Scan complete.

**Auto-fixable:** [N] issues
  - [count] stray control characters (AF-01)
  - [count] unhidden key columns (AF-02/AF-03)
  - [count] measures missing descriptions (AF-04)
  - [count] measures missing display folders (AF-05)

**Report only (manual fix needed):** [N] issues
  - [list each with severity and brief description]
```

If zero fixable issues: output `No auto-fixable issues found. Model is clean.` and skip to Step 6.

---

### Step 3 — Confirm and Apply Fixes

**If PBI_CONFIRM=true:**

```
Apply all [N] auto-fixes? (y/N)
```

Wait for response. On n/N/Enter: output `No fixes applied.` and skip to Step 6.

**If PBI_CONFIRM=false:** proceed directly to applying fixes.

**Apply fixes in this order** (safest first):

**Pass 1 — Stray control characters (AF-01):**
For each affected file:
1. Read the file content using Python
2. Remove any character where `ord(c) < 32 and c not in '\n\r\t'`
3. Write the cleaned content back
4. Output: `Fixed: AF-01 — removed stray control characters from [filename]`

**Pass 2 — Hidden columns (AF-02, AF-03):**
For each affected column:
1. Read the .tmdl file
2. Locate the column block
3. Add `isHidden` property if not present (insert after the column name line, before the next property or block)
4. Write the full file back
5. Output: `Fixed: AF-02 — hidden [TableName].[ColumnName]`

**Pass 3 — Display folders (AF-05):**
For each affected measure:
1. Read the .tmdl file
2. Locate the measure block
3. Add `displayFolder` property with inferred value:
   - Measure expression contains SUM/SUMX on currency/revenue/cost/price columns → `"Financial"`
   - Measure expression contains COUNT/COUNTROWS/DISTINCTCOUNT → `"Counts"`
   - Measure expression contains DIVIDE or returns percentage → `"KPIs"`
   - Measure expression contains DATEYTD/SAMEPERIODLASTYEAR/TOTALYTD/DATEADD → `"Time Intelligence"`
   - Otherwise → `"General"`
4. Write the full file back
5. Output: `Fixed: AF-05 — added displayFolder "[folder]" to [MeasureName]`

**Pass 4 — Descriptions (AF-04):**
For each undescribed measure:
1. Read the measure's DAX expression from the file
2. Generate a plain-language description:
   - 1-3 sentences, max 300 characters
   - Business English (no DAX function names, no markdown)
   - States what the measure calculates and any key filter conditions
   - Ends with a period
3. Add `///` description line immediately above the `measure` keyword line
4. Write the full file back
5. Output: `Fixed: AF-04 — added description to [MeasureName]`

---

### Step 4 — Validate Integrity

After all fixes are applied, validate every modified file:

**TMDL validation:**
For each modified `.tmdl` file, run:
```bash
python -c "
import sys
with open(sys.argv[1], encoding='utf-8') as f:
    content = f.read()
# Check for stray control characters
bad = [c for c in content if ord(c) < 32 and c not in '\n\r\t']
if bad:
    print(f'VALIDATE_FAIL: {len(bad)} stray control characters remain')
    sys.exit(1)
# Check basic TMDL structure
if 'table ' not in content and 'column ' not in content and 'measure ' not in content:
    print('VALIDATE_FAIL: file appears empty or malformed')
    sys.exit(1)
print('VALIDATE_OK')
" "[file_path]" 2>&1
```

**If any file fails validation:**
1. Output: `Validation FAILED for [filename]: [error]`
2. Revert that specific file: `git checkout -- "[file_path]" 2>/dev/null`
3. Output: `Reverted [filename] — flagged for manual review.`
4. Continue validating remaining files.

**If all files pass:**
Output: `Validation passed — all [N] modified files are clean.`

---

### Step 5 — Commit

**If any fixes were applied AND validation passed (at least partially):**

```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add "$PBIP_DIR/" 2>/dev/null
  # IMPORTANT: Replace [N] with the integer count only — never interpolate free-text strings into commit messages
  git commit -m "fix: auto-fix ${FIXES_COUNT} audit findings" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```

Output based on result:
- AUTO_COMMIT=ok: `Auto-committed: fix: auto-fix [N] audit findings`
- AUTO_COMMIT=skip_no_repo: `No git repo — run /pbi:commit to initialise one.`
- AUTO_COMMIT=fail: `File(s) written but git commit failed — run /pbi:commit to save a snapshot.`

---

### Step 6 — Summary Report

Output a final summary:

```
# Audit-Fix Report
**Project:** $PBIP_DIR
**Date:** [current UTC date and time]

## Fixed ([N] issues)
| # | Rule | File | Action |
|---|------|------|--------|
| 1 | AF-01 | [file] | Removed stray control characters |
| 2 | AF-02 | [file] | Hidden [Column] |
| ... | ... | ... | ... |

## Skipped — Manual Fix Required ([N] issues)
| # | Rule | Severity | Issue | Why |
|---|------|----------|-------|-----|
| 1 | R-01 | CRITICAL | Bidirectional: [Table1] → [Table2] | Requires direction choice |
| ... | ... | ... | ... | ... |

## Validation
- Files modified: [N]
- Files passed: [N]
- Files reverted: [N] (if any)

---
*Reminder: Close and reopen the project in Power BI Desktop to see changes.*
```

Write this report to `.pbi/audit-fix-report.md`.

---

### Step 7 — Update .pbi/context.md

Use Read-then-Write to update `.pbi/context.md`:
1. Update `## Last Command`: Command = `/pbi:audit-fix`, Outcome = `Auto-fixed [N] issues, [M] skipped. Report: .pbi/audit-fix-report.md`
2. Append row to `## Command History`; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

### Anti-Patterns
- NEVER modify DAX measure expressions — auto-fix only touches structural properties (isHidden, description, displayFolder, control characters)
- NEVER auto-fix bidirectional relationships — these require user direction choice
- NEVER rename measures or columns — this breaks downstream references
- NEVER commit if validation failed for ALL files — only commit if at least some fixes validated successfully
- NEVER skip the validation step — always validate after applying fixes
- NEVER suggest bidirectional cross-filtering as a fix for relationship issues

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
