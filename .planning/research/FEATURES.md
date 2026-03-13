# Feature Research

**Domain:** Conversational Power BI assistant skill (Claude Code)
**Researched:** 2026-03-13
**Confidence:** HIGH (core categories), MEDIUM (polish/differentiators)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = skill feels broken or useless on first contact.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Pre-flight interrogation: extract business question before any DAX | Every expert source (SQLBI, Sparkco, official MS docs) agrees: AI DAX without model context produces wrong or misleading output. Users who've been burned by generic Copilot output expect this. | MEDIUM | Must cover: what question the report answers, who consumes it, what time grain is needed. |
| Data model state intake | DAX evaluation context depends entirely on relationships, filter flow, and cardinality. A measure that works on one model may silently fail on another. | MEDIUM | Ask for: tables, key relationships (1:M vs M:M), existing measures, date table presence/configuration. |
| Existing measures audit before writing new ones | Duplicating calculations is the most common waste in Power BI work — users expect an assistant to ask "does this already exist?" | LOW | Simple but high-value: ask what measures are already defined before suggesting new ones. |
| Context-aware DAX output | Generated measures must reference actual table/column names from the described model, not placeholder names. | HIGH | Failure mode: AI uses `Sales[Amount]` when user's column is `Fact_Sales[Net Revenue]`. Requires mapping user-described model to output. |
| Phase structure: model → measures → visuals → polish | Users building reports go through this workflow. An assistant that skips phases creates rework — e.g., suggesting visuals before measures are validated breaks flow. | MEDIUM | This is the GSD-style structure from PROJECT.md. Each phase should gate the next. |
| Verification gate per phase | After each phase, confirm the output actually answers the original business question before proceeding. Without this, errors compound across phases. | MEDIUM | Simple: "Does this [model structure / measure / visual layout] answer [business question]? Confirm before we move to the next phase." |
| DAX that handles filter context correctly | Users expect CALCULATE, REMOVEFILTERS, ALLEXCEPT, etc. to be used correctly relative to the described visual context. Filter context mistakes produce numbers that look right but aren't. | HIGH | This is the #1 class of DAX error. Must ask about visual context (row context, slicer setup) before writing time intelligence or ratio measures. |
| Visual type recommendation tied to data shape | Users expect guidance on bar vs line vs matrix — not a tutorial, but an opinionated "use X because Y for this data" recommendation. | LOW | Ground the recommendation in the data shape (categorical, time series, part-to-whole) and the business question. |
| Report polish checklist | Color contrast, title clarity, axis labels, alt text flags. Users expect a conversational assistant to surface these before sign-off. | LOW | Not a full accessibility audit — just the high-value catches: missing titles, color-only encoding, 3D charts, too many slicers. |

---

### Differentiators (Competitive Advantage)

