#!/usr/bin/env python3
"""Post-edit validation hook for TMDL and Python files.

Reads hook input from stdin (JSON), checks the edited file:
- .tmdl files: scans for stray control characters (not \\n, \\r, \\t)
- .py files: runs py_compile to check syntax

Exit codes:
    0 — validation passed (or file type not checked)
    2 — blocking error: validation failed, Claude should fix before continuing
"""
import json
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


def validate_python(file_path):
    """Run py_compile to check Python syntax."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"Python syntax error in {os.path.basename(file_path)}:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return False


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = input_data.get("tool_input", {}).get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    if file_path.endswith(".tmdl"):
        if not validate_tmdl(file_path):
            sys.exit(2)
    elif file_path.endswith(".py"):
        if not validate_python(file_path):
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
