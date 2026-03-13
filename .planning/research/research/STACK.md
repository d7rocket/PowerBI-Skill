# Stack Research

**Domain:** Claude Code skill development (slash commands as structured prompt files)
**Researched:** 2026-03-13
**Confidence:** HIGH — all findings derived from direct inspection of the GSD reference implementation on this machine, which is the authoritative source for this domain.

---

## What "Stack" Means Here

This is not a software stack. There is no npm, no runtime, no compiled artifact. The "stack" for Claude Code skill development is a composition of:

1. **File format conventions** — how a skill is structured
2. **Invocation mechanism** — how Claude discovers and executes it
3. **Interaction patterns** — how interrogation flows and gates are implemented
4. **Reference architecture** — the GSD system as the canonical model

All components are plain Markdown files interpreted at runtime by Claude. The only executable artifact is an optional CLI helper (`gsd-tools.cjs`) that handles state, git commits, and config. For the PBI-SKILL project, no CLI is needed — this is a pure conversational skill.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Claude Code slash command (`.md`) | Current | Skill definition and invocation | The native mechanism. Skills defined as `.md` files in `~/.claude/commands/[namespace]/` are automatically discovered and invocable as `/namespace:skill-name`. No setup required. |
| YAML frontmatter | — | Skill metadata, tool permissions, argument hints | Controls what tools the skill is allowed to call. Omitting it defaults to no tool access. Required for interactive skills. |
| XML-tagged sections | — | Structural prompt organization inside the skill | GSD uses `<purpose>`, `<process>`, `<step>`, `<success_criteria>` tags. These create machine-readable structure without requiring any parser. Claude interprets them as logical boundaries. |
| `AskUserQuestion` tool | — | Structured interrogation with option lists | The correct tool for presenting choices. Enforces option-based UI rather than freeform prompts. Critical for phase-based skills that need to collect decisions before proceeding. |

### Supporting Patterns

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| Workflow file separation (`workflows/` + `commands/`) | Separates thin invocation stub from full workflow logic | Use when the skill logic exceeds ~50 lines. Command file stays small; workflow file carries the detail. GSD does this universally. |
| `@path/to/file.md` references in `execution_context` | Loads external files into context at invocation time | Use for shared references (questioning guides, brand standards, templates) that multiple skills share. Avoids duplication. |
| `<files_to_read>` blocks | Explicit instruction to read files at execution start | Use to load project state (PROJECT.md, REQUIREMENTS.md) before the skill logic runs. More reliable than hoping files are in context. |
| Named `<step>` blocks with `priority="first"` | Sequential step enforcement | Use to ensure initialization happens before any user interaction. `priority="first"` signals non-negotiable ordering. |
| Decision gates via AskUserQuestion | Hard stops that require explicit user confirmation before proceeding | Use at phase transitions, before irreversible actions, or when gathered context is sufficient to proceed. Prevents auto-advancement past points requiring human judgment. |
| Freeform fallback rule | Switches from AskUserQuestion to plain text when user signals they want to explain | Required to avoid trapping users in option lists. See `questioning.md`: if user selects "Let me explain" or gives open-ended reply, stop using AskUserQuestion and ask in plain text. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `~/.claude/commands/[namespace]/` directory | Skill registration location | Files dropped here become available as `/namespace:skill-name`. Subdirectory name becomes the namespace. |
| `~/.claude/get-shit-done/` | Reference implementation directory | Study this. All workflow patterns, template structures, and interrogation conventions are live code here. |
| `gsd-tools.cjs` | CLI helper for state/git/config | Not needed for PBI-SKILL. Only relevant if the skill needs to persist state across sessions or manage git commits. |

---

## Skill File Format (Definitive)

A Claude Code skill is a `.md` file with this structure:

```markdown
---
name: namespace:skill-name
description: One-line description shown in /help and autocomplete
argument-hint: "[optional-args]"
allowed-tools:
  - Read
  - AskUserQuestion
  - Bash
  - Write
  - Task
---
<context>
**Flags:** (if any)
- `--flag` — what it does
</context>

<objective>
What this skill produces. What files/artifacts it creates. What the user can do next.
</objective>

<execution_context>
@path/to/workflow.md
@path/to/reference.md
@path/to/template.md
</execution_context>

<process>
Execute the workflow from @path/to/workflow.md end-to-end.
Preserve all workflow gates (validation, approvals, commits, routing).
</process>
```

The command file is the thin wrapper. All actual logic lives in the workflow file it references.

