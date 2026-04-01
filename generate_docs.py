"""
Generate /pbi Quick Start Guide PDF - Light theme design.
"""
import math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4  # 595.27 x 841.89 points

# ── Colour Palette ───────────────────────────────────────────────
# Main theme: #19414c   Sub theme: #28545f   Accent: #ffc31b
MAIN       = HexColor("#19414C")       # primary teal - headings, dark elements
MAIN_SUB   = HexColor("#28545F")       # secondary teal - sub-elements
MAIN_LIGHT = HexColor("#3A6B78")       # lighter teal - tertiary
MAIN_PALE  = HexColor("#E6F0F2")       # very pale teal - card backgrounds
MAIN_PALE2 = HexColor("#D0E2E6")       # slightly deeper pale teal - alt cards
ACCENT     = HexColor("#FFC31B")       # amber/gold accent
ACCENT_LT  = HexColor("#FFD54F")       # lighter amber
ACCENT_DK  = HexColor("#D4A017")       # darker amber for text on white
PAGE_BG    = white                     # page fill
WHITE      = white
BODY_TEXT  = HexColor("#2E3E44")       # body text - dark teal-gray
TEXT_SEC   = HexColor("#5A7078")       # secondary text - muted teal-gray
CARD_BG    = MAIN_PALE                 # card bg
CARD_BG2   = MAIN_PALE2               # card bg alt
CORAL      = HexColor("#E85D5D")       # error/warning accent
BLUE_ACC   = HexColor("#3A8FBF")       # blue accent (derived from teal family)

# ── Backward-compat aliases (used throughout drawing code) ──
NAVY       = PAGE_BG
NAVY_DEEP  = MAIN
NAVY_MID   = HexColor("#F3F7F8")       # subtle gradient strip
GOLD       = ACCENT
GOLD_LIGHT = ACCENT_LT
GOLD_DIM   = ACCENT_DK
LIGHT_GRAY = BODY_TEXT
SOFT_WHITE = MAIN_PALE
ACCENT_BLUE = BLUE_ACC
TEAL       = HexColor("#28878F")       # teal for model legend
TEXT_DIM   = TEXT_SEC
TEXT_DARK  = MAIN


def draw_bg(c, gradient=True):
    """Light background with subtle top gradient strip."""
    c.setFillColor(NAVY)  # white
    c.rect(0, 0, W, H, fill=1, stroke=0)
    if gradient:
        # subtle gray strip at top
        c.setFillColor(NAVY_MID)
        c.rect(0, H - 120, W, 120, fill=1, stroke=0)
        # blend bar
        for i in range(40):
            t = i / 40.0
            r = NAVY_MID.red * (1 - t) + NAVY.red * t
            g = NAVY_MID.green * (1 - t) + NAVY.green * t
            b = NAVY_MID.blue * (1 - t) + NAVY.blue * t
            c.setFillColor(Color(r, g, b))
            c.rect(0, H - 120 - i * 2, W, 2, fill=1, stroke=0)


def draw_accent_bar(c, y, width=None):
    """Thin teal accent bar."""
    w = width or 80
    c.setFillColor(MAIN)
    c.rect(50, y, w, 3, fill=1, stroke=0)


def draw_pill(c, x, y, w, h, color, radius=8):
    """Rounded rectangle (pill shape)."""
    c.setFillColor(color)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


def draw_diamond(c, cx, cy, size, color):
    """Small diamond accent."""
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx, cy + size)
    p.lineTo(cx + size, cy)
    p.lineTo(cx, cy - size)
    p.lineTo(cx - size, cy)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_circle(c, cx, cy, r, color):
    c.setFillColor(color)
    c.circle(cx, cy, r, fill=1, stroke=0)


def draw_page_number(c, page_num, total=6):
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 22, f"{page_num} / {total}")


def draw_header(c, title, page_num, total=6):
    """Consistent page header with teal accent bar and title."""
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, H - 72, title)
    # thin line under header
    c.setStrokeColor(MAIN_PALE2)
    c.setLineWidth(0.5)
    c.line(50, H - 82, W - 50, H - 82)
    draw_page_number(c, page_num, total)


