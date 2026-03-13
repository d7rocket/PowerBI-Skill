# Pitfalls Research

**Domain:** Structured conversational AI skill for Power BI / DAX development
**Researched:** 2026-03-13
**Confidence:** HIGH (core pitfalls), MEDIUM (skill-file specifics)

---

## Critical Pitfalls

### Pitfall 1: Jumping to DAX Before the Data Model Is Understood

**What goes wrong:**
The skill receives a vague request ("calculate YTD sales") and immediately generates a measure. The measure is syntactically correct but logically wrong — it filters on a dimension column instead of a fact column, ignores an existing date table relationship, or duplicates a measure that already exists under a different name. The user gets plausible-looking DAX that silently returns wrong numbers.

**Why it happens:**
Without knowing the data model (tables, relationships, existing measures, cardinality), an LLM fills in assumptions from training data. Those assumptions reflect generic Power BI patterns, not the user's actual model. LLM-generated DAX is unreliable beyond simple aggregations when model structure is unknown — the AI produces syntactically valid but semantically incorrect code.

**How to avoid:**
The skill MUST require the user to describe the data model before any measure is written. Minimum required context: table names, key relationships, whether a dedicated date table exists, and what related measures already exist. These must be explicit gates — the skill should refuse to proceed without them, not treat them as optional context.

**Warning signs:**
- The skill produces a measure in the first or second response without asking about relationships
- The skill assumes a standard star schema without verifying
- The user reports "the numbers look close but not quite right"
- The generated measure uses `ALL()` or `CALCULATE()` without confirming the filter context intent

**Phase to address:** Phase 1 — Pre-flight interrogation gate

---

### Pitfall 2: Interrogation Questions That Are Too Generic to Extract Useful Context

**What goes wrong:**
The skill asks "Can you describe your data model?" The user gives a vague two-sentence answer. The skill proceeds as if it has enough context. Later, the generated DAX fails because it assumed a direct relationship that doesn't exist, or missed that the model uses a role-playing date table.

**Why it happens:**
Generic open questions allow generic answers. Users don't know what level of detail the skill needs. Without specific, targeted questions ("Does your date table have a direct relationship to the fact table, or do you filter dates through a bridge table?"), the interrogation phase collects noise, not signal. Research confirms that LLMs asking vague follow-up questions receive answers that don't eliminate key ambiguities.

**How to avoid:**
The interrogation phase must use specific, structured questions organized into mandatory and conditional buckets:
- **Mandatory:** Number of fact tables, relationship direction, whether a date table exists and its name, list of existing measures in the same subject area
- **Conditional:** If time intelligence is needed — does the date table have a `DateKey` integer column or a `Date` date column? If % of total is needed — does the total live at a parent dimension level or a fixed value?

Questions should be targeted enough that a "yes/no + one detail" answer is sufficient. Avoid questions where any answer is valid.

**Warning signs:**
- The interrogation phase consists of only one or two questions
- Questions are phrased as "tell me about your model" rather than specific attribute requests
- The user answers in under 50 words and the skill proceeds without follow-up
- The skill does not explicitly confirm relationship direction (single vs. bidirectional)

**Phase to address:** Phase 1 — Pre-flight interrogation gate

---

### Pitfall 3: Verification Gates That Become Rubber Stamps

**What goes wrong:**
After generating a measure, the skill asks "Does this look right to you?" The user says "looks good" without testing it. The skill moves to the next phase. The error surfaces later when the report is deployed. The verification gate existed but added no actual quality assurance.

**Why it happens:**
Verification questions that rely on the user's impressionistic judgment do not verify correctness. "Does this look right?" invites agreement bias. Without a specific, testable check, the gate is theater — it creates the appearance of verification while adding no defense against bad output.

An additional structural problem: asking one LLM instance to review its own output catches far fewer errors than cross-checking against an independent signal. Research on AI-on-AI review confirms that self-review is weaker than external review.

**How to avoid:**
Verification gates must require a concrete, observable test result:
- "Apply this measure to a matrix with [specific dimension] on rows. Does the total match the expected business number for a known period?"
- "Check whether [Measure Name] returns the same result as [Related Existing Measure] when no filters are applied — they should be equal."
- "For a single product with known sales, does the measure return [expected value]?"

The gate should also require the user to confirm: what did they test, against what expected value, and did they match? If the user cannot answer these, the gate should surface this explicitly rather than proceeding.

