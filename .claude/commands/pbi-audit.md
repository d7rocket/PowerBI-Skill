---
name: pbi:audit
description: "19-rule health check across 8 domains with severity grading (CRITICAL/WARN/INFO) and auto-fix for structural issues"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

## Detection

Run ALL of the following detection commands using the Bash tool before proceeding. Save the output — subsequent steps reference these values.

Ensure .pbi/ directory exists and migrate legacy root-level files.
```bash
python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null
python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"
```

Save the `PBIP_DIR` value from the output — all subsequent steps must use it instead of a hardcoded `.SemanticModel`.

```bash
python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"
```

```bash
python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")
```

```bash
python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."
```

Save the PBI_CONFIRM value — use it to decide whether to ask before writing files.
```bash
python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"
```

### Auto-Resume (session-aware)

After detection, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null
   ```
   - If output is `SESSION=active` — context was already loaded this session:
     - Count the table rows in the Model Context table from Session Context.
     - Output on a single line: `Context resumed — [N] tables loaded`
     - Skip any "Model Context Check" (Step 0.5) below — context is already available.
   - If output is `SESSION=new` — first command this session:
     - Output: `Loading model context (first command this session)...`
     - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi/context.md`.
     - Write `**Session-Start:** [current UTC time in ISO 8601]` immediately after the `## Model Context` heading line in `.pbi/context.md`.
     - Output the summary table and: `Context loaded — [N] tables. Ready.`

2. **PBIP_MODE=paste — nearby folder check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null
   ```
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.

---

# /pbi-audit


## Instructions

### Step 0 — Check PBIP detection output

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run /pbi-audit from a directory containing a *.SemanticModel/ folder.

**If PBIP_MODE=file:** output:

```
Auditing model...
```

Then proceed to Step 1.

---

### Step 1 — Read all model metadata

**For TMDL (PBIP_FORMAT=tmdl):**

The File Index has already listed all `.tmdl` file paths.

Use the Read tool to read every `.tmdl` file path returned by the File Index.

**Malformed file guard:** If a `.tmdl` file cannot be read or does not contain a `table` keyword, output: `Warning: [filename] could not be parsed — skipping.` and continue. If model.bim contains invalid JSON, output: `Error: model.bim contains invalid JSON — cannot audit. Check the file in Power BI Desktop.` and stop.

**Empty model guard:** If no tables are found after reading all files, output: `Model is empty — no tables found. Nothing to audit.` and stop.

Use the Read tool to read `$PBIP_DIR/definition/relationships.tmdl` — if not found, treat as "no relationships defined".

From each table `.tmdl` file extract:

- **Table name:** the first non-blank line starting with `table ` — extract the name after `table `
- **Table-level dataCategory:** look for `dataCategory: Time` appearing BEFORE any `column` or `measure` keyword in the file.
- **Measure blocks:** each `measure Name =` or `measure 'Name' =` block. For each measure extract:
  - Name: text after `measure ` up to ` =`, stripping single quotes
  - Whether a `///` description line appears IMMEDIATELY above the measure keyword
  - Whether `formatString:` appears inside the block
  - Whether `displayFolder:` appears inside the block
- **Column blocks:** each `column Name` line. Extract column name, strip quotes. Also extract `dataType:` and `isHidden` property (default false if absent).

From `relationships.tmdl` extract: for each `relationship` block, the fromTable, fromColumn, toTable, toColumn, and crossFilteringBehavior value.

**For TMSL (PBIP_FORMAT=tmsl):**

Read `$PBIP_DIR/model.bim`. If model.bim is >2000 lines, use offset/limit parameters.

Extract:
- `model.tables[]`: table name, dataCategory, measures array, columns array
- For each measure: name, description, formatString, displayFolder
- For each column: name, isHidden
- `model.relationships[]`: fromTable, fromColumn, toTable, toColumn, crossFilteringBehavior

Build an internal metadata structure. Do not output it yet.

---

### Step 2 — Parallel Domain Passes

