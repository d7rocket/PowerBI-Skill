# Architecture Research

**Domain:** Claude Code skill prompt — gate-based interrogation with phased execution
**Researched:** 2026-03-13
**Confidence:** HIGH (derived directly from GSD reference implementation in `new-project.md`, `questioning.md`, and `ui-brand.md`)

---

## Standard Architecture

### System Overview

A GSD-style skill `.md` file is a layered pipeline. The skill file IS the architecture: its sections define the components, and execution flows linearly through them. There is no runtime environment — Claude reads the file as instructions and executes it conversationally.

```
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 1: PREAMBLE                          │
│   <purpose>  |  <required_reading>  |  <auto_mode>          │
│   Declares intent. Forces context load before any action.   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 2: INTERROGATION                       │
│   Deep Questioning → Context Accumulation → Decision Gate   │
│   Inputs:  None (user conversation)                         │
│   Outputs: Resolved context object (mental model)           │
│   Gate:    "Ready to proceed?" — explicit user signal        │
└─────────────────────────────────────────────────────────────┘
                              ↓
                  [Context passes to all phases]
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              LAYER 3: EXECUTION PHASES                       │
│                                                             │
│   ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐ │
│   │  Phase 1   │  │  Phase 2   │  │ Phase 3  │  │Phase 4 │ │
│   │   Model    │→ │  Measures  │→ │ Visuals  │→ │ Polish │ │
│   │  Review    │  │  (DAX)     │  │          │  │        │ │
│   └─────┬──────┘  └─────┬──────┘  └────┬─────┘  └───┬────┘ │
│         ↓               ↓              ↓             ↓      │
│   [Verification]  [Verification] [Verification] [Final OK]  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              LAYER 4: VERIFICATION GATES                     │
│   After each phase: Does this answer the business question?  │
│   Pass → next phase                                         │
│   Fail → return to phase, address gap                       │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Preamble | Declare intent, force context load | `<purpose>`, `<required_reading>` tags; mandatory file reads before user interaction |
| Interrogation Layer | Extract data model state, business question, existing measures | Freeform open question → AskUserQuestion follow-ups → background checklist → decision gate |
| Context Object | Carry gathered facts across all phases | Assembled in Claude's context window from questioning; referenced explicitly in each phase |
| Execution Phase | Perform scoped work (model / measures / visuals / polish) | Stage banner → scoped instructions → outputs → hand-off to verification |
| Verification Gate | Confirm phase output answers the business question | Checkpoint box → explicit user signal (approve / describe issues) → conditional advance or re-work |
| Success Criteria | Define what completion means for the entire skill run | `<success_criteria>` block; each item is observable and checkable |

---

## Recommended File Structure

A single `.md` prompt file — not a directory. Internal sections ARE the structure.

```
pbi-skill.md
├── <purpose>                        # what the skill does and its value
├── <required_reading>               # files Claude must read before acting
│   └── (none needed — self-contained)
│
├── <interrogation_phase>            # Layer 2
│   ├── stage banner                 # GSD ► INTERROGATING
│   ├── opening question             # freeform "What are we building?"
│   ├── follow-up threads            # AskUserQuestion on vague answers
│   ├── pre-flight checklist         # 4 mandatory facts (background, not spoken)
│   └── decision gate                # "Ready to proceed?"
│
├── <phase_1_model_review>           # Layer 3 — first execution phase
│   ├── stage banner                 # GSD ► MODEL REVIEW
│   ├── scoped instructions          # what to do with gathered context
│   ├── outputs                      # what Claude produces
│   └── verification gate            # GSD ► VERIFYING + checkpoint box
│
├── <phase_2_measures>               # Layer 3 — second execution phase
│   ├── stage banner                 # GSD ► MEASURES
│   ├── scoped instructions          # DAX writing with context-awareness rules
│   ├── outputs
│   └── verification gate
│
├── <phase_3_visuals>                # Layer 3 — third execution phase
│   ├── stage banner
│   ├── scoped instructions
│   ├── outputs
│   └── verification gate
│
├── <phase_4_polish>                 # Layer 3 — fourth execution phase
│   ├── stage banner
│   ├── scoped instructions
│   ├── outputs
│   └── final verification gate      # full report review
│
├── <anti_patterns>                  # What Claude must never do
│   ├── no DAX before interrogation completes
│   ├── no duplicate measures
│   └── no skipping verification gates
│
└── <success_criteria>               # Observable outcomes for whole run
```

### Structure Rationale

- **`<purpose>` first:** Claude reads top-to-bottom; framing before instructions prevents misinterpretation of later sections.
- **`<required_reading>` before `<interrogation_phase>`:** Mandatory pre-load ensures context is available before any conversation begins. In GSD `new-project.md` this is the MANDATORY FIRST STEP.
- **Interrogation before all phases:** This is the core architectural constraint from PROJECT.md — "never write a line of DAX until business question, data model state, and existing measures are understood."
- **Verification gates co-located with phases:** Each phase section contains its own gate, not a separate global section. This mirrors GSD's verifier-per-phase pattern and prevents Claude from drifting past a failed gate.
- **`<anti_patterns>` and `<success_criteria>` at the end:** These serve as constraint rails. Claude will have read the full context by the time it acts, so they function as background rules during execution.

---

## Architectural Patterns

### Pattern 1: Mandatory Pre-Flight Check

**What:** The skill opens with a read of mandatory inputs before the first user interaction. For PBI-SKILL, this means establishing the four pre-flight facts before generating anything: (1) business question, (2) data model structure, (3) existing measures, (4) intended output format.

**When to use:** Any skill where later outputs depend on facts that must be gathered upfront. Absence of pre-flight is the exact failure mode described in PROJECT.md ("jumps to DAX without understanding context").

**Trade-offs:** Adds conversation turns at the start; user might feel it's slow. Eliminates all downstream rework from wrong assumptions — the cost is front-loaded and visible, not hidden in bad output.

**Example structure in .md:**
```
## Pre-Flight

