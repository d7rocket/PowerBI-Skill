---
name: new
description: "Generate a complete DAX measure from a plain-English business requirement. Produces the expression, format string, display folder, and description property. Validates against model context when available. Auto-writes to TMDL/TMSL files and auto-commits."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:new

<purpose>
Writing DAX from scratch requires knowing both the business requirement and the model structure. This command handles the translation — the analyst describes WHAT they need, the skill produces HOW in DAX.
</purpose>

<core_principle>
Generate correct, idiomatic DAX that follows the model's existing patterns. Match naming conventions, display folder structure, and format string patterns already in use. Never generate DAX that references tables or columns not in the model. Prefer the simplest DAX that satisfies the requirement — a plain SUM or DIVIDE beats CALCULATE with no filter arguments; do not use VAR/RETURN for a single-use expression; never add IFERROR or defensive BLANK-handling unless the analyst asked for it (DIVIDE already handles division by zero).
</core_principle>

## Instructions

### Step 1 — Collect Requirements

If `$ARGUMENTS` contains a description of the desired measure, use it directly.

Otherwise output: "Describe the measure you want to create:"

Wait for analyst input. Parse the description to extract:
- **Business intent**: what the measure should calculate (e.g., "year-to-date revenue", "running total of orders")
- **Table context**: which table it belongs to (e.g., "in Sales table"). If not specified, ask: "Which table should this measure be added to?"
- **Any constraints**: specific filter conditions, time intelligence, relationships mentioned

---

### Step 2 — Duplication Check

Ask:

> "Does a similar measure already exist in the model?"

Wait for the analyst's answer.

- **No** (or "not sure"): proceed to Step 2.5.
- **Yes**: ask "What's the existing measure? (paste its DAX or name it)"
  - Wait for answer.
  - In Step 3, generate a measure that wraps the existing one rather than duplicating the base logic. Use CALCULATE or a similar wrapper pattern. Example:
    ```dax
    Revenue YTD (Filtered) =
    CALCULATE(
        [Revenue YTD],
        Product[Category] = "Electronics"
    )
    ```
  - In Step 4 output, add under Assumptions: "Wraps existing measure [Name] — extends rather than duplicates logic."
  - Proceed to Step 2.5.

---

### Step 2.5 — Filter-Sensitive Pattern Check

Scan the analyst's stated business intent from Step 1 for these patterns (case-insensitive):

- **Time intelligence keywords:** DATEYTD, SAMEPERIODLASTYEAR, TOTALYTD, DATESYTD, DATEADD, PARALLELPERIOD, DATESBETWEEN
- **Time intelligence phrases:** "year to date", "same period last year", "prior year", "month-to-date", "MTD", "YTD"
- **Ratio/rank keywords:** DIVIDE, RANKX, TOPN, PERCENTILEX
- **Ratio/rank phrases:** "as a percentage", "ratio", "rank", "top N", "share of", "% of"

If **no pattern detected**: proceed directly to Step 3.

If **pattern detected**:
1. Check the preflight block for a `## Visual Context` section.
   - If present: use it and proceed to Step 3.
   - If absent, ask before generating:
     > "This measure is filter-sensitive. Where will it be placed (card, table, matrix) and which slicers or date filters will be active?"
     Save the answer with `detect.py note "Visual Context" "<visual type>; slicers: <list>"`, then proceed to Step 3 and design the DAX for that context (add explicit filters only when the visual cannot supply them).

---

### Step 3 — Generate Measure Components

Generate all five components:

**3a. Measure Name:**
- Use Title Case with spaces (matching typical Power BI convention)
- Be descriptive but concise (e.g., "Revenue YTD", "Total Orders", "Avg Order Value")
- If the model context shows an existing naming pattern (prefix convention, etc.), match it

**3b. DAX Expression:**
- Write correct, efficient DAX that implements the business intent
- Use appropriate functions: SUM/AVERAGE for simple aggregations, CALCULATE with time intelligence for date-based measures, DIVIDE for ratios (omit the third argument — BLANK() is the default)
- Reference actual column names from model context when available
- Follow the same optimisation principles as /pbi:optimise (no unnecessary FILTER on tables, use SUM over SUMX for single columns, etc.)

**3c. Format String:**
- Infer from the measure type:
  - Currency/revenue → `"$#,##0.00"` (or `"#,##0.00"` if currency unknown)
  - Percentage/ratio → `"0.0%"`
  - Count/integer → `"#,##0"`
  - Decimal → `"#,##0.00"`
- If ambiguous, default to `"#,##0.00"` and note the assumption

**3d. Display Folder:**
- Infer from the measure type:
  - Revenue/sales/cost measures → `"Financial"`
  - Count/quantity measures → `"Counts"`
  - Ratio/percentage measures → `"KPIs"`
  - Time intelligence measures → `"Time Intelligence"`
- If model context shows existing display folder patterns, match those instead
- If unsure, use `""` (empty) and note the analyst can set one

**3e. Description:**
- 1–3 sentences, plain business English
- Max 300 characters
- No DAX function names, no markdown
- States what the measure calculates, key filter conditions, and caveats
- Ends with a period

---

### Step 4 — Output Preview

Output the scaffolded measure using this format:

```
**New Measure: [Measure Name]**

### DAX
```dax
[Measure Name] =
[DAX expression]
```

### Properties
- **Format string:** `[format string]`
- **Display folder:** `[display folder]`
- **Description:** [description text]

### Assumptions
- [any assumptions made about column names, table context, format, etc.]
```

---

### Step 5 - Test and write

**Test first (live tier only):** run the candidate with a query-scoped `DEFINE MEASURE` as described in live mode. Fix any error before showing the measure as final, and report the value it returns.

**PBIP_MODE=paste:** say `Copy the DAX above into Power BI Desktop.` and go to Step 6.

**PBIP_MODE=file:**

1. If the analyst did not name a table, ask `Which table should this measure be added to?` The table must exist in the model index.
2. The change is a new measure with all four components from Step 3: expression, `formatString`, `displayFolder`, description.
3. FILE tier, TMDL: insert after the last `measure` block of the table file (after the last `column` block when there are no measures), using the file's tab indentation:

```
	/// [description]
	measure '[Measure Name]' =
			[DAX expression, each line tab-indented]
		formatString: [format string]
		displayFolder: "[display folder]"
```

4. FILE tier, TMSL: append to the table's `"measures"` array (create it if missing). Use the array form for a multi-line expression.

```json
{
  "name": "[Measure Name]",
  "expression": "[DAX expression]",
  "formatString": "[format string]",
  "displayFolder": "[display folder]",
  "description": "[description]"
}
```

5. LIVE tier: create it with `measure_operations`, passing the same four components.
6. Apply with the write procedure of the active tier (core rules section 5, or live mode). Preview and confirm first.
7. Commit message: `feat: add [Measure Name] measure to [Table]`.

---

### Step 6 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:new" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER generate a measure that references columns not in the model (when model context is available)
- NEVER use FILTER(Table, ...) when a direct column filter suffices
- NEVER wrap an expression in CALCULATE without filter arguments
- NEVER use VAR/RETURN when the expression is used only once
- NEVER add IFERROR/ISERROR unless the analyst explicitly requested it
- NEVER skip the format string — every measure should have one
- NEVER auto-push to remote
