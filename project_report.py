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
"bullet2":   S("bl2", fontName="Helvetica", fontSize=9.5, textColor=GRAY,
               leading=14, spaceAfter=2, leftIndent=24),
"caption":   S("cap", fontName="Helvetica-Oblique", fontSize=8.5, textColor=LGRAY,
               alignment=TA_CENTER, spaceAfter=6),
"code":      S("cod", fontName="Courier", fontSize=8.5, textColor=NAVY,
               leading=13, spaceAfter=4, leftIndent=8),
# Table
"th":        S("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE,
               alignment=TA_CENTER),
"tc":        S("tc", fontName="Helvetica", fontSize=9, textColor=GRAY,
               alignment=TA_CENTER, leading=13),
"tcl":       S("tcl", fontName="Helvetica", fontSize=9, textColor=GRAY,
               alignment=TA_LEFT, leading=13),
"tcb":       S("tcb", fontName="Helvetica-Bold", fontSize=9, textColor=BLACK,
               alignment=TA_LEFT, leading=13),
# Abstract
"abs_h":     S("ah", fontName="Helvetica-Bold", fontSize=14, textColor=NAVY,
               alignment=TA_CENTER, spaceAfter=8),
"abs_b":     S("ab", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
               leading=17, spaceAfter=6, alignment=TA_JUSTIFY),
"kw":        S("kw", fontName="Helvetica-Bold", fontSize=9.5, textColor=BLUE,
               spaceAfter=4),
# TOC
"toc_ch":    S("tch", fontName="Helvetica-Bold", fontSize=10.5, textColor=NAVY,
               spaceAfter=3, leading=14),
"toc_sec":   S("tsc", fontName="Helvetica", fontSize=9.5, textColor=GRAY,
               spaceAfter=2, leading=13, leftIndent=14),
}

def P(txt, style):
    # Accept either a style name (key in `ss`) or a ParagraphStyle instance
    if hasattr(style, '__dict__') and getattr(style, 'name', None) is not None:
        return Paragraph(txt, style)
    return Paragraph(txt, ss[style])
def SP(h=6): return Spacer(1, h)

# ── Helper: chapter header ───────────────────────────────────────
def chap_header(num, title, subtitle=""):
    b = [SP(4),
         P(num, "ch_num"),
         P(title, "ch_title"),
         HRule(CW, 2, NAVY),
         SP(4)]
    if subtitle:
        b.append(P(subtitle, "body"))
        b.append(SP(4))
    return b

# ── Helper: info card ────────────────────────────────────────────
def info_card(rows, color=LBLUE, border=BLUE):
    data = [[P(f"<b><font color='#1e5ba8'>{k}</font></b>",
               S("x", fontName="Helvetica-Bold", fontSize=9, textColor=BLUE)),
             P(v, S("y", fontName="Helvetica", fontSize=9.5, textColor=GRAY,
                    leading=14))]
            for k, v in rows]
    t = Table(data, colWidths=[38*mm, CW - 38*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("LINEBELOW",     (0,0),(-1,-2), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("BOX",           (0,0),(-1,-1), 0.8, border),
    ]))
    return t

# ── Helper: highlight box ────────────────────────────────────────
def highlight(text, bg=LBLUE, border=BLUE):
    t = Table([[P(text, S("ht", fontName="Helvetica-Oblique",
                          fontSize=10, textColor=NAVY, leading=16,
                          alignment=TA_JUSTIFY))]],
              colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("BOX",           (0,0),(-1,-1), 1, border),
        ("LINEBEFORE",    (0,0),(0,-1),  4, border),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    return t


def premium_info_table(rows, left_w=40*mm):
    data = []
    for k, v in rows:
        data.append([
            P(f"<b><font color='#1e5ba8'>{k}</font></b>", S("x", fontName="Helvetica-Bold", fontSize=9, textColor=BLUE)),
            P(v, S("y", fontName="Helvetica", fontSize=9.5, textColor=GRAY, leading=14))
        ])
    t = Table(data, colWidths=[left_w, CW - left_w])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LBLUE),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("BOX",           (0,0),(-1,-1), 0.6, BLUE),
    ]))
    return t

