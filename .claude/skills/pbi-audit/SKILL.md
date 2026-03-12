---
name: pbi-audit
description: Run a full model health audit against a PBIP project. Checks naming conventions, relationship health, date table configuration, and measure quality. Produces a severity-graded CRITICAL / WARN / INFO report.
argument-hint: "(no arguments — runs from directory containing .SemanticModel/)"
disable-model-invocation: true
allowed-tools: Read, Write, Bash
model: sonnet
---

## PBIP Context Detection
!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Desktop Check

!`tasklist /fi "imagename eq PBIDesktop.exe" 2>/dev/null | findstr /i "PBIDesktop.exe" >nul 2>&1 && echo "DESKTOP=open" || echo "DESKTOP=closed"`

## PBIP File Index
!`if [ -d ".SemanticModel/definition/tables" ]; then find ".SemanticModel/definition/tables/" -name "*.tmdl" 2>/dev/null; elif [ -f ".SemanticModel/model.bim" ]; then echo "tmsl:.SemanticModel/model.bim"; fi`

## PBIR Detection
!`if [ -d ".Report" ]; then find ".Report/" -name "*.json" -not -name "item.config.json" -not -name "item.metadata.json" 2>/dev/null | head -20 && echo "PBIR=yes"; else echo "PBIR=no"; fi`

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Check PBIP detection output

Read the output from the PBIP Context Detection block above.

**If PBIP_MODE=paste:** output exactly this message and stop. Do not write any files. Do not proceed.

> No PBIP project found in this directory. Run /pbi:audit from a directory containing .SemanticModel/.

**If PBIP_MODE=file:** output a single progress line:

```
Auditing model...
```

Then proceed to Step 1.

---

### Step 1 — Read all model metadata

**For TMDL (PBIP_FORMAT=tmdl):**

The PBIP File Index block has already listed all `.tmdl` file paths under `.SemanticModel/definition/tables/`.

Use the Read tool to read every `.tmdl` file path returned by the PBIP File Index block.

Use the Read tool to read `.SemanticModel/definition/relationships.tmdl` — if not found, treat as "no relationships defined" (do not error).

From each table `.tmdl` file extract:

- **Table name:** the first non-blank line starting with `table ` — extract the name after `table `
- **Table-level dataCategory:** look for `dataCategory: Time` appearing BEFORE any `column` or `measure` keyword in the file. This is a table-level property, not inside a column or measure block.
- **Measure blocks:** each `measure Name =` or `measure 'Name' =` block. For each measure extract:
  - Name: text after `measure ` up to ` =`, stripping single quotes
  - Whether a `///` description line appears IMMEDIATELY above the measure keyword (no blank line between `///` and `measure`)
  - Whether `formatString:` appears inside the block (before the next `measure`, `column`, or end of block)
  - Whether `displayFolder:` appears inside the block (before the next `measure`, `column`, or end of block)
- **Column blocks:** each `column Name` line. Extract column name, strip quotes if present. Also extract `dataType:` for each column. Also extract `isHidden` property (true/false — default false if absent).

From `relationships.tmdl` extract: for each `relationship` block, the fromTable, fromColumn, toTable, toColumn, and crossFilteringBehavior value.

**For TMSL (PBIP_FORMAT=tmsl):**

Use the Read tool to read `.SemanticModel/model.bim`.

If model.bim is >2000 lines, use the offset/limit parameters to read in sections — extract only metadata fields (skip expression bodies after the first line).

From the JSON structure extract:

- `model.tables[]`: table name, dataCategory (flag if "Time"), measures array, columns array
- For each measure: name, description (flag as missing if absent OR if empty string ""), formatString (flag as missing if absent or ""), displayFolder (flag as missing if absent or "")
- For each column: name, isHidden (default false if absent)
- `model.relationships[]`: fromTable, fromColumn, toTable, toColumn, crossFilteringBehavior (flag if "bothDirections")

Build an internal metadata structure. Do not output it yet.

---

### Step 2 — Domain Pass A: Relationships

Accumulate findings_relationships[]:

**Rule R-01 — Bidirectional relationship (CRITICAL):**
- Any relationship where crossFilteringBehavior = "bothDirections" (TMDL or TMSL)
- Subject: `Relationship: [FromTable] → [ToTable]`
- Finding: `Bidirectional filter set on relationship from [FromTable][FromColumn] to [ToTable][ToColumn].`
- Recommendation: `Change crossFilteringBehavior to single-direction (fromTable → toTable). Bidirectional filters create ambiguous filter paths in star schemas and degrade query performance.`

