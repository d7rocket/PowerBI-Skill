# DAX style guide

Read this before writing or reviewing DAX.
It merges this project's simplicity-first style with Microsoft's DAX guidelines (see Attribution).
Where the two differ, simplicity wins and the difference is called out.

## Simplicity first

- Write the simplest expression that answers the business question.
- `SUM ( Sales[Amount] )` beats `CALCULATE ( SUM ( Sales[Amount] ) )`.
- Use `VAR` only when a value is used more than once or when it names a real step. A single-use expression needs no `VAR`/`RETURN`.
- Do not add `IFERROR`, `ISBLANK` guards or `+ 0` unless the analyst asks for that behaviour.
- A measure that only references another measure (`[B] = [A]`) should not exist.
- Do not create two measures with the same expression.

## References and names

- Columns are always written with their table: `'Sales'[Amount]`.
- Measures are always written without a table: `[Revenue]`.
- Variable names say what the value is. Prefix with `_` when the name could clash with a column or table.

## Division

- Use `DIVIDE ( a, b )` instead of `a / b`. It returns BLANK on division by zero.
- Add the third argument only when a specific alternate result is required. `0` and BLANK behave differently in visuals: BLANK hides the row, `0` shows it.
- Inside a row iterator over many rows, `/` is faster, but only when the denominator is guaranteed non-zero.
- Never write `1 - (x / y)` or `1 + (x / y)`. Compute the whole ratio:

```dax
VAR _revenue = SUM ( 'Sales'[Revenue] )
RETURN
    DIVIDE ( _revenue - SUM ( 'Sales'[Cost] ), _revenue )
```

## CALCULATE and filters

- Use a column predicate as the filter argument: `CALCULATE ( [Revenue], 'Sales'[Region] = "North" )`.
- Do not wrap a whole table in `FILTER` to test one column.
- Use `KEEPFILTERS` when the new filter must intersect with the existing one instead of replacing it.
- Use `REMOVEFILTERS` when the intent is to remove filters. Keep `ALL` for when a table result is needed.
- A boolean filter argument cannot reference a measure, another `CALCULATE`, or columns from two tables. Store the value in a variable first.
- Avoid deep `CALCULATE` nesting. Name the steps with variables.
- `TREATAS` is the right tool for a virtual relationship. Prefer it to `INTERSECT`.

## Iterators

- Use `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNTROWS`, `DISTINCTCOUNT` when a plain aggregation does the job.
- Iterate at the grain the calculation needs, not over the whole fact table.
- A measure reference inside an iterator triggers a context transition for every row. That is sometimes required and often expensive. Flag it, do not silently rewrite it.
- Avoid `IF`, `SWITCH` and `IFERROR` inside iterators over large tables. They push work into the slower formula engine.

## Tables

- `SUMMARIZECOLUMNS` is the default for a grouped table with calculations.
- Use `SUMMARIZE` only to get distinct combinations of columns, never with inline aggregations (it can return wrong numbers without an error). Use `ADDCOLUMNS ( SUMMARIZE ( ... ), "Name", CALCULATE ( ... ) )` or `SUMMARIZECOLUMNS` instead.
- `SELECTEDVALUE ( col, alt )` replaces `IF ( HASONEVALUE ( col ), VALUES ( col ), alt )`.

## Time intelligence

- Requires a proper date table with contiguous dates, marked as a date table.
- Prefer the built-in functions (`DATESYTD`, `TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`, `DATESINPERIOD`) to hand-written date filters when the meaning is identical.
- A running total over all time is not a year-to-date. Never convert one into the other.
- `DATESINPERIOD` offsets must match the window exactly: a 12-month window is `-12`, not `-11`.

## Debug-only functions

- `EVALUATEANDLOG` never ships in a model.

## DAX queries (for /pbi:query and testing)

- One `DEFINE` block at most, at the top. Definitions are separated by new lines.
- Define a measure with its table: `DEFINE MEASURE 'Sales'[Name] = ...`. Use it without the table: `[Name]`.
- Always add `ORDER BY` when `EVALUATE` returns more than one row.
- Limit exploratory results with `TOPN` so a query never returns a whole fact table.
- A single value: `EVALUATE ROW ( "Result", [Measure] )`.

## Formatting

SQLBI style, as produced by DAX Formatter:

- Keywords and functions in UPPERCASE.
- Measure name and `=` on the first line, expression below.
- One argument per line for multi-argument calls, indented four spaces.
- `VAR` and `RETURN` each on their own line.

## Where this differs from Microsoft's guidance

- Microsoft recommends `VAR` broadly for readability. This project uses `VAR` only for reuse or a real named step.
- Microsoft's skill auto-applies DAX rewrites. This project always previews and asks first.

## Attribution

Parts of this guide are distilled from the `semantic-model-authoring` skill in Microsoft's `skills-for-fabric` repository (MIT License, Copyright Microsoft Corporation), release v0.3.21.
