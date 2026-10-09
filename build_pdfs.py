#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# build_pdfs.py -- forge the Twin Synergy founding documents as PDFs,
#   the format of business protocol: fixed layout, signable, archivable.
#
# EPIGRAPH: "Let all things be done decently and in order." -- 1 Cor. 14:40
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: every founding markdown document converts to a dignified,
#   readable PDF -- title page, headed sections, tables kept whole,
#   thelemic form throughout -- fit to hand to counsel, a bank, or a partner.
# METHOD:    line-based markdown parse (headings, rules, quotes, lists,
#   tables, code, paragraphs with bold/italic/code spans); fpdf2 with
#   DejaVu faces; one PDF per document into pdf/.
# OBSERVATION: run once; eight PDFs land in pdf/.
# RESULT:    the founding set, in the format of business protocol.
#
# MECHANISM: the parser is deliberately small -- the founding docs use a
#   disciplined markdown subset, so a line state-machine suffices. Tables
#   render via fpdf2's table(); long tables may span pages. multi_cell is
#   always followed by ln() (the pen gotcha is respected).
# DOCTRINE:  the PDF is the presentation; the markdown remains the source
#   of truth. Never edit the PDF -- red-pen the markdown and rebuild.
#
# 93 93/93 -- Love is the law, love under will.

"""Forge all Twin Synergy founding documents as PDFs."""

import re
from pathlib import Path

from fpdf import FPDF, XPos, YPos

REPO = Path(__file__).resolve().parent
PDFDIR = REPO / "pdf"

# -- thelemic form ------------------------------------------------------------
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

GOLD = (212, 175, 55)
INDIGO = (21, 8, 38)
INK = (30, 30, 30)
MUTED = (110, 110, 110)

DOCS = [
    ("TWIN-SYNERGY-CONSTITUTION.md", "The Constitution",
     "Twin Synergy Telecommunications"),
    ("NETWORK-INFRASTRUCTURE.md", "Network Infrastructure",
     "Twin Synergy Telecommunications"),
    ("ORGANIZATION.md", "Organization",
     "Twin Synergy Telecommunications"),
    ("TOR-BLOCKCHAIN-ARCHITECTURE.md", "Tor + Blockchain Architecture",
     "Twin Synergy Telecommunications"),
    ("HOLOGRAPHIC-STICKER.md", "The Holographic Sticker",
     "Twin Synergy Telecommunications"),
    ("SERVICES-INTEGRATION.md", "Services Integration",
     "Twin Synergy Telecommunications"),
    ("TOKENOMICS.md", "The Trinity of Tokenomics",
     "Twin Synergy Telecommunications"),
    ("TWIN-SYNERGY-BLUEPRINT.md", "The Master Blueprint",
     "Twin Synergy Telecommunications"),
    ("SIMULATION-REPORT.md", "Simulation Report — Does the Tokenization Hold?",
     "Twin Synergy Telecommunications"),
    ("SECOND-WEAVE.md", "The Second Weave — Eight Closures",
     "Twin Synergy Telecommunications"),
]


class FoundingPDF(FPDF):
    """MECHANISM: footer on every page; the header lives in the title page
    and section heads instead -- quiet pages, loud structure."""

    def footer(self):
        self.set_y(-15)
        self.set_font("Sans", "", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "All Rights Reserved, Without Prejudice",
                  align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 8, f"{self.page_no()}", align="R")


def fonts(pdf: FoundingPDF) -> None:
    """DOCTRINE: DejaVu carries every glyph the docs use -- no tofu boxes."""
    pdf.add_font("Serif", "", SERIF)
    pdf.add_font("Serif", "B", SERIF_B)
    # No Serif italic on this host -- the "I" style falls back to upright
    # rather than tofu. The distinction survives in the markdown source.
    pdf.add_font("Serif", "I", SERIF)
    pdf.add_font("Sans", "", SANS)
    pdf.add_font("Sans", "B", SANS_B)
    pdf.add_font("Mono", "", MONO)


