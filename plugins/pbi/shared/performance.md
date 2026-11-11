# Performance guide

Read this before performance work.
The method is distilled from Microsoft's DAX performance decision guide (see Attribution).

## Two ways to work

- **Measured** (live mode): run the query, read the timings, change one thing, run again. This is the only way to claim a speed-up.
- **Static** (no live connection): scan the DAX for known slow shapes. Every finding is a hypothesis. Say `Not measured` in the output.

Never state a percentage improvement that was not measured.

## How the engine spends time

- The storage engine (SE) scans compressed columns. It is fast and runs in parallel.
- The formula engine (FE) does everything the storage engine cannot. It is single-threaded.
- Slow DAX is usually DAX that forces row-by-row work into the formula engine, or that makes the storage engine scan the same data many times.

## Measured workflow

1. Resolve every measure the target depends on. Fetch each definition and build one `DEFINE` block that contains them all.
2. Write a test query that reflects real use, for example grouped by the column the report groups by:

```dax
DEFINE
    MEASURE 'Sales'[Target] = <current expression>
EVALUATE
    SUMMARIZECOLUMNS ( 'Product'[Category], "Target", [Target] )
ORDER BY 'Product'[Category]
```

3. Baseline: one warm-up run, then at least two timed runs with the cache cleared. Use the execution-metrics option of `dax_query_operations` (or the `trace_operations` tool) and record total time, FE time, SE time, SE query count and row count.
4. Change only the measure definition in the `DEFINE` block. Keep `EVALUATE` and the grouping identical.
5. Run again the same way. Compare.
6. The result must be identical: same rows, same columns, same values. If anything differs, the rewrite changed the meaning. Discard it.
7. A gain inside the run-to-run noise is not a gain. If runs vary by 100 ms, a 60 ms difference means nothing.
8. Only after a measured, equivalent gain, offer to write the new definition to the model (preview and confirm as always).

## Reading the numbers

| Signal | Likely cause | Look at |
|---|---|---|
| High FE time, many small SE queries | repeated expressions, context transition per row | cache in a variable, iterate at a coarser grain |
| SE rows far above result rows | `FILTER` over a whole table, late filtering | column predicates, `KEEPFILTERS` |
| Several near-identical SE scans | sibling measures that differ only by a filter | compute once, split with variables |
| `CallbackDataID` in the SE query | `IF`, `SWITCH`, `DIVIDE`, `IFERROR` inside an iterator | move the condition into a filter, use `/` when the denominator cannot be zero |
| Slow distinct count | `DISTINCTCOUNT` on a high-cardinality column | `COUNTROWS` when the column is a key, or `SUMX ( VALUES ( col ), 1 )` as an alternative to test |
| Few SE queries, clean plan, still slow | data layout or model shape | model changes, not DAX |

## Rewrites that are safe to propose

These keep the meaning when the stated condition holds.

- `FILTER ( Table, Table[Col] = x )` as a `CALCULATE` argument, testing one column: use `Table[Col] = x`.
- `SUMX ( Table, Table[Col] )`: use `SUM ( Table[Col] )`.
- `CALCULATE ( [Measure] )` with no filter arguments: use `[Measure]`, unless it sits inside an iterator where the context transition is intended.
- `COUNTROWS ( VALUES ( Table[Col] ) )`: use `DISTINCTCOUNT ( Table[Col] )`.
- `COUNTROWS ( CALCULATETABLE ( Table, filters ) )`: use `CALCULATE ( COUNTROWS ( Table ), filters )`.
- `IF ( HASONEVALUE ( col ), VALUES ( col ), alt )`: use `SELECTEDVALUE ( col, alt )`.
- `IFERROR ( a / b, alt )`: use `DIVIDE ( a, b )`, adding `alt` only if it is required.
- The same sub-expression evaluated more than once: store it in a `VAR`.
- `SUMMARIZE` with inline aggregations: use `SUMMARIZECOLUMNS` or `ADDCOLUMNS ( SUMMARIZE ( ... ), ... )`. This one is about correctness as much as speed.

## Flag, do not rewrite

- An iterator whose expression is a measure reference. The context transition may be exactly what the business rule needs.
- Nested iterators, unless the inner one is a plain column reference.
- A running total (`<= MAX ( 'Date'[Date] )`). It is not a year-to-date.
- `DIVIDE ( x, y, 0 )`. The `0` may be deliberate.
- `ALLEXCEPT`, `ALLSELECTED` and relationship overrides (`USERELATIONSHIP`, `CROSSFILTER`). Changing them changes results.

## Beyond DAX

When the DAX is clean and it is still slow, the cause is the model or the query.
Suggest these, never apply them without explicit approval:

- Coarser grain in the visual (month instead of date).
- Removing measure filters on visuals.
- Replacing a bidirectional or many-to-many relationship.
- Reducing column cardinality, fixing data types, removing unused columns.
- Aggregation tables for very large facts.

## Attribution

The measured workflow and the signal table are distilled from `dax-perf-decision-guide.md` and `dax-perf-patterns.md` in the `semantic-model-authoring` skill of Microsoft's `skills-for-fabric` repository (MIT License, Copyright Microsoft Corporation), release v0.3.21.