**Small model shortcut:** If the model has 4 or fewer tables, run all domain passes sequentially (Steps 2a–2h below) without Agent parallelism — the overhead of spawning agents exceeds the benefit.

**For models with 5+ tables:** Spawn 3 parallel Agents to run domain passes concurrently:

**Agent 1 — Relationships + Date Table:**
Pass the extracted metadata (relationships, tables with dataCategory, column dataTypes) and run:
- Domain Pass A: Relationships (rules R-01, R-02, R-03)
- Domain Pass C: Date Table (rules D-01, D-02)

**Agent 2 — Naming + Measures:**
Pass the extracted metadata (all table/measure/column names, measure properties) and run:
- Domain Pass B: Naming (rules N-01, N-02, N-03)
- Domain Pass D: Measures (rules M-01, M-02, M-03)

**Agent 3 — Hidden Columns + PBIR Visuals:**
Pass the extracted metadata (columns with isHidden, relationship columns, PBIR detection output) and run:
- Domain Pass E: Hidden Column Hygiene (rules H-01, H-02, H-03)
- Domain Pass F: Report Layer (rules V-01, V-02, V-03 — only if PBIR=yes)

Each agent returns its findings as a list. Collect all findings after all 3 agents complete.

---

### Step 2a — Domain Pass A: Relationships

Accumulate findings_relationships[]:

**Rule R-01 — Bidirectional relationship (CRITICAL):**
- Any relationship where crossFilteringBehavior = "bothDirections"
- Finding: `Bidirectional filter set on relationship from [FromTable][FromColumn] to [ToTable][ToColumn].`
- Recommendation: `Change crossFilteringBehavior to single-direction. Bidirectional filters create ambiguous filter paths and degrade query performance.`

**Rule R-02 — Isolated table heuristic (WARN):**
- Tables with NO outbound or inbound relationships AND whose name matches fact table patterns (contains "Sales", "Orders", "Transactions", "Invoice", "Fact", or starts without "Dim"/"Date"/"Calendar" prefix) AND has at least one numeric column (dataType: int64, double, decimal)
- Only flag tables with 2+ columns (single-column parameter tables are intentionally standalone)
- Recommendation: `Verify this table is intentionally isolated. Fact tables typically have relationships to dimension tables.`

**Rule R-03 — No relationships at all (INFO):**
- If model has more than 2 tables AND zero relationships total
- Recommendation: `If tables are intentionally standalone this can be ignored.`

---

### Step 2b — Domain Pass B: Naming

Accumulate findings_naming[]:

**Naming inference algorithm:**
1. For each scope (measure names, table names, column names), collect all names
2. For scopes with 4+ names, detect dominant pattern: Title Case, PascalCase, snake_case, Prefix pattern, Mixed
3. Dominant pattern = pattern used by >50% of names in that scope
4. For scopes with fewer than 4 names: skip pattern inference

**Rule N-01 — Blank or whitespace-only name (WARN)**
**Rule N-02 — Special characters (WARN):** Names with leading/trailing spaces, or characters outside letters, digits, spaces, underscores, hyphens, parentheses
**Rule N-03 — Naming style inconsistency (INFO):** Names deviating from inferred dominant pattern. Only emit if 3+ names deviate. Group all deviating names into ONE finding per scope.

---

### Step 2c — Domain Pass C: Date Table

Accumulate findings_date[]:

**Rule D-01 — No date table detected (WARN):** If no table has dataCategory = Time
**Rule D-02 — Date table exists but no Date/DateTime column (INFO):** Table marked as date table but has no column with dateTime/date dataType

If a date table IS found and IS correctly configured: add INFO finding noting it.

---

### Step 2d — Domain Pass D: Measures

Accumulate findings_measures[]:

**Rule M-01 — Empty formatString (WARN):** Any measure with no formatString property
**Rule M-02 — Empty description (INFO):** Any measure with no description
**Rule M-03 — No display folder (WARN):** Any measure with no displayFolder

---

### Step 2e — Domain Pass E: Hidden Column Hygiene

Accumulate findings_columns[]:

**Build relationship column set:** Collect all columns that appear as fromColumn or toColumn in any relationship.

