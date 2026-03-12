---
name: pbi-new
description: Scaffold a new DAX measure from a plain-English description. Generates the DAX expression, naming, format string, display folder, and description. Use when an analyst wants to create a new measure from scratch.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Detection

!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Desktop Check

!`tasklist /fi "imagename eq PBIDesktop.exe" 2>/dev/null | findstr /i "PBIDesktop.exe" >nul 2>&1 && echo "DESKTOP=open" || echo "DESKTOP=closed"`

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Mode Detection

Read the PBIP Detection output.

**If PBIP_MODE=file:** output header:
> File mode — PBIP project detected ([FORMAT]) | Desktop: [STATUS]

Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.
Where [STATUS] is "closed — will write to disk" if DESKTOP=closed, or "open — output is paste-ready" if DESKTOP=open.

**If PBIP_MODE=paste:** output header:
> Paste-in mode — no PBIP project. Output will be copy-paste ready.

Then proceed to Step 1.

---

### Step 1 — Collect Requirements

If `$ARGUMENTS` contains a description of the desired measure, use it directly.

Otherwise output: "Describe the measure you want to create:"

Wait for analyst input. Parse the description to extract:
- **Business intent**: what the measure should calculate (e.g., "year-to-date revenue", "running total of orders")
- **Table context**: which table it belongs to (e.g., "in Sales table"). If not specified, ask: "Which table should this measure be added to?"
- **Any constraints**: specific filter conditions, time intelligence, relationships mentioned

---

### Step 2 — Model Context Check (PBIP_MODE=file only)

If PBIP_MODE=file, read the Session Context for a `## Model Context` section. Use table names, column names, and relationship info to:
- Validate the target table exists
- Use correct column references in the DAX expression
- Reference related tables through established relationships

If no Model Context is available, suggest running `/pbi:load` first but proceed with the analyst's description.

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

### Step 5 — File Write (PBIP_MODE=file and DESKTOP=closed only)

If PBIP_MODE=paste or DESKTOP=open:
- Output: "Copy the DAX above and paste it into Power BI Desktop."
- Skip to Step 6.

If PBIP_MODE=file and DESKTOP=closed:

**Confirm target table:**
If the analyst did not specify a table, ask: "Which table should this measure be added to?"

**If PBIP_FORMAT=tmdl:**
1. Run bash: `grep -rlF "table " ".SemanticModel/definition/tables/" 2>/dev/null` to verify the target table file exists.
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
1. Read `.SemanticModel/model.bim` using the Read tool.
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
5. Output: "Written to: [Measure Name] in .SemanticModel/model.bim"

**Auto-commit:**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add '.SemanticModel/' 2>/dev/null
  git commit -m "feat: add [MEASURE_NAME] measure to [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: feat: add [MEASURE_NAME] measure to [TABLE_NAME]"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
- AUTO_COMMIT=fail: silent (non-fatal)

---

### Step 6 — Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:new`, Timestamp = current UTC ISO 8601, Measure = [Measure Name] in [TableName], Outcome = `New measure scaffolded`
- `## Command History`: Append one row `| [timestamp] | /pbi:new | [Measure Name] | New measure scaffolded |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

---

### Anti-Patterns
- NEVER generate a measure that references columns not in the model (when model context is available)
- NEVER use FILTER(Table, ...) when a direct column filter suffices
- NEVER skip the format string — every measure should have one
- NEVER write to disk when Desktop is open
- NEVER auto-push to remote