Before any analysis or DAX, gather:

- [ ] Business question: what decision does this report support?
- [ ] Tables in scope (names, grain, relationships)
- [ ] Existing calculated columns and measures (names + what they compute)
- [ ] Desired output (single number, trend, comparison, breakdown)

Do not proceed to Phase 1 until all four are established.
```

---

### Pattern 2: Staged Context Injection

**What:** Context gathered in interrogation is explicitly restated at the start of each phase. Claude's context window is long but it can drift; restating "given that the business question is X and existing measures are Y..." anchors each phase to the gathered facts.

**When to use:** Multi-phase skills where context from Phase 1 must inform Phase 3 or 4. Without explicit restatement, later phases can produce outputs inconsistent with early findings.

**Trade-offs:** Adds verbosity to the skill file. Eliminates the failure mode where Phase 3 forgets what was established in interrogation.

**Example:**
```
## Phase 2: Measures

Using the context gathered in Pre-Flight:
- Business question: [recalled from interrogation]
- Existing measures: [recalled — do not duplicate these]
- Model structure: [recalled — respect grain and relationships]

Now write measures that...
```

---

### Pattern 3: Checkpoint Box Verification Gate

**What:** After each phase, pause with a formal checkpoint using GSD's checkpoint box pattern. Present what was produced, ask whether it answers the business question, and branch on the response: advance (pass) or re-work the phase (fail).

**When to use:** After every execution phase in the skill. This is the core verification mechanism from PROJECT.md requirement: "verification gate after each phase: confirm output answers the business question."

**Trade-offs:** Interrupts flow; user must actively respond. The interruption is the feature — it prevents cascading errors where a wrong Phase 1 output silently breaks Phases 2-4.

**Example:**
```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: Verification Required                           ║
╚══════════════════════════════════════════════════════════════╝

Model review complete. Findings:
- [finding 1]
- [finding 2]

Does this accurately reflect your data model?

──────────────────────────────────────────────────────────────
→ Type "approved" to proceed to measures, or describe what's wrong
──────────────────────────────────────────────────────────────
```

---

### Pattern 4: Decision Gate (Interrogation Exit)

**What:** The interrogation phase does not exit on a timer or question count — it exits when Claude has enough context to proceed AND the user signals readiness. This mirrors GSD's questioning decision gate exactly.

**When to use:** End of the interrogation phase only. Do not use mid-phase.

**Trade-offs:** Can extend the questioning turn count if the user is vague. That is correct behavior — it is preferable to over-question than to under-question and produce wrong DAX.

**Example:**
```
When you could accurately describe the business question, model structure,
and existing measures to a third party, offer to proceed:

"I think I have what I need. Ready to start with model review?"

If user says yes → proceed to Phase 1.
If user says no or wants to add more → continue questioning.
```

---

## Data Flow

### Interrogation → Execution Flow

```
User opens skill
    ↓
Interrogation Phase (freeform + AskUserQuestion threads)
    ↓
Context Object assembled (4 mandatory facts + any additional)
    |
    ├──→ Business Question
    ├──→ Data Model State (tables, relationships, grain)
    ├──→ Existing Measures (names, what they compute)
    └──→ Desired Output Format
    ↓
Phase 1: Model Review
    ↓   (uses: Data Model State + Business Question)
Verification Gate 1
    ↓ (approved)
Phase 2: Measures
    ↓   (uses: all 4 context facts + Phase 1 findings)
Verification Gate 2
    ↓ (approved)
Phase 3: Visuals
    ↓   (uses: Business Question + Phase 2 measure names)
Verification Gate 3
    ↓ (approved)
Phase 4: Polish
    ↓   (uses: all prior phase outputs)
Final Verification Gate
    ↓ (approved)
Done
```

### Verification Branch Flow

```
Phase N completes
    ↓
Checkpoint Box presented
    ↓
User response
    ├── "approved" / "yes" / positive signal
    │       ↓
    │   Advance to Phase N+1
    │
    └── describes issue / negative signal
            ↓
        Re-enter Phase N with correction context
            ↓
        Repeat until approved
