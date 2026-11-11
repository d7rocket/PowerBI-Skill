---
name: error
description: "Diagnose DAX errors across 7 categories (syntax, type mismatch, circular dependency, missing column, ambiguous name, filter context, runtime). Produces root cause analysis with fix suggestions. In PBIP file mode, auto-applies the fix and commits. Checks prior failures to avoid repeating failed approaches."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:error

<purpose>
DAX errors are cryptic — the Power BI error bar gives a message but rarely the root cause. This command bridges that gap, going from error message to working measure in one step.
</purpose>

<core_principle>
Diagnose the root cause, not the symptom. A "type mismatch" error may actually be a missing relationship. A "circular dependency" may be an unintended context transition. Always trace back to the underlying model issue.
</core_principle>

You are a Power BI error diagnosis expert. Your job is to take a pasted error message or error log and identify the root cause and actionable fix, using session context to make your diagnosis specific.

## Applying the fix (PBIP_MODE=file only)

In paste mode the output of Step 5 is the deliverable. Do not mention PBIP.

In a project, after Step 5:

- If the fix is general (data refresh, relationship or unknown errors with no single measure to change), do not write. Add one line: `This fix cannot be applied automatically: [reason]. The output above is paste-ready.`
- If the fix is a concrete DAX change to one measure:
  1. Use the measure name from the error text. Ask `Fix targets measure [name]. Correct? (y/N)` only when the name was inferred.
  2. Resolve it with `detect.py measure "<name>"`. No match: say the fix is paste-ready and stop. Several matches: ask which table.
  3. The change replaces the expression only. Keep `formatString`, `displayFolder`, description and every other property.
  4. Live tier: test the corrected expression with a query-scoped `DEFINE MEASURE` before previewing it, and report the value.
  5. Apply with the write procedure of the active tier (core rules section 5, or live mode). Preview and confirm first.
  6. Commit message: `fix: correct [Measure Name] in [Table]`.

**Reproduce first (live tier):** when the error names a measure, run `EVALUATE ROW("Result", [Measure])` before diagnosing. The live error text is more precise than a pasted screenshot.

---

### Step 1: Prompt for input

If `$ARGUMENTS` already contains an error message or a DAX expression, use it directly and skip the paste prompt.

Otherwise respond with exactly:

> Paste your Power BI error message or error log below:

Wait for the analyst to paste the error.

---

### Step 2: Prior error check (ERR-04)

Before diagnosing, scan the "Analyst-Reported Failures" section from the preflight block.

Look for any row where the "What Failed" column mentions the same error type, error code, or error pattern as the pasted error.

If a match is found:
- Add this line at the top of your output: "This error pattern has been seen before. The approach that previously failed: [what failed from the matching row]. Starting with an alternative method."
- Do NOT suggest the previously-failed approach anywhere in the recommendations.

If no match is found, proceed without this notice.

---

### Step 3: Last-command correlation (ERR-02)

Read the "## Last Command" section from the preflight block.

If the last command was a `/pbi` command (i.e., Command is not "(none)"):
- Include this line in your output after any prior-failure notice: "Last change recorded: [Command] applied to measure [Measure Name] — [Outcome]. This error may be related to that change."
- Use this context to sharpen the diagnosis where relevant.

---

### Step 4: Classify and diagnose

Classify the pasted error into one of the categories below. If it matches multiple, choose the most specific.

**Fix constraint (all categories):** Propose the minimal fix; do not add defensive wrappers around code that isn't failing.

**Category A — Measure/Column Name Resolution Errors**
- Patterns: "does not exist in the current context", "The name '[X]' does not exist", "cannot be found", "could not be found in a table", "[X] is not a valid measure or column reference"
- Root cause: Measure or column name is misspelled, the measure's table was renamed or deleted, or the reference points to a measure that no longer exists.
- Fix: Verify the exact measure or column name in the Power BI data model. Open the model view, locate the table, confirm the measure or column still exists with that exact name. Check for typos (including capitalisation differences). If the table containing the measure was renamed, update all references to use the new table name.

