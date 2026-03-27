---
name: pbi:extract
description: "Export a structured summary of your PBIP project (overview, standard, or deep-dive tiers). Use when user says 'extract', 'project summary', 'model summary', or 'export model'."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 4.4.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection (run once)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report`. Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

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

### Auto-Resume

After detection blocks run, apply the following before executing the command:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - Skip any "Model Context Check" (Step 0.5) below — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.


---

# /pbi:extract


## Instructions

### Step 0 — Check PBIP detection output

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found in this directory. Run `/pbi:extract` from a directory containing a `*.SemanticModel/` folder.

**If PBIP_MODE=file:** proceed to Step 1.

---

### Step 1 — Determine extraction tier

Parse `$ARGUMENTS` (after the `extract` keyword) for a tier keyword:

| Keyword | Tier | Model | Token Profile |
|---------|------|-------|---------------|
| `overview`, `quick`, `brief`, `lite` | Overview | Haiku | ~500–1,500 tokens output |
| `standard`, `normal`, `default` | Standard | Sonnet | ~2,000–5,000 tokens output |
| `deep-dive`, `deep`, `full`, `comprehensive` | Deep Dive | Opus | ~5,000–15,000+ tokens output |
| (no keyword / empty) | — | — | Prompt user to choose |

**If no tier keyword is provided**, output the tier picker:

```
Which extraction depth?

**A — Overview** (Haiku)
  Table/measure/relationship counts. Fast, low token usage.
  Best for: quick orientation, sharing a snapshot in chat.

**B — Standard** (Sonnet)
  Full schema: table structures, measure DAX, column types, relationships.
  Best for: onboarding a colleague, documentation, PR descriptions.

**C — Deep Dive** (Opus)
  Everything above + DAX pattern analysis, dependency graph, data-type audit,
  optimisation hints, and business-logic commentary.
  Best for: architecture reviews, handoffs, pre-audit deep dives.
  ⚠ High token usage — expect 5,000–15,000+ output tokens.

Type A, B, or C.
```

Wait for response:
- "A" or "a" → Overview tier
- "B" or "b" → Standard tier
- "C" or "c" → Deep Dive tier
- Anything else → Re-output the tier picker. After 3 invalid responses, default to Standard tier and output: "Defaulting to Standard tier."

---

### Step 2 — Read model files

**For TMDL (PBIP_FORMAT=tmdl):**

Read every `.tmdl` file path from the File Index using the Read tool.

Also read `$PBIP_DIR/definition/relationships.tmdl` (if it exists).

Also read `$PBIP_DIR/definition/expressions.tmdl` (if it exists — contains M/Power Query expressions).

Also read `$PBIP_DIR/definition/model.tmdl` (if it exists — contains model-level properties).

**For TMSL (PBIP_FORMAT=tmsl):**

Read `$PBIP_DIR/model.bim`. If >2000 lines, use offset/limit parameters to read in chunks.

---

### Step 3 — Extract metadata

From the model files, extract into an internal structure:

- **Tables:** name, dataCategory, description
- **Measures:** name, expression (DAX), formatString, description, displayFolder
- **Columns:** name, dataType, isHidden, expression (calculated columns only)
- **Relationships:** fromTable, fromColumn, toTable, toColumn, crossFilteringBehavior, isActive
- **Roles:** security roles if defined
- **Expressions:** M/Power Query partition expressions (source queries)

Count:
- Total tables, measures, columns, relationships
- Calculated columns vs data columns
- Measures with descriptions vs without
- Measures with formatString vs without

---

### Step 4 — Generate output by tier

---

#### Tier: Overview

**Execution model:** Spawn a **haiku Agent** with the following prompt: "Generate a Project Extract — Overview report. Here is the extracted metadata: [pass the full metadata counts, table names, measure names by table, and relationship list]. Format the output exactly as specified below."

Output format:

```
# Project Extract — Overview
**Project:** $PBIP_DIR | **Format:** [TMDL/TMSL] | **Generated:** [UTC timestamp]

## Overview
- **Tables:** [N] ([list names, comma-separated])
- **Measures:** [N] across [M] tables
- **Columns:** [N] ([C] calculated)
- **Relationships:** [N] ([B] bidirectional ⚠ if any)

## Measures by Table
| Table | Measures |
|-------|----------|
| [TableName] | [measure1, measure2, ...] |
| [TableName] | (none) |

## Relationships
[FromTable].[FromColumn] → [ToTable].[ToColumn] (many-to-one)
[... one line per relationship]

---
*Extracted with /pbi:extract overview (Haiku)*
```

---

#### Tier: Standard

**Execution model:** Run directly in current context (Sonnet).

Output format:

```
# Project Extract — Standard
**Project:** $PBIP_DIR | **Format:** [TMDL/TMSL] | **Generated:** [UTC timestamp]

## Model Statistics
| Metric | Count |
|--------|-------|
| Tables | [N] |
| Measures | [N] ([D] documented, [U] undocumented) |
| Columns | [N] ([C] calculated, [H] hidden) |
| Relationships | [N] ([B] bidirectional ⚠) |

## Tables

### [TableName]
**Description:** [description or "(none)"]
**Data Category:** [dataCategory or "Regular"]

**Columns:**
| Column | Type | Hidden | Calculated |
|--------|------|--------|------------|
| [Name] | [dataType] | [Yes/No] | [Yes/No] |

**Measures:**
| Measure | Folder | Format | Documented |
|---------|--------|--------|------------|
| [Name] | [displayFolder or "—"] | [formatString or "—"] | [Yes/No] |

<details>
<summary>DAX — [MeasureName]</summary>

```dax
[full DAX expression]
```

