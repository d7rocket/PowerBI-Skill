# /pbi new

> Detection context (PBIP_MODE, PBIP_FORMAT, PBIP_DIR, File Index, Session Context) is provided by the router.

## Instructions

### Step 0 — Mode Detection

Read the PBIP_MODE from detection context.

**If PBIP_MODE=file:** output header:
> File mode — PBIP project detected ([FORMAT])

Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.

**If PBIP_MODE=paste:** output header:
> Paste-in mode — no PBIP project. Output will be copy-paste ready.

Then proceed to Step 0.5.

---

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table/column context. Proceed to Step 1 using this context — do NOT ask again.
- If `## Model Context` is absent or empty:
  - Ask: "Which table should this measure go in, and which columns are relevant?"
  - Wait for the analyst's answer.
  - Read `.pbi-context.md` with Read tool. Add `## Model Context` section with the analyst's answer. Write back with Write tool.
  - Proceed to Step 1 using the newly stored context.

Note: If model context was provided via `/pbi load` prior to this session, it will already be present — do not overwrite it.

---

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
1. Check Session Context for `## Visual Context` section.
   - If present and non-empty:
     Output: "Using saved visual context: [visual type] with slicers [slicer list]."
     Proceed to Step 3 using this context.
   - If absent or empty:
     Ask before generating:
     > "This measure is filter-sensitive — where will it be placed (e.g., card, table, matrix) and what slicers or date filters will be active?"
     Wait for the analyst's answer.
     Read `.pbi-context.md` with Read tool. Add `## Visual Context` section:
     ```
     ## Visual Context
     - Visual type: [from analyst's answer]
     - Active slicers: [from analyst's answer]
     - Noted: [current ISO 8601 timestamp]
     ```
     Write back with Write tool.
     Proceed to Step 3, incorporating the visual context into the DAX design (e.g., if placed in a card, consider CALCULATE with explicit date filter; if in a matrix with row context, note the slicer interactions).

---

### Step 3 — Generate Measure Components

Generate all five components:

**3a. Measure Name:**
- Use Title Case with spaces (matching typical Power BI convention)
- Be descriptive but concise (e.g., "Revenue YTD", "Total Orders", "Avg Order Value")
- If the model context shows an existing naming pattern (prefix convention, etc.), match it

**3b. DAX Expression:**
- Write correct, efficient DAX that implements the business intent
- Use appropriate functions: SUM/AVERAGE for simple aggregations, CALCULATE with time intelligence for date-based measures, DIVIDE for ratios (with BLANK() default)
- Reference actual column names from model context when available
- Follow the same optimisation principles as /pbi optimise (no unnecessary FILTER on tables, use SUM over SUMX for single columns, etc.)

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

### Step 5 — File Write (PBIP_MODE=file only)

If PBIP_MODE=paste:
- Output: "Copy the DAX above and paste it into Power BI Desktop."
- Skip to Step 6.

If PBIP_MODE=file:

**Confirm target table:**
If the analyst did not specify a table, ask: "Which table should this measure be added to?"

**If PBIP_FORMAT=tmdl:**
1. Run bash: `python ".claude/skills/pbi/scripts/detect.py" search "table " "$PBIP_DIR" 2>/dev/null` to verify the target table file exists. If no output is returned, the table was not found — output "Table [TableName] not found in $PBIP_DIR/definition/tables/. Check the table name and try again." and stop.
2. Read the target `.tmdl` file using the Read tool.
3. Locate the insertion point: after the last existing `measure` block (before the trailing blank line or end of measure section). If no measures exist, insert after the last `column` block.
4. Scaffold the TMDL block using the file's existing indentation (tabs):
```
	/// [description text]
	measure '[Measure Name]' =
			[DAX expression — each line indented with tabs]
		formatString: [format string]
		displayFolder: "[display folder]"
```
5. Write the entire modified file back using the Write tool.
6. Output: "Written to: [Measure Name] in [file path]"

**If PBIP_FORMAT=tmsl:**
1. Read `$PBIP_DIR/model.bim` using the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read in chunks of 1000 lines — read the full file before locating the target table's measures array.
2. Find the target table's `"measures"` array. If no `"measures"` array exists, create one.
3. Append a new measure JSON object:
```json
{
  "name": "[Measure Name]",
  "expression": "[DAX expression — use array form if multiline]",
  "formatString": "[format string]",
  "displayFolder": "[display folder]",
  "description": "[description text]"
}
```
4. Write the entire model.bim back using the Write tool.
5. Output: "Written to: [Measure Name] in $PBIP_DIR/model.bim"

**Auto-commit:**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add "$PBIP_DIR/" 2>/dev/null
  git commit -m "feat: add [MEASURE_NAME] measure to [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: feat: add [MEASURE_NAME] measure to [TABLE_NAME]"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi commit to initialise one."
- AUTO_COMMIT=fail: silent (non-fatal)

---

### Step 6 — Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi new`, Timestamp = current UTC ISO 8601, Measure = [Measure Name] in [TableName], Outcome = `New measure scaffolded`
- `## Command History`: Append one row `| [timestamp] | /pbi new | [Measure Name] | New measure scaffolded |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

---

### Anti-Patterns
- NEVER generate a measure that references columns not in the model (when model context is available)
- NEVER use FILTER(Table, ...) when a direct column filter suffices
- NEVER skip the format string — every measure should have one
- NEVER auto-push to remote

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.