**Warning signs:**
- The verification prompt is "does this look good?" or "any questions?"
- The gate does not specify a test or expected result
- The user's confirmation is a single word ("yes", "looks fine", "ok")
- The skill advances to the next phase after any affirmative, regardless of whether a test was performed

**Phase to address:** Phase 2 — Measure verification gate; also Phase 3 — Visual verification

---

### Pitfall 4: Context Loss Across Phases in a Multi-Turn Conversation

**What goes wrong:**
The skill successfully interrogates the data model in Phase 1. By Phase 3 (visual recommendations), the key constraints established earlier — the bidirectional relationship caveat, the non-standard date table, the existing measure that must be used as a base — are no longer referenced. The phase 3 output contradicts the phase 1 findings.

**Why it happens:**
LLMs degrade measurably in multi-turn conversations. Research confirms an average 39% performance drop across generation tasks in multi-turn vs. single-turn interactions for flagship models including Claude 3.7 Sonnet. The root cause is not context window overflow — it is that LLMs make early assumptions, get "lost," and do not recover when new information contradicts those assumptions. Critical facts from the middle of a long conversation are systematically underweighted due to the "lost-in-middle" phenomenon.

**How to avoid:**
The skill must maintain a structured "context ledger" — a committed summary of established facts that is carried forward into each phase. Before generating any phase output, the skill should explicitly re-state the binding constraints from phase 1:
- Confirmed model facts (table names, relationships, date table)
- Confirmed existing measures that must not be duplicated
- Confirmed business question the report must answer

This summary should be short (bullet points, under 10 lines) and re-injected at the start of each new phase prompt. Do not rely on Claude remembering earlier turns — make the context explicit.

**Warning signs:**
- Phase 3 output references a relationship type or column that contradicts phase 1 findings
- The skill generates a new measure for a calculation already covered in a measure listed during phase 1
- The business question established in phase 1 is no longer referenced by phase 3
- The conversation is more than 20 turns long without a context refresh

**Phase to address:** Phase 2, 3, and 4 — the skill must implement context carry-forward at every phase boundary

---

### Pitfall 5: DAX Generated Without Awareness of Evaluation Context

**What goes wrong:**
The skill generates a measure like `CALCULATE([Sales Amount], FILTER(DimProduct, DimProduct[Category] = "Electronics"))`. This works in a simple card visual. It breaks silently when placed in a matrix with Product on rows — the `FILTER` iterates DimProduct and creates a new filter context that conflicts with the visual's own row context. The user sees inconsistent or blank values.

**Why it happens:**
Filter context and row context interaction is the single most common source of silent DAX errors. Without knowing where the measure will be consumed (card, matrix, table, calculated column), the skill cannot write a correct measure. Generic DAX patterns from training data often omit this consideration. The SQLBI corpus documents this as the most misunderstood area of DAX even for experienced developers.

**How to avoid:**
The interrogation phase must ask "where will this measure be used?" as a required field — not optional context. The answer (card only, matrix with [dimension], table, slicer interaction) determines whether the skill should use `CALCULATE` with table filters, `SELECTEDVALUE`, `HASONEVALUE`, or iterator-based patterns. The measure generation step must include a note on the assumed consumption context and flag if the measure may behave differently in other visuals.

**Warning signs:**
- The skill generates CALCULATE with a table-level FILTER without asking about visual placement
- The measure uses direct column references inside CALCULATE without checking for row context
- No mention of where the measure will be placed appears in the skill's output
- The measure uses `ALL()` on a dimension without confirming whether bidirectional filtering is active

**Phase to address:** Phase 1 — interrogation (consumption context) and Phase 2 — measure generation

---

### Pitfall 6: Skill Prompt Becomes a Tutorial Instead of a Workflow Driver

**What goes wrong:**
The skill file grows to include explanations of what DAX is, why filter context matters, and background on the Power BI data model. The user reads none of it. Claude reads all of it, consuming context budget on explanations that add no behavior. The skill behaves like an educational assistant rather than a structured workflow executor.

**Why it happens:**
When writing a skill, the temptation is to document all relevant knowledge to make the skill "smarter." But the Anthropic skill authoring guidance is explicit: Claude already knows DAX fundamentals. Every token explaining what CALCULATE does is a token that competes with conversation history and phase context. Verbose skill files degrade performance because relevant phase instructions get diluted by educational content.