**Rule R-02 — Isolated table heuristic (WARN):**
- Tables with NO outbound relationships (table does not appear as fromTable in any relationship) AND whose name matches typical patterns: name contains "Sales", "Orders", "Transactions", "Invoice", "Fact", or has no "Dim" prefix (i.e., it could be a fact table)
- Only flag if the table also has at least one numeric column (dataType: decimal or int64) — reduces false positives
- Subject: `Table: [TableName] (potential fact table with no outbound relationships)`
- Finding: `Table [TableName] has no outbound relationships to any other table.`
- Recommendation: `Verify this table is intentionally isolated. Fact tables typically have relationships to dimension tables for filter propagation.`

**Rule R-03 — No relationships at all (INFO):**
- If model has more than 2 tables AND zero relationships total
- Subject: `Model: .SemanticModel`
- Finding: `Model has [N] tables with no relationships defined.`
- Recommendation: `If tables are intentionally standalone this can be ignored. If relationships should exist, define them in Power BI Desktop.`

---

### Step 3 — Domain Pass B: Naming

Accumulate findings_naming[]:

**Naming inference algorithm:**
1. For each scope (measure names, table names, column names), collect all names
2. For scopes with 4+ names, detect dominant pattern:
   - Title Case: majority of words capitalised, spaces between words (e.g., "Revenue YTD", "Sales Amount")
   - PascalCase: no spaces, each word capitalised (e.g., "RevenueYTD", "SalesAmount")
   - snake_case: lowercase with underscores (e.g., "revenue_ytd")
   - Prefix pattern: names start with a consistent short prefix + separator (e.g., "kpi_", "[CAL] ")
   - Mixed: no dominant pattern (skip inference, emit no INFO findings)
3. Dominant pattern = pattern used by >50% of names in that scope
4. For scopes with fewer than 4 names: skip pattern inference — emit no naming INFO findings for that scope

**Rule N-01 — Blank or whitespace-only name (WARN):**
- Subject: `[Scope]: [Name in context]`
- Recommendation: `Provide a descriptive name. Blank names cause display issues in report visuals.`

**Rule N-02 — Special characters (WARN):**
- Names with leading/trailing spaces, or characters outside: letters, digits, spaces, underscores, hyphens, parentheses
- Recommendation: `Rename to remove special characters. Names with special characters require quoting in DAX expressions.`

**Rule N-03 — Naming style inconsistency (INFO):**
- Names deviating from inferred dominant pattern for their scope
- Only emit if 3+ names deviate (avoid noise on small models)
- Group all deviating names into ONE finding per scope (not one finding per name)
- Recommendation: `Standardise on [inferred pattern] (dominant pattern in this model).`

**Rule N-04:** SKIP — display folder is handled exclusively by Domain D Rule M-03. This avoids duplicate findings for the same measure.

---

### Step 4 — Domain Pass C: Date Table

Accumulate findings_date[]:

**Rule D-01 — No date table detected (WARN):**
- If no table has dataCategory = Time (TMDL table-level property) or "Time" (TMSL dataCategory field)
- Subject: `Model: .SemanticModel`
- Finding: `No table is marked as a date table in this model.`
- Recommendation: `Mark your date dimension table as a date table in Power BI Desktop (Table Tools > Mark as date table). Required for DAX time intelligence functions (DATESYTD, TOTALYTD, etc.).`

**Rule D-02 — Date table exists but no Date/DateTime column (INFO):**
- Table is marked as date table (dataCategory = Time) but has no column with dataType: dateTime or dataType: date (TMDL) / "dateTime" or "date" (TMSL)
- Subject: `Table: [DateTableName]`
- Finding: `Table [DateTableName] is marked as a date table but no Date or DateTime column was detected.`
- Recommendation: `Verify the date table has a Date/DateTime column as the key. The date column must contain unique, contiguous dates with no gaps.`

If a date table IS found and IS correctly configured (has Date/DateTime column):
- Add an INFO finding: `Table [DateTableName] is marked as a date table with a Date/DateTime column. Data content validation (gaps, blank dates) requires Power BI Desktop.`

---

### Step 5 — Domain Pass D: Measures

Accumulate findings_measures[]:

**Rule M-01 — Empty formatString (WARN):**
- Any measure with no formatString property (TMDL: no `formatString:` line in block; TMSL: field absent or empty string)
- Subject: `Measure: [Name] in Table: [TableName]`
- Finding: `Measure '[Name]' has no format string.`
- Recommendation: `Add a format string. Examples: '#,##0' for integers, '#,##0.00' for decimals, '0.0%' for percentages. Missing format strings cause inconsistent display in reports.`

**Rule M-02 — Empty description (INFO):**
- Any measure with no description (TMDL: no `///` line immediately above measure keyword; TMSL: "description" field absent OR empty string)
- Subject: `Measure: [Name] in Table: [TableName]`
- Finding: `Measure '[Name]' has no description.`
- Recommendation: `Add a description explaining the business logic. Use /pbi:comment to generate a description automatically.`

