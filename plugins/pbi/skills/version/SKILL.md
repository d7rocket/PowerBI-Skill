---
name: version
description: "Show the installed version of the pbi plugin and what changed in recent releases. Works offline."
model: haiku
allowed-tools: Read, Bash
disable-model-invocation: true
---

## Installed version

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" version 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" version 2>&1 || echo "LOCAL=unknown"`

# /pbi:version

1. Read `${CLAUDE_PLUGIN_ROOT}/shared/CHANGELOG.md`.
2. Output:

```
pbi [LOCAL version]

[the newest three release entries from the changelog: version, date and their bullet points, unchanged]

Update: /plugin update pbi
```

- If `$ARGUMENTS` names a version, show that release entry instead of the newest three.
- If the changelog cannot be read, print the version line and the update line only.
- If the newest changelog entry does not match the installed version, add `Changelog and installed version differ.` Do not guess which is right.

No network access. No project files are read or written.