**How to avoid:**
The skill file must contain only workflow instructions, phase gates, question templates, and output format requirements. It must NOT contain:
- Explanations of DAX concepts
- Background on Power BI architecture
- Tutorials on evaluation context

Test the file: if a section could be replaced with "Claude already knows this," delete it. The skill file should read like a process playbook, not a knowledge base.

**Warning signs:**
- The SKILL.md file exceeds 200 lines before any phase-specific content
- The file contains paragraphs starting with "DAX is..." or "Power BI uses..."
- Phase instructions are buried after three or more paragraphs of background
- The skill generates educational responses when it should be asking interrogation questions

**Phase to address:** Phase 1 (skill file authoring) — structure before content

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skipping the data model confirmation step for "simple" requests | Faster response | Silent errors in measures using wrong relationships | Never — model confirmation takes 2 minutes and prevents rewrites |
| Single open-ended interrogation question instead of structured prompts | Less friction | Insufficient context, measures that look right but aren't | Never for DAX generation; acceptable for general advice questions |
| Relying on user to flag errors instead of requiring testable verification | Fewer turns | Bugs surface in deployment, not development | Never for measures that feed key report visuals |
| Context carried implicitly in conversation history rather than explicit ledger | Shorter prompts | Phase 3+ outputs contradict Phase 1 constraints | Never in conversations expected to exceed 10 turns |
| Including business logic in visual-layer measures instead of base measures | Fewer measures | Logic is trapped in a single visual, not reusable | Only for one-off exploratory analysis, never for production reports |

---

## Integration Gotchas

Common mistakes when connecting to conversational Power BI workflow elements.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Existing measure reuse | Skill generates a new measure that duplicates an existing one under a slightly different name | Interrogation phase must explicitly collect existing measure names and purposes before generation |
| Date table assumptions | Skill assumes a standard `DateKey` integer surrogate key; model uses a `Date` date column | Ask specifically: "What is the primary key column type and name in your date table?" |
| Relationship direction | Skill assumes single-direction relationships; model has bidirectional filters for role-playing dimensions | Ask: "Are any relationships set to bidirectional? If so, which ones?" |
| Visual placement of measures | Skill writes a measure assuming a card visual; it will be used in a matrix | "Where will this measure be displayed?" must be a required interrogation field |
| Calculated column vs. measure | Skill generates a measure when a calculated column is actually needed (row-level computation) | Ask whether the calculation needs to vary by row or aggregate across rows |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| CALCULATE with table-level FILTER over large dimension | Measure works on small dataset, times out on full model | Use column-level predicates (`DimProduct[Category] = "X"`) instead of `FILTER(DimTable, ...)` | Any fact table over ~1M rows with a large dimension table |
| Iterator functions over large tables without early filtering | SUMX over entire fact table is slow | Add a CALCULATETABLE or FILTER to scope the iterator before iterating | Fact tables over 5M rows |
| RELATED() in calculated columns on large tables | Column refresh takes minutes | Pre-join at the model/query level instead | Calculated columns on tables over 500K rows |
| Bidirectional relationships for convenience filtering | Ambiguous filter paths, unexpected cross-filtering | Use explicit CROSSFILTER() in DAX instead of model-level bidirectionality | Any model with 3+ related tables sharing a filter path |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Skill produces measures without explaining what the measure does and why the pattern was chosen | User cannot validate correctness, cannot learn | Include a 2-sentence explanation: what it calculates and which pattern was used |
| Skill asks all interrogation questions in a single massive block | User feels interrogated, provides low-quality answers | Group questions into sets of 3-4, confirm before proceeding |
| Skill advances phases automatically without explicit user confirmation | User misses phase boundary, loses ability to correct early errors | Each phase must end with an explicit checkpoint: "Phase 1 complete. Confirm the above model facts are correct before we write any measures." |
| Skill generates multiple measures in one response | User cannot test one at a time | Generate one measure per response, verify before the next |
| Skill gives a visual recommendation without confirming report audience or output format | Recommendation is wrong for mobile layout, or executive vs. analyst audience | Ask: "Who is the primary audience and where will this report be consumed (desktop, web, mobile)?" |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Interrogation phase:** Often missing relationship direction confirmation — verify bidirectional flag has been asked about
- [ ] **Measure generation:** Often missing consumption context (where the measure will be placed) — verify visual placement was confirmed
- [ ] **Verification gate:** Often missing a testable check — verify the gate specifies what to test, not just "does this look right?"
- [ ] **Phase context carry-forward:** Often missing an explicit model summary at the start of each new phase — verify phase 2+ prompts re-state confirmed model facts
- [ ] **Existing measure inventory:** Often missing a check against already-existing measures — verify the interrogation phase collected existing measure names before generating new ones
- [ ] **DAX explanation:** Often missing the pattern rationale — verify each generated measure includes a 2-sentence explanation of why the pattern was chosen

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| DAX generated without model context, now produces wrong numbers | MEDIUM | Run model interrogation retrospectively; ask user to provide table/relationship details; regenerate with corrected context |
| Verification gate rubber-stamped, error found in production | MEDIUM | Return to measure verification phase; require specific numeric test against known values; re-issue corrected measure |
| Context lost across phases, Phase 3 contradicts Phase 1 | HIGH | Re-run context ledger: ask user to re-confirm Phase 1 findings; treat current output as draft; regenerate Phase 3 output with explicit constraints |
| Skill file too verbose, Claude generating educational content instead of workflow | LOW | Audit SKILL.md; delete any paragraph that explains DAX concepts rather than directing behavior; re-test with focused interrogation request |
| Duplicate measure generated (missed existing measure) | LOW | Ask user to run a search for related measure names in their model; deprecate the new measure if a match is found; consolidate |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| DAX before model is understood | Phase 1: Mandatory pre-flight gate before any code | No DAX appears in Phase 1 output; Phase 1 ends with confirmed model summary |
| Vague interrogation questions | Phase 1: Specific question templates with mandatory/conditional buckets | User answers are specific enough to determine relationship direction and measure naming |
| Rubber-stamp verification gates | Phase 2: Verification gate requires named test and expected value | User confirms what they tested and against what known value |
| Context loss across phases | Phase 2-4: Explicit context ledger re-injected at each phase boundary | Phase 3 output explicitly references constraints established in Phase 1 |
| Evaluation context errors | Phase 1: Visual placement question added to interrogation; Phase 2: CALCULATE pattern selection depends on answer | Generated measure notes assumed visual placement |
| Skill bloat / tutorial content | Phase 1 (skill authoring): Review against conciseness standard | SKILL.md contains no explanatory paragraphs about DAX fundamentals |