**Rule M-03 — No display folder (WARN):**
- Any measure with no displayFolder (TMDL: no `displayFolder:` line in block; TMSL: field absent or empty string)
- Subject: `Measure: [Name] in Table: [TableName]`
- Finding: `Measure '[Name]' has no display folder.`
- Recommendation: `Assign a display folder to group related measures in the Fields pane.`

---

### Step 5b — Domain Pass E: Hidden Column Hygiene

Accumulate findings_columns[]:

**Build relationship column set:** Collect all columns that appear as `fromColumn` or `toColumn` in any relationship. These are relationship key columns.

**Rule H-01 — Relationship key column not hidden (WARN):**
- Any column that is used in a relationship (appears in the relationship column set) AND has `isHidden = false` (or isHidden absent, meaning visible)
- Subject: `Column: [TableName][ColumnName]`
- Finding: `Column '[ColumnName]' in table '[TableName]' is a relationship key but is visible to report users.`
- Recommendation: `Hide this column. Relationship key columns should be hidden — users should filter through the related dimension table instead.`

**Rule H-02 — Foreign key / ID column not hidden (WARN):**
- Any column whose name matches common key/ID patterns AND has `isHidden = false`:
  - Name ends with `Key`, `ID`, `Id`, `_id`, `_key`, `FK`
  - Name equals `id` (case-insensitive)
  - Name starts with `SK_`, `FK_`, `PK_`
- Exclude columns already flagged by H-01 (avoid duplicate findings)
- Subject: `Column: [TableName][ColumnName]`
- Finding: `Column '[ColumnName]' in table '[TableName]' appears to be an internal key/ID column but is visible to report users.`
- Recommendation: `Hide this column if it is only used for relationships or internal logic. Visible ID columns clutter the Fields pane.`

**Rule H-03 — Summary of hidden column hygiene (INFO):**
- If ALL relationship key columns and all detected key/ID columns are already hidden: emit one INFO finding
- Subject: `Model: .SemanticModel`
- Finding: `All detected key/ID columns are already hidden. Column hygiene looks good.`
- Recommendation: `No action needed.`
- Only emit this if zero H-01 and zero H-02 findings were generated.

---

### Step 5c — Domain Pass F: Report Layer (PBIR only)

**Skip this entire step if PBIR Detection output is `PBIR=no`.** Only run when `.Report/` directory exists with PBIR format JSON files.

Accumulate findings_report[]:

**Read PBIR visual files:**

Read each JSON file listed by the PBIR Detection block. PBIR visuals are stored as JSON objects. Look for measure references in these locations within each visual JSON:
- `"dataTransforms"` → `"projections"` → entries with `"queryRef"` containing measure names
- `"dataTransforms"` → `"selects"` → entries with `"measure"` property containing `"property"` (measure name) and `"entity"` (table name)
- Any string matching the pattern `[MeasureName]` that corresponds to a known measure from Step 1

Build two sets:
- **model_measures**: all measure names extracted from Step 1
- **visual_measures**: all measure names referenced in PBIR visual files

**Rule V-01 — Unused measure (INFO):**
- Measures in model_measures but NOT in visual_measures
- Subject: `Measure: [Name] in Table: [TableName]`
- Finding: `Measure '[Name]' is defined in the model but not referenced in any report visual.`
- Recommendation: `Verify this measure is intentionally unused. Unused measures add model overhead and clutter the Fields pane. Consider removing or hiding if not needed.`
- Note: only emit if the model has at least 1 PBIR visual file. Do not flag if there are zero visuals.

**Rule V-02 — Missing measure reference (WARN):**
- Measure names found in visual_measures but NOT in model_measures
- Subject: `Visual reference: [MeasureName]`
- Finding: `A visual references measure '[MeasureName]' which does not exist in the model.`
- Recommendation: `This visual may show errors or blank values. Check if the measure was renamed or removed. Re-create it with /pbi:new or update the visual.`

**Rule V-03 — Report layer summary (INFO):**
- Always emit when PBIR is present
- Subject: `Report: .Report`
- Finding: `Report layer scanned: [N] visuals found, [M] unique measures referenced.`
- Recommendation: `No action needed — informational summary.`

---

### Step 6 — Merge and sort all findings

Combine findings_relationships[] + findings_naming[] + findings_date[] + findings_measures[] + findings_columns[] + findings_report[] into one list.

Sort order: CRITICAL findings first, then WARN, then INFO.

Count totals: N_critical, N_warn, N_info.

---

### Step 7 — Emit the report inline

Output the following markdown report to chat (print in full — no truncation):