def title_page(pdf: FoundingPDF, title: str, org: str) -> None:
    """The title page: mark, title, house, thelemic form."""
    pdf.add_page()
    pdf.ln(38)
    # the twin rule -- two strokes becoming one
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.4)
    cx = 105
    pdf.line(cx - 40, 62, cx + 40, 62)
    pdf.set_line_width(0.6)
    pdf.line(cx - 40, 66, cx + 40, 66)
    pdf.ln(34)
    pdf.set_text_color(*INDIGO)
    pdf.set_font("Serif", "B", 26)
    pdf.multi_cell(0, 12, org, align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_text_color(*GOLD)
    pdf.set_line_width(0.8)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(6)
    pdf.set_text_color(*INK)
    pdf.set_font("Serif", "", 20)
    pdf.multi_cell(0, 11, title, align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(14)
    pdf.set_text_color(*MUTED)
    pdf.set_font("Sans", "", 10)
    for line in ("Sol in Libra, 2026 e.v.",
                 "Johnathan 'Qasparr' (\u039a\u03b1\u03c3\u03c0\u03ac\u03c1\u03c1) Monroe,",
                 "Keeper of the Secret Treasure",
                 "", "93"):
        pdf.cell(0, 6, line, align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def h2(pdf: FoundingPDF, text: str) -> None:
    pdf.ln(6)
    pdf.set_text_color(*INDIGO)
    pdf.set_font("Serif", "B", 14)
    pdf.multi_cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 60, pdf.get_y())
    pdf.ln(3)


def h3(pdf: FoundingPDF, text: str) -> None:
    pdf.ln(3)
    pdf.set_text_color(*INDIGO)
    pdf.set_font("Serif", "B", 11.5)
    pdf.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def body(pdf: FoundingPDF, text: str, quote: bool = False) -> None:
    """Paragraph with **bold**, *italic*, `code` spans."""
    if quote:
        pdf.set_text_color(80, 80, 80)
        pdf.set_font("Serif", "I", 10)
        x = pdf.get_x()
        pdf.set_x(x + 8)
        # quotes render italic; strip span markers rather than leaking them
        clean = text.replace("**", "").replace("`", "")
        pdf.multi_cell(0, 6, clean, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        return
    pdf.set_text_color(*INK)
    # ☉/☽ live in DejaVu Sans, not Serif -- split them out as Sans spans.
    parts = re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`.+?`|[☉☽])", text)
    pdf.set_font("Serif", "", 10.5)
    x0 = pdf.l_margin
    for part in parts:
        if not part:
            continue
        if part in ("☉", "☽"):
            pdf.set_font("Sans", "", 10.5)
            pdf.write(6, part)
        elif part.startswith("**") and part.endswith("**"):
            pdf.set_font("Serif", "B", 10.5)
            pdf.write(6, part[2:-2])
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            pdf.set_font("Serif", "I", 10.5)
            pdf.write(6, part[1:-1])
        elif part.startswith("`") and part.endswith("`"):
            pdf.set_font("Mono", "", 9.5)
            pdf.write(6, part[1:-1])
        else:
            pdf.set_font("Serif", "", 10.5)
            pdf.write(6, part)
        pdf.set_font("Serif", "", 10.5)
    pdf.ln(7)


def bullet(pdf: FoundingPDF, text: str) -> None:
    pdf.set_text_color(*INK)
    pdf.set_font("Serif", "", 10.5)
    x = pdf.get_x()
    pdf.set_x(x + 6)
    pdf.cell(4, 6, "\u2022")
    pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def codeblock(pdf: FoundingPDF, lines: list) -> None:
    pdf.set_fill_color(245, 245, 240)
    pdf.set_font("Mono", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    for ln_ in lines:
        pdf.set_x(pdf.l_margin + 6)
        pdf.multi_cell(0, 5, ln_ or " ", fill=True,
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


def table(pdf: FoundingPDF, rows: list) -> None:
    """MECHANISM: header row bold on gold tint; cells wrap."""
    if not rows:
        return
    widths = [max(len(c) for c in col) for col in zip(*rows)]
    total = sum(widths) or 1
    avail = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = [max(22, avail * w / total) for w in widths]
    # normalize to available width
    scale = avail / sum(col_w)
    col_w = [w * scale for w in col_w]
    pdf.set_font("Sans", "", 8)
    with pdf.table(col_widths=tuple(col_w), line_height=5.2,
                   text_align="LEFT", v_align="T",
                   first_row_as_headings=True) as tbl:
        for row in rows:
            tr = tbl.row()
            for cell in row:
                tr.cell(cell)
    pdf.ln(4)


def build_one(src: str, title: str, org: str) -> Path:
    """Forge one PDF from one markdown source."""
    pdf = FoundingPDF()
    pdf.set_auto_page_break(True, 20)
    fonts(pdf)
    title_page(pdf, title, org)
    pdf.add_page()

    lines = (REPO / src).read_text(encoding="utf-8").splitlines()
    i, n = 0, len(lines)
    in_code = False
    code_lines: list = []
    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            if in_code:
                codeblock(pdf, code_lines)
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        s = line.strip()
        if not s:
            i += 1
            continue
        if s == "---":
            pdf.ln(2)
            pdf.set_draw_color(*GOLD)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue
        if s.startswith("### "):
            h3(pdf, s[4:].strip())
            i += 1
            continue
        if s.startswith("## "):
            h2(pdf, s[3:].strip())
            i += 1
            continue
        if s.startswith("# "):
            # the doc's own title page already said it -- skip the echo,
            # unless it carries real content beyond the title
            i += 1
            continue
        if s.startswith("> "):
            body(pdf, s[2:].strip(), quote=True)
            i += 1
            continue
        if s.startswith("|") and s.endswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            table(pdf, rows)
            continue
        if re.match(r"^(\d+\.\s+|[-*]\s+)", s):
            bullet(pdf, re.sub(r"^(\d+\.\s+|[-*]\s+)", "", s))
            i += 1
            continue
        # plain paragraph -- gather continuations
        para = [s]
        i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(
                ("#", "---", "|", ">", "```")) and not re.match(
                r"^(\d+\.\s+|[-*]\s+)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        body(pdf, " ".join(para))
    out = PDFDIR / (Path(src).stem + ".pdf")
    pdf.output(str(out))
    return out


def main() -> None:
    PDFDIR.mkdir(exist_ok=True)
    for src, title, org in DOCS:
        out = build_one(src, title, org)
        print(f"forged {out.name} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
