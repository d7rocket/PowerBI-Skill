---
name: explain
description: "Deconstruct any DAX measure into a structured plain-English breakdown covering business logic, filter context propagation, row context scope, context transitions, and performance implications. Adapts depth to measure complexity (Simple/Intermediate/Advanced). Works with pasted DAX or reads from PBIP model files."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:explain

<purpose>
Turn opaque DAX into clear, actionable understanding. Analysts need to know WHAT a measure does, WHY it behaves the way it does in visuals, and WHERE performance bottlenecks hide — without reading DAX syntax.
</purpose>

<core_principle>
Explain intent and behavior, not syntax. The output should help someone who has never seen this measure understand its business purpose, its interaction with filter context, and any hidden complexity.
</core_principle>

## Instructions

### Step 1 - Get the measure

- `$ARGUMENTS` contains DAX: use it.
- `$ARGUMENTS` names a measure and `PBIP_MODE=file`: fetch it with `detect.py measure "<name>"` (in live tier, get it from the live model). Several matches: ask which table.
- Otherwise ask `Paste your DAX measure, or name one from the model:` and wait.
- If what comes back has no DAX in it, say `Please paste a DAX measure to explain.` and stop.

---

### Step 2 — Measure Extraction

Once the analyst pastes the measure:

- **Extract the measure name:** everything before the first `=` sign, trimmed of whitespace.
- **If no `=` is found** in the pasted content, use placeholder name `[Measure]` and add at the very top of your output: "Note: No measure name detected — treating entire input as the expression."
- **If `$ARGUMENTS` contains `--table TableName`**, record TableName and include it as a context note in the output (e.g., "Note: Table context provided — `TableName`").

---

### Step 3 — Prior Failure Check

Before generating any output, check the preflight block for the extracted measure name in the **"## Analyst-Reported Failures"** section.

- If the measure name is found in that section, output at the very top (before the Complexity tag):
  > Previous attempt at this measure used [approach X] and failed. Using [approach Y] instead.

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
[Describe what filters are active when this measure evaluates. Include: filters from CALCULATE arguments, filters inherited from visuals/slicers (visuals and slicers contribute filter context — they never create row context), ALL/ALLEXCEPT overrides if present. If no explicit filter manipulation is present, state what context the measure inherits from the report visual.]

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

### Step 5b - Ground it in the model

In a project, name the real tables and relationships the measure depends on, using the model index.
If the measure references another measure, fetch that one too and explain the pair together.
In live tier, when the analyst asks why a value looks wrong, run the measure with `EVALUATE ROW` (or grouped by the column in question) and explain the actual result.

### Step 6 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:explain" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER restate DAX syntax in plain English — explain business logic and intent
- NEVER skip complexity inference — always classify before explaining
- NEVER reference tables, columns or measures that are not in the model index when a project is loaded
- NEVER modify or rewrite the measure — explain only
