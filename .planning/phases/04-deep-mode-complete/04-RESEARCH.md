# Phase 4: Deep Mode Complete - Research

**Researched:** 2026-03-14
**Domain:** Claude Code skill markdown — conversational state machine, phase gate pattern, context re-injection
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PHASE-01 | User entering deep mode sees a model review phase that analyzes their described model and surfaces health issues (M:M relationships, missing date table, bidirectional filters) before any DAX is written | Model health rules already implemented in audit.md (R-01 bidirectional, D-01 missing date table, R-02/R-03 relationship issues). Deep mode model review reuses that rule logic against the user's described model (paste-in context), not PBIP files. |
| VERF-01 | User in deep mode must confirm at each phase boundary before the session advances to the next phase (hard gate — no auto-advance) | Gate pattern already proven in deep.md Step 4 (measures gate). Phase gates use the same pause-and-wait pattern: output gate prompt, list explicit continue/cancel tokens, hold until matched. |
| VERF-02 | User completing deep mode sees a final gate that checks the output answers the business question stated at the start of the session | deep.md Step 4 already implements a partial version of this. Phase 4 must tighten it: the final gate must be a hard stop that restates the business question verbatim from `.pbi-context.md ## Business Question` and block session close until explicitly confirmed. |
| VERF-03 | User at the start of each deep-mode phase sees an explicit context summary (tables, relationships, existing measures, business question) restated to prevent drift | No current implementation. New requirement: at each phase transition, before the next phase begins, output a compact context block drawn from `.pbi-context.md`. |
</phase_requirements>

---

## Summary

Phase 4 extends `commands/deep.md` from a two-step intake+gate workflow into a fully structured four-phase session: (1) context intake, (2) model health review, (3) DAX development, and (4) final verification. The current `deep.md` already handles phases 1 and 3 well — the gap is the model review phase (PHASE-01), hard gate enforcement between all phases (VERF-01), context re-injection at each phase start (VERF-03), and hardening the existing end-of-session gate to block until confirmed (VERF-02).

All work is pure markdown instruction editing in `commands/deep.md` and an update to `tests/acceptance-scenarios.md` (new group for Phase 4 behaviors). No new files or dependencies are needed. The model health review logic reuses the same analysis rules already established in `audit.md` but applied conversationally to a user-described model — it does not require PBIP file access.

The skill operates as a stateful instruction set that Claude executes step by step within a conversation. "Hard gates" are implemented as explicit output patterns that pause and wait for a specific confirmation token, with an explicit instruction to hold and re-output the gate if the user provides anything other than the expected token.

**Primary recommendation:** Rewrite `commands/deep.md` to implement a four-phase structure with hard gates between each phase and context re-injection at each phase start. Add Phase 4 acceptance test scenarios to `tests/acceptance-scenarios.md`.

---

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| `commands/deep.md` | Current file (v4.0 rewrite) | Main implementation target — all four phases live here | Already routed from SKILL.md; single-file change |
| `.pbi-context.md` | Existing schema | State store for business question, model context, existing measures, command history | All commands already read/write this file; no schema changes needed |
| `tests/acceptance-scenarios.md` | Existing file | Manual test script; Phase 4 scenarios appended as a new group | Established pattern from Phase 1 and Phase 2 |

### No New Dependencies

This phase adds no npm packages, no new tools, no new command files. It is entirely a markdown instruction update to one existing file plus new test scenarios.

---

## Architecture Patterns

### Recommended Phase Structure in deep.md

The new `deep.md` implements four named phases in sequence:

```
Phase A — Context Intake       (already exists as Steps 0–2, keep it)
Phase B — Model Review         (new: PHASE-01)
Phase C — DAX Development      (already exists as Step 3 / measures work)
Phase D — Final Verification   (already exists as Step 4, harden for VERF-02)
```

Between each phase: a hard gate (VERF-01). At the start of each phase: a context summary block (VERF-03).

### Pattern 1: Hard Gate

**What:** A phase boundary where the session explicitly pauses and will not advance until the user types a specific confirmation token.

**When to use:** Between Phase A→B, Phase B→C, and at the final verification step (Phase D).

**Implementation:**

