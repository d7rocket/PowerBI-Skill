---
name: pbi:deep
description: "Guided multi-phase DAX workflow: intake, model review, DAX development, verification"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

## Detection

Run ALL of the following detection commands using the Bash tool before proceeding. Save the output — subsequent steps reference these values.

```bash
python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"
```

Save the `PBIP_DIR` value from the output — all subsequent steps must use it instead of a hardcoded `.SemanticModel`.

```bash
python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"
```

```bash
python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")
```

```bash
python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."
```

### Auto-Resume

After detection, apply the following before executing the command:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - Skip any "Model Context Check" (Step 0.5) below — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.

---

# /pbi:deep


## Instructions

---

## Phase A — Context Intake

### Step 0 — Check Existing Context

Read Session Context from detection output. Check `.pbi-context.md` for existing sections:
- `## Business Question` — if present, display: "Business question on file: [content]" and ask "Still the focus, or something new?"
- `## Model Context` — if present, display: "Model context loaded from prior /pbi:load."
- `## Existing Measures` — if present, display: "Existing measures on file: [summary]"

For any section that exists with content, skip asking that question in Step 1.

---

### Step 1 — Full Upfront Intake

Collect all three context dimensions. For each one NOT already in `.pbi-context.md`, ask the question. Ask them ONE AT A TIME (not all at once) to keep the conversation focused.

**Question 1 — Business Question:**
"What business question are we solving? (e.g., 'Compare regional sales performance month-over-month' or 'Track customer retention by cohort')"

Wait for answer. Then proceed to next missing question.

**Question 2 — Data Model State:**
"Describe your data model — key tables, how they relate, and any known issues. (e.g., 'Sales fact → Date dimension, Product dimension. No customer table yet.')"

Wait for answer. Then proceed to next missing question.

**Question 3 — Existing Measures:**
"What measures already exist that are relevant? (paste names, or say 'none yet' / 'not sure')"

Wait for answer.

---

### Step 2 — Write Context

Read `.pbi-context.md` with Read tool. If the file does not exist, create it with a blank template containing these section headers: `## Business Question`, `## Model Context`, `## Existing Measures`, `## Last Command`, `## Command History`, `## Analyst-Reported Failures`. Then add or update these sections with the gathered answers:

- `## Business Question`: The stated business question, verbatim from user
- `## Existing Measures`: The user's answer about existing measures
- `## Last Command`: Command = `/pbi:deep`, Timestamp = current UTC ISO 8601, Outcome = `Deep mode intake complete`
- `## Command History`: Append row, keep 20 max

