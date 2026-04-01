#!/usr/bin/env python3
"""Generate Big-4 consulting-style PDF from .pbi/doc_data.json.

Usage: python gen_pdf.py <doc_data.json> <output.pdf>
Requires: pip install reportlab
"""
import sys
import json
from datetime import datetime

C_NAVY  = '#1B3A6B'
C_GOLD  = '#C9A84C'
C_GREY  = '#F2F2F2'
C_DGREY = '#404040'
C_WHITE = '#FFFFFF'
C_LGREY = '#D9D9D9'
C_GREEN = '#1E6A3A'
C_MGREY = '#808080'


def check_import():
    try:
        import reportlab  # noqa
        return True
    except ImportError:
        print('MISSING_DEP reportlab  —  run: pip install reportlab', file=sys.stderr)
        sys.exit(2)


def make_styles():
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        'h1': S('H1', fontName='Helvetica-Bold', fontSize=17, textColor=HexColor(C_NAVY),
                spaceBefore=20, spaceAfter=4, leading=22),
        'h2': S('H2', fontName='Helvetica-Bold', fontSize=13, textColor=HexColor(C_NAVY),
                spaceBefore=14, spaceAfter=4, leading=17),
        'h3': S('H3', fontName='Helvetica-Bold', fontSize=11, textColor=HexColor(C_NAVY),
                spaceBefore=10, spaceAfter=3),
        'body': S('Body', fontName='Helvetica', fontSize=10, textColor=HexColor(C_DGREY),
                  spaceBefore=4, spaceAfter=8, leading=14),
        'caption': S('Caption', fontName='Helvetica', fontSize=8,
                     textColor=HexColor(C_MGREY), spaceBefore=2, spaceAfter=2),
        'code': S('Code', fontName='Courier', fontSize=8.5,
                  textColor=HexColor(C_GREEN), spaceBefore=2, spaceAfter=4, leading=11,
                  leftIndent=14, backColor=HexColor('#F8F8F8')),
        'cover_title': S('CT', fontName='Helvetica-Bold', fontSize=36,
                         textColor=HexColor(C_NAVY), alignment=TA_CENTER,
                         spaceBefore=0, spaceAfter=6),
        'cover_sub': S('CS', fontName='Helvetica', fontSize=14,
                       textColor=HexColor(C_GOLD), alignment=TA_CENTER,
                       spaceBefore=0, spaceAfter=4),
        'cover_sub2': S('CS2', fontName='Helvetica-Bold', fontSize=14,
                        textColor=HexColor(C_NAVY), alignment=TA_CENTER, spaceAfter=0),
        'cover_body': S('CB', fontName='Helvetica', fontSize=10,
                        textColor=HexColor('#606060'), alignment=TA_CENTER,
                        spaceBefore=4, spaceAfter=2),
        'cover_conf': S('CC', fontName='Helvetica-Bold', fontSize=9,
                        textColor=HexColor('#909090'), alignment=TA_CENTER),
        'toc': S('TOC', fontName='Helvetica', fontSize=10, textColor=HexColor(C_DGREY),
                 spaceBefore=3, spaceAfter=3, leftIndent=20),
        'sm_heading': S('SH', fontName='Helvetica-Bold', fontSize=10,
                        textColor=HexColor(C_NAVY), spaceBefore=8, spaceAfter=3),
        'health_ok': S('HOK', fontName='Helvetica', fontSize=10,
                       textColor=HexColor(C_GREEN), spaceBefore=8),
    }