---

## Sources

- [SQLBI: Introducing AI and agentic development for Business Intelligence](https://www.sqlbi.com/articles/introducing-ai-and-agentic-development-for-business-intelligence/) — primary source on AI DAX generation failure modes; confirms AI needs rich, specific model context to avoid wrong filter patterns
- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — authoritative source on skill file design, progressive disclosure, avoiding verbosity, and verification loop patterns
- [arXiv: LLMs Get Lost In Multi-Turn Conversation (2505.06120)](https://arxiv.org/abs/2505.06120) — research confirming 39% average accuracy drop in multi-turn conversations; root cause is premature assumption-making, not context overflow
- [PromptHub: Why LLMs Fail in Multi-Turn Conversations](https://www.prompthub.us/blog/why-llms-fail-in-multi-turn-conversations-and-how-to-fix-it) — documents four specific failure mechanisms including lost-in-middle and verbosity inflation
- [SQLBI: Row Context and Filter Context in DAX](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/) — authoritative source on evaluation context as the primary DAX correctness hazard
- [SQLBI: Solving errors in CALCULATE filter arguments](https://www.sqlbi.com/articles/solving-errors-in-calculate-filter-arguments/) — specific patterns for CALCULATE filter argument errors
- [Medium: Building an AI Chat Assistant for Power BI Reports](https://medium.com/@michael.hannecke/building-an-ai-chat-assistant-for-power-bi-reports-architecture-and-trade-offs-74200ee608dc) — documents LLM DAX unreliability beyond simple aggregations
- [Tabular Editor: Power BI for intermediates: 7 mistakes you don't want to make](https://tabulareditor.com/blog/power-bi-for-intermediates-7-mistakes-you-dont-want-to-make) — domain-level intermediate mistakes that AI assistants are likely to reproduce
- [Chroma Research: Context Rot — How Increasing Input Tokens Impacts LLM Performance](https://research.trychroma.com/context-rot) — performance degradation with longer context windows

---
*Pitfalls research for: PBI Skill v2 — structured Power BI / DAX conversational skill*
*Researched: 2026-03-13*
