---
name: setup
description: "Enable or remove live mode (Microsoft's Power BI Modeling MCP), with your consent."
model: sonnet
argument-hint: "[status | remove]"
allowed-tools: Read, Bash
disable-model-invocation: true
---

## Environment

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" env 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" env 2>&1 || echo "PYTHON=missing"`

# /pbi:setup

Request: $ARGUMENTS

The plugin works without any of this: explaining, formatting, auditing and editing project files need only Python.
Live mode is optional and is never installed without an explicit yes.

## Step 1 - Report status

Check whether the Power BI Modeling MCP tools are available in this session (tool names containing `powerbi-modeling`; search once if your tools are deferred).

```
pbi setup

  Python            [version | MISSING]
  Node.js / npx     [versions | missing]      needed for live mode only
  Power BI Desktop  [running | not running | not detectable on this system]
  Live mode         [active | registered, restart Claude Code to load it | not set up]
```

- `PYTHON=missing`: say `Python 3 is required. Install it from python.org, then run /pbi:setup again.` and stop.
- Request is `status`: stop here.
- Request is `remove`: go to Step 6.
- Live mode active: go to Step 5.
- Registered but tools not loaded: say `Restart Claude Code (or reconnect it under /mcp), then run /pbi:setup again.` and stop.

## Step 2 - Explain before installing

Show this in full. Do not shorten it.

```
Live mode uses Microsoft's Power BI Modeling MCP server.

What it adds
  - Edits apply straight to the model open in Power BI Desktop, no reopening.
  - New and changed measures are executed and checked before you accept them.
  - /pbi:query runs DAX and shows real results and timings.

What gets installed
  - The npm package @microsoft/powerbi-modeling-mcp (major version 1), started by npx
    as a local process each time Claude Code starts. Nothing else.
  - Requires Node.js. Published for Windows and Linux only.

What you should know
  - It is Microsoft software under Microsoft's own EULA, not this plugin's MIT license:
    https://github.com/microsoft/powerbi-modeling-mcp/blob/main/EULA.txt
  - Microsoft states the software may collect information about your use of it and
    send it to Microsoft.
  - Model metadata and query results it returns become part of this conversation,
    exactly like files Claude reads.
  - This plugin uses it for local Power BI Desktop only. It never connects to a
    Fabric or Power BI service workspace and never publishes.

Install and register it? (y/N)
```

Anything other than `y` or `Y`: say `Nothing was installed. The plugin keeps working on project files.` and stop.

## Step 3 - Check Node

If `NODE` or `NPX` is `missing`: say `Live mode needs Node.js. Install the LTS version from nodejs.org, then run /pbi:setup again.` and stop.
Do not install Node yourself.

## Step 4 - Register

Register at user scope so it is available in every project.

Windows (`PLATFORM=windows`):

```bash
claude mcp add --scope user powerbi-modeling-mcp -- cmd /c npx -y @microsoft/powerbi-modeling-mcp@1 --start
```

Other platforms:

```bash
claude mcp add --scope user powerbi-modeling-mcp -- npx -y @microsoft/powerbi-modeling-mcp@1 --start
```

Then verify with `claude mcp get powerbi-modeling-mcp` and show its output.

- Verified: say `Registered. Restart Claude Code, open your project in Power BI Desktop, then run /pbi:setup once more to accept the EULA and test the connection.` and stop.
- The command failed: show the exact error. Do not retry with different flags. Suggest the manual configuration from Microsoft's README.

## Step 5 - Accept the EULA and test

Only when the MCP tools are available.

1. Make one harmless call: list local Power BI Desktop instances with `connection_operations`.
2. If the server answers that the EULA must be accepted:
   - Ask `Do you accept Microsoft's EULA for the Power BI Modeling MCP server? (link above) (y/N)`.
   - Only on `y` or `Y`, call the `accept_eula` tool, then repeat the call.
   - Otherwise stop. Live mode stays inactive.
3. Report:
   - No Desktop instance: `Live mode is ready. Open a project in Power BI Desktop to use it.`
   - An instance was found: connect to it, run `EVALUATE ROW("ok", 1)` with `dax_query_operations`, and say `Live mode works: connected to [file name].`

## Step 6 - Remove

```bash
claude mcp remove powerbi-modeling-mcp --scope user
```

Say `Live mode removed. The plugin keeps working on project files.`
The npm cache copy can be cleared with `npm cache clean --force`, which the analyst may run themselves.

## Never

- Install or register anything without the explicit `y` from Step 2.
- Accept the EULA on the analyst's behalf without the explicit `y` from Step 5.
- Add `--accepteula` or the `PBI_MODELING_MCP_ACCEPT_EULA` variable to the registration.
- Install Node.js, Python or Power BI Desktop.
