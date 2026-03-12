---
name: pbi-explain
description: Explain a DAX measure in plain English with filter context, row context, and context transition analysis. Use when an analyst asks to explain, understand, or break down a DAX measure or formula.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write
---

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

## Instructions

### Step 1 — Initial Response

Respond to the analyst with exactly:

> Paste your DAX measure below:

Wait for the analyst to paste a DAX measure before proceeding.

---

### Step 2 — Measure Extraction

Once the analyst pastes the measure:

- **Extract the measure name:** everything before the first `=` sign, trimmed of whitespace.
- **If no `=` is found** in the pasted content, use placeholder name `[Measure]` and add at the very top of your output: "Note: No measure name detected — treating entire input as the expression."
- **If `$ARGUMENTS` contains `--table TableName`**, record TableName and include it as a context note in the output (e.g., "Note: Table context provided — `TableName`").

---

### Step 3 — Prior Failure Check

Before generating any output, scan the Session Context above for the extracted measure name in the **"## Analyst-Reported Failures"** section.

- If the measure name is found in that section, output at the very top (before the Complexity tag):
  > ⚠️ Previous attempt at this measure used [approach X] and failed. Using [approach Y] instead.

---

### Step 4 — Complexity Inference

Classify the measure into one of three levels based on its patterns:

**Simple** (use plain language, minimise jargon):
- Measure body contains only: `SUM`, `COUNT`, `AVERAGE`, `MIN`, `MAX`, `DIVIDE`, `IF`, `BLANK`
- Single `CALCULATE` with one filter argument
- No iterator functions (`SUMX`, `AVERAGEX`, `COUNTX`, `MAXX`, `MINX`, `RANKX`, `TOPN`, etc.)
- No time intelligence functions (`DATESYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`, `TOTALYTD`, etc.)

**Intermediate** (explain concepts with brief parentheticals):
- `CALCULATE` with multiple filter arguments
- Single `SUMX` or `AVERAGEX` over a physical table column (no measure references inside the iterator)
- Time intelligence functions (`DATESYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`, `TOTALYTD`, etc.)
- `FILTER` used as a `CALCULATE` argument
- `RELATED` or `RELATEDTABLE`

**Advanced** (full technical depth, name patterns explicitly):
- Iterators (`SUMX`, `AVERAGEX`, etc.) over measure references — context transition present
- `EARLIER`
- `ALLEXCEPT`, `ALLSELECTED`, or `REMOVEFILTERS` with multiple columns
- Nested iterators
- `RANKX` or `TOPN` with complex expressions
- `VAR`/`RETURN` blocks that contain iterators

---

### Step 5 — Output Structure

Produce the following labelled sections in this exact order:

```
_Complexity: [Simple | Intermediate | Advanced]_

**[Measure Name]**

[One paragraph plain-English summary of what the measure calculates. For Simple measures, avoid DAX jargon entirely. For Advanced measures, name the patterns explicitly and explain the implications.]

### Filter Context
[Describe what filters are active when this measure evaluates. Include: filters from CALCULATE arguments, filters inherited from visuals/slicers (row context only relevant when called from a visual), ALL/ALLEXCEPT overrides if present. If no explicit filter manipulation is present, state what context the measure inherits from the report visual.]

### Row Context
[State whether row context is present. Row context exists inside iterator functions (SUMX, AVERAGEX, etc.) and inside calculated columns. If the measure uses an iterator, describe which table provides the row context and what columns are accessible per row. If no iterator is present and this is not a calculated column, state that no row context is active.]

### Context Transitions
[If CALCULATE is present or an iterator calls a measure reference, explain the context transition. For Simple measures with no iterator/measure-ref, write: "No context transition — this measure evaluates in filter context only." For Advanced measures with iterator-over-measure-ref, write: "Context transition present: [MeasureName] is called inside [Iterator], which converts the row context to filter context via an implicit CALCULATE."]

### Performance Notes
[Brief note on any performance implications. If no concern, write: "No performance concerns for this pattern." For slow patterns (FILTER on entire table, nested iterators, RANKX over large tables), name the concern and note that /pbi:optimise can suggest improvements.]

---
**Next steps:** `/pbi:format` · `/pbi:optimise` · `/pbi:comment` · `/pbi:error`
```

---

### Step 6 — Update Session Context

After producing the output, update `.pbi-context.md` using the following steps:

1. Use the **Read** tool to read the current contents of `.pbi-context.md`.
2. Modify the file in memory:
   - **"## Last Command" section:** Set all four fields:
     - `Command: /pbi:explain`
     - `Timestamp: [current ISO 8601 timestamp, e.g. 2026-03-12T10:30:00Z]`
     - `Measure: [extracted measure name]`
     - `Outcome: Success — [one-line summary of what was explained, e.g. "Year-to-date revenue using DATESYTD"]`
   - **"## Command History" table:** Prepend a new row at the top of the table body:
     `| [timestamp] | /pbi:explain | [measure name] | Success |`
   - **Keep Command History to the last 20 rows** — if the table has more than 20 data rows after adding the new one, drop the oldest rows until exactly 20 remain.
   - **Do NOT modify the "## Analyst-Reported Failures" section** — the analyst manages that section manually.
3. Use the **Write** tool to write the full updated file back to `.pbi-context.md`.

Do NOT use bash append commands — always Read then Write to avoid malformed state.