```
# PBI Model Audit Report
**Project:** .SemanticModel
**Format:** [TMDL or TMSL (model.bim)]
**Date:** [current UTC date and time, format: YYYY-MM-DD HH:MM UTC]
**Findings:** [N_critical] CRITICAL · [N_warn] WARN · [N_info] INFO

---

## 🔴 CRITICAL
[one subsection per CRITICAL finding, format:
### [domain tag] [subject]
[finding text]
**Recommendation:** [recommendation text]
]

[If no CRITICAL findings: "## 🔴 CRITICAL\n_None_"]

---

## 🟡 WARN
[one subsection per WARN finding]

[If no WARN findings: "## 🟡 WARN\n_None_"]

---

## 🔵 INFO
[one subsection per INFO finding]

[If no INFO findings: "## 🔵 INFO\n_None_"]

---

*Audit complete. Report written to: audit-report.md*
```

CRITICAL RULES for report output:
- Never use JSON paths (e.g., `model.tables[0]`). Always use actual table and measure names.
- Every finding MUST have a subject (table/measure name) and a Recommendation line.
- Domain tag format: `[Relationships]`, `[Naming]`, `[Date Table]`, `[Measures]`, `[Columns]`, `[Report]`
- Severity emoji: 🔴 CRITICAL, 🟡 WARN, 🔵 INFO (locked by user decision)

---

### Step 8 — Write audit-report.md

Write the exact same report content to `audit-report.md` in the project root (the directory where /pbi:audit was invoked) using the Write tool.

Use Read-then-Write:
1. Attempt to Read `audit-report.md` (may not exist — that is fine)
2. Write the full report content using the Write tool, overwriting any previous audit report

---

### Step 8b — Auto-Fix Mode (optional)

After writing audit-report.md, check if there are any CRITICAL or WARN findings with available auto-fixes.

**Fixable finding types:**
| Rule | Fix Action |
|------|-----------|
| R-01 (bidirectional) | Change `crossFilteringBehavior` from `bothDirections` to `oneDirection` (TMDL) or remove `"crossFilteringBehavior": "bothDirections"` (TMSL) |
| H-01 (relationship key visible) | Add `isHidden` property to column (TMDL: add `isHidden` line; TMSL: set `"isHidden": true`) |
| H-02 (ID column visible) | Same as H-01 |
| M-01 (empty formatString) | Skip — cannot infer correct format without context |
| M-03 (no display folder) | Skip — cannot infer correct folder without context |

If there are zero fixable findings (no R-01, H-01, or H-02): skip to Step 9.

If there are fixable findings, check the Desktop Check output:

**If DESKTOP=open:** Output "Auto-fix available but Desktop is open. Close Desktop and re-run /pbi:audit to apply fixes." Skip to Step 9.

**If DESKTOP=closed:** Output:

```
**Auto-fix available**

[N] findings can be fixed automatically:
- [list each fixable finding: rule, subject, fix action]

Apply all fixes? (y/N)
```

- n, N, Enter, or anything else: Output "No fixes applied." Skip to Step 9.
- y or Y: proceed with fixes.

**Apply fixes:**

**TMDL fixes:**
For each file that needs changes:
1. Read the .tmdl file (Read tool)
2. Apply all fixes for that file:
   - R-01: Find `crossFilteringBehavior: bothDirections` in relationships.tmdl, change to `crossFilteringBehavior: oneDirection`
   - H-01/H-02: Find the column block, add `isHidden` property line after the column declaration (preserve tab indentation). If `isHidden` line already exists, change value to `true`.
3. Write the entire file back (Write tool)

**TMSL fixes:**
1. Read `.SemanticModel/model.bim` (Read tool)
2. Apply all fixes:
   - R-01: Remove or change `"crossFilteringBehavior": "bothDirections"` to `"crossFilteringBehavior": "oneDirection"` in the relationship object
   - H-01/H-02: Set `"isHidden": true` on the column object
3. Write the entire model.bim back (Write tool)

Output for each fix applied:
> Fixed: [rule] — [subject] — [action taken]

**Auto-commit:**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add '.SemanticModel/' 2>/dev/null
  git commit -m "fix: auto-fix [N] audit findings (R-01, H-01, H-02)" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: fix: auto-fix [N] audit findings"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
- AUTO_COMMIT=fail: silent (non-fatal)

---

### Step 9 — Update .pbi-context.md

Use Read-then-Write to update `.pbi-context.md`:
1. Read `.pbi-context.md` using the Read tool
2. Update:
   - `## Last Command` section: Command = `/pbi:audit`, Timestamp = current UTC, Outcome = `Audit complete — [N_critical] CRITICAL, [N_warn] WARN, [N_info] INFO findings. Report written to audit-report.md`
   - `## Command History` section: append a row with same values; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections
4. Write the full updated file using the Write tool
