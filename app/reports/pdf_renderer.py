from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PAGE_WIDTH, _PAGE_HEIGHT = LETTER
MARGIN = 0.55 * inch
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)


def _register_fonts() -> tuple[str, str]:
    """Use Arial on Windows when available so Unicode abstracts render cleanly."""
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        try:
            pdfmetrics.registerFont(TTFont("Arial", str(regular)))
            pdfmetrics.registerFont(TTFont("Arial-Bold", str(bold)))
            return "Arial", "Arial-Bold"
        except Exception:
            pass
    return "Helvetica", "Helvetica-Bold"


BASE_FONT, BOLD_FONT = _register_fonts()


def _styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=sample["Title"],
            fontName=BOLD_FONT,
            fontSize=18,
            leading=22,
            spaceAfter=12,
            alignment=TA_LEFT,
        ),
        "h2": ParagraphStyle(
            "ReportH2",
            parent=sample["Heading2"],
            fontName=BOLD_FONT,
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "ReportH3",
            parent=sample["Heading3"],
            fontName=BOLD_FONT,
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=sample["BodyText"],
            fontName=BASE_FONT,
            fontSize=8.5,
            leading=11,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "ReportBullet",
            parent=sample["BodyText"],
            fontName=BASE_FONT,
            fontSize=8.5,
            leading=11,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=3,
        ),
        "table": ParagraphStyle(
            "ReportTable",
            parent=sample["BodyText"],
            fontName=BASE_FONT,
            fontSize=7,
            leading=8.5,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=sample["BodyText"],
            fontName=BOLD_FONT,
            fontSize=7,
            leading=8.5,
        ),
    }


def _inline_text(markdown_text: str) -> str:
    text = markdown_text.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return escape(text)


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_table_separator(line: str) -> bool:
    cells = _split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def _table_story(table_lines: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    rows: list[list[Paragraph]] = []
    for index, line in enumerate(table_lines):
        if _is_table_separator(line):
            continue
        style = styles["table_header"] if index == 0 else styles["table"]
        rows.append([Paragraph(_inline_text(cell), style) for cell in _split_table_row(line)])

    column_count = max((len(row) for row in rows), default=1)
    for row in rows:
        while len(row) < column_count:
            row.append(Paragraph("", styles["table"]))

    table = Table(
        rows,
        colWidths=[CONTENT_WIDTH / column_count] * column_count,
        repeatRows=1 if rows else 0,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _paragraph_from_lines(lines: list[str], styles: dict[str, ParagraphStyle]) -> Paragraph:
    text = " ".join(line.strip() for line in lines)
    return Paragraph(_inline_text(text), styles["body"])


def _build_story(markdown_text: str) -> list:
    styles = _styles()
    story: list = []
    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    index = 0

    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and _is_table_separator(lines[index + 1]):
            table_lines = [stripped, lines[index + 1].strip()]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            story.extend([_table_story(table_lines, styles), Spacer(1, 8)])
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(_inline_text(stripped[2:]), styles["title"]))
            index += 1
            continue

        if stripped.startswith("## "):
            story.append(Paragraph(_inline_text(stripped[3:]), styles["h2"]))
            index += 1
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(_inline_text(stripped[4:]), styles["h3"]))
            index += 1
            continue

        if stripped.startswith("#### "):
            story.append(Paragraph(_inline_text(stripped[5:]), styles["h3"]))
            index += 1
            continue

        if stripped.startswith("- "):
            story.append(Paragraph("• " + _inline_text(stripped[2:]), styles["bullet"]))
            index += 1
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            next_line = lines[index].strip()
            if (
                not next_line
                or next_line.startswith("#")
                or next_line.startswith("- ")
                or next_line.startswith("|")
            ):
                break
            paragraph_lines.append(next_line)
            index += 1
        story.append(_paragraph_from_lines(paragraph_lines, styles))

    return story


def render_pdf_from_markdown(
    markdown_text: str,
    output_path: Path,
) -> Path:
    """Convert a Markdown report to a PDF file with pure-Python ReportLab."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    story = _build_story(markdown_text)
    if not story:
        story = [Paragraph("No report content.", _styles()["body"])]

    try:
        document = SimpleDocTemplate(
            str(output_path),
            pagesize=LETTER,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            title="Safety Review Brief",
        )
        document.build(story)
    except Exception as exc:
        raise RuntimeError(f"PDF rendering failed: {exc}") from exc

    return output_path
