---
name: menu
description: "Command menu, or ask any DAX or modeling question in plain English."
model: sonnet
argument-hint: "[question or command]"
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:menu

Request: $ARGUMENTS

Never block the analyst.
Solve immediately, ask only when stuck.

## 1. No request: show the menu

If the request is empty, output this and wait:

```
pbi  Power BI DAX co-pilot

  A  Work on a measure   explain, format, optimise, comment, error, new
  B  Work on the model   load, edit, audit, extract, docs
  C  History             diff, commit, undo, changelog, resume
  D  Live Desktop        query, setup
  ?  All commands        help

Type a letter, a command name, or just describe what you need.
```

- A letter: list that group's commands with their one-line purpose (see `/pbi:help`) and ask which one.
- `?`: run the help command.
- Anything else: treat it as a request and continue below.

## 2. Route when the intent is a command

| The request is about | Command |
|---|---|
| what a measure does, how it works | `explain` |
| formatting, readability, indentation | `format` |
| slow measure, performance | `optimise` |
| comments, descriptions, documenting one measure | `comment` |
| an error message | `error` |
| a new measure | `new` |
| the model overview | `load` |
| changing, renaming, removing an object | `edit` |
| model health, best practices, review | `audit` |
| inventory, handover, model export | `extract` |
| documentation deliverable | `docs` |
| what changed | `diff` |
| saving a snapshot | `commit` |
| reverting | `undo` |
| change history | `changelog` |
| where was I | `resume` |
| running DAX, checking a value | `query` |
| installing or enabling live mode | `setup` |
| version, release notes | `version` |

To run a command: read `${CLAUDE_PLUGIN_ROOT}/skills/<command>/SKILL.md` and follow it from its `# /pbi:<command>` heading.
Skip its Preflight block: the project state and core rules are already loaded above.
Do not announce the routing.

Requests for bulk rewrites of every measure (comment all, format all, fix all audit findings) are out of scope since version 8.
Say so in one line and offer the single-object command instead.

## 3. Otherwise: solve it directly

When no command fits, the request is a DAX or modeling question.

1. **Answer immediately.** No questions, no preamble. Ground the answer in the model index and saved notes from the preflight block: use real table, column and measure names.
2. Follow the DAX style guide. In live tier, test any DAX you propose with a query-scoped `DEFINE MEASURE` before presenting it.
3. If the answer implies a model change, do not write it here. End with the command that applies it, for example `Next: /pbi:new` or `/pbi:edit`.

### When the analyst says the answer is wrong

Follow-ups and refinements ("also add...", "make it a percentage") are new requests, not failures.

- **First failure signal** ("that's wrong", "still broken", "not what I meant"): try a different interpretation or approach straight away. No questions.
- **Second failure signal**: work out which context is missing and ask exactly one question.

| The complaint sounds like | Ask |
|---|---|
| calculating the wrong thing | `What business question should this answer? (for example "monthly revenue growth versus last year")` |
| wrong columns, tables or relationships | `Which tables are involved and how do they relate?` |
| it duplicates something | `Which existing measures are already in play?` |
| wrong numbers in a visual | `Which visual is this in, and which slicers or filters are active?` |

Then:

- Save the answer with `detect.py note "<Business Question | Model Notes | Existing Measures | Visual Context>" "<answer>"`.
- Retry immediately with the new context. Never ask "shall I try again?".
- On a further failure, ask about the next gap that has no saved note. Never ask the same question twice.

The failure counter lives in this conversation only.

## 4. Log

When `PBIP_MODE=file` and the request was solved directly (section 3):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:menu" "<request in a few words>" "<outcome>"
```

Routed commands log themselves.