**Rule H-01 — Relationship key column not hidden (WARN):** Column used in a relationship AND isHidden = false
**Rule H-02 — Foreign key / ID column not hidden (WARN):** Column name matches key/ID patterns (ends with Key, ID, Id, _id, _key, FK; equals id; starts with SK_, FK_, PK_) AND isHidden = false. Exclude columns already flagged by H-01.
**Rule H-03 — Summary (INFO):** If ALL key columns are hidden: emit one INFO finding "All detected key/ID columns are already hidden."

---

### Step 2f — Domain Pass F: Report Layer (PBIR only)

**Skip if PBIR=no.**

Read each JSON file listed by PBIR Detection. If a JSON file cannot be parsed (malformed JSON), output: `Warning: [filename] contains invalid JSON — skipping report-layer check for this visual.` and continue with remaining files.

Look for measure references in:
- `"dataTransforms"` → `"projections"` → `"queryRef"`
- `"dataTransforms"` → `"selects"` → `"measure"` → `"property"`

Build model_measures and visual_measures sets.

**Rule V-01 — Unused measure (INFO):** In model but NOT in visuals
**Rule V-02 — Missing measure reference (WARN):** In visuals but NOT in model
**Rule V-03 — Report layer summary (INFO):** Always emit when PBIR is present

---

### Step 2g — Domain Pass G: Advanced Features

Accumulate findings_advanced[]:

**Rule AF-01 — Calculation group present (INFO):**
- If any table has `calculationGroup` property (TMDL: `calculationGroup` keyword in the table file; TMSL: `"calculationGroup"` object in the table JSON)
- Finding: `Calculation group detected: [TableName].`
- Recommendation: `Verify calculation items do not conflict with explicit CALCULATE filters in measures. Measures using SELECTEDMEASURE() are evaluated within the calculation group context — ensure all measures behave correctly when wrapped.`

**Rule AF-02 — Field parameter present (INFO):**
- If any table's columns are generated by a `NAMEOF()` expression (TMDL: expression contains `NAMEOF(`; TMSL: column expression contains `NAMEOF(`)
- Finding: `Field parameter detected: [TableName].`
- Recommendation: `Field parameters are display-only constructs. Verify the parameter table is hidden from report users and that slicer interactions behave as expected.`

---

### Step 2h — Domain Pass H: Performance Heuristics

Accumulate findings_performance[]:

**Rule P-01 — Aggregation table not hidden (WARN):**
- If any table name contains "Agg", "Aggregation", or "Summary" (case-insensitive) AND isHidden = false at the table level (TMDL: no `isHidden` line or `isHidden: false`; TMSL: `"isHidden": false` or absent)
- Finding: `Aggregation table [TableName] is visible to report users.`
- Recommendation: `Aggregation tables should be hidden. Users should interact with the detail table — the engine routes queries to the aggregation table automatically.`

**Rule P-02 — High-cardinality column heuristic (INFO):**
- For each column that is NOT hidden AND is NOT used in any relationship AND whose dataType is `string` AND whose name matches high-cardinality patterns: contains "Description", "Comment", "Note", "Detail", "Address", "Email", "URL", "Path", "FullName", "LongText", or ends with "_desc", "_text", "_notes"
- Only flag if the column is NOT in a table with fewer than 3 columns (small lookup tables often have legitimate text columns)
- Finding: `Column [TableName].[ColumnName] appears to be high-cardinality text. Consider hiding it if not used in visuals.`
- Recommendation: `High-cardinality text columns consume memory and rarely belong in filter panes. Hide them unless they are intentionally exposed for search or display.`

---

### Step 3 — Merge and sort all findings

Combine all findings. Sort: CRITICAL first, then WARN, then INFO.

Count totals: N_critical, N_warn, N_info.

---

### Step 4 — Emit the report inline

Output:

