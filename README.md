# PowerBI DAX Skills for Claude Code

A set of Claude Code slash commands (`/pbi:*`) that turn Claude into a Power BI DAX co-pilot. Paste in a DAX measure and get plain-English explanations, auto-formatting via the DAX Formatter API, optimisation suggestions with rule-based rewrites, inline comments, and error diagnosis — all with session memory that persists across commands.

For PBIP (Power BI Project) users: skills auto-detect `.SemanticModel/` directories, read/write TMDL and TMSL files directly, run model-wide audits with auto-fix, show diffs, manage branches, and commit changes — no copy-paste needed.

---

## Quick Install (add to an existing project)

Copy the `.claude/skills/` folder into any project directory. That's it — Claude Code discovers skills automatically.

**Option A — Clone and copy:**

```bash
git clone https://github.com/deveshd7/PowerBI-Skill.git /tmp/pbi-skill
cp -r /tmp/pbi-skill/.claude your-project/.claude
```

**Option B — Download just the skills (no git needed):**

```bash
# From your project root:
mkdir -p .claude/skills
curl -sL https://github.com/deveshd7/PowerBI-Skill/archive/refs/heads/main.tar.gz | \
  tar xz --strip-components=2 -C .claude/skills "PowerBI-Skill-main/.claude/skills"
```

**Option C — Clone the whole repo and work inside it:**

```bash
git clone https://github.com/deveshd7/PowerBI-Skill.git
cd PowerBI-Skill
claude
```

After installing, open Claude Code in your project directory and type `/` — you should see `pbi:` commands in the list.

---

## Commands

### DAX Measure Commands (paste-in — works anywhere)

| Command | What it does |
|---------|-------------|
| `/pbi:explain` | Explains a DAX measure in plain English — filter context, row context, context transitions, performance notes |
| `/pbi:format` | Formats DAX using the DAX Formatter API (falls back to Claude inline formatting if API is unreachable) |
| `/pbi:optimise` | Applies 10 optimisation rules, detects context-transition guards, outputs side-by-side original vs optimised |
| `/pbi:comment` | Adds inline `//` comments and generates a Description Field value ready to paste into Power BI |
| `/pbi:error` | Diagnoses a Power BI error message using session context, correlates with last command run |
| `/pbi:new` | Scaffolds a new DAX measure from a plain-English description — generates expression, format string, display folder, and description |

### PBIP Project Commands (require `.SemanticModel/` directory)

| Command | What it does |
|---------|-------------|
| `/pbi:load` | Reads your PBIP project and loads table/measure/column context for all other commands |
| `/pbi:audit` | Full model health audit — relationships, naming, date table, measures, hidden column hygiene, PBIR visual layer — with auto-fix mode |
| `/pbi:diff` | Shows a human-readable summary of model changes since the last git commit |
| `/pbi:commit` | Stages `.SemanticModel/` changes and creates a git commit with an auto-generated business-language message |
| `/pbi:edit` | Describe any model change in plain language and have Claude apply it directly to PBIP files |
| `/pbi:undo` | Revert the last auto-committed model change (safety net for edit, comment, error auto-commits) |
| `/pbi:comment-batch` | Apply commenting across all measures in a table or the entire model at once |
| `/pbi:branch` | Create and manage feature branches — create, switch, merge, list |
| `/pbi:changelog` | Generate a human-readable CHANGELOG.md from git history |

### Router

| Command | What it does |
|---------|-------------|
| `/pbi` | Entry point — routes to the right subcommand based on what you describe, or shows a category menu |

---

## How It Works

### Paste-in mode (no PBIP project)

All DAX commands work by pasting a measure directly into chat. Just invoke the command, paste your DAX when prompted, and get the result.

### File mode (PBIP project detected)

When Claude detects a `.SemanticModel/` directory, commands like `/pbi:comment`, `/pbi:error`, `/pbi:edit`, and `/pbi:new` can read and write model files directly. They also check whether Power BI Desktop is open — if it is, output is paste-ready (to avoid file conflicts); if Desktop is closed, changes are written to disk and auto-committed.

