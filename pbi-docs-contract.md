# pbi:docs Output Contract for docgen Compatibility

This document specifies the Markdown output requirements that the `pbi:docs` skill
must follow for its output to be correctly parsed by the `pbi:docgen` pipeline.

**Note:** The `pbi:docs` skill lives in a separate repository. These requirements
must be applied manually to the pbi:docs SKILL.md when updating that skill.

## Markdown Output Requirements

### Code Blocks

All code samples must use fenced code blocks with language tags:

- DAX expressions: ```dax
- M Query / Power Query expressions: ```m
- SQL: ```sql
- Generic code: ```

### Tables

Tabular data (measure tables, source lists, relationship tables) must use standard
pipe table format:

```
| Column A | Column B |
|----------|----------|
| value    | value    |
```

### Prohibited Patterns

Do NOT use custom markers in output. The following are **not** valid and will cause
rendering issues in the docgen pipeline:

- `CODE_BLOCK:` / `END_CODE_BLOCK`
- `TABLE:` / `END_TABLE`

Standard Markdown only.

## Section Headings

Each major section of pbi:docs output should use `##` (H2) headings. The docgen
pipeline uses keyword matching from `section_heading_map.yaml` to categorize
sections. Current keywords cover:

- overview, summary, introduction, about
- data source, gateway, connection, source system, architecture
- dataflow, data flow, refresh, pipeline
- m query, power query, m code, query, transformation
- data model, ssas, relationship, table, measure, dax, column
- parameter, troubleshooting, maintenance, configuration, setting
