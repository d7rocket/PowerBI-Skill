---
name: docs
description: "Client-ready project documentation (Markdown, Word, PDF)."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

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

**If PBIP_MODE=file:** proceed to Step 1. (Do NOT output anything yet — Step 4 asks questions first.)

---

### Step 1 — Read all model files

**For TMDL (PBIP_FORMAT=tmdl):**

Read every table `.tmdl` file listed in the model index (preflight block) using the Read tool. In live tier, the MCP Get and List operations are an equivalent source.

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

Hold this JSON in memory — do NOT write any files yet.

---

### Step 4 — Select detail level and output format(s)

**STOP. Ask TWO questions before generating anything. Do NOT write any files until both are answered. These two questions are required inputs.**

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

**Only after both replies:**

1. Write the JSON data (from Step 3) to `.pbi/doc_data.json` using the Write tool.
2. Then generate the selected format(s):

**Detail level rules — apply to PDF and Word only (Markdown always uses Full):**

| Level  | Sections included |
|:-------|:-----------------|
| Quick  | Title + overview (1 paragraph) + table summary table (name / type / measure count) + measure names by folder (no DAX) + key relationships (max 10) |
| Normal | All Quick sections + full measure table with DAX in fenced blocks + all relationships + health summary (1 paragraph) |
| Full   | All Normal sections + extended business logic narrative + full column listings per table + data sources + report pages + full health detail with finding list |

**Markdown** (choice 1 or 4 — always Full detail regardless of DETAIL_LEVEL):
- Generate a clean markdown document directly from the JSON data (do NOT re-read model files — the JSON has everything). Always include all sections using `##` H2 headings with the exact heading text below:
  - `# [project_name] — Power BI Documentation`
  - `> Generated by /pbi:docs on [date]. Source: $PBIP_DIR ([FORMAT])`
  - `## Overview` (use `overview` field)
  - `## Data Model` (use `erd` + table summary pipe table)
  - `## Measures & KPIs` (grouped by folder; wrap each DAX expression in ` ```dax ` fenced blocks; wrap M/Power Query expressions in ` ```m ` fenced blocks)
  - `## Business Logic` (use `business_logic` field — extended narrative)
  - `## Columns` (full per-table column listings as pipe tables)
  - `## Data Sources` (pipe table with table / type / connection columns)
  - `## Report Pages` (only if report_pages non-empty; pipe table)
  - `## Model Health` (full finding list)
- **Docgen contract reference:** the full output contract (headings, code blocks, tables) is defined in `${CLAUDE_PLUGIN_ROOT}/shared/pbi-docs-contract.md` — consult it when in doubt.
- **Code block rules (CRITICAL — required for docgen pipeline compatibility):**
  - DAX expressions: always use ` ```dax ` fenced blocks — NEVER plain indented text
  - M / Power Query expressions: always use ` ```m ` fenced blocks
  - SQL: use ` ```sql ` fenced blocks
  - Generic code: use plain ` ``` ` fenced blocks
  - NEVER use `CODE_BLOCK:` / `END_CODE_BLOCK` markers — these break the docgen pipeline
- **Table rules:** All tabular data (measure tables, column listings, relationship tables, source lists) MUST use standard pipe table format: `| Col A | Col B |` / `|-------|-------|` — NEVER use `TABLE:` / `END_TABLE` markers
- Write using the Write tool.
- Output: `Markdown written to .pbi/project-docs.md (Full detail)`

**PDF** (choice 2 or 4 — uses DETAIL_LEVEL):
- **Pre-validate dependencies** before attempting generation:
  Run: `python -c "from reportlab.lib.pagesizes import A4; print('PDF_DEPS=ok')" 2>&1`
  If output does NOT contain `PDF_DEPS=ok`: output `PDF export requires reportlab — run: pip install reportlab` and skip PDF generation. Do not attempt the generator script.
- Run: `python "${CLAUDE_PLUGIN_ROOT}/scripts/gen_pdf.py" ".pbi/doc_data.json" ".pbi/project-docs.pdf" "<DETAIL_LEVEL>" 2>&1`
- If output starts with `PDF_OK`: output `PDF written to .pbi/project-docs.pdf ([DETAIL_LEVEL] detail)`
- If output starts with `MISSING_DEP`: output `PDF export requires reportlab — run: pip install reportlab`
- On any other error: show the error output.

**Word** (choice 3 or 4 — uses DETAIL_LEVEL):
- **Pre-validate dependencies** before attempting generation:
  Run: `python -c "from docx import Document; from docx.shared import RGBColor, Pt; print('DOCX_DEPS=ok')" 2>&1`
  If output does NOT contain `DOCX_DEPS=ok`: output `Word export requires python-docx — run: pip install python-docx` and skip Word generation. Do not attempt the generator script.
- Run: `python "${CLAUDE_PLUGIN_ROOT}/scripts/gen_docx.py" ".pbi/doc_data.json" ".pbi/project-docs.docx" "<DETAIL_LEVEL>" 2>&1`
- If output starts with `DOCX_OK`: output `Word document written to .pbi/project-docs.docx ([DETAIL_LEVEL] detail)`
- If output starts with `MISSING_DEP`: output `Word export requires python-docx — run: pip install python-docx`
- On any other error: show the error output.

**After all format attempts (success OR failure):**
- Delete `.pbi/doc_data.json` (cleanup — always run regardless of individual format success/failure):
  `python -c "import os; os.remove('.pbi/doc_data.json')" 2>/dev/null`

---

### Step 5 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:docs" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER output raw file contents without structure — always format as polished documentation
- NEVER include implementation details (file paths, TMDL syntax, internal IDs) in the documentation — keep it stakeholder-friendly
- NEVER skip the Business Logic Summary (`## Business Logic`) — it is the most valuable section for non-technical readers
- NEVER generate documentation from cached context alone — always read the actual model files to ensure accuracy
- NEVER hardcode English — if the model uses French (or other language) names, write the documentation in that language. Default to French for client-facing content unless the model language is clearly English.
- NEVER use `CODE_BLOCK:` / `END_CODE_BLOCK` or `TABLE:` / `END_TABLE` markers — use standard fenced code blocks and pipe tables only (docgen pipeline requirement)
- NEVER attempt Word or PDF generation without pre-validating dependencies first — missing imports (RGBColor, python-docx, reportlab) waste long generation runs that fail near the end
- NEVER write DAX or M expressions as plain indented text — always use fenced code blocks with the correct language tag (`dax`, `m`, `sql`)