### Session Memory

All commands read and write `.pbi-context.md` at the project root. This file tracks:

- **Last Command** — command, timestamp, measure name, outcome
- **Command History** — rolling log of last 20 commands
- **Model Context** — tables, measures, columns, relationships (populated by `/pbi:load`)
- **Analyst-Reported Failures** — you manage this section manually to flag approaches that have already failed

The failure log feeds back into every command: if a measure has a known failed approach, the command will flag it before generating output.

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/claude-code) (the CLI)
- A Claude account (claude.ai or API key)
- For PBIP commands: a Power BI project saved in PBIP format (`.SemanticModel/` directory)

---

## Usage Examples

### Explain a measure

```
/pbi:explain
> Paste your DAX measure below:
Revenue YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))
```

### Scaffold a new measure

```
/pbi:new
> Describe the measure you want to create:
year-to-date revenue filtered to the selected region, in the Sales table
```

### Format a measure

```
/pbi:format
```

Probes the DAX Formatter API at startup. If reachable, uses it. If not, formats inline with a note.

### Optimise a measure

```
/pbi:optimise
```

Checks for 10 common performance issues and shows a side-by-side diff with explanations.

### Audit your model

```
/pbi:audit
```

Runs 6 domain passes (relationships, naming, date table, measures, hidden columns, report layer) and produces a severity-graded report. Offers auto-fix for CRITICAL and WARN findings.

### Comment all measures in a table

```
/pbi:comment-batch Sales
```

### Edit a model file with plain language

```
/pbi:edit
> Describe the change you want to make:
rename [Total Sales] to [Revenue] in the Sales table
```

### Manage branches and history

```
/pbi:branch create add-revenue-measures
/pbi:branch merge
/pbi:diff
/pbi:commit
/pbi:changelog
/pbi:undo
```

---

## Project Structure

```
.
├── .claude/
│   └── skills/
│       ├── pbi/SKILL.md                  ← router / entry point (v2.0.0)
│       ├── pbi-explain/SKILL.md          ← DAX explanation
│       ├── pbi-format/SKILL.md           ← DAX formatting
│       ├── pbi-format/api-notes.md       ← DAX Formatter API reference
│       ├── pbi-optimise/SKILL.md         ← DAX optimisation (10 rules)
│       ├── pbi-comment/SKILL.md          ← DAX commenting + description
│       ├── pbi-comment-batch/SKILL.md    ← batch commenting (v2)
│       ├── pbi-error/SKILL.md            ← error diagnosis
│       ├── pbi-load/SKILL.md             ← PBIP context loader
│       ├── pbi-audit/SKILL.md            ← model audit + auto-fix + PBIR (v2)
│       ├── pbi-new/SKILL.md              ← measure scaffolding (v2)
│       ├── pbi-diff/SKILL.md             ← model change summary
│       ├── pbi-commit/SKILL.md           ← git commit with auto-message
│       ├── pbi-branch/SKILL.md           ← feature branch workflow (v2)
│       ├── pbi-changelog/SKILL.md        ← changelog generation (v2)
│       ├── pbi-edit/SKILL.md             ← plain-language model editing
│       └── pbi-undo/SKILL.md             ← revert last auto-commit
├── .pbi-context.md                       ← session memory (auto-updated)
├── tests/
│   └── fixtures/                         ← sample PBIP projects for testing
└── README.md
```

---

## Roadmap

- **v1.0 (complete):** Paste-in DAX commands — explain, format, optimise, comment, error
- **v1.0 (complete):** PBIP file I/O — load, audit, diff, commit, edit, undo
- **v2.0 (complete):** New measure scaffolding, batch commenting, hidden column hygiene, audit auto-fix, feature branches, changelog, PBIR visual layer audit
- **Next:** Cross-measure dependency graph, side-by-side measure comparison, calculated column support, Power Query error diagnosis

---

## License

MIT
