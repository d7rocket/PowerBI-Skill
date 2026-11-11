#!/usr/bin/env python3
"""Project detection, model index, session log and undo journal for the pbi plugin.

UTF-8 safe. Every /pbi command calls `preflight` once; nothing here needs an LLM.

Usage:
    python detect.py preflight            Project state + model index + history + core rules
    python detect.py model                Model index only (tables, measures, relationships)
    python detect.py measure <name> [table]   Print a measure's definition and location
    python detect.py search <text> [model_dir]  Files containing <text> (fixed string)
    python detect.py log <command> <target> <outcome>   Record a command in .pbi/context.md
    python detect.py note <section> <text | --file path>  Set a named section in .pbi/context.md
    python detect.py record <json_file>   Commit a confirmed model change (file tier) and journal it
    python detect.py journal-last         Print the most recent change that is not undone
    python detect.py journal-undone       Mark the most recent change as undone
    python detect.py snapshot             Commit Desktop-saved files for uncommitted live changes
    python detect.py env                  Node, Claude CLI, Power BI Desktop and MCP status
    python detect.py version              Plugin version from .claude-plugin/plugin.json
    python detect.py gitignore-check      Ensure .gitignore contains the noise-file entries
    python detect.py html-parse <file>    Strip a DAX Formatter HTML response to DAX text
    python detect.py rules                Print shared/core.md
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# Force UTF-8 output (Windows defaults to cp1252 which breaks French accents)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PBI_DIR = '.pbi'
CONTEXT_FILE = os.path.join(PBI_DIR, 'context.md')
JOURNAL_FILE = os.path.join(PBI_DIR, 'journal.jsonl')
LOCK_FILE = os.path.join(PBI_DIR, '.lock')
HISTORY_MAX = 20
MEASURE_LIST_MAX = 300
MCP_PACKAGE = 'powerbi-modeling-mcp'

CONTEXT_TEMPLATE = (
    '# PBI Context\n\n'
    '## Last Command\n'
    '- Command: (none)\n- Timestamp: (none)\n- Measure: (none)\n- Outcome: (none)\n\n'
    '## Command History\n'
    '| Timestamp | Command | Measure Name | Outcome |\n'
    '|-----------|---------|--------------|---------|\n\n'
    '## Analyst-Reported Failures\n'
    '| Timestamp | Command | Measure Name | What Failed | Notes |\n'
    '|-----------|---------|--------------|-------------|-------|\n'
)

LEGACY_FILES = [
    ('.pbi-context.md', CONTEXT_FILE),
    ('project-docs.md', os.path.join(PBI_DIR, 'project-docs.md')),
    ('audit-report.md', os.path.join(PBI_DIR, 'audit-report.md')),
    ('project-extract.md', os.path.join(PBI_DIR, 'project-extract.md')),
]


# ── Small helpers ───────────────────────────────────────────────────

def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def read_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_atomic(path, text):
    """Write via a temp file in the same directory, then rename (watcher-safe)."""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    os.replace(tmp, path)


class Lock:
    """Cross-process lock so two commands cannot interleave context writes."""

    def __enter__(self):
        os.makedirs(PBI_DIR, exist_ok=True)
        deadline = time.time() + 3
        while True:
            try:
                fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(LOCK_FILE) > 10:
                        os.remove(LOCK_FILE)  # stale lock from a crashed run
                        continue
                except OSError:
                    pass
                if time.time() > deadline:
                    return self  # never block the analyst on a lock
                time.sleep(0.05)

    def __exit__(self, *exc):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass


def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=timeout)
        return r.returncode, (r.stdout or '').strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ''


# ── Project detection ───────────────────────────────────────────────

def find_model():
    """Return (model_dir, format, warning). format is tmdl, tmsl or unknown."""
    dirs = sorted(glob.glob('*.SemanticModel')) + glob.glob('.SemanticModel')
    if not dirs:
        return None, None, None
    sm = dirs[0]
    warn = None
    if len(dirs) > 1:
        warn = 'multiple SemanticModel folders found, using ' + sm
    if os.path.isfile(os.path.join(sm, 'model.bim')):
        return sm, 'tmsl', warn
    if os.path.isdir(os.path.join(sm, 'definition', 'tables')):
        return sm, 'tmdl', warn
    return sm, 'unknown', warn


def find_report():
    dirs = sorted(glob.glob('*.Report')) + glob.glob('.Report')
    return dirs[0] if dirs else None


def find_nearby():
    for d in ['..', os.path.join('..', '..'), os.path.join('..', '..', '..')]:
        if glob.glob(os.path.join(d, '*.SemanticModel')) or glob.glob(os.path.join(d, '.SemanticModel')):
            return os.path.abspath(d)
    return ''


def git_state():
    code, _ = run(['git', 'rev-parse', '--is-inside-work-tree'])
    if code != 0:
        return 'no', 'no'
    code, _ = run(['git', 'rev-parse', 'HEAD'])
    return 'yes', ('yes' if code == 0 else 'no')


def migrate_legacy():
    moved = []
    for src, dst in LEGACY_FILES:
        if os.path.isfile(src):
            if os.path.isfile(dst):
                print('MIGRATE_SKIPPED %s (destination exists)' % src)
            else:
                os.makedirs(PBI_DIR, exist_ok=True)
                os.rename(src, dst)
                moved.append(src)
                print('MIGRATED: %s -> %s' % (src, dst))
    return moved


# ── TMDL / TMSL model index ─────────────────────────────────────────

OBJECT_RE = re.compile(r'^(\t| {1,4})(measure|column|hierarchy|partition|calculationGroup|calculationItem)\b\s*(.*)$')


def split_name(rest):
    """Split "'Quoted ''Name''' = expr" or "Plain = expr" into (name, remainder)."""
    rest = rest.strip()
    if rest.startswith("'"):
        i = 1
        out = []
        while i < len(rest):
            if rest[i] == "'":
                if i + 1 < len(rest) and rest[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                return ''.join(out), rest[i + 1:].strip()
            out.append(rest[i])
            i += 1
        return ''.join(out), ''
    m = re.match(r'^([^\s=]+)\s*(.*)$', rest)
    if not m:
        return rest, ''
    return m.group(1), m.group(2)


def prop_value(line):
    val = line.split(':', 1)[1].strip()
    if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        val = val[1:-1]
    return val


def parse_tmdl_table(path):
    try:
        lines = read_text(path).splitlines()
    except (OSError, UnicodeDecodeError) as e:
        print('Warning: %s skipped (%s)' % (path, type(e).__name__), file=sys.stderr)
        return None
    table = {'name': os.path.splitext(os.path.basename(path))[0], 'file': path,
             'measures': [], 'columns': [], 'hidden': False}
    starts = []  # (line_index, kind, obj)
    for i, line in enumerate(lines):
        if line.startswith('table '):
            table['name'] = split_name(line[len('table '):])[0]
            continue
        m = OBJECT_RE.match(line)
        if not m:
            continue
        kind = m.group(2)
        name, remainder = split_name(m.group(3))
        obj = {'name': name, 'line': i + 1}
        if kind == 'measure':
            first = i
            while first > 0 and lines[first - 1].strip().startswith('///'):
                first -= 1
            obj.update({'start': first + 1, 'described': first != i, 'folder': '', 'format': ''})
            table['measures'].append(obj)
        elif kind == 'column':
            obj.update({'dataType': '', 'hidden': False, 'calculated': remainder.startswith('=')})
            table['columns'].append(obj)
        starts.append((i, kind, obj))
    for idx, (i, kind, obj) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        if idx + 1 < len(starts) and starts[idx + 1][1] == 'measure':
            end = starts[idx + 1][2]['start'] - 1  # leave the next measure's /// lines to it
        while end > i + 1 and not lines[end - 1].strip():
            end -= 1
        obj['end'] = end
        for line in lines[i + 1:end]:
            s = line.strip()
            if s.startswith('formatString:') and kind == 'measure':
                obj['format'] = prop_value(s)
            elif s.startswith('displayFolder:') and kind == 'measure':
                obj['folder'] = prop_value(s)
            elif s.startswith('dataType:') and kind == 'column':
                obj['dataType'] = prop_value(s)
            elif s == 'isHidden' and kind == 'column':
                obj['hidden'] = True
    first_obj = starts[0][0] if starts else len(lines)
    table['hidden'] = any(l.strip() == 'isHidden' for l in lines[:first_obj])
    return table


def parse_tmdl_relationships(sm):
    path = os.path.join(sm, 'definition', 'relationships.tmdl')
    rels = []
    if not os.path.isfile(path):
        return rels
    cur = None
    for line in read_text(path).splitlines():
        if line.startswith('relationship '):
            cur = {'name': split_name(line[len('relationship '):])[0], 'from': '', 'to': '',
                   'cross': 'single', 'active': True, 'fromCard': 'many', 'toCard': 'one'}
            rels.append(cur)
            continue
        if cur is None or ':' not in line:
            continue
        key, val = [p.strip() for p in line.split(':', 1)]
        if key in ('fromColumn', 'toColumn'):
            # Table.Column, 'My Table'.'My Column', or a bare column (older layout)
            if val.startswith("'"):
                tbl, rest = split_name(val)
                rest = rest.lstrip('.')
            elif '.' in val:
                tbl, rest = val.split('.', 1)
            else:
                tbl, rest = val, ''
            col = split_name(rest)[0] if rest else ''
            cur['from' if key == 'fromColumn' else 'to'] = '%s[%s]' % (tbl, col)
        elif key == 'crossFilteringBehavior':
            cur['cross'] = 'both' if val == 'bothDirections' else 'single'
        elif key == 'isActive':
            cur['active'] = val.lower() != 'false'
        elif key == 'fromCardinality':
            cur['fromCard'] = val
        elif key == 'toCardinality':
            cur['toCard'] = val
        elif key in ('fromTable', 'toTable'):
            side = 'from' if key == 'fromTable' else 'to'
            cur['_' + side + 'Table'] = split_name(val)[0]
    for r in rels:  # older layout: fromTable/fromColumn on separate lines
        for side in ('from', 'to'):
            tbl = r.pop('_' + side + 'Table', None)
            if tbl and r[side].endswith('[]'):
                r[side] = '%s[%s]' % (tbl, r[side][:-2])
    return rels


def load_tmdl(sm):
    tbl_dir = os.path.join(sm, 'definition', 'tables')
    tables = []
    for f in sorted(glob.glob(os.path.join(tbl_dir, '**', '*.tmdl'), recursive=True)):
        t = parse_tmdl_table(f)
        if t:
            tables.append(t)
    return tables, parse_tmdl_relationships(sm)


def load_tmsl(sm):
    path = os.path.join(sm, 'model.bim')
    try:
        data = json.loads(read_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        print('Warning: model.bim could not be parsed (%s)' % type(e).__name__, file=sys.stderr)
        return [], []
    model = data.get('model', data)
    tables = []
    for t in model.get('tables', []):
        tables.append({
            'name': t.get('name', ''), 'file': path, 'hidden': bool(t.get('isHidden')),
            'measures': [{'name': m.get('name', ''), 'folder': m.get('displayFolder', ''),
                          'format': m.get('formatString', ''), 'described': bool(m.get('description'))}
                         for m in t.get('measures', [])],
            'columns': [{'name': c.get('name', ''), 'dataType': c.get('dataType', ''),
                         'hidden': bool(c.get('isHidden')), 'calculated': c.get('type') == 'calculated'}
                        for c in t.get('columns', [])],
        })
    rels = []
    for r in model.get('relationships', []):
        rels.append({
            'name': r.get('name', ''),
            'from': '%s[%s]' % (r.get('fromTable', ''), r.get('fromColumn', '')),
            'to': '%s[%s]' % (r.get('toTable', ''), r.get('toColumn', '')),
            'cross': 'both' if r.get('crossFilteringBehavior') == 'bothDirections' else 'single',
            'active': r.get('isActive', True) is not False,
            'fromCard': r.get('fromCardinality', 'many'), 'toCard': r.get('toCardinality', 'one'),
        })
    return tables, rels


def load_model(sm, fmt):
    if fmt == 'tmdl':
        return load_tmdl(sm)
    if fmt == 'tmsl':
        return load_tmsl(sm)
    return [], []


def print_model(sm, fmt):
    tables, rels = load_model(sm, fmt)
    n_measures = sum(len(t['measures']) for t in tables)
    print('## Model index (%d tables, %d measures, %d relationships) - read fresh from disk'
          % (len(tables), n_measures, len(rels)))
    if not tables:
        print('(no tables found)')
        return
    print('| Table | Columns | Measures | File |')
    print('|---|---|---|---|')
    for t in tables:
        name = t['name'] + (' (hidden)' if t['hidden'] else '')
        print('| %s | %d | %d | %s |' % (name, len(t['columns']), len(t['measures']),
                                        t['file'].replace('\\', '/')))
    if n_measures:
        print('')
        print('### Measures')
        if n_measures <= MEASURE_LIST_MAX:
            for t in tables:
                if t['measures']:
                    print('- %s: %s' % (t['name'], ' | '.join(m['name'] for m in t['measures'])))
        else:
            print('(%d measures - too many to list. Use `detect.py measure "<name>"` or '
                  '`detect.py search "<text>"`.)' % n_measures)
    if rels:
        print('')
        print('### Relationships')
        for r in rels:
            flags = []
            if r['cross'] == 'both':
                flags.append('BIDIRECTIONAL')
            if not r['active']:
                flags.append('inactive')
            print('- %s -> %s (%s-to-%s%s)' % (r['from'], r['to'], r['fromCard'], r['toCard'],
                                              (', ' + ', '.join(flags)) if flags else ''))


def cmd_measure(name, table=None):
    sm, fmt, _ = find_model()
    if not sm:
        print('MEASURE_ERROR=no PBIP project in this folder')
        return 1
    wanted = name.strip().strip('[]').strip("'")
    found = 0
    if fmt == 'tmdl':
        tables, _ = load_tmdl(sm)
        for t in tables:
            if table and t['name'].lower() != table.lower():
                continue
            for m in t['measures']:
                if m['name'].lower() == wanted.lower():
                    found += 1
                    lines = read_text(t['file']).splitlines()
                    print('MEASURE=%s TABLE=%s FILE=%s LINES=%d-%d' % (
                        m['name'], t['name'], t['file'].replace('\\', '/'), m['start'], m['end']))
                    print('\n'.join(lines[m['start'] - 1:m['end']]))
                    print('---')
    elif fmt == 'tmsl':
        try:
            data = json.loads(read_text(os.path.join(sm, 'model.bim')))
        except (OSError, json.JSONDecodeError):
            data = {}
        for t in data.get('model', data).get('tables', []):
            if table and t.get('name', '').lower() != table.lower():
                continue
            for m in t.get('measures', []):
                if m.get('name', '').lower() == wanted.lower():
                    found += 1
                    print('MEASURE=%s TABLE=%s FILE=%s' % (
                        m.get('name'), t.get('name'), os.path.join(sm, 'model.bim').replace('\\', '/')))
                    print(json.dumps(m, indent=2, ensure_ascii=False))
                    print('---')
    print('MEASURE_MATCHES=%d' % found)
    return 0


def cmd_search(text, model_dir=None):
    """Fixed-string search in model files. UTF-8 safe, no regex surprises."""
    if not model_dir:
        model_dir = find_model()[0]
    if not model_dir:
        return
    files = glob.glob(os.path.join(model_dir, 'definition', '**', '*.tmdl'), recursive=True)
    bim = os.path.join(model_dir, 'model.bim')
    if os.path.isfile(bim):
        files.append(bim)
    for f in sorted(files):
        try:
            if text in read_text(f):
                print(f)
        except (UnicodeDecodeError, OSError) as e:
            print('Warning: %s skipped (%s)' % (f, type(e).__name__), file=sys.stderr)


# ── Session context (.pbi/context.md) ───────────────────────────────

def split_sections(text):
    """Return (preamble, [(heading, body), ...]) keeping order."""
    parts = re.split(r'(?m)^(## .*)$', text)
    pre = parts[0]
    sections = []
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1] if i + 1 < len(parts) else ''))
    return pre, sections


def join_sections(pre, sections):
    out = [pre.rstrip('\n') + '\n'] if pre.strip() else []
    for heading, body in sections:
        out.append('\n' + heading + '\n' + body.strip('\n') + '\n')
    return ''.join(out)


def load_context():
    try:
        text = read_text(CONTEXT_FILE)
    except (FileNotFoundError, UnicodeDecodeError):
        text = ''
    if '## Command History' not in text:
        text = CONTEXT_TEMPLATE + ('\n' + text if text.strip() and '# PBI Context' not in text else '')
    pre, sections = split_sections(text)
    # v7 cached an LLM-built model snapshot here; v8 indexes the model from disk instead
    sections = [(h, b) for h, b in sections
                if not (h == '## Model Context' and '**Session-Start:**' in b)]
    return pre, sections


def cell(text):
    return str(text).replace('|', '/').replace('\r', ' ').replace('\n', ' ').strip()


def cmd_log(command, target, outcome):
    if not find_model()[0] and not os.path.isdir(PBI_DIR):
        print('LOG_SKIPPED=no project')
        return
    ts = now_iso()
    with Lock():
        pre, sections = load_context()
        out = []
        for heading, body in sections:
            if heading == '## Last Command':
                body = ('- Command: %s\n- Timestamp: %s\n- Measure: %s\n- Outcome: %s\n'
                        % (cell(command), ts, cell(target), cell(outcome)))
            elif heading == '## Command History':
                rows = [l for l in body.splitlines() if l.strip().startswith('|')]
                head, data = rows[:2], rows[2:]
                if len(head) < 2:
                    head = ['| Timestamp | Command | Measure Name | Outcome |',
                            '|-----------|---------|--------------|---------|']
                data.append('| %s | %s | %s | %s |' % (ts, cell(command), cell(target), cell(outcome)))
                body = '\n'.join(head + data[-HISTORY_MAX:]) + '\n'
            out.append((heading, body))
        write_atomic(CONTEXT_FILE, join_sections(pre, out))
    print('LOGGED')


def cmd_note(section, text):
    heading = '## ' + section.strip().lstrip('#').strip()
    if heading in ('## Last Command', '## Command History', '## Analyst-Reported Failures'):
        print('NOTE_ERROR=%s is managed; not changed' % heading)
        return 1
    with Lock():
        pre, sections = load_context()
        body = text.strip('\n') + '\n'
        for i, (h, _) in enumerate(sections):
            if h == heading:
                sections[i] = (h, body)
                break
        else:
            sections.append((heading, body))
        write_atomic(CONTEXT_FILE, join_sections(pre, sections))
    print('NOTED ' + heading)
    return 0


def print_context():
    if not os.path.isfile(CONTEXT_FILE):
        return
    _, sections = load_context()
    for heading, body in sections:
        rows = [l for l in body.splitlines() if l.strip().startswith('|')]
        if heading == '## Last Command':
            continue
        if heading == '## Command History':
            data = rows[2:]
            if data:
                print('')
                print('## Recent commands (last %d of %d)' % (min(5, len(data)), len(data)))
                print('\n'.join(rows[:2] + data[-5:]))
            continue
        if heading == '## Analyst-Reported Failures':
            if len(rows) > 2:
                print('')
                print(heading)
                print('\n'.join(rows))
            continue
        if body.strip():
            print('')
            print(heading)
            print(body.strip('\n'))


# ── Undo journal (.pbi/journal.jsonl) ───────────────────────────────

def read_journal():
    entries = []
    try:
        for line in read_text(JOURNAL_FILE).splitlines():
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        pass
    return entries


def last_open_entry(entries):
    undone = {e.get('undoes') for e in entries if e.get('undoes')}
    for e in reversed(entries):
        if e.get('id') and not e.get('undoes') and e['id'] not in undone:
            return e
    return None


def append_journal(entry):
    with Lock():
        existing = ''
        if os.path.isfile(JOURNAL_FILE):
            existing = read_text(JOURNAL_FILE)
            if existing and not existing.endswith('\n'):
                existing += '\n'
        write_atomic(JOURNAL_FILE, existing + json.dumps(entry, ensure_ascii=False) + '\n')


def commit_model(message):
    """Commit the model folder only. Returns (status, short_sha)."""
    sm = find_model()[0]
    if not sm or git_state()[0] != 'yes':
        return 'no-repo', ''
    run(['git', 'add', '--', sm])
    code, _ = run(['git', 'diff', '--cached', '--quiet', '--', sm])
    if code == 0:
        return 'nothing-to-commit', ''
    code, _ = run(['git', 'commit', '-m', message, '--', sm], timeout=30)
    if code != 0:
        return 'commit-failed', ''
    _, sha = run(['git', 'rev-parse', '--short', 'HEAD'])
    return 'ok', sha


def cmd_record(json_file):
    """Record a confirmed model change: commit it (file tier) and journal it.

    One step on purpose. The commit hash in the journal is what /pbi:undo
    reverts, so the script that creates the commit is the one that records it.
    """
    try:
        entry = json.loads(read_text(json_file))
    except (OSError, json.JSONDecodeError) as e:
        print('RECORD_ERROR=%s' % type(e).__name__)
        return 1
    if not isinstance(entry, dict) or entry.get('tier') not in ('file', 'live'):
        print('RECORD_ERROR=expected a JSON object with "tier": "file" or "live"')
        return 1
    entry['id'] = '%d' % int(time.time() * 1000)
    entry['ts'] = now_iso()
    entry['commit'] = ''
    status = 'live'
    if entry['tier'] == 'file':
        status, entry['commit'] = commit_model(entry.get('message') or 'chore: update model')
    append_journal(entry)
    try:
        os.remove(json_file)
    except OSError:
        pass
    print('RECORDED id=%s commit=%s%s' % (entry['id'], status,
                                         (' ' + entry['commit']) if entry['commit'] else ''))
    return 0


def cmd_journal_last():
    entries = read_journal()
    entry = last_open_entry(entries)
    if not entry:
        print('JOURNAL=empty')
        return
    if entry.get('tier') == 'live':
        # a live change is committed only once a snapshot captured the Desktop save
        entry['commit'] = ''
        for e in entries:
            if entry['id'] in (e.get('snapshot') or []):
                entry['commit'] = e.get('commit', '')
    entry['committed'] = bool(entry.get('commit'))
    print(json.dumps(entry, indent=2, ensure_ascii=False))


def cmd_journal_undone():
    entry = last_open_entry(read_journal())
    if not entry:
        print('JOURNAL=empty')
        return
    append_journal({'id': '%d' % int(time.time() * 1000), 'ts': now_iso(), 'undoes': entry['id']})
    print('UNDONE id=' + entry['id'])


def pending_live(entries):
    """Live changes that no snapshot commit has captured yet (and were not undone)."""
    snapped = set()
    for e in entries:
        snapped.update(e.get('snapshot') or [])
    undone = {e.get('undoes') for e in entries if e.get('undoes')}
    return [e for e in entries
            if e.get('tier') == 'live' and e.get('id')
            and e['id'] not in snapped and e['id'] not in undone]


def cmd_snapshot():
    """Commit Desktop-saved files for live changes that are still uncommitted.

    A live change lands in Desktop's memory first; the TMDL files only change when
    the analyst saves in Desktop. This turns that save into a local commit carrying
    the original business message, so history and undo stay accurate.
    """
    sm = find_model()[0]
    pending = pending_live(read_journal())
    if not sm or not pending:
        print('SNAPSHOT=none')
        return
    if git_state()[0] != 'yes':
        print('SNAPSHOT=no-repo')
        return
    code, status = run(['git', 'status', '--porcelain', '--', sm])
    if code != 0 or not status.strip():
        print('SNAPSHOT=waiting (%d live change(s) not saved in Desktop yet)' % len(pending))
        return
    if len(pending) == 1:
        message = pending[0].get('message') or 'chore: apply live model change'
    else:
        message = 'chore: apply %d live model changes' % len(pending)
    status, sha = commit_model(message)
    if status != 'ok':
        print('SNAPSHOT=' + status)
        return
    append_journal({'ts': now_iso(), 'snapshot': [e['id'] for e in pending], 'commit': sha})
    print('SNAPSHOT_COMMITTED=%s %s' % (sha, message))


# ── Environment (Node, Claude CLI, Desktop, MCP) ────────────────────

def desktop_state():
    """Return running, not-running or unknown (non-Windows)."""
    if os.name != 'nt':
        return 'unknown'
    code, out = run(['tasklist', '/FI', 'IMAGENAME eq PBIDesktop.exe', '/FO', 'CSV', '/NH'])
    if code != 0:
        return 'unknown'
    return 'running' if 'PBIDesktop.exe' in out else 'not-running'


def mcp_registered():
    """Config-file hint only. The real test is whether the MCP tools exist in the session."""
    candidates = [os.path.join(os.path.expanduser('~'), '.claude.json'), '.mcp.json']
    for path in candidates:
        try:
            if MCP_PACKAGE in read_text(path):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def tool_version(name):
    exe = name + ('.cmd' if os.name == 'nt' and name in ('npx', 'npm') else '')
    code, out = run([exe, '--version'], timeout=15)
    if code != 0 and os.name == 'nt':
        code, out = run(['cmd', '/c', name, '--version'], timeout=15)
    return out.splitlines()[0] if code == 0 and out else ''


def cmd_env():
    print('PLATFORM=' + ('windows' if os.name == 'nt' else sys.platform))
    print('PYTHON=' + sys.version.split()[0])
    for name in ('node', 'npx', 'claude'):
        v = tool_version(name)
        print('%s=%s' % (name.upper(), v if v else 'missing'))
    print('DESKTOP=' + desktop_state())
    print('LIVE_MCP_CONFIG=' + ('registered' if mcp_registered() else 'not-registered'))


# ── Misc subcommands ────────────────────────────────────────────────

def plugin_version():
    try:
        data = json.loads(read_text(os.path.join(PLUGIN_ROOT, '.claude-plugin', 'plugin.json')))
        return str(data.get('version', 'unknown'))
    except (OSError, json.JSONDecodeError):
        return 'unknown'


def cmd_rules():
    try:
        # Skill placeholders are not expanded in command output, so expand the root here
        text = read_text(os.path.join(PLUGIN_ROOT, 'shared', 'core.md'))
        print(text.replace('${CLAUDE_PLUGIN_ROOT}', PLUGIN_ROOT.replace('\\', '/')))
    except OSError:
        print('CORE_RULES=missing (%s)' % os.path.join(PLUGIN_ROOT, 'shared', 'core.md'))


def gitignore_check():
    """Ensure noise-file entries exist in .gitignore. Prints GITIGNORE_OK."""
    required = ['*.abf', 'localSettings.json', '.pbi/context.md', '.pbi/journal.jsonl',
                '.pbi/.lock', 'SecurityBindings']
    existing_lines = []
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    except FileNotFoundError:
        pass
    present = [line.strip() for line in existing_lines]
    to_add = [e for e in required if e not in present]
    if to_add:
        with open('.gitignore', 'a', encoding='utf-8') as f:
            if existing_lines and not existing_lines[-1].endswith('\n'):
                f.write('\n')
            for entry in to_add:
                f.write(entry + '\n')
    print('GITIGNORE_OK')


def html_parse(tmpfile):
    """Strip a DAX Formatter HTML response to clean DAX text (silent when unusable)."""
    import html as html_lib
    try:
        raw = read_text(tmpfile)
    except (OSError, UnicodeDecodeError):
        return
    m = re.search(r'<div class="formatted"[^>]*>(.*)</div>', raw, re.DOTALL)
    if not m:
        return
    text = m.group(1)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ')
    text = html_lib.unescape(text).replace('\xa0', ' ')
    for line in text.split('\n'):
        print(line.rstrip())


def cmd_preflight():
    print('PBI_VERSION=' + plugin_version())
    sm, fmt, warn = find_model()
    if sm:
        migrate_legacy()
        os.makedirs(PBI_DIR, exist_ok=True)
        if warn:
            print('PBIP_WARN=' + warn)
        print('PBIP_MODE=file PBIP_FORMAT=%s PBIP_DIR=%s' % (fmt, sm))
        rpt = find_report()
        print('PBIR=yes PBIR_DIR=' + rpt if rpt else 'PBIR=no')
        git, commits = git_state()
        print('GIT=%s HAS_COMMITS=%s' % (git, commits))
        print('UNAPPLIED_CHANGES=' + ('yes' if os.path.isfile(os.path.join(sm, 'unappliedChanges.json')) else 'no'))
        print('DESKTOP=' + desktop_state())
        print('LIVE_MCP_CONFIG=' + ('registered' if mcp_registered() else 'not-registered'))
        pending = pending_live(read_journal())
        if pending:
            print('PENDING_LIVE_CHANGES=%d' % len(pending))
        print('')
        print_model(sm, fmt)
        print_context()
    else:
        print('PBIP_MODE=paste')
        nearby = find_nearby()
        if nearby:
            print('NEARBY_PBIP=' + nearby)
        print('DESKTOP=' + desktop_state())
        print('LIVE_MCP_CONFIG=' + ('registered' if mcp_registered() else 'not-registered'))
        print_context()
    print('')
    print('---')
    cmd_rules()


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1
    cmd, args = argv[1], argv[2:]
    if cmd == 'preflight':
        cmd_preflight()
    elif cmd == 'model':
        sm, fmt, _ = find_model()
        if sm:
            print_model(sm, fmt)
        else:
            print('PBIP_MODE=paste')
    elif cmd == 'measure' and args:
        return cmd_measure(args[0], args[1] if len(args) > 1 else None)
    elif cmd == 'search' and args:
        cmd_search(args[0], args[1] if len(args) > 1 else None)
    elif cmd == 'log' and len(args) >= 3:
        cmd_log(args[0], args[1], args[2])
    elif cmd == 'note' and len(args) >= 2:
        if args[1] == '--file' and len(args) >= 3:
            try:
                text = read_text(args[2])
            except OSError as e:
                print('NOTE_ERROR=%s' % type(e).__name__)
                return 1
        else:
            text = args[1]
        return cmd_note(args[0], text)
    elif cmd == 'record' and args:
        return cmd_record(args[0])
    elif cmd == 'journal-last':
        cmd_journal_last()
    elif cmd == 'journal-undone':
        cmd_journal_undone()
    elif cmd == 'snapshot':
        cmd_snapshot()
    elif cmd == 'env':
        cmd_env()
    elif cmd == 'version':
        print('LOCAL=' + plugin_version())
    elif cmd == 'gitignore-check':
        gitignore_check()
    elif cmd == 'html-parse' and args:
        html_parse(args[0])
    elif cmd == 'rules':
        cmd_rules()
    else:
        print('Unknown or incomplete command: ' + cmd, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
