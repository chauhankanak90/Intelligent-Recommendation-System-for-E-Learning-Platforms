# pdf_export.py
from fpdf import FPDF


def generate_roadmap_pdf(student_name: str, target_role: str, analysis: dict = None, roadmap: list = None) -> bytes:
    """Converts student profile analysis + roadmap into a professional, cleanly formatted PDF.
    Returns raw PDF bytes suitable for st.download_button.
    """
    analysis = analysis or {}
    roadmap = roadmap or []

    def safe_text(txt):
        if not txt:
            return ""
        # Convert unicode characters/emojis gracefully to avoid PDF generation errors
        return str(txt).encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Brand Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(37, 99, 235)  # Professional Royal Blue (#2563eb)
    pdf.cell(0, 10, safe_text("Personalized AI Career & Learning Roadmap"), ln=True)

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 116, 139)  # Slate dim
    pdf.cell(0, 6, safe_text("Intelligent Recommendation System for E-Learning Platforms"), ln=True)
    pdf.ln(4)

    # Student Overview Card
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(10, pdf.get_y(), 190, 24, "DF")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.set_xy(14, pdf.get_y() + 3)
    pdf.cell(90, 6, safe_text(f"Learner: {student_name}"), ln=False)
    pdf.cell(90, 6, safe_text(f"Target Career: {target_role}"), ln=True)

    pdf.set_xy(14, pdf.get_y())
    readiness = analysis.get("readiness_score", "N/A")
    pdf.cell(90, 6, safe_text(f"Market Readiness: {readiness}%"), ln=False)
    pdf.cell(90, 6, safe_text(f"Total Milestones: {len(roadmap)} phases"), ln=True)
    pdf.ln(8)

    # Career Advice / Summary
    career_advice = analysis.get("career_advice", "")
    if career_advice:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 8, safe_text("Mentor Strategic Guidance"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(190, 5.5, safe_text(career_advice), ln=True)
        pdf.ln(4)

    # Two-Column Layout: Missing Skills vs Strengths
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(225, 29, 72)  # Rose / Coral for gaps
    pdf.cell(95, 8, safe_text("Identified Skill Gaps"), ln=False)

    pdf.set_text_color(16, 185, 129)  # Emerald for strengths
    pdf.cell(95, 8, safe_text("Demonstrated Strengths"), ln=True)

    missing = analysis.get("missing_skills", [])
    strengths = analysis.get("strengths", [])
    max_items = max(len(missing), len(strengths), 1)

    pdf.set_font("Helvetica", "", 9.5)
    for i in range(max_items):
        gap_txt = f"- {missing[i]}" if i < len(missing) else ""
        str_txt = f"+ {strengths[i]}" if i < len(strengths) else ""

        pdf.set_text_color(71, 85, 105)
        pdf.cell(95, 6, safe_text(gap_txt[:55]), ln=False)
        pdf.cell(95, 6, safe_text(str_txt[:55]), ln=True)

    pdf.ln(6)

    # Week-by-Week Roadmap
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 9, safe_text("Structured Learning Milestones"), ln=True)
    pdf.ln(2)

    for week in roadmap:
        week_num = week.get("Week", "Milestone")
        title = week.get("Core Milestone", "Technical Focus")
        hours = week.get("Estimated Hours", "")
        header_title = f"{week_num}: {title}"
        if hours:
            header_title += f"  [{hours}]"

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, safe_text(header_title), ln=True)

        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(71, 85, 105)

        syllabus = week.get("Syllabus Breakup", "")
        if syllabus:
            pdf.multi_cell(190, 5, safe_text(f"Concepts / Syllabus: {syllabus}"), ln=True)

        plan = week.get("Daily Allocation Plan", "")
        if plan:
            pdf.multi_cell(190, 5, safe_text(f"Daily Routine: {plan}"), ln=True)

        tasks = week.get("Tasks", "")
        if tasks:
            pdf.multi_cell(190, 5, safe_text(f"Practical Tasks: {tasks}"), ln=True)

        project = week.get("Project", "")
        if project:
            pdf.set_font("Helvetica", "I", 9.5)
            pdf.set_text_color(37, 99, 235)
            pdf.multi_cell(190, 5, safe_text(f"Capstone Project: {project}"), ln=True)

        pdf.ln(3)

    try:
        raw_output = pdf.output(dest="S")
        return bytes(raw_output, "latin-1") if isinstance(raw_output, str) else bytes(raw_output)
    except TypeError:
        return bytes(pdf.output())