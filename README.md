from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Flowable
)
import datetime

W4, H4 = A4
LM = RM = 25*mm
TM = BM = 20*mm
CW = W4 - LM - RM   # content width

# ── Palette ────────────────────────────────────────────────────
WHITE   = colors.white
BLACK   = colors.HexColor("#0d0d0d")
INK     = colors.HexColor("#1a1a2e")
GRAY    = colors.HexColor("#4a4a4a")
LGRAY   = colors.HexColor("#888888")
BORDER  = colors.HexColor("#d0d0d0")
NAVY    = colors.HexColor("#1a3a6b")
BLUE    = colors.HexColor("#1e5ba8")
LBLUE   = colors.HexColor("#e8f0fb")
CYAN    = colors.HexColor("#0077b6")
GREEN   = colors.HexColor("#1a7a4a")
LGREEN  = colors.HexColor("#e8f5ee")
RED     = colors.HexColor("#b91c1c")
LRED    = colors.HexColor("#fef2f2")
GOLD    = colors.HexColor("#b45309")
LGOLD   = colors.HexColor("#fffbeb")
ACCENT  = colors.HexColor("#e8f0fb")
DARK    = colors.HexColor("#0f172a")

# ── Custom Flowables ────────────────────────────────────────────
class VRule(Flowable):
    def __init__(self, w, h, c=BORDER):
        self.w, self.h, self.c = w, h, c
    def draw(self):
        self.canv.setFillColor(self.c)
        self.canv.rect(0, 0, self.w, self.h, fill=1, stroke=0)
    def wrap(self, *a): return self.w, self.h

class HRule(Flowable):
    def __init__(self, w, h=1, c=BORDER):
        self.w, self.h, self.c = w, h, c
    def draw(self):
        self.canv.setFillColor(self.c)
        self.canv.rect(0, 0, self.w, self.h, fill=1, stroke=0)
    def wrap(self, *a): return self.w, self.h

# ── Page Events ─────────────────────────────────────────────────
class PageEvents:
    def __init__(self):
        self.chapter = ""

    def on_cover(self, canvas, doc):
        W, H = W4, H4
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # Deep navy top band
        canvas.setFillColor(NAVY)
        canvas.rect(0, H - 82, W, 82, fill=1, stroke=0)
        # Thin gold rule under navy
        canvas.setFillColor(GOLD)
        canvas.rect(0, H - 84, W, 2, fill=1, stroke=0)
        # Bottom band
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, W, 50, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, 50, W, 2, fill=1, stroke=0)
        # Left accent bar
        canvas.setFillColor(BLUE)
        canvas.rect(0, 52, 6, H - 136, fill=1, stroke=0)

    def on_page(self, canvas, doc):
        W, H = W4, H4
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # Top rule
        canvas.setFillColor(NAVY)
        canvas.rect(LM, H - 16*mm, CW, 0.8, fill=1, stroke=0)
        # Header text
        canvas.setFillColor(LGRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(LM, H - 14*mm,
            "PneumoAI — Deep Learning Based Pneumonia Detection")
        canvas.drawRightString(LM + CW, H - 14*mm,
            f"Page {doc.page}")
        # Bottom rule
        canvas.setFillColor(NAVY)
        canvas.rect(LM, 14*mm, CW, 0.8, fill=1, stroke=0)
        canvas.setFillColor(LGRAY)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(LM, 10*mm,
            "BCA Final Year Project  ·  Midnapore College, Dept. of Computer Application  ·  2025–26")
        canvas.drawRightString(LM + CW, 10*mm, "EduMath")

PE = PageEvents()

# ── Style Factory ───────────────────────────────────────────────
def S(name, **kw): return ParagraphStyle(name, **kw)

ss = {
# Cover
"cov_tag":   S("ct", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#aac4ff"),
               alignment=TA_CENTER, letterSpacing=2, spaceAfter=6),
"cov_title": S("cv", fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,
               alignment=TA_CENTER, leading=32, spaceAfter=4),
"cov_sub":   S("cs", fontName="Helvetica", fontSize=12, textColor=colors.HexColor("#c0d4ff"),
               alignment=TA_CENTER, leading=18, spaceAfter=4),
"cov_meta":  S("cm", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#8899cc"),
               alignment=TA_CENTER, spaceAfter=3),
"cov_body":  S("cb", fontName="Helvetica", fontSize=10, textColor=GRAY,
               alignment=TA_JUSTIFY, leading=16, spaceAfter=6),
# Additional cover styles
"cov_college": S("cov_college", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
                  alignment=TA_CENTER, spaceAfter=2),
"cov_aff":     S("cov_aff", fontName="Helvetica", fontSize=9, textColor=GRAY,
                  alignment=TA_CENTER, spaceAfter=2),
"cov_dept":    S("cov_dept", fontName="Helvetica", fontSize=10, textColor=BLUE,
                  alignment=TA_CENTER, spaceAfter=6),
"cov_report":  S("cov_report", fontName="Helvetica-Bold", fontSize=11, textColor=GOLD,
                  alignment=TA_CENTER, spaceAfter=4),
"cov_subtitle":S("cov_subtitle", fontName="Helvetica", fontSize=12, textColor=WHITE,
                  alignment=TA_CENTER, leading=16, spaceAfter=6),
"cov_footer":  S("cov_footer", fontName="Helvetica", fontSize=10, textColor=GRAY,
                  alignment=TA_CENTER, leading=14, spaceAfter=6),
"cov_year":    S("cov_year", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY,
                  alignment=TA_CENTER, spaceAfter=2),
# Certificates
"cert_h":    S("ch2", fontName="Helvetica-Bold", fontSize=16, textColor=NAVY,
               alignment=TA_CENTER, spaceAfter=10, leading=22),
"cert_b":    S("cb2", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
               alignment=TA_CENTER, leading=17, spaceAfter=8),
"sig_name":  S("sn", fontName="Helvetica-Bold", fontSize=10.5, textColor=BLACK),
"sig_role":  S("sr", fontName="Helvetica", fontSize=9, textColor=LGRAY),
# Chapter headers
"ch_num":    S("cn", fontName="Helvetica-Bold", fontSize=9, textColor=BLUE,
               letterSpacing=1.5, spaceAfter=2),
"ch_title":  S("cth", fontName="Helvetica-Bold", fontSize=20, textColor=NAVY,
               leading=26, spaceAfter=4),
"ch_rule":   S("cr", fontName="Helvetica", fontSize=1, spaceAfter=2),
# Section
"sec_h":     S("sh", fontName="Helvetica-Bold", fontSize=13, textColor=NAVY,
               spaceBefore=10, spaceAfter=4, leading=17),
"sec_h2":    S("sh2", fontName="Helvetica-Bold", fontSize=11, textColor=BLUE,
               spaceBefore=6, spaceAfter=3, leading=15),
# Body
"body":      S("bd", fontName="Helvetica", fontSize=10, textColor=GRAY,
               leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
"body_b":    S("bdb", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK,
               leading=16, spaceAfter=4),
"bullet":    S("bl", fontName="Helvetica", fontSize=10, textColor=GRAY,
               leading=15, spaceAfter=3, leftIndent=14, bulletIndent=0),
"bullet2":   S("bl2", fontName="Helvetica`,
}