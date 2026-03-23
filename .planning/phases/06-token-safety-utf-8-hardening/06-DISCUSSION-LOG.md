# Phase 6: Token Safety + UTF-8 Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-23
**Phase:** 06-token-safety-utf-8-hardening
**Areas discussed:** Token error source, Trimming strategy, grep replacement scope, detect.py expansion

---

## Token Error Source

| Option | Description | Selected |
|--------|-------------|----------|
| During /pbi commands | Command .md files are too large | |
| During model file reads | model.bim or .tmdl files are too large | ✓ |
| Not sure | Investigate both | |

**User's choice:** During model file reads
**Notes:** This changed the approach — TOKEN requirements now focus on chunked reading of model files, not trimming command files.

---

## Large Model File Handling (reframed from Trimming strategy)

| Option | Description | Selected |
|--------|-------------|----------|
| Python extraction | detect.py extracts only measures/tables/relationships | |
| Chunked reading | Read model files in chunks using offset/limit | ✓ |
| You decide | Claude picks | |

**User's choice:** Chunked reading
**Notes:** None

---

## grep Replacement Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Measure search only | Replace grep in 4 commands, leave format.md and diff.md | |
| All grep/sed everywhere | Zero shell text processing in skill | ✓ |
| Measure search + format.md | Replace measure grep + format.md HTML parsing | |

**User's choice:** All grep/sed everywhere
**Notes:** User wants strict zero-grep policy, even for operations without UTF-8 risk (diff.md gitignore, format.md HTML parsing).

---

## detect.py Expansion

| Option | Description | Selected |
|--------|-------------|----------|
| Expand detect.py | Add new subcommands to existing file | ✓ |
| Separate scripts | New .py files per function | |
| You decide | Claude picks | |

**User's choice:** Expand detect.py
**Notes:** None

---

## Claude's Discretion

- Chunking strategy for large model files
- detect.py subcommand signatures and output formats
- HTML parsing implementation (regex vs html.parser)

## Deferred Ideas

None
