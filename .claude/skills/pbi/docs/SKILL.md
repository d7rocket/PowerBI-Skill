---
name: pbi:docs
description: "Generate polished, stakeholder-ready project documentation combining model metadata, measure catalog, relationship diagram, data dictionary, and usage guidelines. Formatted for direct sharing — no technical jargon, clear section headers, executive summary."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.1.0
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

### Step 3 — Build structured document data

Construct the following JSON object in memory from everything extracted in Steps 1–2. This is the data contract the generator scripts read.

```
{
  "meta": {
    "project_name": "<infer from $PBIP_DIR — strip .SemanticModel suffix>",
    "pbip_dir": "<PBIP_DIR value>",
    "format": "<tmdl|tmsl>",
    "generated_at": "<current UTC time in ISO 8601>",
    "language": "<en|fr — match model language>"
  },
  "summary": {
    "table_count": <N>,
    "fact_count": <N>,
    "dimension_count": <N>,
    "other_count": <N>,
    "measure_count": <N>,
    "documented_measures": <N — count with non-empty description>,
    "column_count": <N>,
    "calc_columns": <N>,
    "hidden_columns": <N>,
    "relationship_count": <N>,
    "bidi_count": <N>,
    "report_pages": <N or 0>
  },
  "overview": "<3-paragraph plain-language description of what this model does. Reference actual table/measure names. If French model, write in French.>",
  "erd": "<text-based ERD using ASCII arrows. Fact tables centre, dimensions around them. Example:\n  Date ────┐\n           ├──── Sales ──── Customer\n  Product ─┘\n  Cardinality: ──* many-side, 1── one-side. Bidi: <──>. >",
  "tables": [
    {
      "name": "<table name>",
      "type": "<fact|dimension|other>",
      "description": "<1-2 sentence inferred purpose>",
      "columns": [
        {
          "name": "<col name>",
          "data_type": "<dataType>",
          "is_key": <true|false>,
          "is_hidden": <true|false>,
          "notes": "<e.g. → Product[ProductKey] if FK, or empty>"
        }
      ],
      "measures": [
        {
          "name": "<measure name>",
          "expression": "<full DAX, properly indented per SQLBI conventions>",
          "description": "<existing description or empty>",
          "format": "<formatString or empty>",
          "folder": "<displayFolder or empty>"
        }
      ]
    }
  ],
  "relationships": [
    {
      "from_table": "<>",
      "from_column": "<>",
      "to_table": "<>",
      "to_column": "<>",
      "cardinality": "<many-to-one|one-to-one|...>",
      "bidi": <true|false>,
      "active": <true|false>
    }
  ],
  "data_sources": [
    {
      "table": "<table name>",
      "type": "<SQL Server|CSV|Excel|SharePoint|DirectQuery|...>",
      "connection": "<inferred from M expression: server/db, file path, or URL>"
    }
  ],
  "business_logic": "<4-5 paragraph narrative: domain, key KPIs, DAX patterns, how tables work together. Reference actual names. Write in model language.>",
  "health": {
    "bidi_relationships": ["<table1 <──> table2>", ...],
    "undocumented_count": <N>,
    "missing_format_count": <N>,
    "unhidden_keys": ["<Table[Column]>", ...],
    "isolated_tables": ["<TableName>", ...],
    "summary": "<one sentence health summary>"
  },
  "report_pages": [
    {
      "name": "<page name>",
      "visual_count": <N>,
      "visual_types": ["bar chart", "card", ...]
    }
  ]
}
```

Write this JSON to `.pbi/doc_data.json` using the Write tool.

---

### Step 4 — Select detail level and output format(s)

**STOP. Ask TWO questions before generating anything. Do NOT write any files until both are answered.**

**Question 1 — Detail level:**

```
How detailed should the document be?

  [1] Quick       — Executive summary, table overview, measure names only (no DAX)
  [2] Normal      — Full structure, all measures with DAX, relationships, health summary
  [3] Full        — Everything: extended business narrative, all columns, full DAX,
                    data sources, health detail, report pages

Note: the Markdown file (.pbi/project-docs.md) always receives Full detail
regardless of this choice — it is the complete reference copy.

Enter 1, 2, or 3:
```

Wait for the user's reply. Save the chosen level as DETAIL_LEVEL (quick / normal / full).

---

**Question 2 — Output format(s):**

```
Select output format(s):

  [1] Markdown  — .pbi/project-docs.md   (no dependencies)
  [2] PDF       — .pbi/project-docs.pdf  (requires: pip install reportlab)
  [3] Word      — .pbi/project-docs.docx (requires: pip install python-docx)
  [4] All 3

Enter number(s), e.g. 1 or 1,3 or 4:
```

Wait for the user's reply. **Do not write any files until both questions are answered.**

---

**Only after both replies, generate the selected format(s):**

**Detail level rules — apply to PDF and Word only (Markdown always uses Full):**

| Level  | Sections included |
|:-------|:-----------------|
| Quick  | Title + overview (1 paragraph) + table summary table (name / type / measure count) + measure names by folder (no DAX) + key relationships (max 10) |
| Normal | All Quick sections + full measure table with DAX in fenced blocks + all relationships + health summary (1 paragraph) |
| Full   | All Normal sections + extended business logic narrative + full column listings per table + data sources + report pages + full health detail with finding list |

**Markdown** (choice 1 or 4 — always Full detail regardless of DETAIL_LEVEL):
- If PBI_CONFIRM=true: ask "Write to .pbi/project-docs.md? (y/N)". On n/N/Enter: output "Write cancelled." and stop.
- Generate a clean markdown document directly from the JSON data (do NOT re-read model files — the JSON has everything). Always include all sections:
  - `# [project_name] — Power BI Documentation`
  - `> Generated by /pbi:docs on [date]. Source: $PBIP_DIR ([FORMAT])`
  - Section 1: Project Overview (use `overview` field)
  - Section 2: Data Model (use `erd` + table summary table)
  - Section 3: Measures & KPIs (grouped by folder, with full DAX in fenced blocks)
  - Section 4: Business Logic (use `business_logic` field — extended narrative)
  - Section 5: Columns (full per-table column listings)
  - Section 6: Data Sources
  - Section 7: Report Pages (only if report_pages non-empty)
  - Section 8: Model Health (full finding list)
- Write using the Write tool.
- Output: `Markdown written to .pbi/project-docs.md (Full detail)`

**PDF** (choice 2 or 4 — uses DETAIL_LEVEL):
- Run: `python ".claude/skills/pbi/scripts/gen_pdf.py" ".pbi/doc_data.json" ".pbi/project-docs.pdf" "<DETAIL_LEVEL>" 2>&1`
- If output starts with `PDF_OK`: output `PDF written to .pbi/project-docs.pdf ([DETAIL_LEVEL] detail)`
- If output starts with `MISSING_DEP`: output `PDF export requires reportlab — run: pip install reportlab`
- On any other error: show the error output.

**Word** (choice 3 or 4 — uses DETAIL_LEVEL):
- Run: `python ".claude/skills/pbi/scripts/gen_docx.py" ".pbi/doc_data.json" ".pbi/project-docs.docx" "<DETAIL_LEVEL>" 2>&1`
- If output starts with `DOCX_OK`: output `Word document written to .pbi/project-docs.docx ([DETAIL_LEVEL] detail)`
- If output starts with `MISSING_DEP`: output `Word export requires python-docx — run: pip install python-docx`
- On any other error: show the error output.

**After all selected formats are generated:**
- Delete `.pbi/doc_data.json` (cleanup): `python -c "import os; os.remove('.pbi/doc_data.json')" 2>/dev/null`

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