</details>

[repeat <details> block for each measure in this table]

[repeat ### TableName section for each table]

## Relationships
| From | To | Direction | Active |
|------|----|-----------|--------|
| [Table].[Column] | [Table].[Column] | [Single/Both ⚠] | [Yes/No] |

## Documentation Coverage
- **Measures with descriptions:** [D]/[N] ([%])
- **Measures with format strings:** [F]/[N] ([%])
- **Measures with display folders:** [P]/[N] ([%])
- **Key columns hidden:** [H]/[K] ([%])

---
*Extracted with /pbi:extract standard (Sonnet)*
```

---

#### Tier: Deep Dive

**Execution model:** Run directly in current context (Sonnet reads files, then spawns an **opus Agent** for analysis).

The Sonnet context performs Steps 2–3 (file reading and metadata extraction), then spawns an **opus Agent** with the following prompt: "Produce a Deep Dive project extraction report. Here is the full extracted metadata: [pass all tables, columns, measures with full DAX expressions, relationships, roles, expressions]. Analyze the model and generate the report exactly as specified below." The opus Agent instructions:

**Opus Agent instructions:**
Produce the full Deep Dive report including all Standard tier content PLUS:

```
# Project Extract — Deep Dive
**Project:** $PBIP_DIR | **Format:** [TMDL/TMSL] | **Generated:** [UTC timestamp]
⚠ Deep Dive extraction — high token output

[... all Standard tier sections ...]

## DAX Pattern Analysis

### Measure Complexity
| Measure | Estimated Complexity | Key Functions | Nested Depth |
|---------|---------------------|---------------|--------------|
| [Name] | [Simple/Medium/Complex/Advanced] | [CALCULATE, FILTER, etc.] | [N] |

Complexity rules (with examples):
- **Simple:** Single function or arithmetic — e.g., `SUM([Amount])`, `COUNTROWS(Sales)`, `DIVIDE([Revenue], [Cost])`
- **Medium:** CALCULATE with 1–2 filters, basic time intelligence — e.g., `CALCULATE(SUM([Amount]), DATEADD(Date[Date], -1, YEAR))`
- **Complex:** Nested CALCULATE, variables (VAR/RETURN), iterator functions — e.g., `VAR _total = SUMX(Sales, Sales[Qty] * Sales[Price]) RETURN DIVIDE(_total, [Target])`
- **Advanced:** Dynamic filters, SELECTEDVALUE branching, virtual tables — e.g., `CALCULATE([Revenue], FILTER(ALL(Product), Product[Category] = SELECTEDVALUE(Slicer[Category])))`

### Common Patterns Detected
[List DAX patterns found across measures:]
- **Time intelligence:** [measures using DATEADD, SAMEPERIODLASTYEAR, DATESYTD, etc.]
- **Ratio/percentage:** [measures using DIVIDE or division with ALL/ALLSELECTED]
- **Conditional logic:** [measures using SWITCH, IF with multiple branches]
- **Iterator aggregation:** [measures using SUMX, AVERAGEX, MAXX, etc.]
- **Semi-additive:** [measures using LASTNONBLANK, LASTDATE, etc.]

### Measure Dependency Graph
[For each measure that references other measures:]
- [MeasureName] → depends on: [Measure1], [Measure2]
- [MeasureName] → depends on: [Measure3]
[Orphan measures (not referenced by any other measure): list them]
[Root measures (referenced by others but depend on none): list them]

## Data Type Audit
| Column | Current Type | Suggested Type | Reason |
|--------|-------------|----------------|--------|
[Only list columns where the data type looks suspect based on naming conventions:]
- Column named "Date" or "DateTime" but not dateTime type
- Column named "Amount", "Price", "Cost" but not decimal/double type
- Column named "ID", "Key" but not int64/string type
[If no suspects: "All column data types appear consistent with naming conventions."]

## Optimisation Hints
[Based on the full model analysis, list actionable suggestions:]
- **Bidirectional relationships:** [list any, with recommendation]
- **Missing format strings:** [count and example measures]
- **Undocumented measures:** [count and suggestion]
- **Complex measures without variables:** [measures that could benefit from VAR/RETURN]
- **Redundant CALCULATE wrappers:** [measures wrapping a single aggregation in CALCULATE unnecessarily]
- **Missing display folders:** [count, with organisation suggestion]
[If model is clean: "No significant optimisation opportunities detected."]

## Business Logic Summary
[In plain English, describe what this model appears to do based on:]
- Table names and relationships (what domain — sales, finance, HR, etc.)
- Measure names and DAX patterns (what KPIs are tracked)
- Display folder organisation (how the business thinks about metrics)
[2–4 paragraphs. Be specific — reference actual table and measure names.]

---
*Extracted with /pbi:extract deep-dive (Opus)*
*⚠ This extraction used approximately [estimate] output tokens*
```

---

### Step 5 — Write output file

Write the generated report to `project-extract.md` in the project root using the Write tool.

Output: `Extract written to project-extract.md`

---

### Step 6 — Update .pbi-context.md

Use Read-then-Write to update `.pbi-context.md`:
1. Update `## Last Command`: Command = `/pbi:extract [tier]`, Outcome = `Extract complete — [tier] tier, [N] tables, [M] measures. Written to project-extract.md`
2. Append row to `## Command History`; trim to 20 rows max
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

### Anti-Patterns
- NEVER output raw file contents — always structure the output by tier
- NEVER exceed tier boundaries (overview stays high-level, standard adds detail, deep-dive is comprehensive)
- NEVER advance past the tier picker without a valid selection
- NEVER run the Opus agent for non-deep-dive tiers

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.


## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