# ═══════════════════════════════════════════════════════════════
# PAGE 1 - COVER
# ═══════════════════════════════════════════════════════════════
def page_cover(c):
    draw_bg(c, gradient=False)

    # Decorative geometric pattern in top-right (teal rings)
    for i in range(6):
        alpha = 0.06 + i * 0.018
        c.setFillColor(Color(MAIN.red, MAIN.green, MAIN.blue, alpha))
        size = 300 - i * 40
        c.circle(W - 80, H - 100, size, fill=1, stroke=0)

    # Decorative dots grid (subtle teal)
    for row in range(8):
        for col in range(12):
            x = 50 + col * 45
            y = 200 + row * 30
            alpha = 0.08 if (row + col) % 3 == 0 else 0.03
            c.setFillColor(Color(MAIN.red, MAIN.green, MAIN.blue, alpha))
            c.circle(x, y, 2, fill=1, stroke=0)

    # Teal accent bar - large
    c.setFillColor(MAIN)
    c.rect(50, H - 290, 100, 5, fill=1, stroke=0)

    # Title
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 44)
    c.drawString(50, H - 345, "/pbi")

    # Measure " - " width at size 44 to position "Power BI" right after
    pbi_w = pdfmetrics.stringWidth("/pbi", "Helvetica-Bold", 44)
    dash_str = "  -  "
    c.setFillColor(MAIN_LIGHT)
    c.drawString(50 + pbi_w, H - 345, dash_str)
    dash_w = pdfmetrics.stringWidth(dash_str, "Helvetica-Bold", 44)
    c.setFillColor(ACCENT)
    c.drawString(50 + pbi_w + dash_w, H - 345, "Power BI")

    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 44)
    c.drawString(50, H - 395, "DAX Co-Pilot")

    # Subtitle
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 16)
    c.drawString(52, H - 435, "Quick Start Guide for Claude Code")

    # Version badge
    draw_pill(c, 50, H - 480, 100, 28, MAIN, 14)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(100, H - 472, "v4.4.0")

    # Bottom info
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 10)
    c.drawString(50, 60, "Author: d7rocket")
    c.drawString(50, 45, "License: MIT")
    c.drawRightString(W - 50, 60, "github.com/d7rocket")
    c.drawRightString(W - 50, 45, "Claude Code Skill")

    # Thin teal line at bottom
    c.setFillColor(MAIN)
    c.rect(50, 35, W - 100, 1.5, fill=1, stroke=0)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 - WHAT IS /pbi + QUICK START
