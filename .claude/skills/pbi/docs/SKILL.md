---
name: pbi:docs
description: "Generate polished, stakeholder-ready project documentation combining model metadata, measure catalog, relationship diagram, data dictionary, and usage guidelines. Formatted for direct sharing — no technical jargon, clear section headers, executive summary."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.0.0
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

# /pbi:docs

<purpose>
Stakeholders need to understand the model without opening Power BI Desktop. This command produces documentation that answers "what does this model do?" for anyone in the organization.
</purpose>

<core_principle>
Write for business stakeholders, not developers. Every section should be understandable by someone who has never opened Power BI Desktop. Include an executive summary. Organize by business domain, not by table structure.
</core_principle>

## Instructions

### Step 0 — Check PBIP detection output

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run `/pbi:docs` from a directory containing a `*.SemanticModel/` folder.

**If PBIP_MODE=file:** output:

```
Generating project documentation...
```

Then proceed to Step 1.

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

### Step 3 — Generate documentation

Write a polished, stakeholder-ready Markdown document. Use clear headings, tables, and formatting. Write in a professional but accessible tone. Adapt language to the model (e.g., if tables/measures use French names, write documentation in French).

Output format:

```
# [Project Name] — Power BI Documentation

> Auto-generated by `/pbi:docs` on [UTC date]. Source: `$PBIP_DIR` ([TMDL/TMSL])

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

*Generated by `/pbi:docs` on [UTC timestamp]*
```

---

### Step 4 — Write output file

**Confirm check:** If PBI_CONFIRM=true, ask "Write documentation to .pbi/project-docs.md? (y/N)" before writing. On n/N/Enter: "Write cancelled." Skip file write. On y/Y: proceed. If PBI_CONFIRM=false: proceed directly to write (current behavior).

Write the generated document to `.pbi/project-docs.md` in the project root using the Write tool.

Output: `Documentation written to .pbi/project-docs.md`

---

### Step 5 — Update .pbi/context.md

Use Read-then-Write to update `.pbi/context.md`:
1. Update `## Last Command`: Command = `/pbi:docs`, Outcome = `Documentation generated — [N] tables, [M] measures. Written to .pbi/project-docs.md`
2. Append row to `## Command History`; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

### Anti-Patterns
- NEVER output raw file contents without structure — always format as polished documentation
- NEVER include implementation details (file paths, TMDL syntax, internal IDs) in the documentation — keep it stakeholder-friendly
- NEVER skip the Business Logic Summary (Section 4) — it is the most valuable section for non-technical readers
- NEVER generate documentation from cached context alone — always read the actual model files to ensure accuracy
- NEVER hardcode English — if the model uses French (or other language) names, write the documentation in that language

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
