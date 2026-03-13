# Project Research Summary

**Project:** PBI-SKILL v2 — Conversational Power BI / DAX assistant (Claude Code skill)
**Domain:** Structured conversational AI skill for Power BI development
**Researched:** 2026-03-13
**Confidence:** HIGH

## Executive Summary

PBI-SKILL v2 is a Claude Code slash command: a structured `.md` prompt file that drives a phase-gated conversational workflow for Power BI report development. The product is not a software application — it is a prompt architecture that enforces structured interrogation, phased execution, and verification before any DAX is written. The GSD system on this machine is the canonical reference implementation; all architectural patterns, file format conventions, and interaction mechanisms are derived directly from it. There is no runtime dependency, no compiled artifact, and no external API integration required.

The recommended approach is to build the skill as a thin command wrapper (`~/.claude/commands/pbi/skill.md`) that loads a deeper workflow file. The workflow enforces four phases — model review, measures (DAX), visuals, and polish — each preceded by an interrogation phase and followed by a verification gate. The interrogation phase is the differentiator: it extracts business question, data model structure, existing measures, and visual consumption context before any code is generated. This is the direct inversion of the v1 failure mode (DAX generated without model context) and the mechanism that distinguishes the skill from Microsoft Copilot and generic LLM prompting.

The primary risk is not technical — it is workflow discipline. Research confirms that LLMs lose 39% accuracy across multi-turn conversations and that verification gates which don't require specific testable results degrade into rubber stamps. Both risks have known mitigations: explicit context carry-forward at every phase boundary and verification gates that require named tests with expected values, not impressionistic "does this look right?" prompts. All anti-patterns are documented in GSD's reference implementation and can be applied directly.

---

## Key Findings

### Recommended Stack

This skill requires no software stack in the conventional sense. The "stack" is a composition of file format conventions, invocation mechanisms, and interaction patterns — all interpreted at runtime by Claude. Skill files are `.md` files registered in `~/.claude/commands/pbi/` and become available as `/pbi:skill`. No npm, no runtime, no build step.

The GSD reference implementation at `~/.claude/get-shit-done/` is the authoritative source for every pattern used in this skill. All findings are derived from direct inspection of production GSD files (HIGH confidence). No external library or version dependency is required.

**Core technologies:**
- Claude Code slash command (`.md`): Skill definition and invocation — the native mechanism; files in `~/.claude/commands/[namespace]/` are auto-discovered and invocable
- YAML frontmatter: Skill metadata and tool permissions — required; omitting it blocks tool access including `AskUserQuestion`
- XML-tagged sections (`<purpose>`, `<step>`, `<success_criteria>`): Structural prompt organization — creates machine-readable logical boundaries Claude treats as execution contracts
- `AskUserQuestion` tool: Structured interrogation with option lists — enforces option-based UI over freeform prompts; header max 12 characters enforced
- Thin command + deep workflow separation: Command file (~40 lines) loads a workflow file (~300-500 lines) via `@path` reference — keeps invocation stub maintainable while concentrating logic

### Expected Features

The skill's feature set follows a strict dependency chain: interrogation gates everything downstream. Features that bypass this chain conflict with the skill's core value and are explicitly excluded.