def make_table(headers, rows, col_widths=None):
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import cm

    data = [headers] + rows
    col_w = [cm(w) for w in col_widths] if col_widths else None
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1,  0),  HexColor(C_NAVY)),
        ('TEXTCOLOR',    (0, 0), (-1,  0),  HexColor(C_WHITE)),
        ('FONTNAME',     (0, 0), (-1,  0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1,  0),  9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor(C_GREY), HexColor(C_WHITE)]),
        ('FONTNAME',     (0, 1), (-1, -1),  'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1),  9),
        ('TEXTCOLOR',    (0, 1), (-1, -1),  HexColor(C_DGREY)),
        ('GRID',         (0, 0), (-1, -1),  0.5, HexColor(C_LGREY)),
        ('TOPPADDING',   (0, 0), (-1, -1),  4),
        ('BOTTOMPADDING',(0, 0), (-1, -1),  4),
        ('LEFTPADDING',  (0, 0), (-1, -1),  6),
        ('RIGHTPADDING', (0, 0), (-1, -1),  6),
        ('VALIGN',       (0, 0), (-1, -1),  'TOP'),
        ('WORDWRAP',     (0, 0), (-1, -1),  1),
    ]))
    return t


def build_header_footer(project, date_str):
    """Return a function suitable for onLaterPages."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import cm

    W, H = A4

    def draw(canvas, doc):
        canvas.saveState()
        # Header rule
        canvas.setFillColor(HexColor(C_NAVY))
        canvas.rect(cm(2.54), H - cm(1.5), W - cm(5.08), 0.04 * cm, fill=1, stroke=0)
        # Header text
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor(C_MGREY))
        canvas.drawString(cm(2.54), H - cm(1.3), project)
        canvas.setFillColor(HexColor(C_GOLD))
        canvas.drawRightString(W - cm(2.54), H - cm(1.3), 'Power BI Documentation')
        # Footer rule
        canvas.setFillColor(HexColor(C_NAVY))
        canvas.rect(cm(2.54), cm(1.5), W - cm(5.08), 0.04 * cm, fill=1, stroke=0)
        # Footer text
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor(C_MGREY))
        canvas.drawString(cm(2.54), cm(1.1), 'Confidential')
        canvas.drawCentredString(W / 2, cm(1.1), date_str)
        canvas.drawRightString(W - cm(2.54), cm(1.1), f'Page {doc.page}')
        canvas.restoreState()

    return draw


def main():
    if len(sys.argv) < 3:
        print('Usage: gen_pdf.py <doc_data.json> <output.pdf>', file=sys.stderr)
        sys.exit(1)
    check_import()

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        PageBreak, HRFlowable, KeepTogether
    )

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)

    meta    = data.get('meta', {})
    summary = data.get('summary', {})
    tables  = data.get('tables', [])
    project = meta.get('project_name', 'Power BI Model')

    try:
        dt = datetime.fromisoformat(meta.get('generated_at', '').replace('Z', '+00:00'))
        date_str = dt.strftime('%B %d, %Y')
    except Exception:
        date_str = meta.get('generated_at', '')[:10]

    ST = make_styles()
    on_later = build_header_footer(project, date_str)

    doc = SimpleDocTemplate(
        sys.argv[2],
        pagesize=A4,
        leftMargin=cm(2.54), rightMargin=cm(2.54),
        topMargin=cm(2.0),   bottomMargin=cm(2.0),
        title=f'{project} — Power BI Documentation',
        author='pbi:docs',
    )

    story = []

    def hr():
        story.append(HRFlowable(width='100%', thickness=1, color=HexColor(C_GOLD),
                                spaceBefore=2, spaceAfter=6))

    def h1(num, title):
        story.append(Paragraph(f'<b>{num}</b>  {title}', ST['h1']))
        hr()

    def h2(num, title):
        story.append(Paragraph(f'<b>{num}</b>  {title}', ST['h2']))

    def h3(title):
        story.append(Paragraph(f'<b>{title}</b>', ST['sm_heading']))

    def body_blocks(text):
        for chunk in (text or '').split('\n\n'):
            if chunk.strip():
                story.append(Paragraph(chunk.strip(), ST['body']))

    # ── COVER PAGE ──────────────────────────────────────────────────────────
    story.append(Spacer(1, cm(6)))
    story.append(Paragraph(project.upper(), ST['cover_title']))
    story.append(HRFlowable(width='80%', thickness=2,
                             color=HexColor(C_GOLD), spaceAfter=8))
    story.append(Paragraph('POWER BI SEMANTIC MODEL', ST['cover_sub']))
    story.append(Paragraph('TECHNICAL DOCUMENTATION', ST['cover_sub2']))
    story.append(Spacer(1, cm(8)))
    story.append(Paragraph(f'Prepared:  {date_str}', ST['cover_body']))
    story.append(Paragraph(
        f'Source:  {meta.get("pbip_dir","Semantic Model")} ({meta.get("format","").upper()})',
        ST['cover_body']))
    story.append(Paragraph('C O N F I D E N T I A L', ST['cover_conf']))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ───────────────────────────────────────────────────
    story.append(Paragraph('Table of Contents', ST['h1']))
    hr()
    toc_items = [
        ('1.', 'Executive Summary'),
        ('2.', 'Data Model Overview'),
        ('3.', 'Table Details'),
        ('4.', 'Measures & KPIs'),
        ('5.', 'Business Logic'),
        ('6.', 'Data Sources'),
    ]
    if data.get('report_pages'):
        toc_items.append(('7.', 'Report Pages'))
        toc_items.append(('8.', 'Model Health'))
    else:
        toc_items.append(('7.', 'Model Health'))
    for num, title in toc_items:
        story.append(Paragraph(f'<b>{num}</b>  {title}', ST['toc']))
    story.append(PageBreak())

    # ── 1. EXECUTIVE SUMMARY ────────────────────────────────────────────────
    h1('1.', 'Executive Summary')
    body_blocks(data.get('overview', ''))
    h3('At a Glance')
    story.append(make_table(
        ['Metric', 'Value'],
        [
            ['Tables',        f'{summary.get("table_count",0)}  ({summary.get("fact_count",0)} fact · {summary.get("dimension_count",0)} dimension · {summary.get("other_count",0)} other)'],
            ['Measures',      f'{summary.get("measure_count",0)}  ({summary.get("documented_measures",0)} documented)'],
            ['Columns',       f'{summary.get("column_count",0)}  ({summary.get("calc_columns",0)} calculated · {summary.get("hidden_columns",0)} hidden)'],
            ['Relationships', f'{summary.get("relationship_count",0)}  ({summary.get("bidi_count",0)} bidirectional)'],
            ['Report Pages',  str(summary.get('report_pages', 'N/A'))],
        ],
        col_widths=[5, 11.5]
    ))
    story.append(PageBreak())

    # ── 2. DATA MODEL OVERVIEW ───────────────────────────────────────────────
    h1('2.', 'Data Model Overview')
    h2('2.1', 'Entity Relationship Diagram')
    erd = data.get('erd', '')
    if erd:
        safe = erd.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(f'<font name="Courier" size="8.5">{safe}</font>',
                               ST['body']))

    h2('2.2', 'Tables')
    if tables:
        story.append(make_table(
            ['Table', 'Type', 'Cols', 'Measures', 'Description'],
            [[t.get('name',''), t.get('type','').title(),
              str(len(t.get('columns',[]))), str(len(t.get('measures',[]))),
              (t.get('description') or '')[:80]] for t in tables],
            col_widths=[3.5, 2.5, 1.5, 2.5, 6.5]
        ))
    story.append(PageBreak())

    # ── 3. TABLE DETAILS ─────────────────────────────────────────────────────
    h1('3.', 'Table Details')
    for ti, t in enumerate(tables):
        h2(f'3.{ti+1}', f'{t.get("name","?")}  ({t.get("type","other").title()})')
        body_blocks(t.get('description', ''))
        if t.get('columns'):
            h3('Columns')
            story.append(make_table(
                ['Column', 'Data Type', 'Key', 'Hidden', 'Notes'],
                [[c.get('name',''), c.get('data_type',''),
                  'PK' if c.get('is_key') else '',
                  'Yes' if c.get('is_hidden') else '',
                  c.get('notes') or ''] for c in t['columns']],
                col_widths=[4, 3, 1.5, 2, 6]
            ))
        if t.get('measures'):
            h3('Measures')
            story.append(make_table(
                ['Measure', 'Display Folder', 'Format', 'Description'],
                [[m.get('name',''), m.get('folder') or '', m.get('format') or '',
                  (m.get('description') or '')[:65]] for m in t['measures']],
                col_widths=[4.5, 3, 2.5, 6.5]
            ))
    story.append(PageBreak())

    # ── 4. MEASURES & KPIs ───────────────────────────────────────────────────
    h1('4.', 'Measures & KPIs')
    folders = {}
    for t in tables:
        for m in t.get('measures', []):
            key = m.get('folder') or t.get('name', 'Other')
            folders.setdefault(key, []).append(m)

    for fi, (folder, measures) in enumerate(sorted(folders.items())):
        h2(f'4.{fi+1}', folder)
        for m in measures:
            parts = [Paragraph(f'<b>{m.get("name","")}</b>', ST['h3'])]
            if m.get('description'):
                parts.append(Paragraph(m['description'], ST['body']))
            meta_parts = []
            if m.get('format'):
                meta_parts.append(f'Format: {m["format"]}')
            if meta_parts:
                parts.append(Paragraph('  ·  '.join(meta_parts), ST['caption']))
            if m.get('expression'):
                safe_expr = (m['expression']
                             .replace('&', '&amp;')
                             .replace('<', '&lt;')
                             .replace('>', '&gt;'))
                parts.append(Paragraph(safe_expr, ST['code']))
            story.append(KeepTogether(parts))
    story.append(PageBreak())

    # ── 5. BUSINESS LOGIC ────────────────────────────────────────────────────
    h1('5.', 'Business Logic')
    body_blocks(data.get('business_logic', ''))
    story.append(PageBreak())

    # ── 6. DATA SOURCES ──────────────────────────────────────────────────────
    h1('6.', 'Data Sources')
    sources = data.get('data_sources', [])
    if sources:
        story.append(make_table(
            ['Table', 'Source Type', 'Connection'],
            [[s.get('table',''), s.get('type',''), s.get('connection','')] for s in sources],
            col_widths=[4, 3.5, 9]
        ))
    else:
        story.append(Paragraph('Source expressions not available in this project format.',
                               ST['body']))

    # ── 7. REPORT PAGES (optional) ───────────────────────────────────────────
    report_pages = data.get('report_pages', [])
    if report_pages:
        story.append(PageBreak())
        h1('7.', 'Report Pages')
        story.append(make_table(
            ['Page', 'Visuals', 'Visual Types'],
            [[p.get('name',''), str(p.get('visual_count',0)),
              ', '.join(p.get('visual_types',[]))] for p in report_pages],
            col_widths=[5, 2.5, 9]
        ))

    # ── MODEL HEALTH ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    health_num = '8.' if report_pages else '7.'
    h1(health_num, 'Model Health')

    health = data.get('health', {})
    body_blocks(health.get('summary', ''))

    health_rows = []
    if health.get('bidi_relationships'):
        health_rows.append(['Bidirectional relationships',
                            ', '.join(health['bidi_relationships']),
                            'Review — may affect query performance'])
    if health.get('undocumented_count', 0) > 0:
        health_rows.append(['Undocumented measures', str(health['undocumented_count']),
                            'Run /pbi:comment-batch to add descriptions'])
    if health.get('missing_format_count', 0) > 0:
        health_rows.append(['Missing format strings', str(health['missing_format_count']),
                            'Add format strings for consistent display'])
    if health.get('unhidden_keys'):
        health_rows.append(['Unhidden key columns', ', '.join(health['unhidden_keys']),
                            'Consider hiding FK/surrogate key columns'])
    if health.get('isolated_tables'):
        health_rows.append(['Isolated tables', ', '.join(health['isolated_tables']),
                            'No relationships defined'])

    if health_rows:
        story.append(make_table(
            ['Issue', 'Detail', 'Recommendation'],
            health_rows,
            col_widths=[4, 4, 8.5]
        ))
    else:
        story.append(Paragraph(
            'No significant health concerns detected. Model follows best practices.',
            ST['health_ok']
        ))

    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=on_later)
    print(f'PDF_OK {sys.argv[2]}')


if __name__ == '__main__':
    main()
