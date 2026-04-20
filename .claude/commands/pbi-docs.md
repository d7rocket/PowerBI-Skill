---
name: pbi:docs
description: "Generate polished, stakeholder-ready project documentation with executive summary and data dictionary"
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

# /pbi-docs


## Instructions

### Step 0 — Check PBIP detection output

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run `/pbi-docs` from a directory containing a `*.SemanticModel/` folder.

**If PBIP_MODE=file:** proceed to Step 1. (Do NOT output anything yet — questions must be answered first.)

---

### Step 1 — Read all model files

**For TMDL (PBIP_FORMAT=tmdl):**

Read every `.tmdl` file path from the File Index using the Read tool.

Also read:
- `$PBIP_DIR/definition/relationships.tmdl` (if it exists)
- `$PBIP_DIR/definition/expressions.tmdl` (if it exists — contains M/Power Query source expressions)
- `$PBIP_DIR/definition/model.tmdl` (if it exists — contains model-level properties)

**For TMSL (PBIP_FORMAT=tmsl):**

Read `$PBIP_DIR/model.bim`. If >2000 lines, use offset/limit parameters to read in chunks.

**If PBIR=yes:** Read up to 10 PBIR JSON files to gather report page names and visual types.

---

### Step 2 — Extract metadata

From the model files, extract:

- **Tables:** name, description, dataCategory, column count, measure count
- **Measures:** name, expression (DAX), formatString, description, displayFolder
- **Columns:** name, dataType, isHidden, isCalculated (has expression)
- **Relationships:** fromTable, fromColumn, toTable, toColumn, crossFilteringBehavior, isActive
- **Expressions:** M/Power Query partition expressions (table name → source expression)
- **Report pages** (if PBIR): page name, visual count, visual types used

Classify each table:
- **Fact table:** table is on the many-side of at least one relationship, or has "Fact", "Sales", "Orders", "Transactions" in its name
- **Dimension table:** table is on the one-side of at least one relationship, or has "Dim", "Date", "Calendar", "Product", "Customer" in its name
- **Other:** tables that do not match either pattern (standalone, bridge, parameter tables)

---

### Step 3 — Ask before generating

**STOP. Ask TWO questions before generating or writing anything. These are REQUIRED regardless of PBI_CONFIRM — they are not confirm prompts, they are required inputs.**

**Question 1 — Detail level:**

```
How detailed should the document be?

  [1] Quick  — Overview, table summary, measure names only (no DAX)
  [2] Normal — Full structure, all measures with DAX, relationships, health notes
  [3] Full   — Everything: extended narrative, all columns, full DAX, data sources

Enter 1, 2, or 3:
```

Wait for reply. Save as DETAIL_LEVEL (quick / normal / full).

**Question 2 — Confirm write:**

```
Write documentation to .pbi/project-docs.md? (y/N)
```

Wait for reply. On n/N/Enter: output "Cancelled." and stop.

Only after both replies, proceed to Step 4.

---

### Step 4 — Generate documentation

Apply DETAIL_LEVEL rules:
- **Quick:** Include sections 1, 2 (table list only, no column details), 3 (measure names + descriptions only, no DAX), 7 (health). Omit DAX blocks, column tables, sections 4–6.
- **Normal:** Include all sections. Include DAX in `<details>` blocks. Include columns. Omit extended business narrative.
- **Full:** Include all sections. Full DAX, full column listings, extended business logic (3–5 paragraphs), data sources, report pages.

Write a polished, stakeholder-ready Markdown document. Use clear headings, tables, and formatting. Write in a professional but accessible tone. Adapt language to the model (e.g., if tables/measures use French names, write documentation in French).

Output format:

```
# [Project Name] — Power BI Documentation

> Auto-generated by `/pbi-docs` on [UTC date]. Source: `$PBIP_DIR` ([TMDL/TMSL])

---

## 1. Project Overview

[Brief description of what this model covers, inferred from table names, measure names, and business logic. 2–3 sentences. Be specific — reference the actual domain.]

| Metric | Value |
|--------|-------|
| Tables | [N] ([F] fact, [D] dimension, [O] other) |
| Measures | [N] ([with_desc] documented) |
| Columns | [N] ([calc] calculated, [hidden] hidden) |
| Relationships | [N] ([bidi] bidirectional) |
| Report pages | [N or "N/A"] |

---

## 2. Data Model

### Entity Relationship Diagram

[Text-based diagram using arrows to show relationships. Group fact tables in center, dimensions around them:]

    Date ─────┐
              │
    Product ──┤── Sales ──── Customer
              │
    Store ────┘

[Show cardinality: ──* for many-side, ──1 for one-side. Mark bidirectional with <──>.]

### Table Details

#### [TableName] _(Fact / Dimension / Other)_

[1–2 sentence description: inferred purpose from columns, measures, and relationships. Use the table's own description if set.]

**Columns:**

| Column | Type | Key | Hidden | Notes |
|--------|------|-----|--------|-------|
| [Name] | [dataType] | [PK/FK/—] | [Yes/—] | [e.g., "→ Product[ProductKey]" if FK] |

[Repeat for each table. Order: fact tables first, then dimensions, then other.]

---

## 3. Measures & KPIs

[Group by displayFolder. If no folders defined, group by source table.]

### [Display Folder Name or Table Name]

| Measure | Description | Format |
|---------|-------------|--------|
| [Name] | [description if exists, otherwise infer 1-sentence purpose from DAX] | [formatString or "—"] |

<details>
<summary>DAX — [MeasureName]</summary>

```dax
[full DAX expression, properly indented]
```

</details>

[Repeat <details> block for each measure in this group.]

[Repeat section for each display folder / table.]

---

## 4. Business Logic Summary

[In plain English, describe the model's purpose and logic. Cover:]
- What domain this model serves (sales, finance, HR, inventory, etc.)
- Key KPIs tracked and how they are calculated (reference actual measure names)
- Notable DAX patterns used (time intelligence, ratios, conditional logic, iterators)
- How fact and dimension tables work together to support the analysis
- Any calculation groups or field parameters detected

[3–5 paragraphs. Be specific — reference actual table and measure names throughout.]

---

## 5. Data Sources

[If M/Power Query expressions are available in expressions.tmdl or model.bim:]

| Table | Source Type | Connection |
|-------|------------|------------|
| [Name] | [SQL Server / CSV / Excel / SharePoint / API / etc.] | [inferred from M expression: server/database, file path, URL] |

[If no expressions available: "Source expressions not available in this project format."]

---

## 6. Report Pages

[Only include this section if PBIR=yes.]

| Page | Visuals | Key Visual Types |
|------|---------|-----------------|
| [PageName] | [N] | [bar chart, card, table, matrix, slicer, etc.] |

[If PBIR=no: omit this section entirely.]

---

## 7. Model Health Notes

[Brief summary of notable model characteristics. Check for:]
- Bidirectional relationships: [count, with table names if any]
- Undocumented measures: [count] / [total] without descriptions
- Missing format strings: [count] / [total]
- Unhidden key columns: [count] (columns used in relationships but not hidden)
- Isolated tables: [any tables with no relationships]

[If model is clean: "No significant health concerns detected. Model follows best practices."]

---

*Generated by `/pbi-docs` on [UTC timestamp]*
```

---

### Step 5 — Write output file

Write the generated document to `.pbi/project-docs.md` using the Write tool.

Output: `Documentation written to .pbi/project-docs.md ([DETAIL_LEVEL] detail)`

---

### Step 6 — Update .pbi/context.md

Use Read-then-Write to update `.pbi/context.md`:
1. Update `## Last Command`: Command = `/pbi-docs`, Outcome = `Documentation generated — [N] tables, [M] measures. Written to project-docs.md`
2. Append row to `## Command History`; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

### Anti-Patterns
- NEVER output raw file contents without structure — always format as polished documentation
- NEVER include implementation details (file paths, TMDL syntax, internal IDs) in the documentation — keep it stakeholder-friendly
- NEVER skip the Business Logic Summary (Section 4) — it is the most valuable section for non-technical readers
- NEVER generate documentation from cached context alone — always read the actual model files to ensure accuracy
- NEVER hardcode English — if the model uses French (or other language) names, write the documentation in that language
