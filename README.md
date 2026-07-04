<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-7.1.0-blue?style=for-the-badge" alt="Version 7.1.0">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Power_BI-DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI DAX">
</p>

<div align="center">

```
  ╔═══════════════════════════════════════════════════════╗
  ║                                                       ║
  ║   ██████╗ ██████╗ ██╗  · Power BI DAX Co-pilot        ║
  ║   ██╔══██╗██╔══██╗██║  · for Claude Code              ║
  ║   ██████╔╝██████╔╝██║  ·                              ║
  ║   ██╔═══╝ ██╔══██╗██║  · 23 commands  ·  PBIP-native  ║
  ║   ██║     ██████╔╝██║  · UTF-8 safe   ·  local-first  ║
  ║   ╚═╝     ╚═════╝ ╚═╝                        v7.1    ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝
```

**Explain, format, optimise, audit, and edit DAX measures — directly from your terminal.**

Works with pasted DAX *and* with [Power BI Project (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview) files on disk.

[Quick Start](#quick-start) · [Commands](#commands) · [How It Works](#how-it-works) · [Design Principles](#design-principles) · [Installation](#installation-options) · [Examples](#examples)

</div>

---

## Why

Power BI developers live in two disconnected worlds: DAX gets written in a GUI with no CLI and no version-control workflow, and AI assistance forgets your model between every conversation.

- **DAX is write-only.** A six-month-old measure with nested `CALCULATE`, `SUMX`, and `ALLEXCEPT` has no "explain this" button.
- **PBIP projects are unmanaged.** Microsoft gives you TMDL/TMSL text files — but no tooling to audit, diff, commit, or document them.
- **AI assistance starts from zero.** Every new chat re-learns your tables, relationships, and measures.

PBI Skill turns Claude Code into a **persistent, model-aware Power BI co-pilot**: it reads your PBIP files once per session, caches the model structure, and every command — explain, audit, edit, new — works against your *actual* tables and relationships. Read the full story in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).

---

## Quick Start

```powershell
# Windows — one command, all projects
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex
```

```bash
# macOS / Linux / WSL
curl -sL https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.sh | bash
```

Then open Claude Code anywhere and type:

```
/pbi-help
```

No PBIP project? Every paste-in command works with DAX pasted straight into the terminal.

---

## Commands

### 📋 Paste-in — *work anywhere, just paste your DAX*

| Command | What it does |
|:--------|:------------|
| `/pbi-explain` | Structured plain-English breakdown with filter context, row context, and performance notes |
| `/pbi-format` | Reformat DAX for readability via DAX Formatter API (with offline fallback) |
| `/pbi-optimise` | 14-rule performance scan with severity-graded findings and before/after diffs |
| `/pbi-comment` | Add inline `//` comments and description property for Power BI tooltips |
| `/pbi-error` | Diagnose errors across 7 categories with root cause analysis and minimal-fix suggestions |
| `/pbi-new` | Generate a complete measure from plain English — expression, format string, display folder, description |

### 🗂️ PBIP Project — *auto-detected when `*.SemanticModel/` exists*

| Command | What it does |
|:--------|:------------|
| `/pbi-load` | Parse the semantic model (TMDL or TMSL) into session context |
| `/pbi-audit` | 21-rule health check across 8 domains with severity grading and auto-fix |
| `/pbi-audit-fix` | Autonomous pipeline: scan → fix → validate → commit for auto-fixable findings |
| `/pbi-edit` | Modify measures, columns, and tables using plain-English instructions |
| `/pbi-docs` | Generate polished, stakeholder-ready project documentation (Markdown / Word / PDF) |
| `/pbi-extract` | Export model summary at three detail levels (overview, standard, deep-dive) |
| `/pbi-format-batch` | Apply SQLBI-standard formatting to every measure — no API dependency |
| `/pbi-comment-batch` | Add descriptions to every undocumented measure in the model |
| `/pbi-diff` | Human-readable change summary grouped by entity type |
| `/pbi-commit` | Auto-generated business-language commits (local only) |
| `/pbi-undo` | Safely revert the last auto-commit using git revert |
| `/pbi-changelog` | Generate `.pbi/changelog.md` from git history in Keep a Changelog format |

### 🧭 Workflow & Utility

| Command | What it does |
|:--------|:------------|
| `/pbi-deep` | Four-phase guided workflow with hard gates: intake, model review, DAX dev, verification |
| `/pbi-resume` | Restore session context and continue from where you left off |
| `/pbi-settings` | Toggle auto mode (silent writes) vs confirm mode (preview before every write) |
| `/pbi-version` | Display installed version and full changelog history (offline) |
| `/pbi-help` | Complete command reference with offline version check |
| `/pbi` | Interactive menu, backward-compatible router, and free-text DAX solver |

---

## How It Works

```
             ┌───────────────────────────────┐
             │  /pbi-explain  /pbi-audit ... │  ← direct invocation
             └──────────────┬────────────────┘
                            │
             ┌──────────────▼────────────────┐
             │  Each sub-skill runs its own   │
             │  detection blocks + resume     │
             └──────────────┬────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌─────────▼─────────┐
│   Paste-in     │  │    PBIP     │  │    Workflow        │
│ explain format │  │ audit edit  │  │ deep extract       │
│ optimise new   │  │ diff commit │  │ docs resume        │
│ comment error  │  │ undo load   │  │ help settings      │
│                │  │ audit-fix   │  │                    │
│   Sonnet       │  │ Haiku/Son.  │  │   Sonnet/Opus      │
└────────────────┘  └─────────────┘  └────────────────────┘
```

Each command is a self-contained skill: it detects your project format (TMDL or TMSL), loads cached session context, and knows whether it can write files or should stay paste-only. The first command of a session refreshes the model automatically — no explicit `/pbi-load` needed.

---

## Design Principles

| Principle | What it means in practice |
|:----------|:--------------------------|
| **Simplicity-first DAX** | Generated measures are the simplest expression that answers the question. No `CALCULATE` without filter arguments, no single-use `VAR/RETURN`, no defensive `IFERROR` wrappers. |
| **Local-first git** | Never pulls, pushes, or creates PRs. Your files are always the source of truth; git is used purely for local checkpoints and undo. |
| **Solve immediately, interrogate never** | Ask a DAX question, get an answer. No intake forms before the skill will help you. |
| **Session memory** | `.pbi/context.md` persists model structure, command history, and failure flags across commands. |
| **Confirm mode** | By default, every file write shows a preview and asks `(y/N)`. Flip to silent auto-writes with `/pbi-settings`. |
| **UTF-8 safe** | Python-based file operations handle accented characters (é, è, ê, ç, à, ù) in French-language models correctly. |
| **Validated writes** | A post-edit hook checks every TMDL write for stray control characters and space-indentation corruption. |

---

## Examples

<details>
<summary><strong>Explain a measure</strong></summary>

```
/pbi-explain Revenue YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))
```

Structured breakdown — business logic, filter context propagation, context transitions, and performance notes. Depth adapts to measure complexity.
</details>

<details>
<summary><strong>Scaffold a new measure</strong></summary>

```
/pbi-new
> year-to-date revenue filtered to the selected region, in the Sales table
```

Generates the simplest correct DAX plus format string, display folder, and description — validates against your real tables and writes to PBIP if detected.
</details>

<details>
<summary><strong>Audit your model</strong></summary>

```
/pbi-audit
```

8 domain passes — relationships, naming, date table, measure quality, hidden columns, report layer, advanced features, performance. 21 rules, severity-graded, with auto-fix. Parallel agents kick in for models with 5+ tables.
</details>

<details>
<summary><strong>Fix everything automatically</strong></summary>

```
/pbi-audit-fix
```

Autonomous pipeline: scans the model, applies safe fixes (descriptions, control characters, key-column hygiene, display folders), validates file integrity, and commits only if clean.
</details>

<details>
<summary><strong>Edit with plain language</strong></summary>

```
/pbi-edit
> rename [Total Sales] to [Revenue] in the Sales table
```

Finds the measure (accent-safe), shows a before/after preview, applies the change, auto-commits locally.
</details>

<details>
<summary><strong>Version control for your model</strong></summary>

```
/pbi-diff        # what changed since last commit
/pbi-commit      # auto-generated business-language commit
/pbi-undo        # revert the last auto-commit
/pbi-changelog   # release notes from git history
```

All commits are local only — the skill never touches your remotes.
</details>

---

## Installation Options

### PowerShell (Windows)

User-level (default) — available in all projects:

```powershell
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex
```

Project-level — installs into the current directory only:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1))) -Scope project
```

### Bash (macOS / Linux / WSL)

```bash
curl -sL https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.sh | bash
```

### Manual / Git Clone

```bash
git clone https://github.com/d7rocket/PowerBI-Skill.git
cd PowerBI-Skill && claude
```

Upgrading from an older version? Just re-run the installer — it migrates legacy layouts and removes pre-7.1 leftovers automatically.

<details>
<summary><strong>What gets installed</strong></summary>

```
.claude/skills/
  pbi/
    SKILL.md               Base skill (menu + catch-all + backward-compatible router)
    scripts/
      detect.py            UTF-8 detection + search (15 subcommands)
      validate-edit.py     Post-edit TMDL validation hook
      gen_docx.py          Word document generation (/pbi-docs)
      gen_pdf.py           PDF generation (/pbi-docs)
    shared/
      api-notes.md         DAX Formatter API reference
      CHANGELOG.md         Version history
      ui-brand.md          Visual output standards reference
      pbi-docs-contract.md Docgen output contract
  pbi-explain/SKILL.md     23 self-contained sub-skills, each with its own
  pbi-format/SKILL.md      detection blocks, auto-resume, and instructions.
  pbi-optimise/SKILL.md    Invoked as /pbi-<cmd> (e.g., /pbi-explain).
  pbi-comment/SKILL.md
  pbi-error/SKILL.md
  pbi-new/SKILL.md
  pbi-load/SKILL.md
  pbi-audit/SKILL.md
  pbi-audit-fix/SKILL.md   Autonomous scan → fix → validate → commit
  pbi-diff/SKILL.md
  pbi-commit/SKILL.md
  pbi-edit/SKILL.md
  pbi-undo/SKILL.md
  pbi-comment-batch/SKILL.md
  pbi-changelog/SKILL.md
  pbi-format-batch/SKILL.md  Bulk-format all measures (no API dependency)
  pbi-deep/SKILL.md
  pbi-extract/SKILL.md
  pbi-docs/SKILL.md
  pbi-help/SKILL.md
  pbi-version/SKILL.md
  pbi-resume/SKILL.md      Session resume and context restoration
  pbi-settings/SKILL.md    Write-mode toggle (auto / confirm)