# ═══════════════════════════════════════════════════════════════
def page_intro(c):
    draw_bg(c)
    draw_header(c, "What is /pbi?", 2)

    y = H - 115

    # Intro paragraph
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 11)
    lines = [
        "/pbi turns Claude Code into a Power BI DAX co-pilot. It can explain, format,",
        "optimise, comment, and scaffold DAX measures from pasted code - no project needed.",
        "",
        "When pointed at a PBIP project (Power BI Project folder), it can also audit your",
        "semantic model for issues, track changes with local git versioning, batch-comment",
        "measures, and generate stakeholder-ready documentation - all without leaving the CLI.",
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 16

    y -= 20

    # Quick Start section
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 16)
    y -= 5
    c.drawString(50, y, "Quick Start")
    y -= 30

    steps = [
        ("1", "No project? Just paste DAX", "/pbi explain <your DAX>",
         "Works anywhere. Paste a measure and get a plain-English breakdown."),
        ("2", "Have a PBIP project?", "/pbi",
         "Run in the project root. Context auto-loads - no setup needed."),
        ("3", "Full guided session?", "/pbi deep",
         "Multi-phase workflow: intake, model review, DAX development, verification."),
        ("4", "Need a summary?", "/pbi extract",
         "Generates a structured overview of your entire model."),
    ]

    for num, title, cmd, desc in steps:
        # Card background
        draw_pill(c, 45, y - 52, W - 90, 62, CARD_BG, 10)

        # Step number circle
        draw_circle(c, 78, y - 20, 14, MAIN)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(78, y - 25, num)

        # Title + command
        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(102, y - 16, title)

        # Command in accent
        c.setFillColor(ACCENT_DK)
        c.setFont("Helvetica-Bold", 11)
        tw = pdfmetrics.stringWidth(title + "  ", "Helvetica-Bold", 12)
        c.drawString(102 + tw + 10, y - 16, cmd)

        # Description
        c.setFillColor(TEXT_DIM)
        c.setFont("Helvetica", 10)
        c.drawString(102, y - 34, desc)

        y -= 75

    y -= 20

    # How commands work mini-section
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 16)
    y -= 5
    c.drawString(50, y, "How It Knows Your Model")
    y -= 25

    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 10.5)
    info_lines = [
        "Every /pbi invocation runs detection blocks that scan your working directory for a",
        "SemanticModel folder, index all .tmdl or .bim files, check git state, and load session",
        "context from .pbi-context.md. This means every command already knows your tables,",
        "measures, columns, and relationships - no manual configuration required.",
    ]
    for line in info_lines:
        c.drawString(55, y, line)
        y -= 15

    y -= 15

    # Three model format badges
    badges = [("TMDL", "Folder-based format"), ("TMSL", "model.bim (JSON)"), ("PBIR", "Report detection")]
    bx = 55
    for label, sub in badges:
        draw_pill(c, bx, y - 18, 145, 35, MAIN_PALE2, 8)
        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx + 12, y - 4, label)
        c.setFillColor(TEXT_SEC)
        c.setFont("Helvetica", 9)
        c.drawString(bx + 12, y - 16, sub)
        bx += 165


# ═══════════════════════════════════════════════════════════════
# PAGE 3 - COMMAND REFERENCE
# ═══════════════════════════════════════════════════════════════
def page_commands(c):
    draw_bg(c)
    draw_header(c, "Command Reference", 3)

    y = H - 105

    def section_header(label, y_pos):
        draw_pill(c, 45, y_pos - 4, W - 90, 22, MAIN, 6)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(55, y_pos + 2, label)
        return y_pos - 30

    def cmd_row(cmd, desc, model, y_pos, alt=False):
        if alt:
            draw_pill(c, 48, y_pos - 5, W - 96, 18, MAIN_PALE, 4)
        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(58, y_pos, cmd)

        c.setFillColor(LIGHT_GRAY)
        c.setFont("Helvetica", 9.5)
        c.drawString(195, y_pos, desc)

        c.setFillColor(TEXT_DIM)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - 58, y_pos, model)
        return y_pos - 20

    # DAX Commands
    y = section_header("DAX Commands  -  work anywhere, just paste your DAX", y)

    dax_cmds = [
        ("/pbi explain", "Break down DAX into plain English", "Sonnet"),
        ("/pbi format", "Reformat DAX for readability (DAX Formatter API)", "Sonnet"),
        ("/pbi optimise", "Analyse DAX for performance improvements", "Sonnet"),
        ("/pbi comment", "Add inline comments to a measure", "Sonnet"),
        ("/pbi error", "Diagnose a DAX error and suggest fixes", "Sonnet"),
        ("/pbi new", "Scaffold a new measure from plain English", "Sonnet"),
    ]
    for i, (cmd, desc, model) in enumerate(dax_cmds):
        y = cmd_row(cmd, desc, model, y, alt=(i % 2 == 0))

    y -= 10

    # PBIP Commands
    y = section_header("PBIP Commands  -  require a *.SemanticModel/ directory", y)

    pbip_cmds = [
        ("/pbi load", "Read project structure into session context", "Haiku"),
        ("/pbi audit", "Full model health check with auto-fix", "Sonnet"),
        ("/pbi edit", "Modify model entities from plain English", "Sonnet"),
        ("/pbi comment-batch", "Comment all undocumented measures at once", "Sonnet"),
        ("/pbi extract", "Export structured project summary", "Varies"),
        ("/pbi docs", "Generate stakeholder-ready documentation", "Sonnet"),
        ("/pbi diff", "Summarise uncommitted changes", "Haiku"),
        ("/pbi commit", "Stage and commit with generated message", "Haiku"),
        ("/pbi undo", "Revert last auto-commit", "Haiku"),
        ("/pbi changelog", "Generate release notes from recent commits", "Haiku"),
    ]
    for i, (cmd, desc, model) in enumerate(pbip_cmds):
        y = cmd_row(cmd, desc, model, y, alt=(i % 2 == 0))

    y -= 10

    # Workflow + Utility
    y = section_header("Workflow & Utility", y)

    util_cmds = [
        ("/pbi deep", "Guided multi-phase workflow (intake / review / dev / verify)", "Sonnet"),
        ("/pbi help", "Show command reference with version check", "Sonnet"),
        ("/pbi version", "Show version history and changelog", "Sonnet"),
    ]
    for i, (cmd, desc, model) in enumerate(util_cmds):
        y = cmd_row(cmd, desc, model, y, alt=(i % 2 == 0))

    y -= 20

    # Model legend
    draw_pill(c, 45, y - 30, W - 90, 45, MAIN_PALE, 10)
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 9)
    c.drawString(60, y - 8, "Model Selection is Automatic:")
    c.setFillColor(MAIN_LIGHT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(60, y - 22, "Haiku")
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 9)
    c.drawString(97, y - 22, "= fast file/git ops   ")
    c.setFillColor(ACCENT_DK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(225, y - 22, "Sonnet")
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 9)
    c.drawString(268, y - 22, "= DAX reasoning   ")
    c.setFillColor(CORAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(375, y - 22, "Opus")
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 9)
    c.drawString(405, y - 22, "= deep extraction (thorough analysis)")