```

### Key Data Flows

1. **Pre-flight → Phase 1:** Data model structure flows from interrogation into model review. Phase 1 cannot run without it — the skill must block if model facts are incomplete.
2. **Phase 1 findings → Phase 2:** Model review findings (e.g., "table X is at day grain", "measure Y already exists") constrain what DAX Phase 2 is allowed to write. Explicit pass-through prevents duplication.
3. **Phase 2 measure names → Phase 3:** Visual recommendations in Phase 3 must reference the actual measure names produced in Phase 2, not hypothetical ones.
4. **Business question → all gates:** Every verification gate asks a variant of "does this answer the business question?" The business question extracted in interrogation must be restated at every gate to anchor the check.

---

## Scaling Considerations

This is a conversational skill file, not a software service. "Scale" means complexity of the Power BI project being discussed, not user load.

| Project Complexity | Architecture Adjustments |
|--------------------|--------------------------|
| Simple report (1-2 tables, <10 measures) | Interrogation can be brief; Phase 1 will be short; skill runs quickly |
| Medium report (5-10 tables, 10-30 measures) | Full interrogation needed; Phase 2 may produce multiple DAX iterations within one phase run |
| Complex model (10+ tables, 30+ measures, multiple fact tables) | Interrogation must capture full relationship map; Phase 1 should produce a written summary Claude reads back; Phase 2 may need to be split by subject area |

### Scaling Priorities

1. **First bottleneck:** Interrogation quality. If the user gives thin answers, all four phases produce bad output. The skill must probe aggressively and block advancement until context is solid.
2. **Second bottleneck:** Phase 2 scope creep. Complex models tempt Claude to write every possible measure rather than scoped ones. The skill's anti-patterns section must explicitly prohibit writing measures not tied to the stated business question.

---

## Anti-Patterns

### Anti-Pattern 1: Premature DAX Generation

**What people do:** Accept a vague request ("help me with a measure for sales") and immediately write DAX.

**Why it's wrong:** The exact failure mode PROJECT.md was built to fix. Generated DAX may duplicate existing measures, violate model grain, or answer a question the user never asked.

**Do this instead:** Block DAX generation with a hard rule in the skill: "Do not write any DAX until Phase 2 begins. Phase 2 cannot begin until the Pre-Flight checklist is complete and Verification Gate 1 is passed."

---

### Anti-Pattern 2: Implicit Gate Passing

**What people do:** Claude completes a phase, briefly mentions the output, and continues to the next phase without an explicit user approval.

**Why it's wrong:** Verification gates that don't stop are not gates. The user never confirms that the model review was accurate; Claude silently carries a wrong assumption forward.

**Do this instead:** Use the checkpoint box pattern. The visual weight of the box signals "this is a hard stop, not a summary." Require explicit text response before advancing.

---

### Anti-Pattern 3: Stateless Phases

**What people do:** Each phase operates independently without referencing what was gathered in interrogation or discovered in prior phases.

**Why it's wrong:** Phases become disconnected. Phase 3 visual recommendations don't match Phase 2 measure names. Phase 2 DAX duplicates measures found in Phase 1.

**Do this instead:** Begin each phase with an explicit "Using context from interrogation: [facts]" section. This forces continuity and makes the context-awareness requirement visible.

---

### Anti-Pattern 4: Checklist-Walking Interrogation

**What people do (from questioning.md):** Work through a domain list regardless of what the user said. "What tables do you have? What is your grain? What are your existing measures?" — fired as a script.

**Why it's wrong:** Users disengage. Critical context that didn't fit the script gets missed. The conversation feels like a form, not a thinking partnership.

**Do this instead:** Open with "What are you trying to figure out?" Follow their answer. The four pre-flight facts must be gathered by the end of interrogation, but the path to them should follow the user's thread, not a preset order.

---

## Integration Points

### External Services

None. The skill is conversational-only. PROJECT.md explicitly excludes Power BI API integration. Claude cannot read `.pbix` files — all model knowledge comes from user-described context during interrogation.

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Power BI Desktop | None — conversational only | User describes model; Claude never reads files |
| Power BI Service | None | Out of scope per PROJECT.md |
| DAX Studio | None | User may paste query results as text input during interrogation |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Interrogation → Phase 1 | Context window only | No file written; facts live in conversation history |
| Phase N → Gate N | Sequential in same conversation turn | Phase output and gate are in one response block |
| Gate N → Phase N+1 | User approval triggers continuation | Gate is the only mechanism that allows phase advance |
| Any phase → Interrogation | Return path for unresolved ambiguity | If Phase 2 reveals a missing fact, skill should surface it and ask, not guess |

---

## Build Order Implications

The skill must be built in dependency order. Each layer depends on the one before it being correct.

**Build order for PBI-SKILL v2:**

1. **Interrogation layer first.** This is the highest-leverage component. Get the pre-flight checklist right, the question threads right, and the decision gate right. Everything else depends on interrogation quality.

2. **Verification gates second.** Before writing phase logic, define what "pass" and "fail" look like for each gate. This prevents writing phases that produce output that can't be verified.

3. **Phase 1 (Model Review) third.** Scope is narrow: take interrogation context, produce a structured summary of the model. No DAX. Verify the summary is accurate before proceeding.

4. **Phase 2 (Measures) fourth.** Hardest phase. Must enforce: no duplicates, respect grain, tie every measure to the business question. Write last to ensure interrogation and Phase 1 are solid enough to constrain it properly.

5. **Phases 3 and 4 (Visuals, Polish) last.** These are downstream of the hardest work. Build them after Phases 1-2 are stable.

6. **Anti-patterns and success criteria woven in throughout.** These are not a separate step — they are written as constraints inside each phase and gate as the phases are built.

---

## Sources

- `C:/Users/DeveshD/.claude/get-shit-done/workflows/new-project.md` — GSD reference implementation; stage banners, decision gate pattern, agent spawning structure, `<required_reading>` pre-flight pattern (HIGH confidence — direct source)
- `C:/Users/DeveshD/.claude/get-shit-done/references/questioning.md` — Interrogation philosophy, question types, context checklist, decision gate, anti-patterns (HIGH confidence — direct source)
- `C:/Users/DeveshD/.claude/get-shit-done/references/ui-brand.md` — Stage banner format, checkpoint box pattern, status symbols (HIGH confidence — direct source)
- `C:/Users/DeveshD/.planning/PROJECT.md` — Requirements and constraints for PBI-SKILL v2 (HIGH confidence — direct source)

---
*Architecture research for: Claude Code skill prompt (gate-based interrogation + phased execution)*
*Researched: 2026-03-13*