```markdown
### Gate: [Gate Name]

Output exactly:

> **--- Phase Gate ---**
> [Summary of what was completed in the previous phase]
> [One-sentence description of what the next phase will do]
>
> Type **continue** to proceed, or **cancel** to stop.

Wait for the analyst's response.
- If the response is "continue" (case-insensitive): proceed to the next phase.
- If the response is "cancel": output "Session paused. Type /pbi deep to resume." and stop.
- If the response is anything else: re-output the gate prompt. Do NOT advance.
```

**Key discipline:** The third branch ("anything else") is what makes it a hard gate. Claude must re-output the gate rather than interpreting a vague response as confirmation.

### Pattern 2: Context Re-injection Block

**What:** A compact context summary output at the start of each phase, drawn from `.pbi-context.md`.

**When to use:** At the beginning of Phase B, Phase C, and Phase D.

**Implementation:**

```markdown
### Context Summary

Read `.pbi-context.md`. Output:

> **Session context:**
> - Business question: [content of ## Business Question, or "not yet set"]
> - Model: [summary from ## Model Context, max 2 lines]
> - Existing measures: [content of ## Existing Measures, or "none noted"]
>
> If any field shows "not yet set": pause and gather it before continuing.
```

This directly satisfies VERF-03. The "if any field shows not yet set" fallback handles the edge case where a user jumps to deep mode without completing full intake.

### Pattern 3: Model Health Review (PHASE-01)

**What:** A conversational health check of the user's described model, run before any DAX work begins.

**When to use:** Phase B — after intake is complete and gate A→B is confirmed.

**Rules to apply (from audit.md, adapted to conversational context):**

| Rule | Check | Source in audit.md |
|------|-------|--------------------|
| R-01 | Bidirectional filter (CRITICAL) | Step 2a |
| R-02/R-03 | Missing or isolated relationships (WARN) | Step 2a |
| D-01 | No date table (WARN) | Step 2c |
| D-02 | Date table with no date column (INFO) | Step 2c |
| M:M heuristic | Many-to-many relationship (CRITICAL) | Detect when user describes both ends of a relationship as "many" |

**Implementation approach:** Parse the user's model description from `## Model Context` (already written in Phase A). Apply the rules conversationally — no file reading needed. Output findings in the same CRITICAL / WARN / INFO format audit.md uses.

```markdown
### Phase B — Model Review

Read `.pbi-context.md`. Extract ## Model Context.

Analyze the described model for:
1. **Bidirectional relationships** — any mention of "both directions", "both ways", "bi-directional", or filter going both ways → CRITICAL
2. **Many-to-many** — any mention of "many-to-many", "M:M", or both sides described as "many" → CRITICAL
3. **Missing date table** — no table described as a date/calendar/time dimension → WARN
4. **Isolated tables** — tables with no described relationships → WARN (if name pattern suggests a fact table)

Output findings:
> **Model Review:**
> [CRITICAL findings first, then WARN, then INFO]
> [If no issues: "No structural issues detected in your described model."]
>
> [If findings exist]: "These issues are worth addressing before building measures. Continue anyway?"
```

**Important constraint:** The model review only operates on the described model context — it does NOT run PBIP file reads. PBIP users who want file-level analysis should use `/pbi audit`. The model review is intentionally lightweight.

### Pattern 4: Final Verification Gate (VERF-02 hardening)

The current Step 4 in `deep.md` already implements the business question check but it can auto-advance if the user provides an ambiguous answer. The hardened version:

```markdown
### Phase D — Final Verification

Read `.pbi-context.md`. Collect:
- ## Business Question (verbatim)
- ## Command History rows where Command = /pbi new

Output:
> **Final check:**
> Business question on file: "[verbatim business question]"
>
> Measures created this session:
> [list from /pbi new rows in Command History]
>
> Do these measures answer the stated business question? (yes / no)

Wait for response.
- "yes" (case-insensitive, exact match or clear affirmative): output close confirmation prompt
- "no" or any negative: output "What's missing? Continue with /pbi new." Do NOT advance.
- Anything else: re-output the question. Do NOT advance.
```

### Anti-Patterns to Avoid

