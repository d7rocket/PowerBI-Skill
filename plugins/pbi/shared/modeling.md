# Modeling guide

Read this before structural changes (tables, columns, relationships) and before an audit.
Distilled from Microsoft's semantic model guidelines (see Attribution) and this project's audit rules.

## First principle

Consistency over perfection.
In an existing model, follow the conventions it already uses before applying any rule below.

## Shape

- Star schema: fact tables related to denormalized dimension tables through single-column keys, one-to-many.
- Avoid dimension-to-dimension chains (snowflake) and wide flat tables.
- Keep the model lean. Every column costs memory even when nobody uses it.
- More than about 30 visible columns in one table usually means it should be split.
- Every table has at least one relationship, except deliberate utility tables (parameters, measure helpers).

## Names

- Readable business names with spaces: `Sales`, `Order Date`, `Customer Name`.
- No `CamelCase`, `snake_case`, `UPPER_CASE`, and no technical prefixes such as `Dim`, `Fact`, `STG_`.
- Spell words out. Common business acronyms (YTD, MTD) are fine.
- No leading or trailing spaces, tabs, line breaks or emojis in names.
- If the existing model uses another convention consistently, keep it and say so.

## Columns

- Data types: whole numbers for keys, fixed decimal for currency, date for dates. Avoid floating point (`double`) for amounts.
- Hide keys, foreign keys and system columns.
- Hide a numeric column once an explicit measure aggregates it.
- Set `summarizeBy: none` on numbers that must not be aggregated (IDs, year, month number, postal codes).
- Split a date-time column into a date column and a time column. Time precision makes the column nearly unique and inflates the model.
- Watch high-cardinality text columns (GUIDs, transaction IDs).
- Set `sortByColumn` on text that must not sort alphabetically, such as month names.
- Set `dataCategory` on geographic columns.

## Calculated columns

- Prefer a measure whenever the logic is an aggregation or depends on filter context.
- If a per-row value is needed, prefer computing it in Power Query or the source.
- More than about five calculated columns in a model deserves a review.

## Measures

- Explicit measures only. Do not rely on implicit aggregation.
- Every measure has a `formatString`.
- Common format strings: currency `#,##0.00`, whole number `#,##0`, percentage `0.0%`, decimal `#,##0.00`.
- Group measures with `displayFolder`.
- Measures with non-obvious logic get a description that states the business rule, not the name restated.
- Keep measures in the table they describe. A single dedicated measures table is acceptable only when the model already uses one.

## Relationships

- Single direction by default.
- Bidirectional filtering causes ambiguity and slow queries. Use it only when nothing else works, and prefer a measure-based fix (`CROSSFILTER`, `TREATAS`) first.
- Avoid many-to-many unless the business requires it.
- Both key columns have the same data type. Integer keys are faster than text keys.
- No composite keys.
- An inactive relationship must be used by at least one measure through `USERELATIONSHIP`. Otherwise it is dead weight.
- Do not use `USERELATIONSHIP` against a table protected by row-level security.

## Date table

- One real date table, contiguous, marked as a date table (`dataCategory: Time`).
- Prefer a date table from the source or Power Query over a DAX calculated table.
- Turn off auto date/time once a date table exists. It creates a hidden table per date column.
- Include year, quarter, month and day attributes, with month names sorted by month number.

## Hierarchies and calculation groups

- A hierarchy has at least two levels, all from the same table.
- Use a calculation group when the same time-intelligence variants would otherwise be repeated across many measures.
- For a handful of measures, separate measures are simpler.

## Row-level security

- Keep filter expressions simple. Push complex logic to the source.
- Avoid string manipulation functions in security filters.

## Documentation

- Visible tables, columns and measures have descriptions that add knowledge.
- Descriptions help both people and Copilot-style assistants understand the model.

## Severity when auditing

- CRITICAL: wrong numbers are likely (bidirectional ambiguity, many-to-many without need, inline-aggregating `SUMMARIZE`, missing date table with time intelligence, type mismatch on keys).
- WARN: performance or maintainability (floating point amounts, visible keys, missing format strings, unused inactive relationships, heavy calculated columns).
- INFO: hygiene (naming, missing descriptions, display folders).

## Attribution

Parts of this guide are distilled from the `semantic-model-authoring` skill in Microsoft's `skills-for-fabric` repository (MIT License, Copyright Microsoft Corporation), release v0.3.21.