---

## GSD as Reference Implementation — What to Study

GSD is the canonical example of production-quality Claude Code skills. Its patterns are the standard.

### Pattern 1: Thin Command + Deep Workflow

**What it is:** The `commands/gsd/new-project.md` file is 43 lines. The actual logic is in `workflows/new-project.md` (1112 lines). The command file holds: frontmatter metadata, objective, execution_context (file references), and a single instruction to execute the workflow.

**Why it works:** Keeps the invocation stub readable and maintainable. Lets workflow files be updated independently of command registration. The `@path` syntax in `execution_context` loads the workflow into the model's context window automatically.

**Apply to PBI-SKILL:** Create `~/.claude/commands/pbi/skill.md` as the thin wrapper. Put all interrogation logic in a separate workflow file.

### Pattern 2: XML Section Tags as Structural Contracts

**What it is:** GSD wraps every logical unit in named XML tags: `<purpose>`, `<process>`, `<step name="initialize" priority="first">`, `<success_criteria>`, `<failure_handling>`.

**Why it works:** Claude treats these as logical containers. `priority="first"` on a step signals that it must execute before all others — this is how GSD enforces that initialization (running `gsd-tools init`) always precedes user interaction. Named steps create checkpoints Claude can reference in error messages ("see step 'verify_phase_goal'"). It is not formal XML parsing — it is prompt structure that Claude reads as intent.

**Apply to PBI-SKILL:** Use `<step name="interrogate">`, `<step name="model_review">`, `<step name="verify">` to enforce the phase sequence. The interrogation step must have `priority="first"` to prevent any DAX from being written before context is gathered.

### Pattern 3: AskUserQuestion for Structured Interrogation

**What it is:** GSD uses `AskUserQuestion` with `multiSelect: false` or `multiSelect: true` to present concrete options rather than freeform questions. Each call has a `header` (max 12 characters — validation enforces this), a `question`, and `options` with label + description.

**Why it works:** Concrete options prevent vague answers. The user reacts to choices rather than generating responses from scratch. This is faster and produces more structured data for downstream processing. The 12-character header limit is enforced by GSD validation tools — violating it causes the question to fail.

**Apply to PBI-SKILL:** The interrogation phase must use AskUserQuestion for every structured question (table selection, relationship mapping, measure inventory). Only use freeform text when the user explicitly says "let me describe it" — this is the "freeform fallback rule" from `questioning.md`.

### Pattern 4: Decision Gates

**What it is:** GSD uses a "Ready?" gate before advancing from questioning to PROJECT.md creation (new-project.md, Step 3). It presents: "Create PROJECT.md" vs "Keep exploring". The workflow loops until the user confirms readiness.

**Why it works:** Prevents premature advancement. The model cannot exit the interrogation phase unilaterally — it requires explicit user confirmation. This is the mechanism that enforces "never write DAX until context is understood."

**Apply to PBI-SKILL:** After the interrogation phase, gate on: "I have enough context to start the model review. Proceed?" → "Yes, proceed" vs "I have more to share." The skill must not enter the DAX-writing phase without this gate clearing.

### Pattern 5: Phase-Based Execution with Verification

**What it is:** GSD's full workflow is: discuss-phase → plan-phase → execute-phase → verify-phase. Each phase has a stated goal, requirements mapped to it, and a verification step that checks goal achievement (not just task completion). The verifier creates a `VERIFICATION.md` with `passed` / `gaps_found` / `human_needed` status.

**Why it works:** Verification checks whether the phase goal was achieved, not whether tasks ran. If `gaps_found`, the skill routes to gap closure rather than proceeding. This prevents accumulating technical debt where tasks complete but requirements are unmet.

**Apply to PBI-SKILL:** After each phase (model review, measure writing, visual recommendations), verify that the output answers the business question stated at the start. The verification is conversational — ask: "Does this measure answer [the stated question]?" Gate advancement on the answer.

### Pattern 6: Context Carried Forward

**What it is:** GSD's `discuss-phase.md` reads all prior `CONTEXT.md` files before asking any questions. It builds a `<prior_decisions>` block and uses it to skip already-answered questions and annotate new questions with relevant prior decisions.

**Why it works:** Prevents re-asking questions the user already answered. Creates continuity across phases. The user experiences this as "Claude remembers what I said."

