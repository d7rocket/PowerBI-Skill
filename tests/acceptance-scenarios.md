# PBI Skill v4.0 — Acceptance Test Scenarios

Phase 1 manual test script. Run these scenarios to verify all Phase 1 behaviors work correctly after the v4.0 rewrite.

**How to use:** Each scenario has preconditions, steps, expected output, and a pass criterion. Run them in order within each group, as later scenarios in a group may depend on earlier ones.

---

## Group 1: Solve-First Default (PROG-01)

These scenarios verify the core behavior change: free-text requests get an immediate answer with no upfront interrogation.

---

### Scenario S1-01: Free-text DAX request gets immediate answer

**Covers:** PROG-01

**Preconditions:**
- PBIP project open (or no project — paste mode is fine)
- `.pbi-context.md` exists with a `## Model Context` section (run `/pbi load` first if needed)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi I need a measure for total revenue` | Skill outputs a DAX measure immediately. No questions asked. No mode announcement. No preamble like "I'll help you with that." |

**Pass criteria:** DAX measure appears in first response. No interrogation before the answer.

---

### Scenario S1-02: Free-text request in paste mode (no PBIP project)

**Covers:** PROG-01

**Preconditions:**
- Working directory has NO `.SemanticModel` directory (paste mode will be detected)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi calculate year-over-year growth` | Skill outputs DAX for YoY growth immediately in copy-paste ready format |

**Pass criteria:** DAX appears without the skill asking about tables or columns first.

---

### Scenario S1-03: Refinement request is NOT treated as failure

**Covers:** PROG-01

**Preconditions:**
- Skill just answered a DAX request (S1-01 completed)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `make it a percentage` | Skill refines the measure with percentage format. No escalation question. No "Let me get more context." |

**Pass criteria:** Refined answer appears without any escalation question. The word "context" should not appear as a prompt.

---

### Scenario S1-04: Follow-up request is NOT treated as failure

**Covers:** PROG-01

**Preconditions:**
- Skill just answered a DAX request (S1-01 or S1-02 completed)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `can you also add a month-over-month version?` | Skill creates the additional measure. No escalation. |

**Pass criteria:** New measure appears without escalation question. The skill treats this as a continuation, not a failure.

---

## Group 2: Escalation (PROG-02, PROG-03, INTR-01, INTR-02, INTR-03)

These scenarios verify that escalation fires only on explicit failure signals, targets the correct gap, and retries automatically after the user answers.

---

### Scenario S2-01: Failure signal triggers escalation — business question gap

**Covers:** PROG-02, INTR-01

**Preconditions:**
- Skill just answered a DAX request

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `that's not what I meant, I need something different` | Skill outputs "Let me get more context." followed by ONE question about the business question (e.g., "What business question should this measure answer?") |

**Pass criteria:**
- Response begins with "Let me get more context." (or similar brief acknowledgment)
- Exactly ONE question is asked, about the business question
- No checklist of multiple questions
- No question about data model or existing measures

---

### Scenario S2-02: Failure signal triggers escalation — data model gap

**Covers:** PROG-02, INTR-02

**Preconditions:**
- Skill just answered a DAX request

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `wrong columns, that table doesn't exist in my model` | Skill outputs "Let me get more context." followed by ONE question about data model state (tables, relationships) |

**Pass criteria:**
- Response begins with acknowledgment
- Question is specifically about the data model (tables, columns, relationships)
- NOT about business question or existing measures
- Exactly one question

---

### Scenario S2-03: Failure signal triggers escalation — existing measures gap

**Covers:** PROG-02, INTR-03

**Preconditions:**
- Skill just answered a DAX request

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `we already have that measure` | Skill asks about existing measures |

