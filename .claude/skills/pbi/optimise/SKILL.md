---
name: pbi:optimise
description: "Run a 13-rule performance scan on any DAX measure, identifying anti-patterns like unnecessary iterators, FILTER on full tables, nested CALCULATE chains, and missing variable extraction. Produces a severity-graded report with before/after diffs. Works with pasted DAX and PBIP-embedded measures."
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

# /pbi:optimise

<purpose>
Slow measures degrade the entire report experience. This command catches the patterns that cause 90% of DAX performance problems — before they reach production.
</purpose>

<core_principle>
Suggest only changes with measurable performance impact. Never recommend changes that sacrifice readability for marginal gains. Always show before/after diffs so the analyst can judge the trade-off.
</core_principle>

## Instructions

Respond with: "Paste your DAX measure below:"

Wait for the analyst to paste a DAX measure, then follow these steps in order.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text, output: "Please paste a DAX measure to optimise." and stop.

---

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table and related table context. Proceed to Step 1. Use this context when generating rationale for any rewrites.
- If `## Model Context` is absent or empty:
  - Ask: "Which table does this measure belong to, and are there any related tables involved?"
  - Wait for the analyst's answer.
  - Read `.pbi/context.md` with Read tool. Add `## Model Context` section with the answer. Write back with Write tool.
  - Proceed to Step 1 using the noted context.

---

### Step 1 — Measure Extraction

Extract the measure name from text before the first `=`, trimmed of whitespace.

- If no `=` is found, use `[Measure]` as the placeholder name and note: "Could not detect measure name — no `=` found. Showing analysis with placeholder name."
- If `$ARGUMENTS` contains `--table TableName`, record TableName. Include a table context note at the top of your output: "Table context: TableName"

---

### Step 2 — Prior Failure Check

Scan the Session Context for the extracted measure name in the **Analyst-Reported Failures** section.

If found, prepend this flag to your output before any analysis:
"Previous attempt at this measure used [approach recorded] and failed. Applying alternative approach."

---

### Step 3 — CRITICAL GUARD: Iterator-Over-Measure-Reference Detection (context transition guard)

**Perform this check BEFORE applying any optimisation rules.**

Detect any of these iterator functions: SUMX, AVERAGEX, MINX, MAXX, COUNTX, RANKX

Specifically look for cases where the **expression argument** (second argument) is a measure reference — identified as text in square brackets `[MeasureName]` that is NOT preceded by a table name or column syntax (i.e., NOT in the form `Table[Column]`).

**If iterator-over-measure-reference is detected:**

Add this flag to the **Flags** section of your output (do NOT rewrite the flagged iterator):

"Context transition present in [MeasureName]: This measure calls `[ReferencedMeasure]` inside `[Iterator]`, which triggers an implicit CALCULATE, converting row context to filter context. Rewriting iterators over measure references requires verifying the measure behaves correctly under row-context-to-filter-context conversion. Manual verification required before changing this pattern."

Continue analysing the rest of the measure for other optimisable patterns. Apply Rules 1, 2, 3, and 5 to portions of the measure that do NOT involve the guarded iterator-over-measure-reference pattern.

---

### Step 4 — Optimisation Rules

Apply these rules in order. Track each change made.

---

**Rule 1 — FILTER on Entire Table**

DETECT: `FILTER(TableName, condition)` used as a CALCULATE argument where the condition tests a single column.

REWRITE: Replace the FILTER with a direct column filter argument:
```dax
CALCULATE([Measure], Sales[Region] = "North")
```

RATIONALE (brief for simple, full paragraph for complex):
- Simple case: "Column filter uses xmatch internally and avoids a full table scan row-by-row. This is more storage-engine-friendly and typically 10-100x faster on large tables."
- Complex case: Provide a full paragraph explaining the storage engine vs formula engine distinction, xmatch mechanics, and the specific performance implication for the measure's table size and filter cardinality.

---

**Rule 2 — SUMX Over Single Column With No Expression Complexity**

DETECT: `SUMX(TableName, TableName[Column])` where the second argument is a direct column reference with no formula or expression.

REWRITE:
```dax
SUM(Sales[Amount])
```

RATIONALE: "SUM is a native aggregation handled entirely in the storage engine. SUMX iterates row-by-row in the formula engine unnecessarily when summing a single column. Use SUM for direct column aggregation."

---

**Rule 3 — Redundant CALCULATE Wrapper**

DETECT: `CALCULATE([SimpleMeasure])` with no filter arguments — a CALCULATE call wrapping only a measure reference with nothing else.

REWRITE:
```dax
[Total Sales]
```

RATIONALE: "CALCULATE with no filter arguments adds formula engine overhead with no benefit. The measure reference alone evaluates identically in the current filter context."