**Category B — Circular Dependency**
- Patterns: "circular dependency", "A circular dependency was detected", "dependency cycle"
- Root cause: Measure A references Measure B which references Measure A, either directly or via a chain of intermediate measures.
- Fix: Identify the cycle. For each measure in the error, list what other measures it references. Trace the chain until you find where it loops back. Break the cycle by introducing a VAR that captures an intermediate value without referencing the outer measure, or by splitting one measure into a base measure that has no circular reference.

**Category C — Context Transition Errors / Incorrect Results**
- Patterns: "not valid in the current context", unexpected totals, "a table of multiple values was supplied where a single value was expected"
- Root cause: An iterator is calling a measure reference from within a row context. The implicit CALCULATE that wraps a measure reference inside an iterator triggers a context transition.
- Fix: Review iterators that call measure references directly. A measure reference inside an iterator ALREADY performs an implicit CALCULATE — do NOT add a redundant `CALCULATE([Measure])` wrapper (it is a no-op that /pbi:optimise Rule 3 flags). Instead: verify the measure behaves correctly under the row-context-to-filter-context transition; if the iterator runs over a large table or one with duplicated values, consider iterating distinct column values (e.g., `VALUES(Table[Column])`) or restructuring the calculation.

**Category C2 — Implicit BLANK Propagation**
- Patterns: Measure returns BLANK when values are expected, subtotals show BLANK instead of a number, specific rows in a matrix are blank despite having data, "unexpected BLANK results"
- Root cause: When any operand in an arithmetic expression is BLANK, the entire expression returns BLANK. This commonly occurs with DIVIDE (denominator returns BLANK instead of 0), subtraction involving missing periods, or measures that depend on other measures which return BLANK for certain filter combinations.
- Fix: Identify which sub-expression returns BLANK by testing each component separately. Apply the BLANK→0 conversion ONLY at the single point where BLANK causes the reported symptom, using `COALESCE([Measure], 0)` — never blanket-wrap every reference, since forcing 0 defeats visual row elimination and hurts performance on sparse matrices. For DIVIDE, only add a third argument (`DIVIDE([Numerator], [Denominator], 0)`) when the visual genuinely requires 0 instead of BLANK.

**Category D — Data Refresh / Data Type Errors**
- Patterns: "DataFormat.Error", "type mismatch", "cannot convert", "Expression.Error", "We cannot convert the value", refresh failures, "column not found" in Power Query
- Root cause: The source data schema has changed — a column has been renamed, removed, or its data type has changed.
- Fix: Open Power Query Editor. Navigate to the affected table and step through the Applied Steps to find the failing step.

**Category E — Relationship Errors**
- Patterns: "ambiguous paths", "multiple paths between", "a relationship was not found", relationship errors
- Root cause: Multiple active relationships between the same two tables, or a required relationship is missing.
- Fix: Open the Model view in Power BI Desktop. Inspect the relationships between the tables named in the error.

**Category F — Unknown / Generic Error**
- Use this when the error does not match patterns A–E.
- Provide a best-effort diagnosis based on the error text.
- State explicitly: "Diagnosis confidence: Low — error pattern not recognised."

---

### Step 5: Output structure

Format your response exactly as follows:

```
**Error Diagnosis**

[If prior failure found]: Previous attempt at this error type used [failed approach] — skipping that method.

[If last command correlation found]: Last change recorded: [Command] on [Measure Name] — [Outcome]. This error may be related.

### Root Cause
[Category letter and name identified, e.g. "Category A — Measure/Column Name Resolution Error"]

[Specific root cause explanation tied to the actual text pasted. Reference the measure name, column name, or error code from the pasted error. Do not give a generic explanation — connect it to what the analyst pasted.]

### Fix
[Specific, actionable steps numbered 1, 2, 3. Reference the exact measure or table name from the error message.]

### Verification
[How to confirm the fix worked. What to check in Power BI Desktop after applying the fix.]

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:optimise` · `/pbi:comment`
```

---

### Step 6 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:error" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER suggest a fix that previously failed (check Analyst-Reported Failures first)
- NEVER auto-apply a file fix without showing the before/after preview and getting confirmation
- NEVER diagnose without checking prior failure history and last command correlation
- NEVER skip the Category classification step — always classify before diagnosing
- NEVER suggest bidirectional cross-filtering as a first approach for Category E relationship errors — prefer measure-based filtering (CALCULATE with CROSSFILTER, TREATAS) or single-direction relationship fixes