- **Gate skipping:** Never interpret a free-text response as "continue" — the gate token must be exact (case-insensitive match).
- **Context hallucination:** Never synthesize context for the model review. Only analyze what the user explicitly described in `## Model Context`.
- **Premature DAX:** Never generate DAX before Phase B model review is complete and Gate A→B is confirmed.
- **Re-asking gathered context:** Each phase start reads `.pbi-context.md` — never ask for information already written there.
- **Hard-gating the measures gate mid-session:** VERF-01 gates are at phase boundaries only, not after each individual `/pbi new` call (that pattern was established in Phase 2 and must be preserved).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Model health rules | New rule logic from scratch | Reuse audit.md rules (R-01, D-01, R-02, M:M heuristic) conversationally | Rules already validated in production; reimplementing risks inconsistency |
| State persistence | New state sections in `.pbi-context.md` | Existing `## Business Question`, `## Model Context`, `## Existing Measures` sections | No schema changes needed — all context is already written in Phase A |
| Gate confirmation UX | Custom token schemes | Single "continue"/"cancel" token pair, case-insensitive | Simple, consistent with existing measures gate (uses "confirm"/"cancel") |

---

## Common Pitfalls

### Pitfall 1: Soft Gate (Interpreting Vague Responses)

**What goes wrong:** Gate prompt is output, user responds with something like "ok" or "sounds good" — Claude interprets this as confirmation and advances.

**Why it happens:** Claude's default behavior is to be helpful and interpret ambiguous responses charitably. Without an explicit "re-output if not matched" instruction, a soft acknowledgment gets treated as confirmation.

**How to avoid:** The gate instruction must have three explicit branches: (1) exact affirmative → proceed, (2) explicit negative → hold, (3) anything else → re-output the gate. Branch 3 is the critical discipline.

**Warning signs:** VERF-01 acceptance tests will catch this. If the test phrase "ok" advances a gate, the gate is soft.

### Pitfall 2: Context Drift Between Phases

**What goes wrong:** User completes Phase A (intake) and Phase B (model review), then in Phase C receives a DAX suggestion that doesn't reference the business question stated in Phase A.

**Why it happens:** The context summary block (VERF-03) is not output at Phase C start, so the business question becomes invisible to the downstream DAX work.

**How to avoid:** Every phase start outputs the context summary block. The instruction must explicitly read `.pbi-context.md` and surface `## Business Question` before entering the phase's work steps.

**Warning signs:** The phrase "business question" should appear in every phase's opening output. Check VERF-03 test scenarios.

### Pitfall 3: Model Review Applied to PBIP Files

**What goes wrong:** The deep mode model review tries to read `.SemanticModel/` files instead of only analyzing `## Model Context`.

**Why it happens:** The audit.md command reads PBIP files — if the model review instruction references audit.md steps without clarifying the scope, Claude may conflate the two.

**How to avoid:** State explicitly: "This review operates on the described model context only. Do NOT read `.SemanticModel/` files. For file-level audit, direct the user to `/pbi audit`."

**Warning signs:** If the model review step shows "PBIP_MODE=paste" as a blocker or reads TMDL files, it has drifted into audit.md behavior.

### Pitfall 4: Over-Gating (Gates on Individual Actions)

**What goes wrong:** A hard gate fires after every `/pbi new` call or every individual action, making the session tedious.

**Why it happens:** VERF-01 says "each phase boundary" — misread as "each action."

**How to avoid:** Gates are at phase boundaries only: A→B (after intake before model review), B→C (after model review before DAX work), and the final verification. The measures gate in Phase D fires once on the analyst's completion signal, not per measure.

**Warning signs:** If a test session requires more than 3 confirmation steps to build two measures, over-gating has occurred.

### Pitfall 5: Ignoring the Anti-Pattern Note in Current deep.md

**What goes wrong:** The current `deep.md` has an anti-pattern: "NEVER impose phase gates in Phase 1 — that's Phase 3 scope." When rewriting, this note is stale (Phase 1 refers to the original skill phase, not deep mode phase A). If the note is misread, the planner might think phase gates are still out of scope.

**Why it happens:** The note was written during Phase 1 planning to defer deep mode phase gates. Phase 4 is explicitly implementing those gates now.

**How to avoid:** Remove or update this anti-pattern note in the rewritten `deep.md`. Replace it with the correct current anti-patterns.

---

## Code Examples

### Hard Gate Instruction Block

