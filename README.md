<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Plugin-blueviolet?style=for-the-badge" alt="Claude Code Plugin">
  <img src="https://img.shields.io/badge/version-8.0.0-blue?style=for-the-badge" alt="Version 8.0.0">
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
  ║   ██╔═══╝ ██╔══██╗██║  · 22 commands  ·  PBIP-native  ║
  ║   ██║     ██████╔╝██║  · UTF-8 safe   ·  local-first  ║
  ║   ╚═╝     ╚═════╝ ╚═╝                        v8.0    ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝
```

**Explain, write, fix, optimise and audit DAX measures and semantic models, directly from your terminal.**

Works with pasted DAX, with [Power BI Project (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview) files on disk, and live against the model open in Power BI Desktop.

[Quick Start](#quick-start) · [Commands](#commands) · [How It Works](#how-it-works) · [Design Principles](#design-principles) · [Installation](#installation) · [Examples](#examples)

</div>

---

## Why

Power BI developers live in two disconnected worlds: DAX gets written in a GUI with no CLI and no version-control workflow, and AI assistance forgets your model between every conversation.

- **DAX is write-only.** A six-month-old measure with nested `CALCULATE`, `SUMX`, and `ALLEXCEPT` has no "explain this" button.
- **PBIP projects are unmanaged.** Microsoft gives you TMDL/TMSL text files, but no tooling to audit, diff, commit, or document them.
- **AI assistance starts from zero.** Every new chat re-learns your tables, relationships, and measures.

PBI turns Claude Code into a **model-aware Power BI co-pilot**: every command indexes your PBIP project from disk in under a second, so explain, audit, edit and new all work against your *actual* tables and relationships.
With the optional live mode, changes land straight in the model open in Power BI Desktop and new measures are executed before you accept them.
Read the full story in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).

---

## Quick Start

In Claude Code:

```
/plugin install pbi --marketplace d7rocket/PowerBI-Skill
```

Then, from any folder:

```
/pbi:help
```

No PBIP project? The measure commands work with DAX pasted straight into the terminal.

Want live editing and DAX testing against Power BI Desktop? Run `/pbi:setup` once. It is optional and asks before installing anything.

---

## Commands

### Work on a measure - *paste DAX, or name a measure in a project*

| Command | What it does |
|:--------|:------------|
| `/pbi:explain` | Plain-English breakdown with filter context, row context, and performance notes |
| `/pbi:format` | Reformat DAX in SQLBI style via DAX Formatter (with offline fallback) |
| `/pbi:optimise` | 14-rule performance scan with before/after. Measures real timings when live |
| `/pbi:comment` | Add inline `//` comments and the description shown in Power BI tooltips |
| `/pbi:error` | Diagnose errors across 7 categories with root cause and a minimal fix |
| `/pbi:new` | A complete measure from plain English: expression, format string, display folder, description |

### Work on the model - *needs a `*.SemanticModel/` folder*

| Command | What it does |
|:--------|:------------|
| `/pbi:load` | The model at a glance: tables, measures, relationships, editing mode |
| `/pbi:edit` | Change a measure, column, property or relationship from a plain-English instruction |
| `/pbi:audit` | 21-rule health check across 8 domains, severity-graded. Report only |
| `/pbi:docs` | Stakeholder-ready project documentation (Markdown / Word / PDF) |
| `/pbi:extract` | Model inventory at three detail levels (overview, standard, deep-dive) |
| `/pbi:deep` | Guided session with hard gates: intake, model review, DAX development, final check |

### History - *local git only*

| Command | What it does |
|:--------|:------------|
| `/pbi:diff` | Human-readable change summary grouped by object type |
| `/pbi:commit` | A local commit with a generated business-language message |
| `/pbi:undo` | Undo the last `/pbi` change, live or on disk, without rewriting history |
| `/pbi:changelog` | `.pbi/changelog.md` from git history in Keep a Changelog format |
| `/pbi:resume` | Where the last session stopped, and what to do next |

### Live Desktop - *optional*