**Pass criteria:**
- Question is specifically about existing measures (what's already built, measure names)
- NOT about business question or data model
- Exactly one question

---

### Scenario S2-04: After answering escalation, skill retries automatically

**Covers:** PROG-03, INTR-01

**Preconditions:**
- Scenario S2-01 completed — skill just asked a business question

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Answer the business question (e.g., "We track monthly revenue growth compared to the same month last year") | Skill incorporates the answer and outputs a revised solution immediately. No prompt to re-submit. |

**Pass criteria:**
- Revised DAX appears without user needing to type the original request again
- Skill does NOT ask "Shall I try again?" or "Want me to retry?"
- New solution reflects the business question context provided

---

### Scenario S2-05: Re-escalation targets next unresolved gap

**Covers:** PROG-02, PROG-03, INTR-02

**Preconditions:**
- S2-04 completed — skill retried after business question escalation
- User signals failure again

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `still wrong, the columns don't match my model` | Skill asks about data model state (NOT about business question again) |

**Pass criteria:**
- Question is about data model (tables, columns, relationships)
- Business question is NOT re-asked (already answered in S2-04)
- One question only

---

### Scenario S2-06: Escalation state persists in .pbi-context.md

**Covers:** PROG-02, PROG-03

**Preconditions:**
- S2-04 completed — escalation occurred and user answered

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Open `.pbi-context.md` in the project directory and inspect it | File contains `## Escalation State` section with the gathered context |

**Pass criteria:**
- `## Escalation State` section exists in `.pbi-context.md`
- Section contains the gap type that was answered (e.g., business question)
- The answered context is summarized in the section (not "awaiting")

---

## Group 3: Deep Mode (PROG-04)

These scenarios verify the `/pbi deep` entry point and sequential intake flow.

---

### Scenario S3-01: Deep mode invocation with no arguments

**Covers:** PROG-04

**Preconditions:**
- `.pbi-context.md` is empty or has no `## Business Question` section (delete it or use a fresh project)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi deep` | Skill asks "What business question are we solving?" (or equivalent). Single question only. |

**Pass criteria:**
- First question is about the business question
- Only ONE question asked, not all three at once
- No DAX output yet — intake mode active

---

### Scenario S3-02: Deep mode asks questions sequentially

**Covers:** PROG-04

**Preconditions:**
- S3-01 completed — skill just asked about business question

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Answer the business question (e.g., "Compare regional sales performance month-over-month") | Skill asks about data model state |
| 2 | Answer the data model question (e.g., "Sales fact table linked to Date and Product dimensions") | Skill asks about existing measures |
| 3 | Answer the existing measures question (e.g., "We have Total Sales and Sales LY") | Skill outputs a context summary and asks what to work on |

**Pass criteria:**
- Questions asked one at a time, waiting for answer between each
- All three questions asked in order: business question → data model → existing measures
- After all three answered, context summary is output

---

### Scenario S3-03: Deep mode skips questions with existing context

**Covers:** PROG-04

**Preconditions:**
- `.pbi-context.md` has both `## Business Question` AND `## Model Context` sections with content

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi deep` | Skill acknowledges existing context for business question and model, then asks ONLY about existing measures |

**Pass criteria:**
- Skill skips questions for sections already in `.pbi-context.md`
- Only the MISSING question (existing measures) is asked
- Existing context is acknowledged, not ignored and not re-asked

---

### Scenario S3-04: Deep mode with description argument

**Covers:** PROG-04

**Preconditions:**
- `.pbi-context.md` is empty or no relevant sections

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi deep build a regional sales comparison dashboard` | Skill acknowledges the description, then still asks remaining intake questions (data model, existing measures) |

**Pass criteria:**
- Description is acknowledged
- Intake questions still proceed for remaining gaps
- Skill does NOT skip intake just because a description was provided

---

### Scenario S3-05: Deep mode context persists for other commands

**Covers:** PROG-04

**Preconditions:**
- S3-02 completed — full deep mode intake done, context written to `.pbi-context.md`

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi new revenue by region measure` | Skill generates the measure using business question and model context from the deep mode session |

**Pass criteria:**
- Generated measure references context gathered during deep mode (e.g., correct table names, relevant business context)
- Skill does NOT re-ask for context that was gathered in deep mode

---

## Group 4: Existing Behavior Preservation

These scenarios verify that the v4.0 changes didn't break existing subcommand routing.

---

### Scenario S4-01: Explicit subcommand still routes correctly

**Covers:** PROG-01 (preservation aspect)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi explain CALCULATE(SUM(Sales[Amount]), FILTER(ALL(Date), Date[Year] = YEAR(TODAY())))` | Skill routes to explain command and outputs an explanation of the DAX |

**Pass criteria:**
- Explanation output, not a DAX solution
- No solve-first behavior triggered
- Explanation covers what CALCULATE, SUM, FILTER, ALL do in context

---

### Scenario S4-02: Empty /pbi shows updated menu

**Covers:** PROG-01 (preservation aspect)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi` (with no arguments) | Category menu appears with options A through E |

**Pass criteria:**
- Menu shows exactly options A, B, C, D, and E
- Option E is "Deep mode" or "Full structured workflow with upfront context gathering"
- Menu prompt says "Type A, B, C, D, or E"

---

### Scenario S4-03: Haiku-routed commands still work

**Covers:** PROG-01 (preservation aspect)

**Preconditions:**
- Working directory is a PBIP project with a git repo and at least one commit (use `tests/fixtures/pbip-tmdl/` if needed)

**Steps:**

| # | User action | Expected skill response |
|---|-------------|------------------------|
| 1 | Type `/pbi diff` | Routes to diff command via haiku Agent, outputs a summary of model changes |

**Pass criteria:**
- Diff output appears (or "no changes" if clean)
- No solve-first behavior
- No behavioral change from v3.0

---

## Verification Notes

- Run smoke tests S1-01 and S4-02 first — these are the fastest confirmation that routing works
- Group 2 scenarios must be run in sequence (S2-01 through S2-06) as they share state
- Group 3 requires a clean `.pbi-context.md` for S3-01 — create a temp copy if needed
- `.pbi-context.md` lives in the root of the open project (or wherever Claude is running from)