~/.claude/commands/
  pbi-<cmd>.md             One slash-command descriptor per sub-skill
```

</details>

---

## Requirements

- [**Claude Code**](https://docs.anthropic.com/en/claude-code) CLI
- A Claude account (claude.ai or API key)
- Python 3.8+ on PATH (used for UTF-8-safe file operations)
- For PBIP commands: a project saved in [PBIP format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

> **Note:** Power BI Desktop does not hot-reload external PBIP file changes — close and reopen the project after the skill edits model files.

---

## Roadmap

- [x] Paste-in DAX commands · PBIP file I/O · measure scaffolding
- [x] Model audit (21 rules) + autonomous audit-fix pipeline
- [x] Deep mode workflow · project extraction · stakeholder docs (Word/PDF)
- [x] Sub-skill architecture — every command its own `/pbi-<cmd>` skill
- [x] Session-aware auto-load · `.pbi/` context directory · write-mode toggle
- [x] Simplicity-first DAX · edit-validation hook · flat v7.1 structure
- [ ] Cross-measure dependency graph
- [ ] Side-by-side measure comparison
- [ ] Calculated column support
- [ ] Power Query error diagnosis

---

## Contributing

Issues and pull requests are welcome. If you hit a bug in a specific command, include the command name, your project format (TMDL/TMSL), and the DAX involved — `/pbi-version` output helps too. See [CHANGELOG](.claude/skills/pbi/shared/CHANGELOG.md) for release history.

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built for Power BI developers who live in the terminal.</sub>
</p>
