#!/usr/bin/env python3
"""Post-edit validation hook for TMDL and Python files.

Reads hook input from stdin (JSON), checks the edited file:
- .tmdl files: scans for stray control characters (not \\n, \\r, \\t)
             and for space-indented lines (TMDL requires tabs)
- .py files: runs py_compile to check syntax

Exit codes:
    0 — validation passed (or file type not checked)
    1 — warning: non-blocking issue found (e.g., space indentation in TMDL)
    2 — blocking error: validation failed, Claude should fix before continuing
"""
import json
import re
import sys
import os
import py_compile


def validate_tmdl(file_path):
    """Check for stray control characters in TMDL files."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"TMDL validation: cannot read {file_path}: {e}", file=sys.stderr)
        return False

    bad_chars = []
    for i, ch in enumerate(content):
        if ord(ch) < 32 and ch not in "\n\r\t":
            line_num = content[:i].count("\n") + 1
            bad_chars.append((line_num, repr(ch)))

    if bad_chars:
        print(f"TMDL validation FAILED — stray control characters in {os.path.basename(file_path)}:", file=sys.stderr)
        for line_num, char_repr in bad_chars[:10]:
            print(f"  Line {line_num}: {char_repr}", file=sys.stderr)
        if len(bad_chars) > 10:
            print(f"  ... and {len(bad_chars) - 10} more", file=sys.stderr)
        return False

    return True


def check_tmdl_indentation(file_path):
    """Warn on space-indented lines in TMDL files (TMDL requires tabs).

    Flags lines matching ^\\t* +\\S — i.e., optional tabs followed by one or
    more spaces before content. Returns True when no space indentation found.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        print(f"TMDL indentation check: cannot read {file_path}: {e}", file=sys.stderr)
        return True  # unreadable already reported by control-char check

    pattern = re.compile(r"^\t* +\S")
    bad_lines = [i + 1 for i, line in enumerate(lines) if pattern.match(line)]

    if bad_lines:
        print(f"TMDL indentation WARNING — space-indented lines in {os.path.basename(file_path)} (TMDL requires tabs):", file=sys.stderr)
        for line_num in bad_lines[:10]:
            print(f"  Line {line_num}: space indentation", file=sys.stderr)
        if len(bad_lines) > 10:
            print(f"  ... and {len(bad_lines) - 10} more", file=sys.stderr)
        return False

    return True


def validate_python(file_path):
    """Run py_compile to check Python syntax.

    Compiles to a throwaway temp cfile (deleted afterwards) so the syntax
    check never pollutes the project with .pyc bytecode. Note: os.devnull
    cannot be used as cfile on Windows — py_compile rejects non-regular files.
    """
    import tempfile
    fd, tmp_cfile = tempfile.mkstemp(suffix=".pyc")
    os.close(fd)
    try:
        py_compile.compile(file_path, cfile=tmp_cfile, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"Python syntax error in {os.path.basename(file_path)}:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return False
    finally:
        try:
            os.remove(tmp_cfile)
        except OSError:
            pass


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = input_data.get("tool_input")
    if tool_input is None:
        print("validate-edit: unexpected hook schema — 'tool_input' key missing", file=sys.stderr)
        sys.exit(0)  # non-blocking: still pass to avoid false failures on schema changes
    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    if file_path.endswith(".tmdl"):
        if not validate_tmdl(file_path):
            sys.exit(2)
        if not check_tmdl_indentation(file_path):
            sys.exit(1)  # non-blocking warning
    elif file_path.endswith(".py"):
        if not validate_python(file_path):
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
