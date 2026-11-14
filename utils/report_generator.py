
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)
from xml.sax.saxutils import escape

from models.schemas import SkillMatchResult


def generate_ats_report(
    result: SkillMatchResult,
    score: float
) -> bytes:
    """Generate an ATS skill-match PDF report."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=(612, 792),
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeadingCustom",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#1E40AF"),
            spaceBefore=18,
            spaceAfter=10,
        )
    )

    story = []

    # ---------- Header ----------
    story.append(
        Paragraph("SKILLMATCH AI", styles["ReportTitle"])
    )

    story.append(
        Paragraph(
            "Resume Skill Compatibility Report",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))

    generated_at = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"Generated on: {generated_at}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 24))

    # ---------- Score ----------
    story.append(
        Paragraph(
            "Skill Match Score",
            styles["SectionHeadingCustom"]
        )
    )

    story.append(
        Paragraph(
            f"<b>{score:.1f}%</b>",
            styles["Title"]
        )
    )

    matched_count = len(result.matched)
    unmatched_count = len(result.unmatched)
    total_count = matched_count + unmatched_count

    # ---------- Summary Table ----------
    summary_data = [
        ["Metric", "Value"],
        ["Matched Skills", str(matched_count)],
        ["Missing Skills", str(unmatched_count)],
        ["Total Required Skills", str(total_count)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.5 * inch, 2.0 * inch]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F1F5F9")
            ]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1),
             0.3, colors.HexColor("#CBD5E1")),
        ])
    )

    story.append(summary_table)

    # ---------- Skill Sections ----------
    def add_skill_section(title, skills):
        story.append(
            Paragraph(
                title,
                styles["SectionHeadingCustom"]
            )
        )

        if not skills:
            story.append(
                Paragraph("None identified.", styles["Normal"])
            )
            return

        items = [
            ListItem(
                Paragraph(escape(skill), styles["Normal"])
            )
            for skill in skills
        ]

        story.append(
            ListFlowable(
                items,
                bulletType="bullet",
                leftIndent=20
            )
        )

    add_skill_section("Matched Skills", result.matched)
    add_skill_section("Missing Skills", result.unmatched)

    # ---------- Disclaimer ----------
    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "<b>Important:</b> This report measures "
            "skill coverage against the job description. "
            "It is not a comprehensive ATS evaluation "
            "or a prediction of hiring success.",
            styles["Normal"]
        )
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