```
# PBI Model Audit Report
**Project:** $PBIP_DIR
**Format:** [TMDL or TMSL (model.bim)]
**Date:** [current UTC date and time, format: YYYY-MM-DD HH:MM UTC]
**Findings:** [N_critical] CRITICAL · [N_warn] WARN · [N_info] INFO

---

## CRITICAL
[one subsection per CRITICAL finding, format:
### [domain tag] [subject]
[finding text]
**Recommendation:** [recommendation text]
]

[If no CRITICAL findings: "## CRITICAL\n_None_"]

---

## WARN
[one subsection per WARN finding]

---

## INFO
[one subsection per INFO finding]

---

*Audit complete. Report written to: audit-report.md*
```

Domain tag format: `[Relationships]`, `[Naming]`, `[Date Table]`, `[Measures]`, `[Columns]`, `[Report]`

---

### Step 5 — Write audit-report.md

Write the exact same report content to `audit-report.md` in the project root using the Write tool.

---

### Step 5b — Auto-Fix Mode (optional)

After writing audit-report.md, check if there are any CRITICAL or WARN findings with available auto-fixes.

**Fixable finding types:**
| Rule | Fix Action |
|------|-----------|
| R-01 (bidirectional) | Ask direction preference, then change crossFilteringBehavior |
| H-01 (relationship key visible) | Add isHidden property to column |
| H-02 (ID column visible) | Same as H-01 |
| M-01 (empty formatString) | Skip — cannot infer correct format |
| M-03 (no display folder) | Skip — cannot infer correct folder |

If there are zero fixable findings: skip to Step 6.

If there are fixable findings, output:

```
**Auto-fix available**

[N] findings can be fixed automatically:
- [list each fixable finding: rule, subject, fix action]

Apply all fixes? (y/N)
```

- n, N, Enter, or anything else: Output "No fixes applied." Skip to Step 6.
- y or Y: proceed with fixes.

**Apply fixes:**

**R-01 direction prompt (before applying):**
For each R-01 finding, ask:
> Relationship [FromTable] → [ToTable] is bidirectional. Which direction should filter?
> **A** — [FromTable] → [ToTable] (single direction, many-to-one side filters)
> **B** — [ToTable] → [FromTable] (reverse)

Wait for answer. Apply the chosen direction.

**TMDL fixes:**
For each file that needs changes:
1. Read the .tmdl file
2. Apply all fixes (R-01: change crossFilteringBehavior to chosen direction; H-01/H-02: add isHidden property)
3. Write the entire file back

**TMSL fixes:**
1. Read model.bim
2. Apply all fixes
3. Write entire model.bim back

Output for each fix: `Fixed: [rule] — [subject] — [action taken]`

**Auto-commit:**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add "$PBIP_DIR/" 2>/dev/null
  git commit -m "fix: auto-fix [N] audit findings (R-01, H-01, H-02)" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: fix: auto-fix [N] audit findings"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi-commit to initialise one."
- AUTO_COMMIT=fail: silent

**Auto-fix example walkthrough:**
Given a model with a bidirectional relationship `Sales[ProductKey] → Product[ProductKey]` and a visible key column `Sales[ProductKey]`:
1. Prompt: "Relationship Sales → Product is bidirectional. Which direction? A — Sales → Product, B — Product → Sales"
2. User picks A → set crossFilteringBehavior to `oneDirection` (many-to-one: Product filters Sales)
3. Add `isHidden` to `Sales[ProductKey]` column block
4. Write back the modified `.tmdl` files
5. Commit: `fix: auto-fix 2 audit findings (R-01, H-01)`

---

### Step 6 — Update .pbi/context.md

Use Read-then-Write to update `.pbi/context.md`:
1. Update `## Last Command`: Command = `/pbi-audit`, Outcome = `Audit complete — [N_critical] CRITICAL, [N_warn] WARN, [N_info] INFO findings. Report written to audit-report.md`
2. Append row to `## Command History`; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

### Anti-Patterns
- NEVER auto-fix without confirmation — always show the fix list and ask
- NEVER change relationship direction without asking which direction to keep
- NEVER add, remove, rename, or rewrite measure expressions during audit — auto-fix only touches structural properties (isHidden, crossFilteringBehavior)
- NEVER report findings without severity classification (CRITICAL/WARN/INFO)