**Must have (table stakes — P1):**
- Pre-flight interrogation protocol (business question, grain, model topology, existing measures, visual placement) — this IS the differentiator; without it the skill is just another DAX assistant
- Data model state intake (tables, relationships, date table name and key type, cardinality) — all DAX correctness depends on this context
- Existing measures audit before writing new ones — prevents duplicate measure sprawl, the most common waste in Power BI projects
- Context-aware DAX output (uses user's actual table and column names, not placeholders) — the most common complaint about AI-generated DAX; non-context-aware output is immediately unusable
- Phase-gated workflow: model review → measures → visuals → polish — structure prevents the v1 failure mode; phases gate each other
- Verification gate at end of each phase (requires named test and expected value, not "does this look right?") — prevents bad output from propagating across phases
- Visual type recommendation tied to data shape and business question — completes the phase scope at low implementation cost
- Report polish checklist (high-signal items: missing titles, color-only encoding, 3D charts, slicer overload) — closes the workflow loop

**Should have (competitive differentiators — P2, add after v1 validation):**
- Duplicate measure detection heuristic — conversational check against user-described existing measures before generation
- Model health flags during intake — surface M:M relationships, missing date table, bidirectional filters, high-cardinality columns proactively
- Visual anti-pattern warnings (pie charts > 8 slices, KPI cards without context, slicers that contradict measure assumptions) — one-sentence callouts, high signal-to-noise

**Defer (v2+):**
- DAX pattern selection (pattern-first generation against a curated pattern library) — high value but requires pattern library and classification logic; needs v1 to prove base workflow first
- Phase completion confirmation with explicit rollback gate — risk of over-engineering before basic phase discipline is validated
- Business question traceability as persistent inline annotation throughout all phases — UX refinement for v2

**Anti-features (deliberately excluded):**
- DAX tutorial generation — conflicts with phase discipline; shifts skill to educational mode
- Generic report templates — false sense of progress without model context
- Power BI API / `.pbix` file operations — this is a conversational `.md` prompt; no file system or service connector access
- Free-form "ask me anything" mode — destroys structured workflow; use parking-lot pattern instead ("noted — we'll address that in phase X")

### Architecture Approach

The skill architecture is a layered pipeline: preamble → interrogation → phased execution → verification gates. The skill `.md` file IS the architecture; its sections define the components and execution flows linearly through them. There is no runtime environment — Claude reads the file as instructions and executes conversationally. The interrogation layer is the highest-leverage component: it produces a context object (four mandatory facts) that all subsequent phases depend on. Each execution phase consumes from this context object and produces phase-specific output, which is then evaluated by a co-located verification gate before the next phase begins.

**Major components:**
1. **Preamble** (`<purpose>`, `<required_reading>`) — declares intent and forces context load before any user interaction; top position is non-negotiable
2. **Interrogation Layer** — extracts four mandatory facts (business question, data model structure, existing measures, visual consumption context) using freeform open question followed by `AskUserQuestion` threads; exits only via decision gate with explicit user readiness signal; never exits on question count or timer
3. **Context Object** — structured summary of interrogation findings carried forward explicitly (not implicitly via conversation history) into every phase; mitigates the documented 39% multi-turn accuracy drop
4. **Execution Phases (1-4)** — scoped, sequential; each opens by restating binding context constraints from interrogation; no phase may reference or generate content from a later phase
5. **Verification Gates** — co-located with each phase; require a specific named test and expected value; branch on explicit user approval (advance) or explicit issue description (re-work phase); never advance on impressionistic "looks good"
6. **Anti-Patterns Block** — hard constraints placed at end of skill file; active throughout execution as background rails

**Build order (dependency-driven):**
1. Interrogation layer first — everything depends on its quality
2. Verification gate definitions second — define pass/fail before writing phases
3. Phase 1 (Model Review) third — narrow scope, no DAX, establishes context carry-forward
4. Phase 2 (Measures) fourth — hardest phase; constrained by Phase 1 findings
5. Phases 3-4 (Visuals, Polish) last — downstream of the hard work

### Critical Pitfalls

1. **DAX generated before data model is understood** — Hard gate in the skill: no DAX appears until pre-flight checklist is complete and Phase 1 verification gate passes. Any measure in Phase 1 output is a failure signal.

2. **Vague interrogation questions that produce vague context** — Questions must be specific enough that "yes/no + one detail" is a sufficient answer. Mandatory buckets: relationship direction (single vs. bidirectional), date table key type and name, existing measure names and purpose. Conditional buckets: date key type (for time intelligence), parent level (for % of total).

3. **Verification gates that become rubber stamps** — Gates must specify what to test and what the expected value is. "Does this look right?" is an anti-pattern. Correct form: "Apply this measure to a matrix with [dimension] on rows. For [known period], does the result match [expected value]?"

4. **Context loss across phases (documented: 39% accuracy drop in multi-turn conversations)** — Explicit context ledger injected at the start of every phase. Phases 2-4 must open with: confirmed table names, confirmed relationships, confirmed existing measures, confirmed business question. Relying on Claude remembering earlier turns is the failure mode.

5. **DAX written without awareness of visual consumption context** — "Where will this measure be used?" is a required interrogation field, not optional context. The answer determines whether `CALCULATE` with table filter, `SELECTEDVALUE`, `HASONEVALUE`, or iterator patterns is correct. The generated measure must note its assumed consumption context.

6. **Skill file becomes a tutorial** — The skill file must contain only workflow instructions, phase gates, question templates, and output format requirements. No DAX concept explanations, no Power BI background paragraphs. Test: if a section could be replaced with "Claude already knows this," delete it.

---

## Implications for Roadmap

Research points to a 4-phase delivery structure with a foundational interrogation layer built first. Phase order is dictated by the dependency chain in FEATURES.md and the build order derived from ARCHITECTURE.md.

### Phase 1: Interrogation Foundation
**Rationale:** The interrogation layer is the highest-leverage component. Everything else depends on it. Building it first also validates the core differentiator before any DAX logic is written. This is the direct response to the v1 failure mode.
**Delivers:** A working pre-flight interrogation that extracts all four mandatory context facts (business question, data model structure, existing measures, visual consumption context) and exits through a decision gate requiring explicit user readiness signal
**Addresses:** Pre-flight interrogation protocol, data model state intake, existing measures audit (table stakes P1 features)
**Avoids:** Pitfall 1 (DAX before model understood), Pitfall 2 (vague interrogation), Pitfall 4 (context loss — establishes what the context object must contain)
**Research flag:** Well-documented patterns (GSD `questioning.md`, `new-project.md` decision gate). Skip `/gsd:research-phase` — apply GSD patterns directly.

### Phase 2: Verification Gate Architecture
**Rationale:** Define what pass/fail looks like for each gate before writing phase logic. This prevents writing phases that produce unverifiable output. ARCHITECTURE.md recommends this explicitly as step 2 of the build order.
**Delivers:** Checkpoint box pattern for each phase (model review, measures, visuals, polish), each with a specific test requirement and explicit branch logic (advance vs. re-work)
**Addresses:** Verification gate (table stakes P1), phase-gated workflow structure (P1)
**Avoids:** Pitfall 3 (rubber-stamp verification), Pitfall 4 (context loss — gates are the mechanism that surfaces context drift before it propagates)
**Research flag:** Standard patterns available (GSD `ui-brand.md` checkpoint box format). Skip `/gsd:research-phase`.

### Phase 3: Phase 1 — Model Review
**Rationale:** Narrow scope (no DAX, just a structured model summary), makes it the safest first execution phase to build. Establishes the context carry-forward pattern that Phases 2-4 inherit. Cannot be built before interrogation and gate architecture are stable.
**Delivers:** Model review phase that takes interrogation context and produces a structured, human-readable summary of the data model (tables, relationships, health flags), with a verification gate requiring confirmation before any measure writing begins
**Addresses:** Data model state intake (completes P1), model health flags (P2 — partial; surface M:M, missing date table, bidirectionality during model review)
**Avoids:** Pitfall 1 (hard gate: no DAX in this phase), Pitfall 3 (gate is defined in Phase 2), Pitfall 5 (visual context already captured in interrogation)
**Research flag:** Standard patterns. Skip `/gsd:research-phase`.

### Phase 4: Phase 2 — Measures (DAX)
**Rationale:** Hardest phase; requires interrogation, gate architecture, and model review to all be stable before attempting it. Must enforce no-duplicate rule, respect grain, tie every measure to the business question, and select correct patterns based on visual consumption context.
**Delivers:** Context-aware DAX generation (uses actual table/column names), one measure per response, 2-sentence pattern rationale with each measure, consumption-context note, verification gate requiring a named test against an expected value
**Addresses:** Context-aware DAX output (P1), verification gate — measures phase (P1), duplicate measure detection (P2 — integrated as pre-generation check), DAX evaluation context awareness (critical pitfall)
**Avoids:** Pitfall 1 (gated behind Phase 3), Pitfall 3 (specific testable gate), Pitfall 4 (context ledger re-injected at phase open), Pitfall 5 (consumption context from interrogation drives pattern selection)
**Research flag:** May benefit from `/gsd:research-phase` for DAX pattern selection if adding P3 feature (pattern-first generation). Skip for v1 scope.

### Phase 5: Phases 3 and 4 — Visuals and Polish
**Rationale:** Downstream of the hardest work. Low complexity, high perceived value. Build after Phases 1-2 (model review and measures) are stable, since visual recommendations must reference actual measure names from Phase 4.
**Delivers:** Visual type recommendations grounded in data shape and business question; report polish checklist (missing titles, color-only encoding, 3D charts, slicer overload); final verification gate
**Addresses:** Visual type recommendation (P1), report polish checklist (P1), visual anti-pattern warnings (P2 — integrate into polish phase), audience/output format question (confirmed in interrogation)
**Avoids:** Pitfall 4 (context ledger re-injected, Phase 3 output references Phase 4 measure names explicitly)
**Research flag:** Standard patterns. Skip `/gsd:research-phase`.

### Phase Ordering Rationale

- **Interrogation before everything:** The dependency chain in FEATURES.md is explicit — business question gates model intake, which gates measures audit, which gates DAX generation. No phase can produce correct output without the one before it.
- **Gates before phases:** Defining verification criteria before writing phases prevents the failure mode where phases produce output that can't be meaningfully evaluated. ARCHITECTURE.md recommends this order explicitly.
- **Model review before measures:** Phase 1 (model review) discovers facts (existing measures, relationship direction, grain) that directly constrain what Phase 2 (measures) is allowed to write. Building Phase 2 without Phase 1 findings in place produces the context-drift anti-pattern.
- **Visuals and polish last:** Both depend on measure names and structure from Phase 2. Building them in parallel with measures creates inconsistency.
- **Single skill file, not a directory:** For v1, all logic lives in one workflow file loaded by a thin command wrapper. No session state file needed — the skill is single-session. Add `STATE.md` persistence in v2 if context compaction across sessions becomes a user need.

### Research Flags

Phases with well-documented patterns (skip `/gsd:research-phase`):
- **Phase 1 (Interrogation):** GSD `questioning.md` and `new-project.md` decision gate are direct source. Apply patterns verbatim.
- **Phase 2 (Verification Gates):** GSD `ui-brand.md` checkpoint box format is the standard. No research needed.
- **Phase 3 (Model Review):** Narrow scope with no DAX. Standard GSD phase pattern applies.
- **Phase 5 (Visuals, Polish):** Low complexity, standard recommendation patterns.

Phases that may benefit from deeper research during planning:
- **Phase 4 (Measures / DAX):** If DAX pattern selection (P3 feature) is pulled into v1 scope, a pattern library and classification logic will need design. Current v1 scope (context-aware generation without pattern-first classification) does not require research. Flag for v2 planning.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All findings from direct inspection of GSD reference implementation on this machine — the authoritative source |
| Features | HIGH (core), MEDIUM (polish/differentiators) | Core P1 features grounded in SQLBI expert sources and Microsoft Learn; P2/P3 features grounded in community sources and domain inference |
| Architecture | HIGH | Derived directly from GSD production workflow files (`new-project.md`, `questioning.md`, `ui-brand.md`) — no inference required |
| Pitfalls | HIGH (critical pitfalls), MEDIUM (skill-file specifics) | Critical pitfalls grounded in peer-reviewed research (arXiv multi-turn study) and authoritative domain sources (SQLBI); skill-file specifics from Anthropic best practices |

**Overall confidence:** HIGH

### Gaps to Address

- **DAX pattern classification (v2):** The research identifies DAX pattern-first generation as a high-value v2 differentiator but does not define the pattern library structure. When pulled into scope, a separate research step is needed to define the pattern taxonomy (ratio, running total, period comparison, ranking, conditional accumulation) and the classification logic that maps interrogation answers to pattern categories.

- **Brownfield model handling:** The skill design assumes the user is describing their model conversationally. For users with complex existing models (10+ tables, 30+ measures), the interrogation may need a structured capture format (written model summary the user fills in). This is not a v1 blocker — the interrogation phase can handle it conversationally — but it is a known scaling pressure point. No dedicated research has been done; handle during Phase 1 (Interrogation) implementation with a fallback option: "If you have a complex model, paste your table list and I'll work through it with you."

- **Session state persistence:** STACK.md documents a v2 pattern (write `STATE.md` after interrogation, offer "Resume from last session" at skill start). This is not needed for v1 — all context lives in the conversation. No research done; defer to v2 planning.

---

## Sources

### Primary (HIGH confidence)
- `C:/Users/DeveshD/.claude/get-shit-done/workflows/new-project.md` — command file format, decision gate pattern, phase structure
- `C:/Users/DeveshD/.claude/get-shit-done/workflows/discuss-phase.md` — interrogation patterns, AskUserQuestion usage, freeform fallback rule
- `C:/Users/DeveshD/.claude/get-shit-done/references/questioning.md` — interrogation philosophy, anti-patterns, decision gate
- `C:/Users/DeveshD/.claude/get-shit-done/references/ui-brand.md` — checkpoint box pattern, stage banners, status symbols
- `C:/Users/DeveshD/.claude/get-shit-done/references/verification-patterns.md` — verification approach, phase pass/fail criteria
- `C:/Users/DeveshD/.planning/PROJECT.md` — PBI-SKILL v2 requirements and constraints
- [arXiv: LLMs Get Lost In Multi-Turn Conversation (2505.06120)](https://arxiv.org/abs/2505.06120) — 39% accuracy drop in multi-turn conversations, root cause analysis
- [SQLBI: Introducing AI and Agentic Development for BI](https://www.sqlbi.com/articles/introducing-ai-and-agentic-development-for-business-intelligence/) — AI DAX failure modes, five building blocks for effective workflows
- [SQLBI: Row Context and Filter Context in DAX](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/) — evaluation context as primary DAX correctness hazard

### Secondary (MEDIUM confidence)
- [Sparkco: Deep Dive into AI-Generated DAX Formulas](https://sparkco.ai/blog/deep-dive-into-ai-generated-dax-formulas) — 15% manual adjustment rate for AI-generated DAX, iterative refinement needs
- [Microsoft Learn: Overview of Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction) — official Copilot scope, Premium licensing requirement, 10,000 character limit
- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — skill file design, progressive disclosure, verification loop patterns
- [Power BI Copilot Best Practices 2026](https://powerbiconsulting.com/blog/power-bi-copilot-best-practices-2026) — lean schema recommendations, model prep for AI accuracy
- [Tabular Editor: Power BI intermediate mistakes](https://tabulareditor.com/blog/power-bi-for-intermediates-7-mistakes-you-dont-want-to-make) — domain-level errors AI assistants are likely to reproduce

### Tertiary (supporting)
- [PromptHub: Why LLMs Fail in Multi-Turn Conversations](https://www.prompthub.us/blog/why-llms-fail-in-multi-turn-conversations-and-how-to-fix-it) — four failure mechanisms including lost-in-middle
- [Chroma Research: Context Rot](https://research.trychroma.com/context-rot) — performance degradation with longer context
- [Microsoft Learn: Choose the best visual](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-decision-guide) — visual type decision framework
- [Power BI Accessibility Best Practices](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) — 4.5:1 contrast, alt text, keyboard nav (informs polish checklist scope)

---
*Research completed: 2026-03-13*
*Ready for roadmap: yes*