---

**Rule 4 — Iterator Over Measure Reference**

DO NOT REWRITE. Handled by the CRITICAL GUARD in Step 3. See Flags section.

---

**Rule 5 — Nested Iterators**

DETECT: An iterator function (SUMX, AVERAGEX, MINX, MAXX, COUNTX, RANKX) directly containing another iterator function as its expression argument.

FLAG with this explanation in the **Flags** section:
"Nested iterators create a Cartesian product: every row in the outer table iterates every row in the inner table. This can be extremely slow on large tables. Review whether the inner iteration is necessary or can be collapsed."

REWRITE ONLY IF: The inner iteration is trivially collapsible — meaning the inner expression is a plain column reference with no formula. If the inner expression contains a formula or depends on both tables, flag only and do not rewrite.

---

**Rule 6 — Unnecessary SWITCH(TRUE())**

DETECT: `SWITCH(TRUE(), condition1, result1, condition2, result2, ...)` where conditions are simple equality tests against the same column.

REWRITE:
```dax
SWITCH(Table[Col], "A", result1, "B", result2, default)
```

RATIONALE: "SWITCH with a value argument evaluates the expression once and matches. SWITCH(TRUE()) evaluates every condition sequentially even after a match is found in some engines. Use the value form when all conditions test the same expression."

---

**Rule 7 — Verbose HASONEVALUE + VALUES Pattern**

DETECT: `IF(HASONEVALUE(Table[Col]), VALUES(Table[Col]), fallback)`

REWRITE:
```dax
SELECTEDVALUE(Table[Col], fallback)
```

RATIONALE: "SELECTEDVALUE is a purpose-built function that replaces the HASONEVALUE + VALUES two-step pattern. Functionally identical, but clearer intent and marginally faster."

---

**Rule 8 — DIVIDE With Explicit Zero**

DETECT: `DIVIDE(numerator, denominator, 0)` — DIVIDE with 0 as the alternate result.

FLAG only (do not rewrite). Add to the **Flags** section:
"DIVIDE(x, y, 0) returns 0 on division by zero. The default alternate (when omitted) is BLANK(). Zero and BLANK() behave differently in visuals: BLANK() hides the row, 0 shows it. Verify the third argument matches the intended visual behaviour."

This is an INFO flag, not a rewrite — the analyst may intentionally want 0.

---

**Rule 9 — COUNTROWS(VALUES()) vs DISTINCTCOUNT**

DETECT: `COUNTROWS(VALUES(Table[Col]))` or `COUNTROWS(DISTINCT(Table[Col]))` — counting distinct values via a two-function chain.

REWRITE:
```dax
DISTINCTCOUNT(Table[Col])
```

RATIONALE: "DISTINCTCOUNT is a native aggregation that handles the distinct-count pattern in a single storage engine request. COUNTROWS(VALUES(...)) materialises the distinct value list first, then counts — adding unnecessary formula engine overhead."

---

**Rule 10 — CALCULATETABLE Inside COUNTROWS**

DETECT: `COUNTROWS(CALCULATETABLE(Table, filter1, filter2, ...))` where the result is used as a scalar count.

REWRITE:
```dax
CALCULATE(COUNTROWS(Table), filter1, filter2, ...)
```

RATIONALE: "CALCULATE wrapping COUNTROWS pushes filters to the storage engine in a single query. CALCULATETABLE materialises the filtered table first, then counts rows — which forces the formula engine to handle the intermediate table."

---

**Rule 11 — SUMMARIZE Used for Aggregation**

DETECT: `SUMMARIZE(Table, GroupColumn, "ResultName", AggregateExpression)` where SUMMARIZE includes an inline aggregate expression (third+ arguments beyond table and grouping columns).

FLAG: "SUMMARIZE with inline aggregation is deprecated by Microsoft. It can silently produce incorrect results when the aggregate references columns outside the GROUP BY list."

REWRITE:
```dax
ADDCOLUMNS(
    SUMMARIZE(Table, Table[GroupColumn]),
    "ResultName", CALCULATE(SUM(Table[Column]))
)
```

RATIONALE: "ADDCOLUMNS + SUMMARIZE is the recommended replacement. SUMMARIZE can ignore grouping context when the expression references columns outside the GROUP BY — producing wrong numbers without any error. ADDCOLUMNS evaluates each expression in a clean filter context per group."

---

**Rule 12 — FILTER on RELATEDTABLE**

DETECT: `FILTER(RELATEDTABLE(Table), condition)` used as a CALCULATE argument where the condition tests a single column.

REWRITE (single-column condition only):
```dax
CALCULATE([Measure], RelatedTable[Column] = "Value")
```

