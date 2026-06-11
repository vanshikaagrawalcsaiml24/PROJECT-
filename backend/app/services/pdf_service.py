"""
PDF Report Service.

Generates a clean, simple, and professional PDF report from
a ``ProjectBlueprintResponse`` using ReportLab.
"""

import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas import ProjectBlueprintResponse

logger = logging.getLogger(__name__)

# ── Color palette (Simple, Minimalist, Clean) ─────────────────────────────────
PRIMARY = colors.HexColor("#2d3748")      # Slate gray
ACCENT = colors.HexColor("#4a5568")       # Medium gray
HIGHLIGHT = colors.HexColor("#2b6cb0")    # Deep blue accent for subheadings
LIGHT_BG = colors.HexColor("#f7fafc")     # Warm white background
WHITE = colors.white
TEXT_DARK = colors.HexColor("#1a202c")    # Off-black for text
TEXT_MUTED = colors.HexColor("#718096")   # Slate gray for secondary text


def _build_styles() -> dict:
    """Build and return a dict of ReportLab paragraph styles."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "CustomTitle",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=TEXT_DARK,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=28,
        ),
        "subtitle": ParagraphStyle(
            "CustomSubtitle",
            fontName="Helvetica",
            fontSize=14,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=18,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=TEXT_DARK,
            spaceBefore=14,
            spaceAfter=6,
            leftIndent=0,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=ACCENT,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=TEXT_DARK,
            leading=15,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=TEXT_DARK,
            leading=14,
            leftIndent=14,
            bulletIndent=6,
            spaceAfter=2,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=8,
            textColor=colors.HexColor("#2d3748"),
            backColor=colors.HexColor("#f7fafc"),
            borderColor=colors.HexColor("#e2e8f0"),
            borderWidth=0.5,
            borderPadding=6,
            leading=11,
            leftIndent=8,
            rightIndent=8,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "Meta",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
        ),
    }
    return styles


def _section_header(text: str, styles: dict) -> list:
    """Return a list of flowables for a simple, clean section header."""
    return [
        Spacer(1, 0.4 * cm),
        Paragraph(text, styles["h1"]),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#e2e8f0"), spaceBefore=2, spaceAfter=8),
    ]


def _bullet_list(items: list[str], styles: dict) -> list:
    """Return bullet-point paragraphs for a list of strings."""
    return [
        Paragraph(f"• {item}", styles["bullet"])
        for item in items
        if item
    ]


def _format_code_block(code_text: str, styles: dict) -> Paragraph:
    """Format multiline code text with html line breaks and escape characters."""
    if not code_text:
        return Paragraph("", styles["code"])
        
    html_escaped_lines = []
    lines = code_text.split("\n")
    if len(lines) > 60:
        lines = lines[:60] + ["... (truncated for readability)"]
        
    for line in lines:
        leading_spaces_count = len(line) - len(line.lstrip(' '))
        nbsp_prefix = "&nbsp;" * leading_spaces_count
        escaped_content = line.lstrip(' ').replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_escaped_lines.append(nbsp_prefix + escaped_content)
    
    code_html = "<br/>".join(html_escaped_lines)
    return Paragraph(code_html, styles["code"])


def generate_pdf(blueprint: ProjectBlueprintResponse) -> bytes:
    """
    Generate a clean and simple PDF report from a ``ProjectBlueprintResponse``.

    Parameters
    ----------
    blueprint:
        The fully populated project blueprint.

    Returns
    -------
    bytes
        Raw PDF bytes ready to stream as a file download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"{blueprint.project_idea} — Project Blueprint",
        author="ProjectMentor AI",
    )

    styles = _build_styles()
    story = []

    # ── Cover Page (Minimalist & Clean) ───────────────────────────────────────
    story.append(Spacer(1, 4 * cm))
    
    story.append(Paragraph("PROJECTMENTOR AI", ParagraphStyle(
        "CoverHeader",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=15,
    )))
    
    story.append(HRFlowable(width="30%", thickness=1, color=colors.HexColor("#cccccc"), spaceAfter=20, hAlign="CENTER"))
    
    story.append(Paragraph(blueprint.project_idea, ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=10,
        leading=30,
    )))
    
    story.append(Paragraph("Project Blueprint Report", ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=30,
    )))
    
    story.append(Spacer(1, 2 * cm))
    
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')}",
        styles["meta"],
    ))
    
    if blueprint.metadata:
        meta_text = (
            f"Powered by {blueprint.metadata.provider.title()} | "
            f"Model: {blueprint.metadata.model} | "
            f"Generation Time: {blueprint.metadata.execution_time_seconds:.1f}s"
        )
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(meta_text, styles["meta"]))
        
    story.append(PageBreak())

    # ── 1. Problem Statement ──────────────────────────────────────────────────
    story.extend(_section_header("1. Problem Statement", styles))
    story.append(Paragraph(blueprint.problem_statement or "Not available.", styles["body"]))

    if blueprint.project_overview:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Project Overview", styles["h2"]))
        story.append(Paragraph(blueprint.project_overview, styles["body"]))

    # ── 2. Objectives ─────────────────────────────────────────────────────────
    story.extend(_section_header("2. Objectives", styles))
    story.extend(_bullet_list(blueprint.objectives, styles))

    # ── 3. Target Users ───────────────────────────────────────────────────────
    if blueprint.target_users:
        story.extend(_section_header("3. Target Users", styles))
        story.extend(_bullet_list(blueprint.target_users, styles))

    # ── 4. Key Features ───────────────────────────────────────────────────────
    story.extend(_section_header("4. Key Features", styles))
    story.extend(_bullet_list(blueprint.features, styles))

    # ── 5. Tech Stack ─────────────────────────────────────────────────────────
    story.extend(_section_header("5. Recommended Tech Stack", styles))
    ts = blueprint.tech_stack
    tech_rows = [
        ["Category", "Technologies"],
        ["Frontend", ", ".join(ts.frontend) or "—"],
        ["Backend", ", ".join(ts.backend) or "—"],
        ["Database", ", ".join(ts.database) or "—"],
        ["Deployment", ", ".join(ts.deployment) or "—"],
        ["AI / ML", ", ".join(ts.ai_ml) or "—"],
        ["Dev Tools", ", ".join(ts.devtools) or "—"],
    ]
    tech_table = Table(tech_rows, colWidths=[5 * cm, 12 * cm])
    tech_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_DARK),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(tech_table)

    # ── 6. System Architecture ────────────────────────────────────────────────
    story.extend(_section_header("6. System Architecture", styles))
    story.append(Paragraph(blueprint.architecture or "Not available.", styles["body"]))

    if blueprint.architecture_components:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Architecture Components", styles["h2"]))
        comp_rows = [["Component", "Role"]]
        for comp in blueprint.architecture_components:
            comp_rows.append([comp.name, comp.role])
        comp_table = Table(comp_rows, colWidths=[6 * cm, 11 * cm])
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#cbd5e0")),
        ]))
        story.append(comp_table)

    # ── 7. Database Design ────────────────────────────────────────────────────
    story.extend(_section_header("7. Database Design", styles))

    if blueprint.database:
        db = blueprint.database
        story.append(Paragraph(
            f"<b>Recommended Database:</b> {db.recommended_database} ({db.database_type})",
            styles["body"]
        ))
        if db.design_rationale:
            story.append(Paragraph(db.design_rationale, styles["body"]))
        story.append(Spacer(1, 0.3 * cm))

        for table in db.tables:
            story.append(Paragraph(f"Table: {table.name}", styles["h2"]))
            if table.description:
                story.append(Paragraph(table.description, styles["body"]))
            if table.columns:
                col_rows = [["Column", "Type", "Constraints"]]
                for col in table.columns:
                    col_rows.append([col.name, col.type, col.constraints])
                col_table = Table(col_rows, colWidths=[5 * cm, 5 * cm, 7 * cm])
                col_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_DARK),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#cbd5e0")),
                ]))
                story.append(col_table)
                story.append(Spacer(1, 0.2 * cm))

        if db.relationships:
            story.append(Paragraph("Relationships", styles["h2"]))
            story.extend(_bullet_list(db.relationships, styles))

        if db.sql_schema:
            story.append(Paragraph("SQL Schema (DDL)", styles["h2"]))
            story.append(_format_code_block(db.sql_schema, styles))
    else:
        # Fall back to legacy database_suggestions
        for db_sug in blueprint.database_suggestions:
            story.append(Paragraph(
                f"<b>{db_sug.recommended_db}</b> ({db_sug.database_type}): {db_sug.rationale}",
                styles["body"]
            ))
            story.extend(_bullet_list(db_sug.tables_or_collections, styles))

    # ── 8. API Design ─────────────────────────────────────────────────────────
    story.extend(_section_header("8. API Design", styles))

    if blueprint.apis:
        api = blueprint.apis
        story.append(Paragraph(
            f"<b>Base URL:</b> {api.base_url} | <b>Auth:</b> {api.authentication}",
            styles["body"]
        ))
        story.append(Spacer(1, 0.3 * cm))

        api_rows = [["Method", "Endpoint", "Description", "Auth"]]
        for endpoint in api.apis:
            api_rows.append([
                endpoint.method,
                endpoint.endpoint,
                endpoint.description[:60] + ("..." if len(endpoint.description) > 60 else ""),
                "Yes" if endpoint.auth_required else "No",
            ])
        api_table = Table(api_rows, colWidths=[2 * cm, 5.5 * cm, 7.5 * cm, 2 * cm])
        api_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#cbd5e0")),
        ]))
        story.append(api_table)
    else:
        # Fall back to legacy api_suggestions
        api_rows = [["Method", "Endpoint", "Description"]]
        for api_sug in blueprint.api_suggestions:
            api_rows.append([api_sug.method, api_sug.endpoint, api_sug.description])
        if len(api_rows) > 1:
            api_table = Table(api_rows, colWidths=[2.5 * cm, 6 * cm, 8.5 * cm])
            api_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_DARK),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#cbd5e0")),
            ]))
            story.append(api_table)

    # ── 9. Development Roadmap ────────────────────────────────────────────────
    story.extend(_section_header("9. Development Roadmap", styles))

    if blueprint.roadmap:
        rm = blueprint.roadmap
        story.append(Paragraph(
            f"<b>Duration:</b> {rm.total_duration} | <b>Team:</b> {rm.team_size} | "
            f"<b>Methodology:</b> {rm.methodology}",
            styles["body"]
        ))
        story.append(Spacer(1, 0.3 * cm))
        for week in rm.roadmap:
            story.append(Paragraph(
                f"Week {week.week}: {week.theme}", styles["h2"]
            ))
            story.extend(_bullet_list(week.tasks, styles))
            if week.milestone:
                story.append(Paragraph(
                    f"Milestone: {week.milestone}",
                    styles["body"]
                ))
            story.append(Spacer(1, 0.15 * cm))
    else:
        # Fall back to legacy development_roadmap
        for phase in blueprint.development_roadmap:
            story.append(Paragraph(f"{phase.phase} ({phase.duration})", styles["h2"]))
            story.extend(_bullet_list(phase.tasks, styles))

    # ── 10. Future Scope ──────────────────────────────────────────────────────
    story.extend(_section_header("10. Future Scope", styles))
    story.extend(_bullet_list(blueprint.future_scope, styles))

    # ── 11. System Diagrams ───────────────────────────────────────────────────
    if blueprint.diagrams or blueprint.mermaid_diagram:
        story.extend(_section_header("11. System Diagrams", styles))
        
        # Architecture Diagram
        if blueprint.diagrams and blueprint.diagrams.architecture_diagram:
            diag = blueprint.diagrams.architecture_diagram
            story.append(Paragraph(f"<b>{diag.title or 'System Architecture Diagram'}</b>", styles["h2"]))
            story.append(_format_code_block(diag.mermaid, styles))
            story.append(Spacer(1, 0.3 * cm))
        elif blueprint.mermaid_diagram:
            story.append(Paragraph("<b>System Architecture Diagram</b>", styles["h2"]))
            story.append(_format_code_block(blueprint.mermaid_diagram, styles))
            story.append(Spacer(1, 0.3 * cm))
            
        # Data Flow Diagram
        if blueprint.diagrams and blueprint.diagrams.data_flow_diagram:
            diag = blueprint.diagrams.data_flow_diagram
            story.append(Paragraph(f"<b>{diag.title or 'Data Flow Diagram'}</b>", styles["h2"]))
            story.append(_format_code_block(diag.mermaid, styles))
            story.append(Spacer(1, 0.3 * cm))
            
        # Entity Relationship Diagram
        if blueprint.diagrams and blueprint.diagrams.er_diagram:
            diag = blueprint.diagrams.er_diagram
            story.append(Paragraph(f"<b>{diag.title or 'Entity Relationship Diagram'}</b>", styles["h2"]))
            story.append(_format_code_block(diag.mermaid, styles))
            story.append(Spacer(1, 0.3 * cm))
            
        # Sequence Diagram
        if blueprint.diagrams and blueprint.diagrams.sequence_diagram:
            diag = blueprint.diagrams.sequence_diagram
            story.append(Paragraph(f"<b>{diag.title or 'Sequence Diagram'}</b>", styles["h2"]))
            story.append(_format_code_block(diag.mermaid, styles))
            story.append(Spacer(1, 0.3 * cm))



    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Paragraph(
        f"Generated by ProjectMentor AI | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["meta"]
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info("PDF generated | size=%d bytes", len(pdf_bytes))
    return pdf_bytes