# ═══════════════════════════════════════════════════════════════
# PAGE 4 - FLOW DIAGRAM
# ═══════════════════════════════════════════════════════════════
def page_flow(c):
    draw_bg(c)
    draw_header(c, "How It Works", 4)

    # ── Main flow (vertical, centered) ──
    def flow_box(cx, cy, text, color=CARD_BG, text_color=MAIN, w=220, h=36, font_size=10):
        draw_pill(c, cx - w/2, cy - h/2, w, h, color, 10)
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", font_size)
        c.drawCentredString(cx, cy - 4, text)

    def arrow_down(cx, y_from, y_to, color=MAIN_LIGHT):
        c.setStrokeColor(color)
        c.setLineWidth(1.8)
        c.line(cx, y_from, cx, y_to + 6)
        # arrowhead
        c.setFillColor(color)
        p = c.beginPath()
        p.moveTo(cx, y_to)
        p.lineTo(cx - 5, y_to + 10)
        p.lineTo(cx + 5, y_to + 10)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def arrow_right(x_from, x_to, cy, color=GOLD):
        c.setStrokeColor(color)
        c.setLineWidth(1.8)
        c.line(x_from, cy, x_to - 6, cy)
        c.setFillColor(color)
        p = c.beginPath()
        p.moveTo(x_to, cy)
        p.lineTo(x_to - 10, cy - 5)
        p.lineTo(x_to - 10, cy + 5)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def arrow_left(x_from, x_to, cy, color=GOLD):
        c.setStrokeColor(color)
        c.setLineWidth(1.8)
        c.line(x_from, cy, x_to + 6, cy)
        c.setFillColor(color)
        p = c.beginPath()
        p.moveTo(x_to, cy)
        p.lineTo(x_to + 10, cy - 5)
        p.lineTo(x_to + 10, cy + 5)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    cx = W / 2
    y = H - 118

    # Step 1 - User input
    flow_box(cx, y, 'User types  /pbi [subcommand]', MAIN, WHITE, 280, 36, 11)
    arrow_down(cx, y - 18, y - 48)
    y -= 65

    # Step 2 - Detection
    det_w = 420
    det_h = 70
    draw_pill(c, cx - det_w/2, y - det_h/2, det_w, det_h, MAIN_PALE, 12)
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, y + 14, "Detection Blocks (run once)")
    # sub-items in two columns
    det_items = [
        ("PBIP Detection", "File Index"),
        ("Git State", "Session Context"),
    ]
    c.setFont("Helvetica", 9)
    c.setFillColor(MAIN_SUB)
    lx = cx - 120
    rx = cx + 30
    iy = y - 5
    for left, right in det_items:
        draw_diamond(c, lx - 12, iy + 3, 3, ACCENT)
        c.setFillColor(MAIN_SUB)
        c.setFont("Helvetica", 9)
        c.drawString(lx, iy, left)
        draw_diamond(c, rx - 12, iy + 3, 3, ACCENT)
        c.setFillColor(MAIN_SUB)
        c.setFont("Helvetica", 9)
        c.drawString(rx, iy, right)
        iy -= 14

    arrow_down(cx, y - det_h/2, y - det_h/2 - 30)
    y = y - det_h/2 - 47

    # Step 3 - Auto-Resume
    flow_box(cx, y, 'Auto-Resume (load/restore context)', MAIN_PALE2, MAIN, 300, 32, 10)
    arrow_down(cx, y - 16, y - 46)
    y -= 63

    # Step 4 - Router (diamond shape conceptually, but we'll use a wider box)
    rw = 340
    rh = 38
    draw_pill(c, cx - rw/2, y - rh/2, rw, rh, ACCENT, 10)
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, y - 4, "Router - match keyword to subcommand")

    # Branch left: keyword match
    # Branch right: no match (free text)
    branch_y = y - rh/2

    # Left branch label
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx - 110, branch_y - 8, "keyword match")
    # Right branch label
    c.drawCentredString(cx + 110, branch_y - 8, "no match")

    # Left arrow down
    left_cx = cx - 110
    arrow_down(left_cx, branch_y, branch_y - 38)
    y_branch = branch_y - 55

    # Left: Command executes
    flow_box(left_cx, y_branch, 'Command Executes', MAIN_SUB, WHITE, 180, 32, 10)

    # Model labels below
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawCentredString(left_cx, y_branch - 25, "Sonnet = DAX reasoning")
    c.drawCentredString(left_cx, y_branch - 37, "Haiku = file / git ops")

    arrow_down(left_cx, y_branch - 50, y_branch - 78)
    y_epi = y_branch - 95

    # Epilogue
    flow_box(left_cx, y_epi, 'Post-Command Epilogue', MAIN_PALE2, MAIN, 190, 30, 9)
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawCentredString(left_cx, y_epi - 24, "auto-stage changes + update context bar")

    # Right branch: Solve-First
    right_cx = cx + 110
    arrow_down(right_cx, branch_y, branch_y - 38)
    y_sf = branch_y - 55

    flow_box(right_cx, y_sf, 'Solve-First Handler', CORAL, WHITE, 180, 32, 10)
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawCentredString(right_cx, y_sf - 25, "Immediate DAX answer")

    arrow_down(right_cx, y_sf - 38, y_sf - 65)
    y_chk = y_sf - 80

    # Check: user says wrong?
    chk_w = 180
    chk_h = 30
    draw_pill(c, right_cx - chk_w/2, y_chk - chk_h/2, chk_w, chk_h, MAIN_PALE2, 8)
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(right_cx, y_chk - 4, 'User says "wrong" twice?')

    # No arrow - loops back
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawString(right_cx + chk_w/2 + 8, y_chk - 1, "No: silent retry")

    # Yes arrow down
    c.setFillColor(MAIN_SUB)
    c.setFont("Helvetica", 8)
    c.drawString(right_cx - 10, y_chk - chk_h/2 - 10, "Yes")
    arrow_down(right_cx, y_chk - chk_h/2, y_chk - chk_h/2 - 30)
    y_esc = y_chk - chk_h/2 - 47

    flow_box(right_cx, y_esc, 'Escalation', ACCENT, MAIN, 170, 30, 10)
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawCentredString(right_cx, y_esc - 24, "Ask 1 targeted question")
    c.drawCentredString(right_cx, y_esc - 36, "about the missing context")

    arrow_down(right_cx, y_esc - 48, y_esc - 72)
    y_retry = y_esc - 88

    flow_box(right_cx, y_retry, 'Retry with Context', MAIN_SUB, WHITE, 170, 30, 10)

    # ── Legend at bottom ──
    y_leg = 65
    draw_pill(c, 40, y_leg - 12, W - 80, 40, MAIN_PALE, 10)
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica", 8.5)
    c.drawString(58, y_leg + 12, "Detection, auto-resume, and the epilogue run every invocation. The router inspects")
    c.drawString(58, y_leg - 1, "the first keyword to pick a subcommand. Unrecognised input goes to the Solve-First handler.")