RATIONALE: "FILTER(RELATEDTABLE(Table), ...) materialises the related table and iterates row by row. A direct relationship filter pushes the condition to the storage engine. This matters on large related tables."

If the condition is complex (multiple columns, OR logic, dynamic filters), FLAG only — do not rewrite. Add to the **Flags** section: "FILTER(RELATEDTABLE(...)) with complex condition — review whether a direct filter is possible."

---

**Rule 13 — Semi-Additive Pattern Opportunities**

DETECT: Manual date filtering patterns that replicate built-in time intelligence:
- `CALCULATE([Measure], FILTER(ALL('Date'), 'Date'[Date] <= MAX('Date'[Date])))` → running total
- `CALCULATE([Measure], FILTER('Date', 'Date'[Year] = YEAR(TODAY()) && 'Date'[Date] <= TODAY()))` → year-to-date
- `CALCULATE([Measure], FILTER(ALL('Date'[Date]), ...))` with date-range logic equivalent to DATEADD or SAMEPERIODLASTYEAR

FLAG: "This measure implements manual date filtering that could use a built-in time intelligence function. Built-in functions (TOTALYTD, DATEADD, SAMEPERIODLASTYEAR, DATESYTD) are engine-optimised and handle edge cases (fiscal years, blank dates) more reliably."

REWRITE ONLY IF the pattern directly maps to a standard function:
- Running total with `<= MAX(Date)` → `CALCULATE([Measure], DATESYTD('Date'[Date]))`
- Year-to-date with year/date filter → `TOTALYTD([Measure], 'Date'[Date])`
- Prior year comparison → `CALCULATE([Measure], SAMEPERIODLASTYEAR('Date'[Date]))`

If the pattern uses custom fiscal calendars or non-standard date hierarchies, flag only: "Custom date logic detected — verify fiscal calendar requirements before converting to built-in time intelligence."

---

### Step 6 — Multiple Valid Rewrites

If more than one valid rewrite exists for any portion of the measure, show each option as a labelled alternative with a brief trade-off comparison.

Format:
- Option A (simpler): `[rewrite]` — [trade-off note]
- Option B (more explicit): `[rewrite]` — [trade-off note]

---

### Step 7 — Complexity Inference

Infer complexity using the same rules as `/pbi:explain`:
- **Simple**: SUM, DIVIDE, basic CALCULATE with one filter, straightforward arithmetic
- **Intermediate**: CALCULATE with multiple filters, time intelligence (DATESYTD, SAMEPERIODLASTYEAR), RELATED, basic iterators (SUMX over a column)
- **Advanced**: Context transitions, nested iterators, EARLIER, ALLEXCEPT, USERELATIONSHIP, multiple nested CALCULATE, iterator-over-measure-reference patterns

Rationale depth follows complexity:
- Simple → brief rationale (one sentence per change)
- Intermediate → two to three sentences per change
- Advanced → full paragraph per change, explaining the engine-level mechanism

---

### Step 8 — Output

Produce output in this structure:

```
_Complexity: [Simple | Intermediate | Advanced]_

**[Measure Name] — Optimisation**

### Original
```dax
[paste the original measure exactly as received]
```

### Optimised
```dax
[the rewritten measure with all applicable rules applied]
```
If no rules apply, write: "No optimisation opportunities detected. This measure already follows efficient patterns."

### Changes
- [Change 1 description]: [rationale — scaled to complexity]
- [Change 2 description]: [rationale]

### Flags (if any)
- [Context-transition flag for iterator-over-measure-ref — if detected]
- [Nested iterator warning — if detected]

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:comment` · `/pbi:error`
```

If no Flags apply, omit the Flags section entirely.

---

### Step 9 — Update .pbi/context.md

After producing output, update `.pbi/context.md` using Read then Write:

1. Read the current `.pbi/context.md`
2. Update the **Last Command** section with these four lines in this exact order:
   - Command: /pbi:optimise
   - Timestamp: [current UTC ISO 8601]
   - Measure: [measure name]
   - Outcome: Optimised — [list of rule numbers applied, e.g. Rule 1, Rule 2]; Flags: [flags raised, or "None"]
3. Append a new row to **Command History**. Keep history to the last 20 rows. If there are already 20 rows, remove the oldest before appending.
   - Format: `| [timestamp] | /pbi:optimise | [measure name] | Optimised — [rules applied] |`
4. Do not modify the **Analyst-Reported Failures** section.
5. Write the updated file back to `.pbi/context.md`.

### Anti-Patterns
- NEVER rewrite iterator-over-measure-reference patterns — flag only (CRITICAL GUARD)
- NEVER change business logic — optimisation must preserve semantics
- NEVER suggest removing CALCULATE when it controls context transitions
- NEVER rewrite complex nested iterators without flagging — only rewrite trivially collapsible cases

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