```markdown
### Gate: Intake to Model Review

Output exactly:

> **--- Gate: Model Review ---**
> Context gathered. Next: I will review your described model for structural issues before any DAX is written.
>
> Type **continue** to proceed, or **cancel** to stop the session.

Wait for the analyst's response.
- Response is "continue" (case-insensitive): proceed to Phase B — Model Review.
- Response is "cancel": output "Session paused. Use /pbi deep to restart." and stop.
- Any other response: re-output the gate prompt above. Do NOT advance.
```

### Context Re-injection Block

```markdown
### Context Summary (output at each phase start)

Read `.pbi-context.md`. Output:

> **Current session context:**
> - Business question: [## Business Question content, or "(not set)"]
> - Model: [## Model Context content, first 2 lines, or "(not set)"]
> - Existing measures: [## Existing Measures content, or "(none noted)"]

If any field is "(not set)": pause and collect it before continuing (re-run the appropriate intake question from Step 1).
```

### Model Health Review (Phase B)

```markdown
### Phase B — Model Review

Read `.pbi-context.md ## Model Context`. Analyze the described model for these issues:

**CRITICAL checks:**
- Bidirectional relationship: any mention of "both directions", "both ways", or filter propagating both ways
- Many-to-many (M:M): any description where both sides of a relationship are "many"

**WARN checks:**
- No date/calendar table: no table described as a date, calendar, or time dimension
- Isolated fact table: a table with "Sales", "Orders", "Transactions" in its name and no described relationship

Output:

> **Model Review:**
>
> [CRITICAL section — list each CRITICAL issue with recommendation]
> [WARN section — list each WARN issue with recommendation]
> [INFO: "No structural issues detected." if all checks pass]
>
> [If issues found]: These findings won't block DAX work, but addressing them now will improve measure reliability.

Then proceed to Gate: Model Review to DAX.
```

### Phase D Final Verification Gate

```markdown
### Phase D — Final Verification

Read `.pbi-context.md`. Collect ## Business Question and all /pbi new rows from ## Command History.

Output:

> **Final verification:**
>
> **Business question:** [verbatim content of ## Business Question]
>
> **Measures created this session:**
> [For each /pbi new row in Command History: "- [Measure Name]"]
> (If no /pbi new rows: "- No measures generated via /pbi new in this session.")
>
> Do these measures answer the stated business question? (yes / no)

Wait for response.
- "yes" (or clear affirmative — "yep", "yeah", "correct", "they do"): output close prompt:
  > All measures complete — confirm to close the session. (confirm / cancel)
- "no" (or any negative): output "What's missing? Continue with /pbi new." Resume Phase C state.
- Anything else: re-output the question above. Do NOT advance.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| deep.md stub with intake only | Full four-phase structure with gates | Phase 4 (this phase) | Deep mode becomes a real structured workflow, not just a context-gathering preamble |
| Step 4 measures gate (soft — "yes" or free-text) | Hard gate with re-output on unmatched response | Phase 4 (this phase) | Prevents accidental session close; VERF-02 now genuinely enforced |
| No model review phase | Phase B model review before DAX | Phase 4 (this phase) | PHASE-01 satisfied; analyst sees health issues before wasted measure work |
| Context visible only during intake | Context summary block at each phase start | Phase 4 (this phase) | VERF-03 satisfied; drift between long phases eliminated |

**Deprecated/outdated in current deep.md:**
- Anti-pattern note "NEVER impose phase gates in Phase 1 — that's Phase 3 scope": stale deferral note from original Phase 1. Remove it when rewriting.
- Step 3 "What would you like to work on first?" open-ended prompt: replace with Gate A→B leading into structured Phase B then Phase C.

---

## Open Questions

1. **Gate token: "continue" vs "confirm"**
   - What we know: The existing measures gate uses "confirm"/"cancel". VERF-01 gates are new.
   - What's unclear: Should VERF-01 gates use the same token ("confirm") for consistency, or a distinct token ("continue") to differentiate mid-session gates from the terminal close gate?
   - Recommendation: Use "continue"/"cancel" for mid-session phase gates (A→B, B→C) and preserve "confirm"/"cancel" for the terminal close gate in Phase D. This provides visual differentiation between "advance to next phase" and "close the session."

2. **Model review when Model Context is sparse**
   - What we know: The review reads `## Model Context` written during Phase A intake. That section contains whatever the analyst described — it may be vague ("Sales fact, Date dim") or detailed.
   - What's unclear: If the description is too sparse to evaluate any health rule, should the review ask a follow-up question or pass through silently?
   - Recommendation: If context is too sparse to evaluate, output: "Model description is brief — no specific issues detected. If you have known relationship concerns, describe them and I'll flag risks." This avoids blocking Phase B while still surfacing the pattern.

3. **Number of plans**
   - What we know: ROADMAP.md says "Plans: TBD" for Phase 4. Based on the changes required, the work is a single cohesive rewrite of `deep.md` plus acceptance test scenarios.
   - Recommendation: Two plans — Plan 01: rewrite `deep.md` (all four requirements); Plan 02: write Phase 4 acceptance test scenarios. Mirrors the same structure used in Phase 1 (implementation + tests as separate plans).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual acceptance scenarios (markdown) |
| Config file | none — manual execution |
| Quick run command | Open `tests/acceptance-scenarios.md` and run the Phase 4 group |
| Full suite command | Run all groups in `tests/acceptance-scenarios.md` and `tests/phase2-acceptance-scenarios.md` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PHASE-01 | Model review phase surfaces health issues before DAX | manual | n/a — conversational | ❌ Wave 0 (Phase 4 group in acceptance-scenarios.md) |
| VERF-01 | Hard gate holds until "continue" — does not advance on vague input | manual | n/a — conversational | ❌ Wave 0 |
| VERF-02 | Final gate blocks session close until business question confirmed | manual | n/a — conversational | ❌ Wave 0 |
| VERF-03 | Context summary output at start of each phase | manual | n/a — conversational | ❌ Wave 0 |

All test types are manual-only. Justification: the behaviors are Claude conversational responses — there is no automated runner that can execute `/pbi deep` and evaluate response quality. Manual acceptance scenarios are the established pattern for this project (see `tests/acceptance-scenarios.md` and `tests/phase2-acceptance-scenarios.md`).

### Sampling Rate

- **Per task commit:** Smoke test — run S4-01 (model review fires before DAX) and S4-03 (gate holds on "ok" input) from the Phase 4 scenario group
- **Per wave merge:** Full Phase 4 scenario group (estimated 6–8 scenarios)
- **Phase gate:** All acceptance scenario groups green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] Phase 4 group in `tests/acceptance-scenarios.md` — covers PHASE-01, VERF-01, VERF-02, VERF-03
- [ ] No framework install needed — existing markdown test file pattern is sufficient

---

## Sources

### Primary (HIGH confidence)

- Direct read of `commands/deep.md` — current implementation, Phase A intake (Steps 0–3) and Phase D gate (Step 4)
- Direct read of `commands/audit.md` — model health rules (R-01, D-01, R-02/R-03, M:M) reused in Phase B
- Direct read of `SKILL.md` — routing table confirms `deep` routes to `commands/deep.md`, sonnet direct execution
- Direct read of `tests/acceptance-scenarios.md` and `tests/phase2-acceptance-scenarios.md` — established test scenario format

### Secondary (MEDIUM confidence)

- `.planning/REQUIREMENTS.md` — PHASE-01, VERF-01, VERF-02, VERF-03 requirement descriptions
- `.planning/ROADMAP.md` — Phase 4 success criteria (5 criteria listed)
- `.planning/phases/01-skill-core-escalation/01-CONTEXT.md` — historical decision: "Full phase gates, model review phase, and verification gates are Phase 3 (now Phase 4) — out of scope here"

### Tertiary (LOW confidence)

None — all findings are grounded in direct file reads.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — implementation target (`commands/deep.md`) and test file (`tests/acceptance-scenarios.md`) are known existing files
- Architecture: HIGH — gate pattern is directly observed in existing deep.md Step 4; model health rules are directly observed in audit.md; no external dependencies
- Pitfalls: HIGH — soft gate risk is directly observable from the current Step 4 implementation which has an ambiguous "yes or any affirmative" branch; remaining pitfalls derived from reading existing anti-pattern notes

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (stable domain — no external libraries, no API versioning concerns)