# ═══════════════════════════════════════════════════════════════
# PAGE 5 - KEY CONCEPTS
# ═══════════════════════════════════════════════════════════════
def page_concepts(c):
    draw_bg(c)
    draw_header(c, "Key Concepts", 5)

    y = H - 115

    concepts = [
        ("Session Context", ".pbi-context.md",
         "Auto-created file that tracks your model structure (tables, measures, columns,\n"
         "relationships), command history (last 20 commands), and escalation state.\n"
         "Loaded automatically every time you run /pbi."),
        ("Auto-Resume", "Zero-setup context loading",
         "No need to run /pbi load manually. When a PBIP project is detected, context\n"
         "loads automatically on every invocation. If context already exists, it resumes\n"
         "instantly. If not, it auto-loads the full project."),
        ("Auto-Commit", "Automatic local versioning",
         "Commands that modify your model (edit, comment, error, new, audit) auto-commit\n"
         "changes to local git. Use /pbi undo to revert the last auto-commit.\n"
         "All commits are LOCAL only - nothing is ever pushed."),
        ("Local-First Git", "Your files are the source of truth",
         "The skill NEVER runs git pull, git fetch, git push, or creates PRs.\n"
         "This policy exists because pulling previously overwrote local PBIP changes\n"
         "and broke relationships. Git is used only for local version control."),
        ("Smart Model Selection", "Right model for the job",
         "Haiku handles file and git operations (fast, cost-efficient). Sonnet handles\n"
         "DAX reasoning and analysis (smart, thorough). Opus is reserved for deep-dive\n"
         "extraction when maximum analysis depth is needed."),
        ("Supported Formats", "TMDL + TMSL",
         "TMDL: folder-based format with individual .tmdl files per table.\n"
         "TMSL: single model.bim JSON file (large-file chunked reading at 2000 lines).\n"
         "Both formats are fully supported for all commands."),
    ]

    icon_colors = [ACCENT, MAIN_SUB, BLUE_ACC, CORAL, ACCENT_LT, MAIN_LIGHT]

    for i, (title, subtitle, desc) in enumerate(concepts):
        card_h = 82
        draw_pill(c, 45, y - card_h + 12, W - 90, card_h, CARD_BG, 10)

        # Icon circle
        draw_circle(c, 78, y - 10, 16, icon_colors[i % len(icon_colors)])
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(78, y - 15, str(i + 1))

        # Title
        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(105, y - 5, title)

        # Subtitle
        c.setFillColor(ACCENT_DK)
        tw = pdfmetrics.stringWidth(title + "  ", "Helvetica-Bold", 12)
        c.setFont("Helvetica", 10)
        c.drawString(105 + tw + 8, y - 5, subtitle)

        # Description lines
        c.setFillColor(TEXT_DIM)
        c.setFont("Helvetica", 9)
        desc_lines = desc.split("\n")
        dy = y - 22
        for line in desc_lines:
            c.drawString(105, dy, line.strip())
            dy -= 13

        y -= card_h + 10


