# pdf_export.py
from fpdf import FPDF


def generate_roadmap_pdf(student_name: str, target_role: str, analysis: dict, roadmap: list) -> bytes:
    """Student ke profile analysis + roadmap ko ek clean PDF mein convert karta hai.
    Returns raw PDF bytes — Streamlit ke st.download_button mein directly use ho sakta hai.
    """
    # Safe text handling function taaki special characters PDF ko corrupt na karein
    def safe_text(txt):
        if not txt:
            return ""
        # Emojis aur special quotes/dashes ko standard text se badalna
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    
    # Page settings
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header section
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(67, 56, 202) # Violet/Purple Accent Color
    pdf.cell(0, 12, safe_text("AI Career Roadmap"), ln=True)

    # Student Info block
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, safe_text(f"Student: {student_name}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Target Role: {target_role}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Readiness Score: {analysis.get('readiness_score', 'N/A')}%"), ln=True)
    pdf.ln(4)

    # Missing Skills Section
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(67, 56, 202)
    pdf.cell(0, 10, safe_text("Missing Skills"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    
    missing_skills = analysis.get("missing_skills", [])
    if missing_skills:
        for skill in missing_skills:
            pdf.cell(0, 7, safe_text(f"- {skill}"), ln=True)
    else:
        pdf.cell(0, 7, safe_text("No critical gaps identified!"), ln=True)
    pdf.ln(2)

    # Strengths Section
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(67, 56, 202)
    pdf.cell(0, 10, safe_text("Strengths"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    
    strengths = analysis.get("strengths", [])
    if strengths:
        for s in strengths:
            pdf.cell(0, 7, safe_text(f"- {s}"), ln=True)
    else:
        pdf.cell(0, 7, safe_text("None analyzed yet."), ln=True)
    pdf.ln(6)

    # Roadmap Section Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(67, 56, 202)
    pdf.cell(0, 10, safe_text("Week-by-Week Roadmap"), ln=True)
    pdf.ln(2)

    # Roadmap Content Iteration
    for week in roadmap:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(67, 56, 202)
        week_title = f"{week.get('Week', '')} - {week.get('Core Milestone', '')}"
        pdf.multi_cell(190, 7, safe_text(week_title), ln=True)
        
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 10)
        
        if week.get("Syllabus Breakup"):
            pdf.multi_cell(190, 6, safe_text(f"Syllabus: {week['Syllabus Breakup']}"), ln=True)
        if week.get("Daily Allocation Plan"):
            pdf.multi_cell(190, 6, safe_text(f"Daily Plan: {week['Daily Allocation Plan']}"), ln=True)
        
        pdf.ln(4)

    # Output formatting fallback for safe bytes rendering in Streamlit
    try:
        raw_output = pdf.output(dest='S')
        return bytes(raw_output, 'latin-1') if isinstance(raw_output, str) else bytes(raw_output)
    except TypeError:
        return bytes(pdf.output())