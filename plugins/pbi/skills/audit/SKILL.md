---
name: audit
description: "Health check of the model, graded by severity. Report only."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:audit

<purpose>
Model quality degrades silently — bidirectional filters create ambiguity, unhidden keys clutter filter panes, missing format strings confuse report consumers. This command surfaces problems before they reach stakeholders.
</purpose>

<core_principle>
Grade by impact, not count. One CRITICAL bidirectional filter matters more than ten INFO findings. The audit reports and suggests. It never changes the model.
</core_principle>

## Instructions

### Step 0 — Check PBIP detection output

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run /pbi:audit from a directory containing a *.SemanticModel/ folder.

**If PBIP_MODE=file:** read `shared/modeling.md` (path in the core rules), then proceed to Step 1. In live tier, read the model through the MCP Get and List operations instead of the files.

---

### Step 1 — Read all model metadata

**For TMDL (PBIP_FORMAT=tmdl):**

The model index in the preflight block lists every table file.

Use the Read tool to read every table `.tmdl` file listed there.

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

**Agent 3 — Hidden Columns + PBIR Visuals + Advanced Features + Performance:**
Pass the extracted metadata (columns with isHidden, relationship columns, table-level properties, calculation group / NAMEOF markers, PBIR detection output) and run:
- Domain Pass E: Hidden Column Hygiene (rules H-01, H-02, H-03)
- Domain Pass F: Report Layer (rules V-01, V-02, V-03 — only if PBIR=yes)
- Domain Pass G: Advanced Features (rules AF-01, AF-02)
- Domain Pass H: Performance Heuristics (rules P-01, P-02)

Each agent returns its findings as a list. Collect all findings after all 3 agents complete.

---

### Step 2a — Domain Pass A: Relationships

Accumulate findings_relationships[]:

**Rule R-01 — Bidirectional relationship (CRITICAL):**
- Any relationship where crossFilteringBehavior = "bothDirections"
- Finding: `Bidirectional filter set on relationship from [FromTable][FromColumn] to [ToTable][ToColumn].`
- Recommendation: `Change crossFilteringBehavior to single-direction. Bidirectional filters create ambiguous filter paths and degrade query performance.`
- **Exception note (include in the finding):** if this is a deliberate many-to-many bridge or RLS-propagation pattern (securityFilteringBehavior), document it instead of changing it.

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
**Rule M-02 — Empty description (WARN):** Any measure with no description — blank tooltips directly affect report consumers
**Rule M-03 — No display folder (INFO):** Any measure with no displayFolder — organisational nicety, not consumer-facing

---

### Step 2e — Domain Pass E: Hidden Column Hygiene

Accumulate findings_columns[]:

**Build relationship column set:** Collect all columns that appear as fromColumn or toColumn in any relationship.

**Rule H-01 — Relationship key column not hidden (WARN):** Column used in a relationship AND isHidden = false
**Rule H-02 — Foreign key / ID column not hidden (WARN):** Column name matches key/ID patterns (ends with Key, ID, Id, _id, _key, FK; equals id; starts with SK_, FK_, PK_) AND isHidden = false. Exclude columns already flagged by H-01. **When PBIR=yes:** also exclude columns referenced in report visuals (from the Domain Pass F visual-reference scan) — a visible ID column that is deliberately used in a visual is not a hygiene problem.
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
- Finding: `Column [TableName].[ColumnName] appears to be high-cardinality text. Consider removing it in Power Query if it is not used in visuals.`
- Recommendation: `Remove unused high-cardinality columns in Power Query — hiding only declutters the field list, it does NOT reduce VertiPaq memory (hidden columns are still loaded and compressed).`

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

*Audit complete. Report written to: .pbi/audit-report.md*
```

Domain tag format: `[Relationships]`, `[Naming]`, `[Date Table]`, `[Measures]`, `[Columns]`, `[Report]`

---

### Step 5 — Write .pbi/audit-report.md

Write the exact same report content to `.pbi/audit-report.md` in the project root using the Write tool.

---

### Step 5b - Fixing findings

The audit only reports. It never changes the model.
End the report with one line pointing at the fix path for the top finding, for example `Next: /pbi:edit to make the Sales to Date relationship single-direction`.

### Step 6 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:audit" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER change the model during an audit. Report, suggest the fix, and point at /pbi:edit.
- NEVER report findings without severity classification (CRITICAL/WARN/INFO)