# ═══════════════════════════════════════════════════════════════
# PAGE 6 - TIPS & TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════
def page_tips(c):
    draw_bg(c)
    draw_header(c, "Tips & Troubleshooting", 6)

    y = H - 115

    # Tips section
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 14)
    y -= 2
    c.drawString(50, y, "Tips")
    y -= 28

    tips = [
        ("Interactive menu", "Type /pbi with no arguments to see a category menu (A-G)."),
        ("Free-text routing", 'Just ask: /pbi how do I calculate YoY growth? - the router figures it out.'),
        ("Auto-fix", "Audit can auto-fix critical issues: bidirectional filters, unhidden key columns."),
        ("UTF-8 safe", "All commands handle French accented characters (e, e, e, c, a, u) correctly."),
        ("Parallel audit", "Models with 5+ tables spawn 3 parallel agents for faster health checks."),
        ("Context bar", "Every command ends with a visual context usage indicator showing session state."),
    ]

    for title, desc in tips:
        draw_diamond(c, 58, y + 3, 4, ACCENT)
        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(72, y, title)
        tw = pdfmetrics.stringWidth(title, "Helvetica-Bold", 10)
        c.setFillColor(TEXT_SEC)
        c.setFont("Helvetica", 10)
        c.drawString(72 + tw + 8, y, "-  " + desc)
        y -= 22

    y -= 25

    # Troubleshooting section
    c.setFillColor(MAIN)
    c.setFont("Helvetica-Bold", 14)
    y -= 2
    c.drawString(50, y, "Troubleshooting")
    y -= 28

    issues = [
        ("PBIP not detected?",
         "Symptom: PBIP_MODE=paste even though a project exists.",
         "Fix: Ensure CWD is the project root containing the .SemanticModel/ folder.",
         CORAL),
        ("Git not initialized?",
         "Symptom: diff, commit, undo, changelog unavailable.",
         "Fix: Run /pbi commit - it auto-initializes a git repo and creates the first commit.",
         ACCENT),
        ("Context stale or corrupted?",
         "Symptom: Auto-resume shows outdated tables or measures.",
         "Fix: Run /pbi load to rebuild context from scratch.",
         BLUE_ACC),
        ("Measure name not found?",
         "Symptom: Command says a measure doesn't exist, but it does.",
         "Fix: Skill uses Python UTF-8 search. Verify file encoding if issue persists.",
         MAIN_SUB),
        ("TMDL indentation broken?",
         "Symptom: Power BI Desktop shows parse errors after an edit.",
         "Fix: TMDL uses tabs, not spaces. Check for space-to-tab conversion issues.",
         MAIN_LIGHT),
    ]

    for title, symptom, fix, color in issues:
        card_h = 62
        draw_pill(c, 45, y - card_h + 12, W - 90, card_h, CARD_BG, 8)

        # Colored left accent
        c.setFillColor(color)
        c.roundRect(45, y - card_h + 12, 4, card_h, 2, fill=1, stroke=0)

        c.setFillColor(MAIN)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(62, y - 3, title)

        c.setFillColor(TEXT_SEC)
        c.setFont("Helvetica", 9)
        c.drawString(62, y - 18, symptom)

        c.setFillColor(ACCENT_DK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(62, y - 33, fix)

        y -= card_h + 10

    # Footer
    y -= 10
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(W / 2, y, "For more details, run  /pbi help  inside Claude Code  |  v4.4.0  |  MIT License")


# ═══════════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════════
def main():
    output = "pbi-quick-start-guide.pdf"
    c = canvas.Canvas(output, pagesize=A4)
    c.setTitle("/pbi - Power BI DAX Co-Pilot - Quick Start Guide")
    c.setAuthor("d7rocket")
    c.setSubject("Quick Start Guide for the /pbi Claude Code Skill")

    page_cover(c)
    c.showPage()
    page_intro(c)
    c.showPage()
    page_commands(c)
    c.showPage()
    page_flow(c)
    c.showPage()
    page_concepts(c)
    c.showPage()
    page_tips(c)
    c.showPage()

    c.save()
    print(f"PDF generated: {output}")

if __name__ == "__main__":
    main()