Do NOT modify `## Analyst-Reported Failures`.
Do NOT modify `## Model Context` (that's managed by /pbi:load).

Write the full file back with Write tool.

---

### Gate A→B — Intake to Model Review

Output exactly:

> **--- Gate: Model Review ---**
> Context gathered. Next: I will review your described model for structural issues before any DAX is written.
>
> Type **continue** to proceed, or **cancel** to stop the session.

Wait for the analyst's response.
- Response contains "continue" (case-insensitive, e.g., "continue", "continue please", "yes continue"): proceed to Phase B — Model Review.
- Response is "cancel": output "Session paused. Use /pbi:deep to restart." and stop.
- Any other response: re-output the gate prompt above. Do NOT advance.

---

## Phase B — Model Review

### Step B1 — Context Summary

Read `.pbi-context.md`. Output:

> **Current session context:**
> - Business question: [## Business Question content, or "(not set)"]
> - Model: [## Model Context first 2 lines, or "(not set)"]
> - Existing measures: [## Existing Measures content, or "(none noted)"]

If any field is "(not set)": pause and collect it before continuing (re-run the appropriate intake question from Phase A Step 1).

---

### Step B2 — Analyze Described Model

Read `.pbi-context.md ## Model Context`. Analyze the described model conversationally for health issues.

**This review operates on the described model context only. Do NOT read `$PBIP_DIR/` files. For file-level audit, direct the user to `/pbi:audit`.**

**CRITICAL checks:**
- **Bidirectional relationship** — any mention of "both directions", "both ways", "bi-directional", or filter going both ways
- **Many-to-many (M:M)** — any description where both sides of a relationship are "many", or explicit mention of "many-to-many" or "M:M"

**WARN checks:**
- **No date/calendar table** — no table described as a date, calendar, or time dimension
- **Isolated fact table** — a table with "Sales", "Orders", "Transactions" in its name and no described relationship

---

### Step B3 — Output Model Review Findings

Output:

> **Model Review:**
>
> [CRITICAL findings first — list each with a brief recommendation]
> [WARN findings next — list each with a brief recommendation]
> [If no issues found: "No structural issues detected in your described model."]
> [If model description is too sparse to evaluate any rule: "Model description is brief — no specific issues detected. If you have known relationship concerns, describe them and I'll flag risks."]
>
> [If any issues found]: "These findings won't block DAX work, but addressing them now will improve measure reliability."

Then proceed to Gate B→C.

---

### Gate B→C — Model Review to DAX Development

Output exactly:

> **--- Gate: DAX Development ---**
> Model review complete. Next: DAX development phase where we build measures for your business question.
>
> Type **continue** to proceed, or **cancel** to stop the session.

Wait for the analyst's response.
- Response contains "continue" (case-insensitive, e.g., "continue", "continue please", "yes continue"): proceed to Phase C — DAX Development.
- Response is "cancel": output "Session paused. Use /pbi:deep to restart." and stop.
- Any other response: re-output the gate prompt above. Do NOT advance.

---

## Phase C — DAX Development

### Step C1 — Context Summary

Read `.pbi-context.md`. Output:

> **Current session context:**
> - Business question: [## Business Question content, or "(not set)"]
> - Model: [## Model Context first 2 lines, or "(not set)"]
> - Existing measures: [## Existing Measures content, or "(none noted)"]

If any field is "(not set)": pause and collect it before continuing (re-run the appropriate intake question from Phase A Step 1).

---

### Step C2 — Open DAX Development

Output:

> **DAX Development phase:**
> Context saved to .pbi-context.md. All /pbi commands will use this context going forward.
>
> Available commands: **explain** · **format** · **optimise** · **comment** · **new** · **error** · **edit** · **audit** · **diff** · **commit** (see `/pbi:help` for full list)
>
> What would you like to work on first?
> When you've finished generating measures, say "done" to review your session before closing.

The user can now use any /pbi subcommand. The gathered context informs all responses via Session Context detection.

---

## Phase D — Final Verification

This phase activates ONLY when the analyst signals completion of the measures phase.

**Trigger phrases (case-insensitive):** "done", "that's all the measures", "finished", "I think we're good", "complete", "all done", "that's it"

**Do NOT trigger** this phase after each individual /pbi:new call. Wait for explicit analyst signal.

---

### Step D1 — Context Summary

Read `.pbi-context.md`. Output:

> **Current session context:**
> - Business question: [## Business Question content, or "(not set)"]
> - Model: [## Model Context first 2 lines, or "(not set)"]
> - Existing measures: [## Existing Measures content, or "(none noted)"]

---

### Step D2 — Final Verification Gate

Read `.pbi-context.md`. Collect:
- `## Business Question` — verbatim content
- All rows from `## Command History` where Command = `/pbi:new`

Output:

> **Final verification:**
>
> **Business question:** [verbatim content of ## Business Question]
>
> **Measures created this session:**
> [For each /pbi:new row in Command History: "- [Measure Name]"]
> (If no /pbi:new rows: "- No measures generated via /pbi:new in this session.")
>
> Do these measures answer the stated business question? (yes / no)

Wait for the analyst's response.
- "yes" (or clear affirmative — "yep", "yeah", "correct", "they do"): output close prompt:
  > All measures complete — confirm to close the deep mode session. (confirm / cancel)
- "no" or any negative: output "What's missing? Continue with /pbi:new." Resume Phase C state.
- Anything else: re-output the question above. Do NOT advance.

---

### Step D3 — Session Close

Wait for confirm/cancel response.
- "confirm": Output "Deep mode session closed. Use /pbi:diff or /pbi:commit to review and save your changes."
- "cancel" (or anything else): Output "Session kept open. Continue with /pbi:new or other commands." Resume Phase C state.

---

## Anti-Patterns

- NEVER enter deep mode unless the user explicitly typed `/pbi:deep` — no automatic upgrade
- NEVER ask all 3 intake questions at once — ask one, wait, ask next
- NEVER re-ask a question if the answer is already in `.pbi-context.md`
- NEVER advance past a phase gate on vague input ("ok", "sounds good", "yes") — the response must contain "continue" (case-insensitive). Re-output the gate.
- NEVER run model review against `$PBIP_DIR/` files — Phase B operates on described context only. For file-level audit, direct the user to `/pbi:audit`.
- NEVER generate DAX before Gate A→B is confirmed — model review must complete first
- NEVER trigger the final verification gate (Phase D) after each individual /pbi:new call — it fires only on analyst completion signal
- NEVER advance past the final gate if the business question check returns "no" — offer to continue generating
- NEVER impose gates on individual /pbi:new calls within Phase C — gates are at phase boundaries only

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.