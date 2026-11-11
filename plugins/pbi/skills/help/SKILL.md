---
name: help
description: "List every /pbi command with a one-line purpose, grouped by what it needs (pasted DAX, a PBIP project, or live Desktop)."
model: haiku
allowed-tools: Bash
disable-model-invocation: true
---

## Installed version

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" version 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" version 2>&1 || echo "LOCAL=unknown"`

# /pbi:help

Output exactly this, with the installed version filled in:

```
pbi [LOCAL version]  Power BI DAX co-pilot

WORK ON A MEASURE (paste DAX, or name a measure in a project)
  /pbi:explain    What a measure does, in plain English
  /pbi:format     Format DAX (SQLBI style)
  /pbi:optimise   Find slow patterns; measures real timings when live
  /pbi:comment    Add comments and a description
  /pbi:error      Diagnose a DAX error and fix it
  /pbi:new        Write a new measure from a business need

WORK ON THE MODEL (needs a PBIP project folder)
  /pbi:load       Model at a glance
  /pbi:edit       Change a measure, column, property or relationship
  /pbi:audit      Health check with severities (report only)
  /pbi:extract    Model inventory for handover
  /pbi:docs       Client-ready documentation
  /pbi:deep       Guided session for a hard problem

HISTORY (local git only, nothing is ever pushed)
  /pbi:diff       What changed since the last commit
  /pbi:commit     Save a snapshot with a business message
  /pbi:undo       Undo the last /pbi change
  /pbi:changelog  Change history in business language
  /pbi:resume     Where the last session stopped

LIVE DESKTOP (optional, after /pbi:setup)
  /pbi:query      Run a DAX query against the open model
  /pbi:setup      Enable live editing through Microsoft's Power BI Modeling MCP

OTHER
  /pbi:menu       Menu, or ask anything in plain English
  /pbi:version    Installed version and release notes
  /pbi:help       This list

Every change to a model is previewed and needs your "y" before it is written.
Report commands (pages, visuals) are planned for a later release.
```

If `$ARGUMENTS` names a command, output only that command's line and one usage example.