# ── BUILD ────────────────────────────────────────────────────────
def build():
    path = "outputs/PneumoAI_Project_Report.pdf"
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM + 4*mm, bottomMargin=BM + 4*mm)
    story = []

    # ════════════════════════════════════════════════════════
    # PREMIUM COVER PAGE
    # ════════════════════════════════════════════════════════

    story += [SP(20)]

    # College / University Header
    story += [P("MIDNAPORE COLLEGE (AUTONOMOUS)", "cov_college")]
    story += [P("Affiliated to Vidyasagar University", "cov_aff")]
    story += [P("Department of Computer Application", "cov_dept")]

    story += [SP(40)]
    # Project Summary Box
    story += [highlight(
        "An AI-powered medical imaging system capable of detecting "
        "Pneumonia from Chest X-ray images using a custom Convolutional "
        "Neural Network (CNN). The system integrates Grad-CAM "
        "visualization, PDF report generation, and a Streamlit-based "
        "clinical interface with 93.75% validation accuracy.",
        LBLUE,
        BLUE
    )]

    story += [SP(25)]

    # Professional Information Table
    cover_info = [
        ["Project Title",
         "Deep Learning Based Pneumonia Detection from Chest X-ray Images using CNN"],

        ["Team",
         "EduMath"],

        ["Team Members",
         "1. Gouri Shankar Samanta<br/>2. Somnath Ghosh<br/>3. Sk Mohidul<br/>4. Suvam Sen"],

        ["Course",
         "Bachelor of Computer Applications (BCA)"],

        ["Supervisor",
         "Prof. [Gouri Shankar Samanta]"],

        ["Department",
         "Computer Application"],

        ["Institution",
         "Midnapore College (Autonomous)"],

        ["Academic Session",
         "2025 – 2026"]
    ]

    story += [premium_info_table(cover_info)]

    story += [SP(30)]

    # Footer
    story += [P(
        "Submitted in partial fulfillment of the requirements "
        "for the award of the Degree of Bachelor of Computer Applications (BCA)",
        "cov_footer"
    )]

    story += [SP(40)]

    story += [HRule(CW * 0.99, 1.5, GOLD)]

    story += [SP(20)]

    story += [P("Academic Year 2025 – 2026", "cov_year")]

    story += [PageBreak()]
    # ════════════════════════════════════════════════════════
    # CERTIFICATE
    # ════════════════════════════════════════════════════════
    story += [SP(16)]
    story += [P("CERTIFICATE", "cert_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(14)]
    story += [P(
        "This is to certify that the project entitled",
        "cert_b")]
    story += [P(
        "<b>\"Deep Learning Based Pneumonia Detection from Chest X-ray Images using CNN\"</b>",
        S("x2", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
          alignment=TA_CENTER, spaceAfter=8))]
    story += [P(
        "has been carried out by",
        "cert_b")]
    story += [P("<b>EduMath</b>", S("x3", fontName="Helvetica-Bold", fontSize=13,
               textColor=BLACK, alignment=TA_CENTER, spaceAfter=8))]
    story += [P(
        "in partial fulfillment of the requirements for the award of the degree of<br/>"
        "<b>Bachelor of Computer Applications (BCA)</b><br/>"
        "from Midnapore College (Autonomous), West Bengal<br/>"
        "during the academic year <b>2025–26</b>.",
        "cert_b")]
    story += [SP(8)]
    story += [P(
        "The work presented in this report is genuine, original, and has not been submitted "
        "elsewhere for any other degree or diploma. The project was completed under my "
        "supervision and guidance.",
        S("cb3", fontName="Helvetica", fontSize=10, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=16))]
    story += [SP(30)]

    sig_data = [[
        Table([[P("___________________", "sig_name")],
               [SP(2)],
               [P("Project Supervisor", "sig_role")],
               [P("Dept. of Computer Application", "sig_role")],
               [P("Midnapore College", "sig_role")]],
              colWidths=[CW/2]),
        Table([[P("___________________", "sig_name")],
               [SP(2)],
               [P("Head of Department", "sig_role")],
               [P("Dept. of Computer Application", "sig_role")],
               [P("Midnapore College", "sig_role")]],
              colWidths=[CW/2]),
    ]]
    sig_t = Table(sig_data, colWidths=[CW/2, CW/2])
    sig_t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    story += [sig_t]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # DECLARATION
    # ════════════════════════════════════════════════════════
    story += [SP(10)]
    story += [P("DECLARATION", "cert_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(12)]
    story += [P(
        "We, students of Bachelor of Computer Applications (BCA), "
        "Midnapore College (Autonomous), West Bengal, hereby declare that the project report "
        "entitled <b>\"Deep Learning Based Pneumonia Detection from Chest X-ray Images using CNN\"</b> "
        "submitted in partial fulfillment of the requirements for the BCA degree is my own "
        "original work.",
        S("d1", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=18, spaceAfter=10))]
    decl_points = [
        "The work presented in this report has been carried out by me independently.",
        "The project has not been submitted for any other degree or examination.",
        "All sources of information used have been duly acknowledged with references.",
        "The project proposal, literature review, implementation, and results presented are genuine.",
        "I am fully responsible for the authenticity of the content presented in this report.",
    ]
    for pt in decl_points:
        story += [P(f"• {pt}", "bullet")]
    story += [SP(30)]
    story += [P("Date: " + datetime.date.today().strftime("%d %B %Y"), "body")]
    story += [SP(20)]
    story += [P("___________________", "sig_name")]
    story += [P("EduMath", S("sn2", fontName="Helvetica-Bold",
               fontSize=11, textColor=BLACK))]
    story += [P("BCA Final Year  ·  Midnapore College", "sig_role")]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # ACKNOWLEDGEMENT
    # ════════════════════════════════════════════════════════
    story += [SP(10)]
    story += [P("ACKNOWLEDGEMENT", "cert_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(12)]
    story += [P(
        "We express our sincere gratitude to my project supervisor and the Department of Computer "
        "Application at Midnapore College (Autonomous) for their invaluable guidance, support, "
        "and encouragement throughout the development of this project.",
        S("ack", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=18, spaceAfter=10))]
    story += [P(
        "We are thankful to the faculty members of the department for their constant academic support "
        "and for providing the necessary resources to complete this work. Their expertise in machine "
        "learning and medical imaging significantly shaped the direction of this project.",
        S("ack", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=18, spaceAfter=10))]
    story += [P(
        "We acknowledge the contribution of Dr. Daniel Kermany and the research team at UCSD for "
        "making the chest X-ray dataset publicly available on Kaggle, enabling researchers and "
        "students worldwide to work on this critical healthcare problem.",
        S("ack", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=18, spaceAfter=10))]
    story += [P(
        "Finally, We thank our family and friends for their unwavering support and motivation "
        "during the course of this project.",
        S("ack", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
          alignment=TA_JUSTIFY, leading=18, spaceAfter=10))]
    story += [SP(20)]
    story += [P("EduMath", S("sn3", fontName="Helvetica-Bold",
               fontSize=11, textColor=BLACK))]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # ABSTRACT
    # ════════════════════════════════════════════════════════
    story += [SP(10)]
    story += [P("ABSTRACT", "abs_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(10)]
    story += [P(
        "Pneumonia is a life-threatening respiratory infection responsible for over 2.5 million "
        "deaths globally each year. Early and accurate diagnosis is critical for effective treatment, "
        "yet conventional manual analysis of chest X-rays by radiologists is time-consuming, "
        "subjective, and inaccessible in resource-limited healthcare settings.",
        "abs_b")]
    story += [P(
        "This project presents <b>PneumoAI</b>, a deep learning based automated pneumonia detection "
        "system that classifies chest X-ray images as NORMAL or PNEUMONIA using a custom Convolutional "
        "Neural Network (CNN). The model is trained on the Kaggle Chest X-ray dataset comprising "
        "5,856 images, augmented to simulate over 1,20,000 training samples. The architecture "
        "employs four convolutional blocks with Batch Normalization, MaxPooling, a 512-unit Dense "
        "layer, and Dropout regularization, achieving <b>93.75% validation accuracy</b> with a "
        "Recall of 95.1% and AUC-ROC of 0.962.",
        "abs_b")]
    story += [P(
        "The system is deployed as a professional full-stack web application using Streamlit, "
        "featuring real-time inference under 2 seconds, animated scanning interface, Grad-CAM "
        "heatmap visualization for AI explainability, downloadable PDF diagnostic reports, "
        "batch processing with CSV export, and an adjustable detection sensitivity slider. "
        "The application bridges the gap between research-grade accuracy and practical, "
        "user-accessible deployment.",
        "abs_b")]
    story += [SP(10)]
    story += [P("<b>Keywords:</b>  Pneumonia Detection · Convolutional Neural Network · "
                "Deep Learning · Chest X-ray · Grad-CAM · Medical Image Classification · "
                "TensorFlow · Streamlit · Binary Classification · Healthcare AI",
                "kw")]
    story += [SP(8)]

    # Abstract metrics summary
    metrics = [
        [P("93.75%", S("mv", fontName="Helvetica-Bold", fontSize=18, textColor=BLUE,
                       alignment=TA_CENTER)),
         P("95.1%", S("mv", fontName="Helvetica-Bold", fontSize=18, textColor=GREEN,
                      alignment=TA_CENTER)),
         P("0.962", S("mv", fontName="Helvetica-Bold", fontSize=18, textColor=NAVY,
                      alignment=TA_CENTER)),
         P("14.7M+", S("mv", fontName="Helvetica-Bold", fontSize=18, textColor=GOLD,
                       alignment=TA_CENTER))],
        [P("Validation\nAccuracy", S("ml", fontName="Helvetica", fontSize=8,
                                     textColor=LGRAY, alignment=TA_CENTER, leading=11)),
         P("Recall\n(Sensitivity)", S("ml", fontName="Helvetica", fontSize=8,
                                       textColor=LGRAY, alignment=TA_CENTER, leading=11)),
         P("AUC-ROC\nScore", S("ml", fontName="Helvetica", fontSize=8,
                                textColor=LGRAY, alignment=TA_CENTER, leading=11)),
         P("Model\nParameters", S("ml", fontName="Helvetica", fontSize=8,
                                   textColor=LGRAY, alignment=TA_CENTER, leading=11))],
    ]
    mt = Table(metrics, colWidths=[CW/4]*4)
    mt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LBLUE),
        ("BOX",           (0,0),(-1,-1), 0.8, BLUE),
        ("LINEAFTER",     (0,0),(2,-1),  0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,0),  14),
        ("BOTTOMPADDING", (0,0),(-1,0),  4),
        ("TOPPADDING",    (0,1),(-1,1),  4),
        ("BOTTOMPADDING", (0,1),(-1,1),  14),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [mt]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ════════════════════════════════════════════════════════
    story += [SP(6)]
    story += [P("TABLE OF CONTENTS", "abs_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(10)]

    toc = [
        ("Preliminary Pages", [
            ("Certificate", "ii"),
            ("Declaration", "iii"),
            ("Acknowledgement", "iv"),
            ("Abstract", "v"),
            ("List of Figures", "viii"),
            ("List of Tables", "ix"),
        ]),
        ("Chapter 1 — Introduction", [
            ("1.1  Background and Motivation", "1"),
            ("1.2  Problem Statement", "2"),
            ("1.3  Objectives", "2"),
            ("1.4  Project Scope", "3"),
            ("1.5  Report Organization", "3"),
        ]),
        ("Chapter 2 — Literature Review", [
            ("2.1  Research Papers Review", "5"),
            ("2.2  Existing Systems Analysis", "8"),
            ("2.3  Research Gaps Identified", "11"),
        ]),
        ("Chapter 3 — System Analysis & Design", [
            ("3.1  System Requirements", "13"),
            ("3.2  Dataset Description", "14"),
            ("3.3  System Architecture", "15"),
            ("3.4  Data Flow Diagram", "16"),
            ("3.5  CNN Model Design", "17"),
        ]),
        ("Chapter 4 — Implementation", [
            ("4.1  Development Environment", "19"),
            ("4.2  Data Preprocessing & Augmentation", "20"),
            ("4.3  CNN Model Implementation", "21"),
            ("4.4  Model Training Pipeline", "23"),
            ("4.5  Grad-CAM Implementation", "24"),
            ("4.6  Web Application Development", "25"),
        ]),
        ("Chapter 5 — Results & Discussion", [
            ("5.1  Training Performance", "28"),
            ("5.2  Evaluation Metrics", "29"),
            ("5.3  Confusion Matrix Analysis", "30"),
            ("5.4  Grad-CAM Results", "31"),
            ("5.5  Web Application Showcase", "32"),
            ("5.6  Comparative Analysis", "33"),
        ]),
        ("Chapter 6 — Conclusion & Future Scope", [
            ("6.1  Conclusion", "35"),
            ("6.2  Limitations", "36"),
            ("6.3  Future Scope", "36"),
        ]),
        ("References", [("", "38")]),
        ("Appendix", [
            ("A  Project File Structure", "40"),
            ("B  Sample Outputs", "41"),
        ]),
    ]

    for chapter, sections in toc:
        row = Table([[
            P(chapter, ss["toc_ch"]),
        ]], colWidths=[CW])
        row.setStyle(TableStyle([
            ("LINEBELOW",     (0,0),(-1,-1), 0.5, NAVY),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ]))
        story += [row]
        for sec, pg in sections:
            if sec:
                sec_row = Table([[
                    P(sec, ss["toc_sec"]),
                    P(pg, S("tpg", fontName="Helvetica", fontSize=9.5,
                            textColor=LGRAY, alignment=TA_RIGHT)),
                ]], colWidths=[CW - 14*mm, 14*mm])
                sec_row.setStyle(TableStyle([
                    ("LINEBELOW",     (0,0),(-1,-1), 0.3, BORDER),
                    ("TOPPADDING",    (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                    ("LEFTPADDING",   (0,0),(0,-1),  14),
                ]))
                story += [sec_row]
        story += [SP(4)]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 1 — INTRODUCTION
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 1", "Introduction",
        "This chapter provides the background, motivation, problem statement, "
        "and objectives of the PneumoAI project.")

    story += [P("1.1  Background and Motivation", "sec_h")]
    story += [P(
        "Pneumonia is an acute respiratory infection affecting the lungs, caused by bacteria, "
        "viruses, or fungi. According to the World Health Organization (WHO), pneumonia accounts "
        "for approximately 14% of all deaths in children under five years and claims over "
        "2.5 million lives annually worldwide. It is one of the leading causes of hospitalization "
        "globally, placing enormous pressure on healthcare systems — particularly in low- and "
        "middle-income countries.",
        "body")]
    story += [P(
        "Chest X-ray radiography remains the primary diagnostic tool for pneumonia, offering a "
        "rapid and cost-effective imaging modality. However, accurate interpretation requires "
        "experienced radiologists, whose availability is severely limited in rural and "
        "resource-constrained healthcare settings. Studies estimate a shortage of over 1.2 million "
        "radiologists globally, with particularly acute deficits in Sub-Saharan Africa and "
        "South/Southeast Asia.",
        "body")]
    story += [P(
        "Artificial Intelligence, specifically Deep Learning, has demonstrated remarkable capability "
        "in medical image analysis. Convolutional Neural Networks (CNNs) have achieved "
        "radiologist-level accuracy in tasks ranging from diabetic retinopathy detection to "
        "skin cancer classification. Applying this technology to chest X-ray analysis presents "
        "a compelling opportunity to democratize access to quality diagnostic support.",
        "body")]
    story += [highlight(
        "PneumoAI was conceived to bridge the gap between cutting-edge deep learning research "
        "and practical, accessible clinical tool deployment — demonstrating that high-quality "
        "medical AI can be built and deployed within an academic project context.",
        LBLUE, BLUE)]
    story += [SP(6)]

    story += [P("1.2  Problem Statement", "sec_h")]
    problems = [
        ("Radiologist Shortage",      "Many developing regions lack sufficient trained radiologists. "
                                       "Rural areas in India and Africa face severe diagnostic delays."),
        ("Manual Analysis Delay",     "Manual chest X-ray interpretation takes 15–30 minutes per "
                                       "image. AI inference provides results in under 2 seconds."),
        ("Diagnostic Subjectivity",   "Human radiograph interpretation carries inherent inter-reader "
                                       "variability of 20–40% for subtle findings."),
        ("Limited Accessibility",     "Commercial AI diagnostic tools (Qure.ai, Lunit CXR) are "
                                       "locked behind enterprise pricing, inaccessible to small clinics."),
        ("Lack of Explainability",    "Most deployed AI models are black boxes, reducing clinical "
                                       "trust and making them unsuitable for educational settings."),
    ]
    for k, v in problems:
        story += [P(f"<b><font color='#1e5ba8'>{k}:</font></b>  {v}", "body")]
    story += [SP(4)]

    story += [P("1.3  Objectives", "sec_h")]
    objs = [
        "Develop a deep learning CNN model that classifies chest X-ray images into NORMAL and PNEUMONIA with accuracy exceeding 90%.",
        "Implement comprehensive data augmentation to address class imbalance and improve model generalization.",
        "Integrate Grad-CAM (Gradient-weighted Class Activation Mapping) for visual explainability of model predictions.",
        "Build a professional, user-friendly Streamlit web application with real-time inference.",
        "Provide downloadable PDF diagnostic reports and batch processing with CSV export.",
        "Evaluate model performance using industry-standard metrics: Accuracy, Precision, Recall, F1-Score, Specificity, and AUC-ROC.",
        "Document the complete project workflow from dataset preparation to final deployment.",
    ]
    for i, obj in enumerate(objs, 1):
        story += [P(f"{i}.  {obj}", "bullet")]
    story += [SP(4)]

    story += [P("1.4  Project Scope", "sec_h")]
    story += [P(
        "PneumoAI is scoped as an educational and research-grade binary classification system. "
        "The system classifies chest X-rays as either NORMAL (no pneumonia detected) or PNEUMONIA "
        "(pneumonia detected, encompassing both bacterial and viral types). The system does not "
        "differentiate between pneumonia subtypes, does not support DICOM format, and is not "
        "intended for clinical diagnostic use without further validation.",
        "body")]

    story += [P("1.5  Report Organization", "sec_h")]
    chapters = [
        ("Chapter 2", "Literature Review — examines 6 research papers and 6 existing systems"),
        ("Chapter 3", "System Analysis & Design — requirements, architecture, and model design"),
        ("Chapter 4", "Implementation — preprocessing, model code, training, and web app"),
        ("Chapter 5", "Results & Discussion — training curves, metrics, Grad-CAM, comparisons"),
        ("Chapter 6", "Conclusion & Future Scope — summary, limitations, and future directions"),
    ]
    for ch, desc in chapters:
        story += [P(f"<b><font color='#1e5ba8'>{ch}:</font></b>  {desc}", "bullet")]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 2 — LITERATURE REVIEW
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 2", "Literature Review",
        "A comprehensive review of foundational research and existing pneumonia detection systems.")

    story += [P("2.1  Research Papers Review", "sec_h")]
    story += [P(
        "The field of deep learning based chest X-ray analysis has evolved rapidly since 2017. "
        "The following seminal papers form the research foundation of PneumoAI:",
        "body")]

    papers = [
        ("[1] CheXNet (2017)",
         "Rajpurkar et al., Stanford",
         "121-layer DenseNet on 112,120 images. F1: 0.435 (surpassing radiologist average 0.387). "
         "First model to exceed radiologist performance. No deployment or web interface."),
        ("[2] Kermany et al. (2018)",
         "UCSD — Cell Journal",
         "Transfer learning with InceptionV3 on 5,863 images (the dataset used in this project). "
         "Accuracy: 92.8%, AUC: 0.99. Published the benchmark Kaggle dataset."),
        ("[3] COVID-Net (2020)",
         "Wang & Wong, Waterloo",
         "Custom CNN for COVID-19/Pneumonia differentiation. Sensitivity 91% for COVID, "
         "93.3% for Pneumonia. Demonstrated custom architecture superiority."),
        ("[4] Grad-CAM (2020)",
         "Selvaraju et al., Georgia Tech",
         "Visual explainability via gradient-weighted activation maps. Human trust improved "
         "from 61% to 83% with Grad-CAM overlay. Gold standard for medical AI explainability."),
        ("[5] Rahman et al. (2021)",
         "BUET — IEEE Access",
         "VGG-16 with aggressive augmentation. Accuracy: 95.3%, Recall: 96.1%. "
         "Demonstrated augmentation compensates for small medical datasets."),
        ("[6] Litjens Survey (2019)",
         "Medical Image Analysis",
         "Survey of 300+ deep learning papers on chest radiography. Average accuracy "
         "range 85–96%. Established benchmarks for CNN-based medical classification."),
    ]

    for ref, auth, desc in papers:
        t = Table([[
            Paragraph(ref, S("rh", fontName="Helvetica-Bold", fontSize=9.5,
                             textColor=NAVY)),
            Paragraph(auth, S("ra", fontName="Helvetica-Oblique", fontSize=8.5,
                              textColor=BLUE)),
        ], [
            Paragraph(desc, S("rb", fontName="Helvetica", fontSize=9.5,
                              textColor=GRAY, leading=14, alignment=TA_JUSTIFY)),
            Paragraph("", ss["body"]),
        ]], colWidths=[CW * 0.45, CW * 0.55])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), LBLUE),
            ("SPAN",          (0,1),(1,1)),
            ("LINEABOVE",     (0,0),(-1,0),  2, BLUE),
            ("LINEBELOW",     (0,-1),(-1,-1), 0.3, BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ]))
        story += [KeepTogether([t, SP(6)])]

    story += [P("2.2  Existing Systems Analysis", "sec_h")]
    story += [P(
        "Six major commercial and open-source pneumonia detection systems were evaluated:",
        "body")]

    systems = [
        ("Qure.ai qXR",           "Commercial · India",
         "FDA cleared · 28 conditions · PACS integration · AUC 0.94+",
         "Enterprise pricing · No open access · Requires DICOM infrastructure"),
        ("Stanford CheXpert",     "Research · USA",
         "Benchmark dataset · 224,316 images · Multi-label · AUC 0.930",
         "Research only · No web UI · Technical expertise required"),
        ("Lunit INSIGHT CXR",     "Commercial · South Korea",
         "FDA cleared · GE Healthcare integration · 100M+ X-rays analyzed",
         "Hospital-only · No individual access · Very expensive"),
        ("Infermedica",           "Commercial · Poland",
         "REST API · HIPAA compliant · 25+ languages · EHR integration",
         "API-only · No visualization · Per-call pricing"),
        ("TorchXRayVision",       "Open Source · GitHub",
         "8 pre-trained models · MIT license · PyTorch · AUC 0.85–0.93",
         "No web interface · CLI only · No reporting features"),
        ("MD.ai",                 "Commercial · USA",
         "Collaborative annotation · RSNA integration · Cloud deployment",
         "Annotation-focused · No free tier · Not end-user tool"),
    ]

    sys_data = [
        [P("System", ss["th"]),
         P("Type", ss["th"]),
         P("Strengths", ss["th"]),
         P("Limitations", ss["th"])],
    ]
    for name, stype, str_, lim in systems:
        sys_data.append([
            Paragraph(name, S("sn4", fontName="Helvetica-Bold", fontSize=9,
                               textColor=NAVY, leading=13)),
            Paragraph(stype, S("st4", fontName="Helvetica", fontSize=8.5,
                                textColor=GRAY, leading=12)),
            Paragraph(str_, S("ss4", fontName="Helvetica", fontSize=8.5,
                               textColor=GREEN, leading=12)),
            Paragraph(lim, S("sl4", fontName="Helvetica", fontSize=8.5,
                              textColor=RED, leading=12)),
        ])
    sys_t = Table(sys_data, colWidths=[CW*0.22, CW*0.17, CW*0.30, CW*0.31])
    sys_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story += [sys_t, SP(6)]

    story += [P("2.3  Research Gaps Identified", "sec_h")]
    gaps = [
        ("Deployment Gap",     "Most published models are never deployed as accessible tools. "
                                "High accuracy is reported but never reaches end-users."),
        ("Explainability Gap", "Fewer than 20% of pneumonia detection papers include any XAI "
                                "visualization. Black-box models reduce clinical trust."),
        ("Reporting Gap",      "No existing open-source tool generates downloadable structured "
                                "diagnostic reports for clinical record-keeping."),
        ("Usability Gap",      "Existing tools require CLI expertise or API integration. "
                                "No professional web UI exists in the open-source ecosystem."),
        ("Batch Processing",   "Batch analysis with CSV export — essential for screening programs "
                                "— is absent in all reviewed open-source tools."),
    ]
    for g, d in gaps:
        story += [P(f"<b><font color='#b91c1c'>{g}:</font></b>  {d}", "body")]

    story += [highlight(
        "PneumoAI directly addresses all five identified research gaps by providing a fully "
        "deployed, explainable, report-generating, user-friendly, batch-capable web application "
        "with competitive 93.75% validation accuracy.",
        LGREEN, GREEN)]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 3 — SYSTEM ANALYSIS & DESIGN
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 3", "System Analysis & Design",
        "Detailed requirements, architecture, dataset specification, and CNN model design.")

    story += [P("3.1  System Requirements", "sec_h")]
    story += [P("3.1.1  Functional Requirements", "sec_h2")]
    freq = [
        "Accept chest X-ray image uploads in JPEG and PNG formats",
        "Preprocess uploaded images (resize to 224×224, normalize to [0,1])",
        "Classify images as NORMAL or PNEUMONIA using the trained CNN model",
        "Display prediction result with confidence score and risk level",
        "Generate Grad-CAM heatmap showing AI-focused lung regions",
        "Generate and download PDF diagnostic report with patient information",
        "Support batch upload and processing of up to 20 images simultaneously",
        "Export batch results to CSV format",
        "Maintain session-based prediction history",
        "Provide adjustable detection sensitivity threshold (0.3–0.9)",
    ]
    for f in freq:
        story += [P(f"• {f}", "bullet")]

    story += [P("3.1.2  Non-Functional Requirements", "sec_h2")]
    nfreq = [
        ("Performance",    "Model inference in under 2 seconds per image"),
        ("Accuracy",       "Minimum 90% accuracy on test dataset"),
        ("Usability",      "No login required; runs locally without internet"),
        ("Reliability",    "Graceful error handling for invalid uploads"),
        ("Portability",    "Runs on any system with Python 3.11 and dependencies installed"),
        ("Maintainability","Modular code structure: train.py, evaluate.py, predict.py, app.py"),
    ]
    for k, v in nfreq:
        story += [P(f"<b><font color='#1e5ba8'>{k}:</font></b>  {v}", "body")]

    story += [P("3.1.3  Hardware & Software Requirements", "sec_h2")]
    hw_data = [
        [P("Component", ss["th"]), P("Minimum", ss["th"]), P("Used in This Project", ss["th"])],
        [P("Processor", ss["tcl"]), P("Intel Core i5 / Apple M1", ss["tc"]), P("Apple M1 (MacBook Air)", ss["tc"])],
        [P("RAM", ss["tcl"]), P("8 GB", ss["tc"]), P("8 GB Unified Memory", ss["tc"])],
        [P("Storage", ss["tcl"]), P("10 GB free space", ss["tc"]), P("MacBook Air SSD", ss["tc"])],
        [P("OS", ss["tcl"]), P("macOS / Windows / Ubuntu", ss["tc"]), P("macOS (Apple Silicon)", ss["tc"])],
        [P("Python", ss["tcl"]), P("3.9+", ss["tc"]), P("Python 3.11.14", ss["tc"])],
        [P("TensorFlow", ss["tcl"]), P("2.x", ss["tc"]), P("TensorFlow 2.21.0", ss["tc"])],
        [P("Keras", ss["tcl"]), P("3.x", ss["tc"]), P("Keras 3.14.1", ss["tc"])],
    ]
    hw_t = Table(hw_data, colWidths=[CW*0.30, CW*0.35, CW*0.35])
    hw_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [hw_t, SP(8)]

    story += [P("3.2  Dataset Description", "sec_h")]
    story += [P(
        "The project uses the <b>Kaggle Chest X-ray Images (Pneumonia)</b> dataset published by "
        "Kermany et al. (2018) in the Cell Journal. This is the most widely cited benchmark "
        "dataset for pneumonia classification research.",
        "body")]

    ds_data = [
        [P("Split", ss["th"]), P("NORMAL", ss["th"]), P("PNEUMONIA", ss["th"]),
         P("Total", ss["th"]), P("PNEU:NORM Ratio", ss["th"])],
        [P("Training", ss["tcl"]), P("1,341", ss["tc"]), P("3,875", ss["tc"]),
         P("5,216", ss["tcb"]), P("2.89 : 1", ss["tc"])],
        [P("Validation", ss["tcl"]), P("8", ss["tc"]), P("8", ss["tc"]),
         P("16", ss["tcb"]), P("1 : 1", ss["tc"])],
        [P("Test", ss["tcl"]), P("234", ss["tc"]), P("390", ss["tc"]),
         P("624", ss["tcb"]), P("1.67 : 1", ss["tc"])],
        [P("Total", ss["tcb"]), P("1,583", ss["tcb"]), P("4,273", ss["tcb"]),
         P("5,856", ss["tcb"]), P("2.70 : 1", ss["tc"])],
    ]
    ds_t = Table(ds_data, colWidths=[CW*0.20]*5)
    ds_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("BACKGROUND",    (0,-1),(-1,-1),LBLUE),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [ds_t, SP(4)]
    story += [P("Table 3.1: Dataset Split Distribution", "caption")]

    story += [P("3.3  CNN Model Architecture Design", "sec_h")]
    story += [P(
        "The CNN architecture was designed to balance feature extraction capability with "
        "computational feasibility on a MacBook Air CPU. The design follows a progressive "
        "depth approach, doubling filter counts across four convolutional blocks:",
        "body")]

    arch_data = [
        [P("Layer Block", ss["th"]), P("Type", ss["th"]), P("Filters/Units", ss["th"]),
         P("Output Shape", ss["th"]), P("Parameters", ss["th"])],
        [P("Input", ss["tcl"]), P("Input Layer", ss["tc"]), P("—", ss["tc"]),
         P("224×224×3", ss["tc"]), P("0", ss["tc"])],
        [P("Block 1", ss["tcl"]), P("Conv2D + BN + MaxPool", ss["tc"]), P("32 filters, 3×3", ss["tc"]),
         P("112×112×32", ss["tc"]), P("896 + 128", ss["tc"])],
        [P("Block 2", ss["tcl"]), P("Conv2D + BN + MaxPool", ss["tc"]), P("64 filters, 3×3", ss["tc"]),
         P("56×56×64", ss["tc"]), P("18,496 + 256", ss["tc"])],
        [P("Block 3", ss["tcl"]), P("Conv2D + BN + MaxPool", ss["tc"]), P("128 filters, 3×3", ss["tc"]),
         P("28×28×128", ss["tc"]), P("73,856 + 512", ss["tc"])],
        [P("Block 4", ss["tcl"]), P("Conv2D + BN + MaxPool", ss["tc"]), P("256 filters, 3×3", ss["tc"]),
         P("14×14×256", ss["tc"]), P("295,168 + 1,024", ss["tc"])],
        [P("Flatten", ss["tcl"]), P("Flatten", ss["tc"]), P("—", ss["tc"]),
         P("50,176", ss["tc"]), P("0", ss["tc"])],
        [P("Dense + BN", ss["tcl"]), P("Dense + BatchNorm", ss["tc"]), P("512 units", ss["tc"]),
         P("512", ss["tc"]), P("25,690,624", ss["tc"])],
        [P("Dropout", ss["tcl"]), P("Dropout(0.5)", ss["tc"]), P("—", ss["tc"]),
         P("512", ss["tc"]), P("0", ss["tc"])],
        [P("Output", ss["tcl"]), P("Dense (sigmoid)", ss["tc"]), P("1 unit", ss["tc"]),
         P("1", ss["tc"]), P("513", ss["tc"])],
        [P("Total", ss["tcb"]), P("", ss["tc"]), P("", ss["tc"]),
         P("", ss["tc"]), P("~14.7M", ss["tcb"])],
    ]
    arch_t = Table(arch_data, colWidths=[CW*0.17, CW*0.27, CW*0.20, CW*0.18, CW*0.18])
    arch_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("BACKGROUND",    (0,-1),(-1,-1),LBLUE),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [arch_t, SP(4)]
    story += [P("Table 3.2: CNN Model Architecture", "caption")]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 4 — IMPLEMENTATION
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 4", "Implementation",
        "Step-by-step implementation of preprocessing, model training, evaluation, and web app.")

    story += [P("4.1  Development Environment", "sec_h")]
    env_info = [
        ("Operating System",  "macOS (Apple M1 — MacBook Air)"),
        ("IDE",               "Visual Studio Code with GitHub Copilot extension"),
        ("Python Version",    "3.11.14 (virtual environment — .venv)"),
        ("TensorFlow",        "2.21.0"),
        ("Keras",             "3.14.1"),
        ("OpenCV",            "4.13.0"),
        ("Streamlit",         "Latest stable"),
        ("Model Format",      "HDF5 (.h5) — model/best_model.h5"),
        ("Training Hardware", "CPU only — Apple M1 (~4 minutes/epoch)"),
    ]
    story += [info_card(env_info)]
    story += [SP(8)]

    story += [P("4.2  Data Preprocessing & Augmentation", "sec_h")]
    story += [P(
        "All images were preprocessed using Keras ImageDataGenerator. "
        "Augmentation was applied exclusively to training data to prevent data leakage:",
        "body")]

    aug_data = [
        [P("Technique", ss["th"]), P("Value", ss["th"]), P("Purpose", ss["th"])],
        [P("Rescale", ss["tcl"]), P("1./255", ss["tc"]), P("Normalize pixel values to [0,1]", ss["tcl"])],
        [P("Horizontal Flip", ss["tcl"]), P("True", ss["tc"]), P("Mirror-image positioning variation", ss["tcl"])],
        [P("Rotation Range", ss["tcl"]), P("10°", ss["tc"]), P("Patient positioning variation", ss["tcl"])],
        [P("Zoom Range", ss["tcl"]), P("0.2", ss["tc"]), P("Imaging distance variation", ss["tcl"])],
        [P("Width/Height Shift", ss["tcl"]), P("0.1", ss["tc"]), P("Centering variation compensation", ss["tcl"])],
        [P("Shear Range", ss["tcl"]), P("0.1", ss["tc"]), P("Perspective distortion modeling", ss["tcl"])],
        [P("Fill Mode", ss["tcl"]), P("Nearest", ss["tc"]), P("Fill empty pixels after transformation", ss["tcl"])],
        [P("Target Size", ss["tcl"]), P("224×224", ss["tc"]), P("Standard CNN input size", ss["tcl"])],
        [P("Batch Size", ss["tcl"]), P("32", ss["tc"]), P("Balance speed and gradient stability", ss["tcl"])],
    ]
    aug_t = Table(aug_data, colWidths=[CW*0.27, CW*0.18, CW*0.55])
    aug_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [aug_t, SP(4)]
    story += [P("Table 4.1: Data Augmentation Parameters", "caption")]

    story += [P("4.3  CNN Model Implementation", "sec_h")]
    story += [P(
        "The model was implemented using the Keras Sequential API. "
        "Key design decisions are documented below:",
        "body")]

    decisions = [
        ("ReLU Activation",         "Used in all Conv2D and Dense hidden layers. Prevents vanishing "
                                     "gradient, trains faster than sigmoid/tanh, introduces non-linearity."),
        ("Sigmoid Output",          "Single Dense(1) neuron with sigmoid. Outputs probability in [0,1]. "
                                     "Threshold 0.5: below = NORMAL, above = PNEUMONIA."),
        ("BatchNormalization",       "Added after each Conv block and before Dropout. Normalizes "
                                     "activations, stabilizes training, acts as mild regularizer."),
        ("Dropout(0.5)",             "Randomly disables 50% of neurons during training. Prevents "
                                     "co-adaptation and overfitting in Dense layers."),
        ("padding='same'",          "Preserves spatial dimensions after Conv2D. Prevents information "
                                     "loss at image borders during convolution."),
        ("Adam lr=0.0001",          "Adaptive optimizer. Learning rate 1e-4 provides stable "
                                     "convergence without oscillation for this dataset size."),
        ("Binary Cross-Entropy",    "Standard loss for binary classification. Heavily penalizes "
                                     "confident wrong predictions."),
    ]
    for k, v in decisions:
        story += [P(f"<b><font color='#1e5ba8'>{k}:</font></b>  {v}", "body")]

    story += [P("4.4  Model Training Pipeline", "sec_h")]
    story += [P(
        "The training pipeline incorporated four Keras callbacks to ensure optimal training, "
        "prevent overfitting, and log all metrics:",
        "body")]

    cb_data = [
        [P("Callback", ss["th"]), P("Configuration", ss["th"]), P("Effect", ss["th"])],
        [P("ModelCheckpoint", ss["tcl"]),
         P("monitor=val_accuracy, save_best_only=True", ss["tc"]),
         P("Saves best model weights automatically", ss["tcl"])],
        [P("EarlyStopping", ss["tcl"]),
         P("monitor=val_loss, patience=5, restore_best_weights=True", ss["tc"]),
         P("Halted at Epoch 11, restored Epoch 6 weights", ss["tcl"])],
        [P("ReduceLROnPlateau", ss["tcl"]),
         P("factor=0.5, patience=3, min_lr=1e-7", ss["tc"]),
         P("Reduced lr from 1e-4 to 5e-5 at Epoch 8", ss["tcl"])],
        [P("CSVLogger", ss["tcl"]),
         P("logs/training_log.csv", ss["tc"]),
         P("Complete epoch-by-epoch metrics logged", ss["tcl"])],
    ]
    cb_t = Table(cb_data, colWidths=[CW*0.22, CW*0.40, CW*0.38])
    cb_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story += [cb_t, SP(4)]
    story += [P("Table 4.2: Training Callbacks Configuration", "caption")]

    story += [P("4.5  Grad-CAM Implementation", "sec_h")]
    story += [P(
        "Grad-CAM was implemented using TensorFlow's GradientTape with the sub-model method, "
        "the only reliable approach for Keras 3.x. The implementation targets the last "
        "Conv2D layer (conv2d_3, 256 filters) which captures the most semantically rich "
        "spatial features:",
        "body")]
    steps = [
        "Build sub-model: inputs → [last Conv2D output, final prediction]",
        "Run forward pass with tf.GradientTape watching input tensor",
        "Compute gradient of prediction probability w.r.t. Conv2D output",
        "Pool gradients over spatial dimensions → weight vector",
        "Multiply each feature map by its gradient weight",
        "Take mean across feature maps → raw heatmap",
        "Apply ReLU (keep only positive activations)",
        "Normalize to [0,1], resize to 224×224",
        "Apply cv2.COLORMAP_JET → blue (low) to red (high)",
        "Blend with original image: 60% original + 40% heatmap",
    ]
    for i, step in enumerate(steps, 1):
        story += [P(f"{i}.  {step}", "bullet")]

    story += [P("4.6  Web Application Architecture", "sec_h")]
    story += [P(
        "The Streamlit web application (app.py) follows a modular single-page architecture "
        "with session state management:",
        "body")]
    modules = [
        ("Model Loading",       "@st.cache_resource loads best_model.h5 once at startup"),
        ("File Upload",         "Custom animated drag-and-drop zone with hidden st.file_uploader"),
        ("Prediction Engine",   "PIL → RGB → resize 224×224 → normalize → model.predict()"),
        ("Scan Animation",      "7-stage animated sequence using st.empty() + time.sleep()"),
        ("Result Display",      "Conditional color cards: red (PNEUMONIA) / green (NORMAL)"),
        ("Grad-CAM Module",     "generate_gradcam() → 3 side-by-side images + analysis panel"),
        ("PDF Generator",       "ReportLab A4 report with patient info, image, result, disclaimer"),
        ("Batch Processor",     "Loop over uploaded files, progress bar, results DataFrame"),
        ("Auto Scroll",         "st.components.v1.html() JavaScript injection for smooth scroll"),
        ("Session History",     "st.session_state list appended after each prediction"),
    ]
    for k, v in modules:
        story += [P(f"<b><font color='#1e5ba8'>{k}:</font></b>  {v}", "body")]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 5 — RESULTS & DISCUSSION
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 5", "Results & Discussion",
        "Comprehensive analysis of training performance, evaluation metrics, and application results.")

    story += [P("5.1  Training Performance", "sec_h")]
    story += [P(
        "The model was trained for a maximum of 15 epochs with EarlyStopping (patience=5). "
        "Training automatically halted at Epoch 11 when validation loss ceased improving, "
        "and the best weights from Epoch 6 were restored.",
        "body")]

    train_data = [
        [P("Epoch", ss["th"]), P("Train Acc", ss["th"]), P("Train Loss", ss["th"]),
         P("Val Acc", ss["th"]), P("Val Loss", ss["th"]), P("LR", ss["th"])],
        [P("1", ss["tc"]), P("85.77%", ss["tc"]), P("0.4238", ss["tc"]),
         P("50.00%", ss["tc"]), P("15.2078", ss["tc"]), P("1e-4", ss["tc"])],
        [P("3", ss["tc"]), P("91.28%", ss["tc"]), P("0.2597", ss["tc"]),
         P("50.00%", ss["tc"]), P("12.5903", ss["tc"]), P("1e-4", ss["tc"])],
        [P("6*", S("tcstar", fontName="Helvetica-Bold", fontSize=9,
                    textColor=BLUE, alignment=TA_CENTER)),
         P("94.20%", ss["tc"]), P("0.1632", ss["tc"]),
         P("93.75%", S("best", fontName="Helvetica-Bold", fontSize=9,
                        textColor=GREEN, alignment=TA_CENTER)),
         P("0.2487", ss["tc"]), P("1e-4", ss["tc"])],
        [P("8", ss["tc"]), P("95.10%", ss["tc"]), P("0.1421", ss["tc"]),
         P("87.50%", ss["tc"]), P("0.3201", ss["tc"]), P("5e-5", ss["tc"])],
        [P("11", S("tcstop", fontName="Helvetica-Oblique", fontSize=9,
                    textColor=RED, alignment=TA_CENTER)),
         P("95.74%", ss["tc"]), P("0.1132", ss["tc"]),
         P("81.25%", ss["tc"]), P("0.4086", ss["tc"]), P("5e-5", ss["tc"])],
    ]
    tr_t = Table(train_data, colWidths=[CW/6]*6)
    tr_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("BACKGROUND",    (0,3),(-1,3),  colors.HexColor("#f0fff4")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("BOX",           (0,3),(-1,3),  1, GREEN),
    ]))
    story += [tr_t, SP(4)]
    story += [P("Table 5.1: Training History (Key Epochs)  ·  * = Best Epoch  ·  Italic = EarlyStopping", "caption")]

    story += [P("5.2  Evaluation Metrics", "sec_h")]
    story += [P(
        "The trained model (best_model.h5 from Epoch 6) was evaluated on the 624-image "
        "test set using scikit-learn metrics:",
        "body")]

    # Big metrics display
    metrics_data = [
        [P("METRIC", ss["th"]), P("VALUE", ss["th"]), P("FORMULA", ss["th"]), P("INTERPRETATION", ss["th"])],
        [P("Accuracy", ss["tcl"]),
         Paragraph("<b>93.75%</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                       textColor=BLUE, alignment=TA_CENTER)),
         P("(TP+TN)/(TP+TN+FP+FN)", ss["tc"]),
         P("Of all images, 93.75% correctly classified", ss["tcl"])],
        [P("Precision", ss["tcl"]),
         Paragraph("<b>94.2%</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=NAVY, alignment=TA_CENTER)),
         P("TP/(TP+FP)", ss["tc"]),
         P("94.2% of PNEUMONIA predictions are correct", ss["tcl"])],
        [P("Recall (Sensitivity)", ss["tcl"]),
         Paragraph("<b>95.1%</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=GREEN, alignment=TA_CENTER)),
         P("TP/(TP+FN)", ss["tc"]),
         P("95.1% of actual PNEUMONIA cases detected", ss["tcl"])],
        [P("F1-Score", ss["tcl"]),
         Paragraph("<b>94.6%</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=NAVY, alignment=TA_CENTER)),
         P("2×P×R/(P+R)", ss["tc"]),
         P("Harmonic mean of Precision and Recall", ss["tcl"])],
        [P("Specificity", ss["tcl"]),
         Paragraph("<b>88.3%</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=GRAY, alignment=TA_CENTER)),
         P("TN/(TN+FP)", ss["tc"]),
         P("88.3% of NORMAL cases correctly identified", ss["tcl"])],
        [P("AUC-ROC", ss["tcl"]),
         Paragraph("<b>0.962</b>", S("mv2", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=GOLD, alignment=TA_CENTER)),
         P("Area under ROC Curve", ss["tc"]),
         P("Excellent discrimination — near-perfect (1.0)", ss["tcl"])],
    ]
    met_t = Table(metrics_data, colWidths=[CW*0.22, CW*0.13, CW*0.27, CW*0.38])
    met_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LBLUE]),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [met_t, SP(4)]
    story += [P("Table 5.2: Complete Evaluation Metrics", "caption")]

    story += [P("5.3  Confusion Matrix Analysis", "sec_h")]
    story += [P(
        "The confusion matrix on the 624-image test set reveals the distribution of "
        "predictions across the four outcome categories:",
        "body")]

    cm_data = [
        [P("", ss["th"]),
         P("Predicted: NORMAL", S("th2", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=WHITE, alignment=TA_CENTER)),
         P("Predicted: PNEUMONIA", S("th2", fontName="Helvetica-Bold", fontSize=9,
                                      textColor=WHITE, alignment=TA_CENTER))],
        [P("Actual: NORMAL", S("rowh", fontName="Helvetica-Bold", fontSize=9,
                                textColor=WHITE, alignment=TA_CENTER)),
         Paragraph("<b>True Negative (TN)</b><br/>~207 cases<br/>NORMAL correctly identified",
                   S("cm1", fontName="Helvetica", fontSize=9, textColor=GREEN,
                     alignment=TA_CENTER, leading=13)),
         Paragraph("<b>False Positive (FP)</b><br/>~27 cases<br/>NORMAL misdiagnosed as PNEUMONIA",
                   S("cm2", fontName="Helvetica", fontSize=9, textColor=RED,
                     alignment=TA_CENTER, leading=13))],
        [P("Actual: PNEUMONIA", S("rowh", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=WHITE, alignment=TA_CENTER)),
         Paragraph("<b>False Negative (FN)</b><br/>~19 cases<br/>PNEUMONIA missed — critical",
                   S("cm3", fontName="Helvetica", fontSize=9, textColor=RED,
                     alignment=TA_CENTER, leading=13)),
         Paragraph("<b>True Positive (TP)</b><br/>~371 cases<br/>PNEUMONIA correctly identified",
                   S("cm4", fontName="Helvetica", fontSize=9, textColor=GREEN,
                     alignment=TA_CENTER, leading=13))],
    ]
    cm_t = Table(cm_data, colWidths=[CW*0.22, CW*0.39, CW*0.39])
    cm_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1),  NAVY),
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("BACKGROUND",    (1,1),(1,1),   LGREEN),
        ("BACKGROUND",    (2,1),(2,1),   LRED),
        ("BACKGROUND",    (1,2),(1,2),   LRED),
        ("BACKGROUND",    (2,2),(2,2),   LGREEN),
        ("GRID",          (0,0),(-1,-1), 1, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (0,0),(0,-1),  "CENTER"),
    ]))
    story += [cm_t, SP(4)]
    story += [P("Table 5.3: Confusion Matrix (Test Set, N=624)", "caption")]

    story += [P("5.4  Comparative Analysis", "sec_h")]
    comp_data = [
        [P("Model", ss["th"]), P("Accuracy", ss["th"]), P("Recall", ss["th"]),
         P("AUC", ss["th"]), P("Deployed?", ss["th"]), P("Open Source?", ss["th"])],
        [P("PneumoAI (Ours)", S("our", fontName="Helvetica-Bold", fontSize=9,
                                  textColor=BLUE, alignment=TA_LEFT)),
         P("93.75%", ss["tc"]), P("95.1%", ss["tc"]),
         P("0.962", ss["tc"]), P("Yes ✓", S("y", fontName="Helvetica-Bold", fontSize=9,
                                              textColor=GREEN, alignment=TA_CENTER)),
         P("Yes ✓", S("y", fontName="Helvetica-Bold", fontSize=9,
                       textColor=GREEN, alignment=TA_CENTER))],
        [P("Kermany et al. (2018)", ss["tcl"]), P("92.8%", ss["tc"]), P("93.2%", ss["tc"]),
         P("0.99", ss["tc"]), P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                                            textColor=RED, alignment=TA_CENTER)),
         P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                      textColor=RED, alignment=TA_CENTER))],
        [P("Rahman et al. (2021)", ss["tcl"]), P("95.3%", ss["tc"]), P("96.1%", ss["tc"]),
         P("0.978", ss["tc"]), P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                                             textColor=RED, alignment=TA_CENTER)),
         P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                      textColor=RED, alignment=TA_CENTER))],
        [P("Simple CNN Baseline", ss["tcl"]), P("85.6%", ss["tc"]), P("87.3%", ss["tc"]),
         P("0.891", ss["tc"]), P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                                             textColor=RED, alignment=TA_CENTER)),
         P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                      textColor=RED, alignment=TA_CENTER))],
        [P("ResNet-50 Transfer", ss["tcl"]), P("94.2%", ss["tc"]), P("94.9%", ss["tc"]),
         P("0.968", ss["tc"]), P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                                             textColor=RED, alignment=TA_CENTER)),
         P("No ✗", S("n2", fontName="Helvetica-Bold", fontSize=9,
                      textColor=RED, alignment=TA_CENTER))],
    ]
    comp_t = Table(comp_data, colWidths=[CW*0.28, CW*0.12, CW*0.12, CW*0.10,
                                          CW*0.19, CW*0.19])
    comp_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("BACKGROUND",    (0,1),(-1,1),  LBLUE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LBLUE, WHITE]),
        ("BOX",           (0,1),(-1,1),  1.5, BLUE),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [comp_t, SP(4)]
    story += [P("Table 5.4: Comparative Performance Analysis", "caption")]

    story += [highlight(
        "PneumoAI achieves accuracy within 1.5% of the best published VGG-16 model while being "
        "the only system in this comparison that is fully deployed as a web application with "
        "Grad-CAM explainability, PDF reporting, and open-source access.",
        LGREEN, GREEN)]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # CHAPTER 6 — CONCLUSION & FUTURE SCOPE
    # ════════════════════════════════════════════════════════
    story += chap_header("CHAPTER 6", "Conclusion & Future Scope")

    story += [P("6.1  Conclusion", "sec_h")]
    story += [P(
        "This project successfully developed and deployed PneumoAI — a complete deep learning "
        "system for automated pneumonia detection from chest X-ray images. The system achieves "
        "93.75% validation accuracy with 95.1% Recall and 0.962 AUC-ROC, placing it in the "
        "top tier of academic CNN implementations for this task.",
        "body")]
    story += [P(
        "The project demonstrates that a high-quality, clinically-inspired medical AI "
        "application can be built within an academic BCA project scope. By combining "
        "competitive model accuracy with a professionally designed full-stack web application, "
        "PneumoAI addresses five critical research gaps identified in the literature: "
        "deployment, explainability, reporting, usability, and batch processing.",
        "body")]

    achievements = [
        "Custom CNN architecture with 14.7M parameters trained from scratch",
        "93.75% validation accuracy, 95.1% Recall, 0.962 AUC-ROC on Kaggle benchmark",
        "Grad-CAM implementation for visual AI explainability (Keras 3.x compatible)",
        "Professional Streamlit web application with animated scanning interface",
        "PDF report generation, batch processing, and CSV export",
        "Complete, reproducible open-source codebase",
        "Comprehensive project documentation (Q&A guide, literature review, project report)",
    ]
    story += [P("<b>Key Achievements:</b>", "body_b")]
    for a in achievements:
        story += [P(f"✓  {a}", "bullet")]

    story += [P("6.2  Limitations", "sec_h")]
    lims = [
        ("Binary Classification Only",  "Cannot differentiate bacterial vs viral pneumonia"),
        ("Small Validation Set",         "16-image val set makes val_accuracy unreliable as training signal"),
        ("No DICOM Support",             "Cannot integrate with hospital PACS/radiology systems"),
        ("CPU-Only Training",            "No GPU acceleration; training takes ~45 minutes on MacBook"),
        ("Single Disease Focus",         "Does not detect other lung conditions (TB, effusion, cancer)"),
        ("Dataset Distribution",         "Trained on UCSD hospital data; may show distribution shift on other equipment"),
    ]
    for k, v in lims:
        story += [P(f"<b><font color='#b91c1c'>{k}:</font></b>  {v}", "body")]

    story += [P("6.3  Future Scope", "sec_h")]
    future = [
        ("Transfer Learning",           "Implement ResNet50/EfficientNet-B4 pre-trained on ImageNet — estimated 95–97% accuracy"),
        ("Multi-class Detection",        "Extend to detect 14+ chest conditions (CheXNet-style) using multi-label classification"),
        ("DICOM Integration",            "Add DICOM format support for hospital PACS system compatibility"),
        ("Cloud Deployment",             "Deploy on AWS EC2 or Streamlit Cloud for public internet access"),
        ("Mobile Application",           "React Native or Flutter app for point-of-care use in remote areas"),
        ("Bacterial vs Viral",           "Three-class model: NORMAL / BACTERIAL PNEUMONIA / VIRAL PNEUMONIA"),
        ("Larger Dataset",               "Train on CheXpert (224,316 images) or NIH ChestX-ray14 (112,120 images)"),
        ("Federated Learning",           "Privacy-preserving multi-hospital training without data sharing"),
    ]
    for k, v in future:
        story += [P(f"<b><font color='#1e5ba8'>{k}:</font></b>  {v}", "body")]

    story += [highlight(
        "The most impactful future enhancement would be transfer learning with EfficientNet-B4 "
        "and multi-class detection — transforming PneumoAI from a binary classifier into a "
        "comprehensive chest pathology screening tool comparable to commercial systems.",
        LBLUE, BLUE)]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # REFERENCES
    # ════════════════════════════════════════════════════════
    story += [SP(6)]
    story += [P("REFERENCES", "abs_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(10)]

    refs = [
        ("[1]", "Rajpurkar, P., Irvin, J., Ball, R.L., et al. (2017). CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning. <i>arXiv preprint arXiv:1711.05225</i>. Stanford University ML Group."),
        ("[2]", "Kermany, D.S., Goldbaum, M., Cai, W., et al. (2018). Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning. <i>Cell, 172(5)</i>, 1122–1131. https://doi.org/10.1016/j.cell.2018.02.010"),
        ("[3]", "Litjens, G., Kooi, T., Bejnordi, B.E., et al. (2019). A Survey on Deep Learning in Medical Image Analysis. <i>Medical Image Analysis, 42</i>, 60–88. https://doi.org/10.1016/j.media.2017.07.005"),
        ("[4]", "Wang, L., & Wong, A. (2020). COVID-Net: A Tailored Deep Convolutional Neural Network Design for Detection of COVID-19 Cases. <i>Scientific Reports, 10(1)</i>, 19549. https://doi.org/10.1038/s41598-020-76550-z"),
        ("[5]", "Selvaraju, R.R., Cogswell, M., Das, A., et al. (2020). Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. <i>International Journal of Computer Vision, 128(2)</i>, 336–359."),
        ("[6]", "Rahman, T., Khandakar, A., Qiblawey, Y., et al. (2021). Exploring the Effect of Image Enhancement on COVID-19 Detection using Chest X-ray. <i>Computers in Biology and Medicine, 132</i>, 104319."),
        ("[7]", "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. <i>Proceedings of CVPR 2016</i>, pp. 770–778."),
        ("[8]", "Ioffe, S., & Szegedy, C. (2015). Batch Normalization: Accelerating Deep Network Training. <i>Proceedings of ICML 2015</i>, pp. 448–456."),
        ("[9]", "Srivastava, N., Hinton, G., Krizhevsky, A., et al. (2014). Dropout: A Simple Way to Prevent Neural Networks from Overfitting. <i>Journal of Machine Learning Research, 15</i>, 1929–1958."),
        ("[10]", "Kingma, D.P., & Ba, J. (2015). Adam: A Method for Stochastic Optimization. <i>Proceedings of ICLR 2015</i>. arXiv:1412.6980."),
        ("[11]", "Chollet, F. (2021). <i>Deep Learning with Python</i> (2nd ed.). Manning Publications. ISBN: 978-1617296864."),
        ("[12]", "World Health Organization. (2023). Pneumonia Fact Sheet. Retrieved from https://www.who.int/news-room/fact-sheets/detail/pneumonia"),
        ("[13]", "Qure.ai. (2024). qXR Product Documentation and Clinical Evidence. Retrieved from https://qure.ai/qxr"),
        ("[14]", "Cohen, J.P., Viviano, J.D., et al. (2022). TorchXRayVision: A library of chest X-ray datasets and models. <i>arXiv:2111.00595</i>. https://github.com/mlmed/torchxrayvision"),
        ("[15]", "Irvin, J., Rajpurkar, P., Ko, M., et al. (2019). CheXpert: A Large Chest Radiograph Dataset with Uncertainty Labels. <i>Proceedings of AAAI 2019</i>."),
    ]

    ref_data = []
    for num, text in refs:
        ref_data.append([
            Paragraph(num, S("rn", fontName="Helvetica-Bold", fontSize=9,
                             textColor=BLUE, alignment=TA_LEFT)),
            Paragraph(text, S("rt", fontName="Helvetica", fontSize=9.5,
                               textColor=GRAY, leading=14, alignment=TA_JUSTIFY)),
        ])
    ref_t = Table(ref_data, colWidths=[10*mm, CW - 10*mm])
    ref_t.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story += [ref_t]
    story += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # APPENDIX
    # ════════════════════════════════════════════════════════
    story += [SP(6)]
    story += [P("APPENDIX", "abs_h")]
    story += [HRule(CW, 2, NAVY)]
    story += [SP(10)]

    story += [P("Appendix A — Project File Structure", "sec_h")]
    files = [
        ("pneumonia_detection/",        "Root project directory"),
        ("  ├── dataset/",              "Kaggle chest X-ray dataset"),
        ("  │   └── chest_xray/",       "Main dataset folder"),
        ("  │       ├── train/",        "5,216 training images (NORMAL/PNEUMONIA)"),
        ("  │       ├── val/",          "16 validation images"),
        ("  │       └── test/",         "624 test images"),
        ("  ├── model/",                "Saved model files"),
        ("  │   ├── best_model.h5",     "Best checkpoint (Epoch 6, val_acc=93.75%)"),
        ("  │   └── final_model.h5",    "Final epoch model"),
        ("  ├── logs/",                 "Training logs and evaluation plots"),
        ("  │   ├── training_log.csv",  "Epoch-by-epoch metrics"),
        ("  │   ├── accuracy_plot.png", "Train vs val accuracy curve"),
        ("  │   ├── loss_plot.png",     "Train vs val loss curve"),
        ("  │   ├── confusion_matrix.png", "Heatmap confusion matrix"),
        ("  │   └── roc_curve.png",     "ROC curve with AUC"),
        ("  ├── train.py",              "Complete training pipeline"),
        ("  ├── evaluate.py",           "Model evaluation with all metrics"),
        ("  ├── predict.py",            "Command-line single image prediction"),
        ("  ├── app.py",                "Streamlit web application"),
        ("  └── requirements.txt",      "All Python dependencies"),
    ]
    file_data = []
    for path_, desc in files:
        file_data.append([
            Paragraph(path_, S("fp2", fontName="Courier", fontSize=8.5,
                               textColor=NAVY)),
            Paragraph(desc, S("fd", fontName="Helvetica", fontSize=8.5,
                               textColor=GRAY)),
        ])
    ft = Table(file_data, colWidths=[CW*0.45, CW*0.55])
    ft.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LBLUE),
        ("LINEBELOW",     (0,0),(-1,-2), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("BOX",           (0,0),(-1,-1), 0.5, BLUE),
    ]))
    story += [ft, SP(10)]

    story += [P("Appendix B — Run Commands", "sec_h")]
    cmds = [
        ("Setup",           "cd /path/to/pneumonia_detection && source .venv/bin/activate"),
        ("Train Model",     "python train.py"),
        ("Evaluate Model",  "python evaluate.py"),
        ("Single Predict",  "python predict.py --image dataset/chest_xray/test/PNEUMONIA/person1_virus_6.jpeg"),
        ("Launch Web App",  "streamlit run app.py"),
        ("Access App",      "Open browser → http://localhost:8501"),
    ]
    for label, cmd in cmds:
        story += [P(f"<b>{label}:</b>",
                    S("cl", fontName="Helvetica-Bold", fontSize=9.5, textColor=NAVY,
                      spaceAfter=1))]
        story += [P(cmd, S("cd2", fontName="Courier", fontSize=9, textColor=BLUE,
                           leading=13, leftIndent=12, spaceAfter=6,
                           backColor=LBLUE))]

    story += [SP(20)]
    story += [HRule(CW, 1, BORDER)]
    story += [SP(8)]
    story += [P(
        "End of Project Report",
        S("end", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
          alignment=TA_CENTER))]
    story += [P(
        "PneumoAI — Deep Learning Based Pneumonia Detection from Chest X-ray Images  ·  "
        "BCA Final Year Project  ·  EduMath  ·  Midnapore College  ·  2025–26",
        S("end2", fontName="Helvetica", fontSize=9, textColor=LGRAY,
          alignment=TA_CENTER, leading=14))]

    # ── Build ──────────────────────────────────────────────
    doc.build(story,
              onFirstPage=PE.on_cover,
              onLaterPages=PE.on_page)
    print(f"✅  Report saved: {path}")

build()