| Command | What it does |
|:--------|:------------|
| `/pbi:setup` | Check requirements and enable live mode (Microsoft's Power BI Modeling MCP), with your consent |
| `/pbi:query` | Run a DAX query against the open model and show the result, optionally with timings |

### Utility

| Command | What it does |
|:--------|:------------|
| `/pbi:menu` | Interactive menu, or ask any DAX or modeling question in plain English |
| `/pbi:version` | Installed version and release notes (offline) |
| `/pbi:help` | The command list |

---

## How It Works

```
                 /pbi:explain   /pbi:edit   /pbi:audit  ...
                              │
              ┌───────────────▼────────────────┐
              │  Preflight (one script call)   │
              │  project, model index, history │
              └───────────────┬────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌────────▼─────────┐
│   Paste mode   │   │    File tier    │   │    Live tier     │
│  no project    │   │  PBIP on disk   │   │  Desktop is open │
│  DAX in, DAX   │   │  edits TMDL or  │   │  edits the model │
│  out           │   │  TMSL files     │   │  through the MCP │
└────────────────┘   └─────────────────┘   └──────────────────┘
```

Every command starts with one fast script call that detects the project, indexes the model from disk (tables, measures, relationships) and reads the session history.
Nothing is cached, so the index is never stale.

Changes follow the same path in both tiers: **preview, your `y`, apply, verify, record**.

- **File tier** edits the TMDL or TMSL files, re-reads the result from disk, and commits locally. If the project is open in Desktop, accept its refresh prompt to see the change.
- **Live tier** applies the change to the model open in Desktop, reads it back, and executes the measure to check it returns a value. Press Ctrl+S in Desktop and the next command commits the saved files with the original message.

### Live mode and Microsoft's MCP server

Live mode uses Microsoft's [Power BI Modeling MCP server](https://github.com/microsoft/powerbi-modeling-mcp).
It is **not installed with this plugin**.
`/pbi:setup` explains what it is, then registers it only if you say yes.

Things to know before you do:

- It is Microsoft software under [Microsoft's own EULA](https://github.com/microsoft/powerbi-modeling-mcp/blob/main/EULA.txt), not this project's MIT license.
- Microsoft states the software may collect information about your use of it and send it to Microsoft.
- It needs Node.js and is published for Windows and Linux.
- This plugin uses it for local Power BI Desktop only. It never connects to a Fabric or Power BI service workspace, and never deploys or publishes.

Remove it any time with `/pbi:setup remove`.

---

## Design Principles

| Principle | What it means in practice |
|:----------|:--------------------------|
| **Simplicity-first DAX** | Generated measures are the simplest expression that answers the question. No `CALCULATE` without filter arguments, no single-use `VAR/RETURN`, no defensive `IFERROR` wrappers. |
| **Preview, then confirm** | Every change to a model shows a before/after and needs your `y`. There is no auto mode. |
| **Verified writes** | After every change the object is read back. In live mode the measure is executed. The command tells you which checks actually ran. |
| **Local only** | Never pulls, pushes, or creates PRs, and never touches the Power BI service. Git is used purely for local checkpoints and undo. |
| **Solve immediately** | Ask a DAX question, get an answer. No intake forms before the co-pilot will help you. |
| **Always-fresh model** | The model is indexed from disk on every command. `.pbi/context.md` keeps command history, notes and failure flags. |
| **UTF-8 safe** | Python-based file operations handle accented characters (é, è, ê, ç, à, ù) in French-language models correctly. |
| **Validated TMDL** | A post-edit hook checks every TMDL write for stray control characters and space-indentation corruption. |

---

## Examples

<details>
<summary><strong>Explain a measure</strong></summary>

```
/pbi:explain Revenue YTD
```

Name a measure from your project, or paste the DAX. You get the business logic, filter context propagation, context transitions, and performance notes. Depth adapts to measure complexity.
</details>

<details>
<summary><strong>Write a new measure</strong></summary>

```
/pbi:new year-to-date revenue for the selected region, in the Sales table
```

Generates the simplest correct DAX plus format string, display folder, and description, validated against your real tables. In live mode it is executed first. You see a preview and confirm before anything is written.
</details>

<details>
<summary><strong>Audit your model</strong></summary>

```
/pbi:audit
```

8 domain passes: relationships, naming, date table, measure quality, hidden columns, report layer, advanced features, performance. 21 rules, severity-graded, each with a suggested fix. The audit never changes the model.
</details>

<details>
<summary><strong>Edit with plain language</strong></summary>

```
/pbi:edit rename [Total Sales] to [Revenue] in the Sales table
```

Finds the measure (accent-safe), updates every reference to the old name, shows a before/after preview, applies the change on your `y`, verifies it, and commits locally.
</details>

<details>
<summary><strong>Check a number</strong></summary>

```
/pbi:query Revenue by Product[Category] --timings
```

Runs the DAX against the model open in Desktop and shows the result with engine timings. Read-only. Needs live mode.
</details>

<details>
<summary><strong>Version control for your model</strong></summary>

```
/pbi:diff        # what changed since last commit
/pbi:commit      # business-language commit
/pbi:undo        # undo the last /pbi change
/pbi:changelog   # release notes from git history
```

All commits are local only. The plugin never touches your remotes.
</details>

---

## Installation

### Install

Inside Claude Code (version 2.1.275 or later):

```
/plugin install pbi --marketplace d7rocket/PowerBI-Skill
```

Or from a shell:

```bash
claude plugin marketplace add d7rocket/PowerBI-Skill
claude plugin install pbi@powerbi-skill
```

### Update

```
/plugin update pbi
```

### Upgrading from version 7

Version 8 is a plugin, and the commands are renamed from `/pbi-explain` to `/pbi:explain`.
The old installer copied files into `~/.claude`. Remove them once so the old commands do not linger:

```powershell
# Windows PowerShell
$names = "explain","format","optimise","comment","error","new","load","audit","audit-fix","diff","commit","edit","undo","comment-batch","changelog","extract","deep","docs","help","version","resume","settings","format-batch"
Remove-Item -Recurse -Force "$HOME\.claude\skills\pbi" -ErrorAction SilentlyContinue
foreach ($n in $names) {
  Remove-Item -Recurse -Force "$HOME\.claude\skills\pbi-$n" -ErrorAction SilentlyContinue
  Remove-Item -Force "$HOME\.claude\commands\pbi-$n.md" -ErrorAction SilentlyContinue
}
```

```bash
# macOS / Linux / WSL
rm -rf ~/.claude/skills/pbi
for n in explain format optimise comment error new load audit audit-fix diff commit edit undo comment-batch changelog extract deep docs help version resume settings format-batch; do
  rm -rf ~/.claude/skills/pbi-$n ~/.claude/commands/pbi-$n.md
done
```

Your projects need no migration. `.pbi/context.md` is read as before, and `.pbi/settings.json` is simply ignored.

Removed in version 8: `/pbi-settings`, `/pbi-comment-batch`, `/pbi-format-batch` and `/pbi-audit-fix`. See the [changelog](plugins/pbi/shared/CHANGELOG.md).

### Develop locally

```bash
git clone https://github.com/d7rocket/PowerBI-Skill.git
cd PowerBI-Skill
claude --plugin-dir plugins/pbi
python tests/test_detect.py
```

<details>
<summary><strong>What gets installed</strong></summary>

```
plugins/pbi/
  .claude-plugin/plugin.json   Manifest (the version lives here)
  skills/<command>/SKILL.md    22 commands, invoked as /pbi:<command>
  scripts/
    detect.py                  Preflight, model index, session log, change journal
    validate-edit.py           Post-edit TMDL validation hook
    gen_docx.py                Word document generation (/pbi:docs)
    gen_pdf.py                 PDF generation (/pbi:docs)
  hooks/hooks.json             Registers the TMDL validation hook
  shared/
    core.md                    Rules every command follows
    live-mode.md               How live editing works
    dax-style.md               DAX style guide
    modeling.md                Modeling guide
    performance.md             Performance guide
    api-notes.md               DAX Formatter API reference
    ui-brand.md                Visual output standards
    pbi-docs-contract.md       Docgen output contract
    CHANGELOG.md               Version history
```

Nothing from Microsoft is installed unless you run `/pbi:setup` and agree.

</details>

---

## Requirements

- [**Claude Code**](https://docs.anthropic.com/en/claude-code) 2.1.275 or later
- A Claude account (claude.ai or API key)
- Python 3.8+ on PATH (used for UTF-8-safe file operations)
- For model commands: a project saved in [PBIP format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- For live mode only: Node.js and Power BI Desktop

---

## Roadmap

- [x] Paste-in DAX commands · PBIP file I/O · measure scaffolding
- [x] Model audit (21 rules) · deep mode workflow · stakeholder docs (Word/PDF)
- [x] Simplicity-first DAX · edit-validation hook
- [x] Claude Code plugin · always-fresh model index · change journal and undo
- [x] Live mode: edit and test against Power BI Desktop · `/pbi:query`
- [ ] Report commands (pages, visuals, themes)
- [ ] Cross-measure dependency graph
- [ ] Side-by-side measure comparison
- [ ] Power Query error diagnosis

---

## Contributing

Issues and pull requests are welcome. If you hit a bug in a specific command, include the command name, your project format (TMDL/TMSL), whether live mode was active, and the DAX involved. `/pbi:version` output helps too. See the [changelog](plugins/pbi/shared/CHANGELOG.md) for release history.

## Acknowledgements

The DAX, modeling and performance guides draw on Microsoft's [skills-for-fabric](https://github.com/microsoft/skills-for-fabric) (MIT License).

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built for Power BI developers who live in the terminal.</sub>
</p>
