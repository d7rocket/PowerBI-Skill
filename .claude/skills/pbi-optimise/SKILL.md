---
name: pbi-optimise
description: Optimise a DAX measure for performance with rationale for each change. Use when an analyst asks to optimise, improve performance, speed up, or rewrite a DAX measure.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write
---

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

## Instructions

Respond with: "Paste your DAX measure below:"

Wait for the analyst to paste a DAX measure, then follow these steps in order.

---

### Step 1 — Measure Extraction

Extract the measure name from text before the first `=`, trimmed of whitespace.

- If no `=` is found, use `[Measure]` as the placeholder name and note: "Could not detect measure name — no `=` found. Showing analysis with placeholder name."
- If `$ARGUMENTS` contains `--table TableName`, record TableName. Include a table context note at the top of your output: "Table context: TableName"

---

### Step 2 — Prior Failure Check

Scan the Session Context above for the extracted measure name in the **Analyst-Reported Failures** section.

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

Pattern example:
```dax
CALCULATE([Measure], FILTER(Sales, Sales[Region] = "North"))
```

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

Pattern example:
```dax
SUMX(Sales, Sales[Amount])
```

REWRITE:
```dax
SUM(Sales[Amount])
```

RATIONALE: "SUM is a native aggregation handled entirely in the storage engine. SUMX iterates row-by-row in the formula engine unnecessarily when summing a single column. Use SUM for direct column aggregation."

---

**Rule 3 — Redundant CALCULATE Wrapper**

DETECT: `CALCULATE([SimpleMeasure])` with no filter arguments — a CALCULATE call wrapping only a measure reference with nothing else.

Pattern example:
```dax
CALCULATE([Total Sales])
```

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

Pattern example:
```dax
SUMX(Sales, SUMX(Products, Sales[Qty] * Products[Price]))
```

FLAG with this explanation in the **Flags** section:
"Nested iterators create a Cartesian product: every row in the outer table iterates every row in the inner table. This can be extremely slow on large tables. Review whether the inner iteration is necessary or can be collapsed."

REWRITE ONLY IF: The inner iteration is trivially collapsible — meaning the inner expression is a plain column reference with no formula. If the inner expression contains a formula or depends on both tables, flag only and do not rewrite.

---

**Rule 6 — Unnecessary SWITCH(TRUE())**

DETECT: `SWITCH(TRUE(), condition1, result1, condition2, result2, ...)` where conditions are simple equality tests against the same column.

Pattern example:
```dax
SWITCH(TRUE(), Table[Col] = "A", result1, Table[Col] = "B", result2, default)
```

REWRITE:
```dax
SWITCH(Table[Col], "A", result1, "B", result2, default)
```

RATIONALE: "SWITCH with a value argument evaluates the expression once and matches. SWITCH(TRUE()) evaluates every condition sequentially even after a match is found in some engines. Use the value form when all conditions test the same expression."

---

**Rule 7 — Verbose HASONEVALUE + VALUES Pattern**

DETECT: `IF(HASONEVALUE(Table[Col]), VALUES(Table[Col]), fallback)` — the common verbose pattern for getting a single selected value.

Pattern example:
```dax
IF(HASONEVALUE(Table[Col]), VALUES(Table[Col]), fallback)
```

REWRITE:
```dax
SELECTEDVALUE(Table[Col], fallback)
```

RATIONALE: "SELECTEDVALUE is a purpose-built function that replaces the HASONEVALUE + VALUES two-step pattern. Functionally identical, but clearer intent and marginally faster."

---

**Rule 8 — DIVIDE With Explicit Zero**

DETECT: `DIVIDE(numerator, denominator, 0)` — DIVIDE with 0 as the alternate result.

Pattern example:
```dax
DIVIDE(numerator, denominator, 0)
```

FLAG only (do not rewrite). Add to the **Flags** section:
"DIVIDE(x, y, 0) returns 0 on division by zero. The default alternate (when omitted) is BLANK(). Zero and BLANK() behave differently in visuals: BLANK() hides the row, 0 shows it. Verify the third argument matches the intended visual behaviour."

This is an INFO flag, not a rewrite — the analyst may intentionally want 0.

---

**Rule 9 — COUNTROWS(VALUES()) vs DISTINCTCOUNT**

DETECT: `COUNTROWS(VALUES(Table[Col]))` or `COUNTROWS(DISTINCT(Table[Col]))` — counting distinct values via a two-function chain.

Pattern example:
```dax
COUNTROWS(VALUES(Table[Col]))
```

REWRITE:
```dax
DISTINCTCOUNT(Table[Col])
```

RATIONALE: "DISTINCTCOUNT is a native aggregation that handles the distinct-count pattern in a single storage engine request. COUNTROWS(VALUES(...)) materialises the distinct value list first, then counts — adding unnecessary formula engine overhead."

---

**Rule 10 — CALCULATETABLE Inside COUNTROWS**

DETECT: `COUNTROWS(CALCULATETABLE(Table, filter1, filter2, ...))` where the result is used as a scalar count.

Pattern example:
```dax
COUNTROWS(CALCULATETABLE(Table, filter1, filter2, ...))
```

REWRITE:
```dax
CALCULATE(COUNTROWS(Table), filter1, filter2, ...)
```

RATIONALE: "CALCULATE wrapping COUNTROWS pushes filters to the storage engine in a single query. CALCULATETABLE materialises the filtered table first, then counts rows — which forces the formula engine to handle the intermediate table."

---

### Step 6 — Multiple Valid Rewrites

If more than one valid rewrite exists for any portion of the measure, show each option as a labelled alternative with a brief trade-off comparison.

Format:
- Option A (simpler): `[rewrite]` — [trade-off note]
- Option B (more explicit): `[rewrite]` — [trade-off note]

Example:
- Option A (simpler): `CALCULATE([Measure], Region[Name] = "North")` — easier to read, slightly less explicit about table.
- Option B (more explicit): `CALCULATE([Measure], TREATAS({"North"}, Region[Name]))` — preferred when filter context from visuals must be preserved.

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
<!-- Rules 1-7, 9-10 produce changes; Rules 4 and 8 produce flags only. -->
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

### Step 9 — Update .pbi-context.md

After producing output, update `.pbi-context.md` using Read then Write:

1. Read the current `.pbi-context.md`
2. Update the **Last Command** section:
   - Command: `/pbi:optimise`
   - Measure: [measure name]
   - Rules applied: [list of rule numbers applied, e.g. Rule 1, Rule 2]
   - Flags raised: [list flags raised, or "None"]
   - Timestamp: [current date/time]
3. Append a new row to **Command History**. Keep history to the last 20 rows. If there are already 20 rows, remove the oldest before appending.
   - Format: `| [timestamp] | /pbi:optimise | [measure name] | Optimised — [rules applied] |`
4. Do not modify the **Analyst-Reported Failures** section.
5. Write the updated file back to `.pbi-context.md`.
