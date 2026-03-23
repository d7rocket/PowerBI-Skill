<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-4.3-blue?style=for-the-badge" alt="Version 4.3">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Power_BI-DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI DAX">
</p>

<div align="center">

```
  ██████╗ ██████╗ ██╗
  ██╔══██╗██╔══██╗██║
  ██████╔╝██████╔╝██║   Power BI DAX Co-pilot
  ██╔═══╝ ██╔══██╗██║   for Claude Code
  ██║     ██████╔╝██║
  ╚═╝     ╚═════╝ ╚═╝   v4.3
```

**Explain, format, optimise, audit, and edit DAX measures — directly from your terminal.**
Works with pasted DAX *and* with Power BI Project (PBIP) files on disk.

</div>

---

## Quick Start

```powershell
# Install (Windows) — one command, all projects
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex

# Then open Claude Code and type:
/pbi
```

```bash
# Install (macOS / Linux / WSL)
curl -sL https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.sh | bash
```

---

## What's New in v4.3

| Feature | Details |
|:--------|:--------|
| **Python-first UTF-8** | All file ops use Python with `encoding='utf-8'`. French accents handled correctly. Zero grep/sed. |
| **`/pbi docs`** | Generate polished project documentation for stakeholders |
| **`/pbi version`** | View full version history offline from within Claude Code |
| **Context tracking** | Progress bar estimates context usage, suggests `/clear` when high |
| **Installer overhaul** | `-Scope project\|user`, correct GitHub URL, all files included |
| **Token safety** | Chunked reading for large model.bim files — no more 10K token errors |

---

## Commands

### Paste-in — *work anywhere, just paste your DAX*

| Command | What it does |
|:--------|:------------|
| `explain` | Plain-English breakdown |
| `format` | Auto-format via DAX Formatter API |
| `optimise` | 13-rule performance scan with diff |
| `comment` | Add `//` comments + description |
| `error` | Diagnose errors (7 categories) |
| `new` | Scaffold a measure from plain English |

### PBIP Project — *auto-detected when `*.SemanticModel/` exists*

| Command | What it does |
|:--------|:------------|
| `audit` | Model health scan + auto-fix (19 rules) |
| `edit` | Change your model with plain language |
| `docs` | Project documentation for stakeholders |
| `extract` | Export documentation (3 tiers) |
| `diff` | Human-readable change summary |
| `commit` | Business-language auto-commits |
| `undo` | Revert the last auto-commit |
| `changelog` | Generate CHANGELOG from git history |
| `comment-batch` | Comment every measure in a table |

### Workflow & Utility

| Command | What it does |
|:--------|:------------|
| `deep` | Guided workflow: intake, model review, DAX dev, verification |
| `version` | Full version history with release notes |
| `help` | Command reference with update check |

> All commands are invoked as `/pbi <command>` — e.g. `/pbi audit`

---

## How It Works

```
                 ┌─────────────────────────┐
                 │   You type /pbi [cmd]    │
                 └────────────┬────────────┘
                              │
                 ┌────────────▼────────────┐
                 │    5 detection blocks    │
                 │  PBIP? Format? Git? etc  │
                 └────────────┬────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼───────┐ ┌────▼────┐ ┌────────▼────────┐
     │   Paste-in     │ │  PBIP   │ │   Workflow      │
     │ explain format │ │ audit   │ │ deep extract    │
     │ optimise new   │ │ edit    │ │ docs version    │
     │ comment error  │ │ diff    │ │ help            │
     │                │ │ commit  │ │                 │
     │   Sonnet       │ │ Haiku   │ │   Sonnet/Opus   │
     └────────────────┘ └─────────┘ └─────────────────┘
```

| Feature | How |
|:--------|:----|
| **Auto-Resume** | Context loads automatically — no `/pbi load` needed |
| **Local-First Git** | Never pulls, pushes, or creates PRs. Your files are the source of truth. |
| **Session Memory** | `.pbi-context.md` persists model context, command history, failure flags |
| **Smart Routing** | Sonnet for DAX reasoning, Haiku for file ops, Opus for deep extraction |
| **UTF-8 Safe** | Python-based search handles French accents (e, e, c, a, u) |

---

## Installation Options

### PowerShell (Windows)

User-level (default) — available in all projects:

```powershell
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex
```

Project-level — installs into current directory only:

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

Or copy just the skill into an existing project:

```bash
git clone https://github.com/d7rocket/PowerBI-Skill.git /tmp/pbi-skill
cp -r /tmp/pbi-skill/.claude your-project/.claude
```

<details>
<summary>What gets installed</summary>

```
.claude/skills/pbi/
  SKILL.md              Router + detection blocks
  commands/             19 command files (.md)
  scripts/detect.py     UTF-8 detection + search (10 subcommands)
  shared/
    api-notes.md        DAX Formatter API reference
    CHANGELOG.md        Version history
```

</details>

---

## Examples

<details>
<summary><strong>Explain a measure</strong></summary>

```
/pbi explain

> Revenue YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))
```
Get a structured breakdown — filter context, row context, context transitions, and performance notes.
</details>

<details>
<summary><strong>Scaffold a new measure</strong></summary>

```
/pbi new
> year-to-date revenue filtered to the selected region, in the Sales table
```
Generates the DAX, format string, display folder, and description — writes to PBIP if detected.
</details>

<details>
<summary><strong>Audit your model</strong></summary>

```
/pbi audit
```
8 domain passes: relationships, naming, date table, measure quality, hidden columns, report layer, advanced features, performance. Severity-graded report with auto-fix.
</details>

<details>
<summary><strong>Edit with plain language</strong></summary>

```
/pbi edit
> rename [Total Sales] to [Revenue] in the Sales table
```
Finds the measure, applies the change, auto-commits.
</details>

<details>
<summary><strong>Deep mode</strong></summary>

```
/pbi deep
```
Four-phase guided workflow with hard gates: business context intake, model review, DAX development, final verification.
</details>

<details>
<summary><strong>Version control</strong></summary>

```
/pbi diff        # what changed since last commit
/pbi commit      # auto-generated business-language commit
/pbi undo        # revert the last auto-commit
/pbi changelog   # generate CHANGELOG.md from history
```
All commits are local only.
</details>

---

## Requirements

- [**Claude Code**](https://docs.anthropic.com/en/claude-code) CLI
- A Claude account (claude.ai or API key)
- For PBIP commands: a project in [PBIP format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

---

## Roadmap

- [x] Paste-in DAX commands (explain, format, optimise, comment, error)
- [x] PBIP file I/O (load, audit, diff, commit, edit, undo)
- [x] Measure scaffolding, batch commenting, audit auto-fix, changelog
- [x] Single-skill router, one-liner install, parallel audit agents
- [x] Auto-resume context, local-first git, expanded audit rules
- [x] Deep mode workflow, project extraction (3 tiers)
- [x] Python-first UTF-8, `/pbi docs`, context tracking
- [x] Installer overhaul, token safety, `/pbi version`
- [ ] Cross-measure dependency graph
- [ ] Side-by-side measure comparison
- [ ] Calculated column support
- [ ] Power Query error diagnosis

---

## License

MIT

---

<p align="center">
  <sub>Built for Power BI developers who live in the terminal.</sub>
</p>
