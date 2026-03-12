---
name: pbi-load
description: Load PBIP model context for use by DAX commands. Use when the analyst asks to load model context or when a PBIP project is present.
disable-model-invocation: true
model: haiku
allowed-tools: Read
---

Model context loading is available when a PBIP project is present (Phase 2).

For now, paste your DAX measure directly into any `/pbi` command — all DAX commands work without prior model loading.

**Available commands:**
- `/pbi:explain` — explain a DAX measure
- `/pbi:format` — format a DAX measure to SQLBI style
- `/pbi:optimise` — optimise a DAX measure with rationale
- `/pbi:comment` — add inline comments and generate a Description field value
- `/pbi:error` — diagnose a Power BI error