**Apply to PBI-SKILL:** After gathering data model state and business question in the interrogation phase, carry those forward into every subsequent phase. A measure-writing phase that has forgotten the table structure or business question is the failure mode PBI-SKILL v1 had.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Thin command + workflow file | All logic in command file | Only for very short skills (< 40 lines of process). Anything interrogation-based outgrows this quickly. |
| AskUserQuestion for options | Freeform questions | Only when the answer space is genuinely unbounded. For structured data like table names and measure lists, AskUserQuestion forces specificity. |
| XML-tagged step blocks | Unstructured numbered list | If the skill has no conditional branches or error handling. Once you need `priority="first"` or step-level failure handling, switch to tagged blocks. |
| Separate namespace directory (`commands/pbi/`) | Top-level command file | Only valid if there will be exactly one skill with no related commands. A namespace groups PBI-related skills (skill, debug, check) under `/pbi:`. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Freeform "What do you want to build?" as opening | GSD's questioning.md explicitly lists "shallow acceptance" as an anti-pattern. Open questions produce vague context. | Pre-structured interrogation covering: table inventory, relationship map, existing measures, calculated columns, and business question. |
| Jumping directly to DAX generation | The documented failure mode of PBI-SKILL v1. Every failure (wrong context, missed measures, wrong business question) stems from skipping pre-flight. | Gate all code generation behind a completed interrogation + explicit user confirmation gate. |
| `Task` spawning for a conversational skill | Task spawns subagents with fresh context windows. Conversational skills need continuous context (the interrogation results must be available when DAX is written). | Run all phases inline within the same skill invocation, using in-memory context. Only use Task for parallel research agents (like GSD's 4 parallel researchers). |
| Generic educational DAX output | PROJECT.md explicitly marks this as out of scope. Generic tutorials don't use the user's actual model. | Context-driven output only. Every measure references the specific tables, relationships, and existing measures gathered in the interrogation. |
| YOLO mode without a verification gate | Auto-advancing from interrogation to code generation without asking "does this answer your question?" produces correct-looking but wrong output. | Explicit verification gate after each phase output. |

---

## Stack Patterns by Variant

**If the skill needs to persist context across sessions (future v2):**
- Write a `STATE.md` file after interrogation completes
- Read it at skill start: if STATE.md exists, offer "Resume from last session" vs "Start fresh"
- This is how GSD handles context compaction — artifacts persist even if the context window is lost

**If the skill will have multiple related commands (future):**
- Structure as `commands/pbi/skill.md`, `commands/pbi/debug.md`, `commands/pbi/review.md`
- All under `/pbi:` namespace
- Share a common reference file (`references/pbi-interrogation.md`) loaded via `execution_context` in each command

**If the interrogation needs to handle brownfield state (existing reports):**
- Add a detection step at initialization: does the user have an existing report or are they starting fresh?
- Brownfield: interrogate the existing model structure first, identify what already exists
- Greenfield: begin with blank model questions
- Mirror GSD's brownfield detection in `new-project.md` Step 2

---

## Version Compatibility

No versioned dependencies. Claude Code skill files are interpreted by whatever model is running. The `allowed-tools` frontmatter key must use exact tool names supported by the current Claude Code version:

| Tool Name | Purpose | Notes |
|-----------|---------|-------|
| `AskUserQuestion` | Structured option-based questions | Available in current Claude Code. Header max 12 chars enforced. |
| `Read` | File reading | Always available |
| `Write` | File writing | Required if skill creates output files |
| `Bash` | Shell commands | Required if skill runs CLI tools |
| `Task` | Subagent spawning | Required only if skill needs parallel agents |

---

## Sources

- Direct inspection of `C:/Users/DeveshD/.claude/commands/gsd/new-project.md` — command file format (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.claude/get-shit-done/workflows/new-project.md` — workflow structure and phase gates (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.claude/get-shit-done/workflows/discuss-phase.md` — interrogation patterns, AskUserQuestion usage, freeform fallback rule (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.claude/get-shit-done/workflows/execute-phase.md` — verification patterns, wave execution, subagent spawning (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.claude/get-shit-done/references/questioning.md` — interrogation philosophy, anti-patterns, decision gate pattern (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.claude/get-shit-done/references/verification-patterns.md` — verification approach, what "done" means (HIGH confidence)
- Direct inspection of `C:/Users/DeveshD/.planning/PROJECT.md` — PBI-SKILL requirements and constraints (HIGH confidence)

---
*Stack research for: Claude Code skill development (PBI-SKILL v2)*
*Researched: 2026-03-13*
