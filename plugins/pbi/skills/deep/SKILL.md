---
name: deep
description: "Guided session for a hard DAX or modeling problem. Use only when asked for explicitly."
model: sonnet
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:deep

Front-load the context, then build.
No DAX is written before the intake and the model review are done.
Every measure must trace back to the stated business question.

Notes are stored with `detect.py note "<Section>" "<text>"` and come back in the preflight block of every later command.

## Phase A - Intake

### A1 - Use what is already known

From the preflight block:

- A `Business Question` note exists: show it and ask `Still the focus, or something new?`
- An `Existing Measures` note exists: show it in one line.
- `PBIP_MODE=file`: the model index is the model description. Do not ask the analyst to describe the model.

### A2 - Ask what is missing

One question at a time. Wait for each answer.

1. **Business question** (if not on file): `What business question are we solving? (for example "compare regional sales month over month")`
2. **Model** (paste mode only): `Describe your model: key tables, how they relate, and any known issues.`
3. **Existing measures** (if not on file): in a project, list the measures from the model index that look relevant and ask `Are these the ones in play, and is anything missing?` In paste mode ask `Which existing measures are relevant? (paste names, or "none yet")`

### A3 - Save

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" note "Business Question" "<verbatim answer>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" note "Existing Measures" "<answer>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" note "Model Notes" "<paste-mode model description, if any>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:deep" "<business question in a few words>" "Intake complete"
```

In paste mode with no project folder, notes cannot be saved. Keep them in the conversation and say so once.

### Gate A to B

> **Gate: model review.** Context gathered. Next I review the model for structural risks before any DAX is written.
> Type **continue** to proceed, or **cancel** to stop.

- The reply contains `continue`: go to Phase B.
- `cancel`: say `Session paused. Run /pbi:deep to pick it up again.` and stop.
- Anything else: show the gate again. Do not advance.

## Phase B - Model review

Read the modeling guide first.

Review only what bears on the business question:

- In a project: use the model index (tables, relationships, BIDIRECTIONAL and inactive flags). Read a table file only when the question depends on its columns. For a full health check point to `/pbi:audit`.
- In paste mode: review the described model.

Check, in this order:

- **CRITICAL**: bidirectional relationships on the path the question uses, many-to-many relationships.
- **WARN**: no date table when the question involves time, a fact table with no relationship, an inactive relationship the question seems to need.

Output:

```
**Model review** for: [business question]

[CRITICAL findings, each with a one-line recommendation]
[WARN findings, each with a one-line recommendation]
[or: No structural risks for this question.]
```

If there are findings, add: `These do not block DAX work, but fixing them first makes the measures more reliable.`

### Gate B to C

> **Gate: DAX development.** Model review done. Next we build the measures for your question.
> Type **continue** to proceed, or **cancel** to stop.

Same rules as the first gate.

## Phase C - DAX development

Say:

```
Business question: [question]
Existing measures: [summary]

What do you want to build first? Say "done" when the measures are complete.
```

From here the analyst works with the normal commands (`/pbi:new`, `/pbi:edit`, `/pbi:explain`, `/pbi:query` and the rest) or asks directly.
The saved notes inform every one of them through the preflight block.
There are no gates inside this phase.

## Phase D - Final check

Only when the analyst signals completion ("done", "finished", "that's all", "we're good").
Never after each individual measure.

List the measures created this session: the `/pbi:new` and `/pbi:edit` rows under recent commands, plus anything built in this conversation.

```
**Final check**

Business question: [verbatim]

Measures built:
- [name]: [how it serves the question, one line]

Do these answer the question? (yes / no)
```

- In live tier, run each measure once with `/pbi:query`-style `EVALUATE ROW` and show the values next to the names.
- `yes`: say `Session complete. /pbi:diff to review, /pbi:commit to save.` and log `Deep session closed`.
- `no`: ask `What is missing?` and return to Phase C.
- Anything else: ask again.

## Never

- Enter deep mode unless the analyst ran `/pbi:deep`.
- Ask the intake questions all at once, or re-ask one whose answer is on file.
- Advance past a gate on a vague reply ("ok", "sure"). The reply must contain `continue`.
- Write DAX before the second gate.
- Ask the analyst to describe a model that the project already contains.