Features that set this skill apart from Copilot and generic LLM prompting. These align with the core value in PROJECT.md: never write DAX until the business question and model state are understood.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Interrogation protocol with structured pre-flight | Copilot and ChatGPT accept vague requests and produce plausible-but-wrong DAX. This skill's interrogation phase prevents that class of failure entirely. The questioning is the product. | MEDIUM | Requires a defined question set: business question, grain, model topology, existing measures, date table state. This is what makes the skill GSD-quality. |
| Duplicate measure detection heuristic | Before writing any measure, analyze user-described existing measures to identify potential duplicates or near-duplicates. Prevents measure sprawl — a real, named pain point in large Power BI projects. | MEDIUM | Conversational: "You have `Total Revenue` — is your new measure different from that in any filter context?" |
| Business question traceability | Every measure and visual recommendation traces back explicitly to the stated business question. Keeps scope tight and prevents gold-plating. | LOW | Pattern: "This measure answers [business question] by [mechanism]. If the question changes, this measure changes too." |
| DAX pattern selection over freeform generation | Instead of generating arbitrary DAX, the skill identifies the correct pattern category first (ratio, running total, period comparison, ranking, conditional accumulation) and then fills in model-specific details. Pattern-first generation produces more reliable output. | HIGH | SQLBI and Tabular Editor document well-established DAX patterns. Grounding in patterns reduces hallucination risk. |
| Model health flags during intake | During data model state intake, surface warnings proactively: M:M relationships, missing date table, bidirectional filters, high-cardinality columns in relationships. Most AI tools skip this. | MEDIUM | These are the same checks a senior consultant runs before touching DAX. The skill should run them conversationally. |
| Phase completion confirmation with explicit rollback gate | If the verification gate at the end of a phase fails (output doesn't answer the business question), the skill has a defined path back to re-interrogation rather than patching forward. Most AI tools patch forward — they add more DAX to fix DAX. | MEDIUM | This is what separates structured workflow from ad-hoc prompting. "The verification failed — let's go back to the model state intake." |
| Visual anti-pattern warnings | Flag known bad practices in real-time: pie charts with >8 slices, 3D bars, KPI cards with no context, slicers that contradict measure filter assumptions. | LOW | One-sentence callouts with the reason and the fix. High signal-to-noise — not a lecture. |

---

### Anti-Features (Deliberately Not Built)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| DAX tutorial generation | Users ask "explain CALCULATE to me" or "teach me time intelligence." Seems educational. | Shifts the skill from a task-executor to a teacher. Slows down people who know DAX (the primary audience). Creates verbose, padded responses. | Link to SQLBI or Microsoft Learn. One-line context when a pattern is used: "Using REMOVEFILTERS here because your measure needs to ignore slicer context." |
| Generic report templates | "Give me a sales dashboard template." Feels like it saves time. | Templates without model context produce unusable scaffolding. The user still has to map every field. False sense of progress. | Run the full interrogation first. Let the template emerge from the actual model and business question. |
| Automated API / .pbix file operations | Power Automate, XMLA endpoint writes, REST API calls. Technically possible adjacent territory. | This is a conversational skill — a `.md` prompt file. It has no file system access and no service connector. Building toward API operations is a scope expansion that breaks the constraint. | Explicitly out of scope per PROJECT.md. Recommend external tools (Tabular Editor, XMLA) when the user needs programmatic model changes. |
| Comprehensive accessibility audit | Running a full WCAG compliance check or accessibility report. | Requires actual visual rendering — impossible from a conversational description. Produces false assurance if the skill appears to audit something it cannot see. | Surface the high-signal items only (color-only encoding, missing alt text pattern, contrast ratio guidance) as part of the polish phase checklist. |
| Multi-measure performance optimization | Analyzing VertiPaq stats, storage engine vs formula engine splits, DirectQuery optimization. | Requires actual query performance data (DAX Studio / VertiPaq Analyzer output) to be meaningful. Without it, recommendations are guesswork. | Point to DAX Studio and DAX Optimizer for this work. Out of scope for conversational skill. |
| Free-form "ask me anything about Power BI" mode | Feels like a full assistant. | Destroys the structured workflow. Users will ask random questions mid-phase, derail the interrogation, and get half-baked answers. The skill's value comes from the structure, not breadth. | Maintain phase discipline. Parking lot pattern: "That's outside our current phase — noted. We'll address it in [phase X]." |

---

## Feature Dependencies

```
[Pre-flight interrogation: business question]
    └──required by──> [Data model state intake]
                          └──required by──> [Existing measures audit]
                                                └──required by──> [Context-aware DAX output]

[Context-aware DAX output]
    └──required by──> [Verification gate: measures phase]
                          └──required by──> [Visual type recommendation]
                                                └──required by──> [Verification gate: visuals phase]
                                                                      └──required by──> [Report polish checklist]

[Model health flags during intake] ──enhances──> [Data model state intake]
[Duplicate measure detection] ──enhances──> [Existing measures audit]
[DAX pattern selection] ──enhances──> [Context-aware DAX output]
[Business question traceability] ──enhances──> [Verification gate: measures phase]
[Phase completion confirmation with rollback] ──enhances──> [Verification gate: measures phase]

[DAX tutorial generation] ──conflicts with──> [Phase discipline / structured workflow]
[Free-form Q&A mode] ──conflicts with──> [Pre-flight interrogation]
```

### Dependency Notes

- **Pre-flight interrogation requires data model state intake:** The business question cannot be assessed without knowing what data is available to answer it. These two run sequentially in phase 1.
- **Context-aware DAX requires existing measures audit:** You cannot write non-duplicate, context-correct DAX until you know what already exists in the model.
- **Verification gate requires business question traceability:** The gate cannot evaluate "does this answer the question?" without the original question being explicitly carried forward through each phase.
- **DAX pattern selection enhances context-aware DAX:** Pattern-first generation is a strategy for producing reliable DAX — it layers on top of the base requirement, not a replacement for it.
- **DAX tutorial generation conflicts with phase discipline:** Educational mode encourages open-ended conversation that breaks the linear interrogation-to-output workflow. These two modes are incompatible in the same interaction.

---

## MVP Definition

This is a Claude Code skill file (a `.md` prompt). The "launch" is a working skill file Devesh can use daily. MVP = minimum scope where the skill is better than the current one on first use.

### Launch With (v1)

- [ ] Pre-flight interrogation protocol — why essential: this IS the differentiator. Without it, the skill is just another DAX assistant.
- [ ] Data model state intake (tables, relationships, date table, existing measures) — why essential: all downstream DAX and visual output is only as good as this context.
- [ ] Phase-gated workflow: model review → measures → visuals → polish — why essential: structure prevents the failure mode where measures are written before the model is understood.
- [ ] Verification gate at end of measures phase — why essential: the one gate that prevents bad DAX from propagating into visuals and report polish.
- [ ] Context-aware DAX output (uses user's actual table/column names) — why essential: the most common complaint about AI-generated DAX; non-context-aware output is immediately unusable.
- [ ] Visual type recommendation tied to data shape and business question — why essential: covers the full workflow scope, low complexity, high perceived value.
- [ ] Report polish checklist (high-signal items only) — why essential: completes the phase workflow. Low complexity, high completeness signal.

### Add After Validation (v1.x)

- [ ] Duplicate measure detection heuristic — trigger: user reports wasted time discovering duplicates after the skill has been used in anger.
- [ ] Model health flags during intake — trigger: user hits a model-related DAX error (M:M filter ambiguity, missing date table) that the pre-flight didn't catch.
- [ ] Visual anti-pattern warnings — trigger: user discovers polish issues the skill missed (3D charts, overloaded slicers).

### Future Consideration (v2+)

- [ ] DAX pattern selection (pattern-first generation) — defer: requires a curated pattern library and classification logic. High complexity, high value, but needs v1 to prove out the base workflow first.
- [ ] Phase completion confirmation with rollback gate — defer: requires testing to find the right rollback trigger. Risk of over-engineering the workflow before validating basic phase discipline.
- [ ] Business question traceability as explicit inline annotation — defer: the concept is in the v1 gates, but surfacing it as a named, persistent annotation through all phases is a UX refinement for v2.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Pre-flight interrogation protocol | HIGH | MEDIUM | P1 |
| Data model state intake | HIGH | MEDIUM | P1 |
| Context-aware DAX output | HIGH | HIGH | P1 |
| Phase-gated workflow structure | HIGH | MEDIUM | P1 |
| Verification gate (measures phase) | HIGH | MEDIUM | P1 |
| Existing measures audit | HIGH | LOW | P1 |
| Visual type recommendation | MEDIUM | LOW | P1 |
| Report polish checklist | MEDIUM | LOW | P1 |
| Duplicate measure detection | HIGH | MEDIUM | P2 |
| Model health flags during intake | HIGH | MEDIUM | P2 |
| Visual anti-pattern warnings | MEDIUM | LOW | P2 |
| DAX pattern selection | HIGH | HIGH | P3 |
| Phase rollback gate | MEDIUM | HIGH | P3 |
| Business question traceability annotation | MEDIUM | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Microsoft Copilot for Power BI | Generic LLM (ChatGPT/Claude no skill) | This Skill |
|---------|-------------------------------|--------------------------------------|------------|
| Pre-flight interrogation | No — accepts prompt immediately | No — accepts prompt immediately | Yes — gated, structured |
| Data model context | Reads actual semantic model metadata (requires Premium) | User must describe manually, no structure enforced | User describes, skill enforces structure |
| Existing measures awareness | Partial — can read model | No | Explicit audit step before DAX |
| Phase discipline | No — single-turn Q&A | No | Yes — model → measures → visuals → polish |
| Verification gates | No | No | Yes — after each phase |
| Duplicate measure detection | No | No | Yes (v1.x) |
| Model health warnings | No (separate Power Advisor tool) | No | Yes (v1.x) |
| DAX pattern grounding | Partial — freeform with some patterns | Partial — freeform with hallucination risk | Yes (v2) |
| Works without Premium license | No — requires F64+ or P1 SKU | Yes | Yes |
| Works from described context (no .pbix access) | No — requires live semantic model | Yes | Yes — designed for this |

---

## Sources

- [SQLBI: Introducing AI and Agentic Development for BI](https://www.sqlbi.com/articles/introducing-ai-and-agentic-development-for-business-intelligence/) — expert analysis of AI assistant failure modes, five building blocks for effective AI workflows
- [SQLBI: AI in Power BI — Time to Pay Attention](https://www.sqlbi.com/articles/ai-in-power-bi-time-to-pay-attention/) — expert critique of current conversational BI limitations, multi-step reasoning gaps
- [Sparkco: Deep Dive into AI-Generated DAX Formulas](https://sparkco.ai/blog/deep-dive-into-ai-generated-dax-formulas) — documented accuracy limitations (15% manual adjustment rate), user needs for validation and iterative refinement
- [Microsoft Learn: Overview of Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction) — official feature scope, 10,000 character prompt limit, Premium licensing requirement
- [Microsoft Learn: Write DAX queries with Copilot](https://learn.microsoft.com/en-us/dax/dax-copilot) — official DAX Copilot capability scope
- [Microsoft Learn: Choose the best visual for your data in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-decision-guide) — visual type decision framework
- [Power BI Copilot Best Practices 2026](https://powerbiconsulting.com/blog/power-bi-copilot-best-practices-2026) — lean schema recommendations, model prep requirements for AI accuracy
- [Power BI Data Modeling Best Practices (CaseWhen)](https://casewhen.co/blog/best-practices-for-for-data-modeling-in-power-bi) — relationship types, cardinality gotchas, date table requirements
- [DAX Optimizer](https://www.daxoptimizer.com/) — reference for what expert-level model review looks like (out of scope for this skill, but informs what flags to surface)
- [Tabular Editor 3](https://tabulareditor.com) — reference for Best Practice Analyzer patterns (informs model health flag content)
- [Power BI Accessibility Best Practices (Microsoft Learn)](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) — 4.5:1 contrast requirement, alt text, keyboard nav — informs polish checklist scope

---

*Feature research for: PBI Skill v2 — conversational Power BI assistant (Claude Code skill)*
*Researched: 2026-03-13*
