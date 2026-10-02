import streamlit as st
import pandas as pd
import json

import gemini
import recommendation as rec
import database as db
import pdf_export
from streamlit_option_menu import option_menu

# ----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Learning & Career Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database schema safely
db.init_db()

# ----------------------------------------------------------------------------
# 2. PREMIUM MODERN AI SAAS THEME (Deep Navy + Royal Blue + Glassmorphism)
# ----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg-main: #080e1a;
        --bg-surface: #0f172a;
        --bg-elevated: #162238;
        --bg-card: rgba(17, 26, 46, 0.85);
        --bg-card-hover: rgba(23, 37, 66, 0.95);
        --border-subtle: rgba(59, 130, 246, 0.16);
        --border-active: rgba(59, 130, 246, 0.45);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --text-faint: #64748b;
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-glow: rgba(37, 99, 235, 0.35);
        --primary-soft: rgba(37, 99, 235, 0.14);
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --emerald-soft: rgba(16, 185, 129, 0.14);
        --accent-rose: #f43f5e;
        --rose-soft: rgba(244, 63, 94, 0.14);
        --accent-amber: #f59e0b;
        --amber-soft: rgba(245, 158, 11, 0.14);
        --radius-xl: 18px;
        --radius-lg: 14px;
        --radius-md: 10px;
        --radius-sm: 6px;
        --shadow-subtle: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 25px rgba(37, 99, 235, 0.2);
    }

    /* Base Typography & Canvas */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 10%, #0d1b33 0%, #080e1a 45%, #050912 100%) !important;
        color: var(--text-main);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-main) !important;
        letter-spacing: -0.025em;
    }

    p, span, label, div {
        color: var(--text-main);
    }

    /* Subtle Glassmorphic Scrollbars */
    ::-webkit-scrollbar { width: 7px; height: 7px; }
    ::-webkit-scrollbar-track { background: var(--bg-main); }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* ---------------- Sidebar Redesign ---------------- */
    [data-testid="stSidebar"] {
        background-color: #0b1324 !important;
        border-right: 1px solid rgba(59, 130, 246, 0.12) !important;
    }

    .sidebar-brand-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.6rem 0.2rem 1.2rem 0.2rem;
    }

    .sidebar-brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 800;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45);
    }

    .sidebar-brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        line-height: 1.2;
        color: #f8fafc;
    }

    .sidebar-brand-sub {
        font-size: 0.76rem;
        color: var(--text-muted);
        margin-top: 2px;
    }

    .sidebar-status-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.16);
        border-radius: var(--radius-md);
        padding: 0.85rem 1rem;
        margin-top: 1.2rem;
        font-size: 0.82rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* ---------------- Hero Section & Animations ---------------- */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(16, 26, 48, 0.95) 0%, rgba(13, 21, 38, 0.85) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-xl);
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.8rem;
        box-shadow: var(--shadow-subtle), var(--shadow-glow);
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.28) 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #93c5fd !important;
        background: rgba(37, 99, 235, 0.16);
        border: 1px solid rgba(59, 130, 246, 0.35);
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 0.9rem;
    }

    .hero-badge::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #60a5fa;
        box-shadow: 0 0 8px #60a5fa;
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        line-height: 1.25;
        margin: 0.2rem 0 0.8rem 0;
        background: linear-gradient(135deg, #ffffff 30%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        font-size: 0.96rem;
        color: var(--text-muted);
        max-width: 820px;
        line-height: 1.6;
        margin-bottom: 1.2rem;
    }

    .hero-feature-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 0.8rem;
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        color: #cbd5e1;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 4px 10px;
        border-radius: var(--radius-sm);
    }

    /* ---------------- Metrics & KPI Cards ---------------- */
    div[data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.2rem 1.3rem !important;
        box-shadow: var(--shadow-subtle) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: var(--border-active) !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #60a5fa !important;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* ---------------- SaaS Input Cards & Forms ---------------- */
    div.stForm {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: 2rem 2.2rem !important;
        box-shadow: var(--shadow-subtle) !important;
    }

    /* Text inputs & text areas */
    .stTextInput input, .stTextArea textarea {
        background: #0b1324 !important;
        border: 1px solid rgba(59, 130, 246, 0.22) !important;
        color: #f8fafc !important;
        border-radius: var(--radius-md) !important;
        font-size: 0.92rem !important;
        padding: 0.55rem 0.8rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }

    /* Selectbox: style the control but do NOT add padding (it hides the value) */
    .stSelectbox [data-baseweb="select"] > div {
        background: #0b1324 !important;
        border: 1px solid rgba(59, 130, 246, 0.22) !important;
        border-radius: var(--radius-md) !important;
        min-height: 44px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stSelectbox [data-baseweb="select"] > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }

    /* Make sure the selected value is visible */
    .stSelectbox [data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] input {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        font-size: 0.92rem !important;
    }

    /* Dropdown list (rendered in a portal outside .stSelectbox) */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background: #0f172a !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="popover"] li:hover {
        background: #162238 !important;
    }

    .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stRadio label {
        color: #cbd5e1 !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.35rem !important;
    }

    /* Slider accent */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #3b82f6 !important;
        border: 2px solid #ffffff !important;
    }

    div[data-testid="stSlider"] > div > div > div > div {
        background: linear-gradient(90deg, #2563eb, #06b6d4) !important;
    }

    /* ---------------- Modern Buttons ---------------- */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding: 0.65rem 1.4rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    .stDownloadButton > button {
        background: rgba(37, 99, 235, 0.12) !important;
        color: #60a5fa !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background: rgba(37, 99, 235, 0.22) !important;
        border-color: #60a5fa !important;
        transform: translateY(-1px) !important;
    }

    /* ---------------- Chips, Badges & Cards ---------------- */
    .saas-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-subtle);
    }

    .mentor-quote-card {
        background: linear-gradient(135deg, rgba(22, 34, 58, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 4px solid #3b82f6;
        border-radius: var(--radius-lg);
        padding: 1.3rem 1.5rem;
        margin: 1.2rem 0;
        font-size: 0.95rem;
        line-height: 1.65;
        color: #e2e8f0;
    }

    .mentor-quote-card b {
        color: #93c5fd;
        font-size: 0.98rem;
    }

    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 5px 12px;
        margin: 3px 5px 4px 0;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        border: 1px solid;
    }

    .badge-gap {
        background: var(--rose-soft);
        color: #fda4af !important;
        border-color: rgba(244, 63, 94, 0.35);
    }
    .badge-gap::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #f43f5e;
    }

    .badge-strength {
        background: var(--emerald-soft);
        color: #6ee7b7 !important;
        border-color: rgba(16, 185, 129, 0.35);
    }
    .badge-strength::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10b981;
    }

    /* ---------------- Status & Fallback Banners ---------------- */
    .banner-fallback {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-left: 4px solid #f59e0b;
        color: #fde68a !important;
        padding: 0.95rem 1.25rem;
        border-radius: var(--radius-md);
        margin: 1.2rem 0;
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .banner-busy {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-left: 4px solid #3b82f6;
        color: #bfdbfe !important;
        padding: 0.95rem 1.25rem;
        border-radius: var(--radius-md);
        margin: 1.2rem 0;
        font-size: 0.9rem;
        line-height: 1.55;
    }

    /* ---------------- Timeline Roadmap Cards ---------------- */
    .timeline-milestone-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .timeline-milestone-card:hover {
        border-color: var(--border-active);
        transform: translateX(3px);
    }

    .milestone-week-tag {
        display: inline-block;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        color: #60a5fa;
        background: rgba(37, 99, 235, 0.18);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        margin-bottom: 0.4rem;
    }

    .milestone-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.4rem;
    }

    .milestone-detail-row {
        font-size: 0.88rem;
        color: var(--text-muted);
        margin-top: 0.45rem;
        line-height: 1.5;
    }

    .milestone-detail-row b {
        color: #cbd5e1;
    }

    .resource-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.2rem 1.3rem;
        margin-bottom: 0.9rem;
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .resource-card:hover {
        border-color: var(--border-active);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    }

    /* ---------------- Chat Styling Polish ---------------- */
    [data-testid="stChatMessage"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.8rem 1rem !important;
        margin-bottom: 0.8rem !important;
    }

    [data-testid="stChatInput"] {
        background: #0b1324 !important;
        border: 1px solid var(--border-active) !important;
        border-radius: var(--radius-lg) !important;
    }

    div[data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }

    hr {
        border-color: rgba(59, 130, 246, 0.12) !important;
        margin: 1.8rem 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & PERSISTENCE
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-icon">✦</div>
            <div>
                <div class="sidebar-brand-title">Career Studio AI</div>
                <div class="sidebar-brand-sub">Intelligent E-Learning Mentor</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Robust option menu with synchronized fallback
    menu_options = ["Dashboard & Roadmap", "Interactive Quiz", "AI Doubts Chatbot"]
    default_idx = 0
    if st.session_state.get("active_menu") in menu_options:
        default_idx = menu_options.index(st.session_state["active_menu"])

    selected_menu = option_menu(
        menu_title=None,
        options=menu_options,
        icons=["speedometer2", "lightning-charge", "chat-square-dots"],
        default_index=default_idx,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "0.95rem"},
            "nav-link": {
                "font-size": "0.91rem",
                "border-radius": "8px",
                "margin": "4px 0",
                "color": "#94a3b8",
                "font-weight": "500",
                "--hover-color": "#131d33",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
                "color": "#ffffff",
                "font-weight": "600",
                "box-shadow": "0 4px 14px rgba(37, 99, 235, 0.35)",
            },
        },
    )

    # Guarantee selected_menu is never None or blank
    if not selected_menu:
        selected_menu = st.session_state.get("active_menu", "Dashboard & Roadmap")
    st.session_state["active_menu"] = selected_menu

    st.markdown("<hr style='margin: 1.2rem 0 !important;'>", unsafe_allow_html=True)

    # API Configuration Status indicator
    api_ready = gemini.is_configured()
    if api_ready:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #10b981; padding: 4px 0;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                <span>AI Service Connected</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #f59e0b; padding: 4px 0;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; display: inline-block;"></span>
                <span>Offline / Safe Mode</span>
            </div>
        """, unsafe_allow_html=True)

    # Saved Profiles Loader (SQLite)
    try:
        recent_profiles = db.get_recent_profiles(limit=5)
    except Exception:
        recent_profiles = []

    if recent_profiles:
        with st.expander("Saved Profiles", expanded=False):
            for p in recent_profiles:
                p_name = p.get("name", "Student")
                p_goal = p.get("goal", "Goal")
                if st.button(f"{p_name} ({p_goal})", key=f"load_prof_{p.get('id')}", use_container_width=True):
                    st.session_state.current_student = p_name
                    st.session_state.student_id = p.get("id")
                    try:
                        an_data = json.loads(p.get("analysis_json") or "{}")
                        rm_data = json.loads(p.get("roadmap_json") or "[]")
                        if not isinstance(rm_data, list):
                            rm_data = []
                        st.session_state.profile_data = {
                            "profile_analysis": an_data,
                            "roadmap": rm_data,
                            "source": "database",
                        }
                        st.session_state.form_name = p_name
                        st.session_state.form_goal = p_goal
                        st.session_state.form_skills = p.get("skills", "")
                        st.session_state.form_level = p.get("level", "Beginner")
                        st.session_state.form_study_time = int(p.get("study_time") or 2)
                        st.rerun()
                    except Exception:
                        st.caption("Could not parse saved roadmap.")

    st.markdown("""
        <div class="sidebar-status-card">
            <b>Pro-Tip:</b> Update your daily hours and skills anytime to regenerate a dynamic, tailored milestone plan.
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 4. TAB 1 — DASHBOARD & CAREER ROADMAP
# ----------------------------------------------------------------------------
if selected_menu == "Dashboard & Roadmap":
    # Hero Banner
    st.markdown("""
        <div class="hero-container">
            <span class="hero-badge">AI-Powered Career Intelligence</span>
            <h1 class="hero-title">Architect Your Future in Tech</h1>
            <p class="hero-description">
                Diagnose critical skill gaps, generate actionable week-by-week roadmaps, and match directly with
                top-tier curated courses engineered around your personal time commitment.
            </p>
            <div class="hero-feature-pills">
                <span class="hero-pill">⚡ Precision Gap Analysis</span>
                <span class="hero-pill">🗺️ Structured Milestones</span>
                <span class="hero-pill">🎯 Smart Course Matching</span>
                <span class="hero-pill">📄 PDF Export Ready</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Default session state initialization
    st.session_state.setdefault("profile_data", None)
    st.session_state.setdefault("current_student", "Aman Kumar")
    st.session_state.setdefault("student_id", None)
    st.session_state.setdefault("form_name", "Aman Kumar")
    st.session_state.setdefault("form_goal", "Data Scientist")
    st.session_state.setdefault("form_skills", "Python, Basic SQL, Excel")
    st.session_state.setdefault("form_level", "Beginner")
    st.session_state.setdefault("form_study_time", 2)
    st.session_state.setdefault("form_timeline", 12)

    # Career Profile Form
    st.markdown("### Step 1: Tell Us About Your Career Ambitions")
    st.caption("Provide your current technical standing so our AI engine can benchmark your profile against industry standards.")

    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Full Name", value=st.session_state.form_name, placeholder="e.g. Aman Kumar")
            target_role = st.text_input("Target Career Goal", value=st.session_state.form_goal, placeholder="e.g. Data Scientist, Full Stack Developer")
            level_options = ["Beginner", "Intermediate", "Advanced"]
            lvl_idx = level_options.index(st.session_state.form_level) if st.session_state.form_level in level_options else 0
            level = st.selectbox("Current Professional Level", level_options, index=lvl_idx)
        with col2:
            current_skills = st.text_area(
                "Known Skills & Tools (comma separated)",
                value=st.session_state.form_skills,
                placeholder="e.g. Python, SQL, Git, Excel, Pandas",
                height=98,
            )
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                timeline_weeks = st.slider("Roadmap Duration (Weeks)", min_value=4, max_value=16, value=st.session_state.form_timeline)
            with sub_col2:
                study_time = st.slider("Daily Study Commitment (Hours)", min_value=1, max_value=8, value=st.session_state.form_study_time)

        submit_profile = st.form_submit_button("✦ Generate Personalized Learning Path", use_container_width=True)

    if submit_profile:
        if not user_name.strip() or not target_role.strip():
            st.warning("Please provide both your name and target career goal.")
        else:
            with st.spinner("Analyzing profile against live industry benchmarks & drafting roadmap..."):
                raw_response = gemini.generate_career_roadmap(
                    user_name=user_name,
                    target_role=target_role,
                    current_skills=current_skills,
                    timeline_weeks=timeline_weeks,
                    level=level,
                    study_time=study_time,
                )
                try:
                    data = json.loads(raw_response)
                    st.session_state.profile_data = data
                    st.session_state.current_student = user_name
                    st.session_state.form_name = user_name
                    st.session_state.form_goal = target_role
                    st.session_state.form_skills = current_skills
                    st.session_state.form_level = level
                    st.session_state.form_study_time = study_time
                    st.session_state.form_timeline = timeline_weeks

                    # Persist to SQLite database
                    student_id = db.save_student_profile(
                        user_name, "N/A", "N/A", current_skills, target_role, level, study_time
                    )
                    db.save_roadmap(
                        student_id,
                        json.dumps(data.get("profile_analysis", {})),
                        json.dumps(data.get("roadmap", [])),
                    )
                    st.session_state.student_id = student_id

                    if data.get("source") == "fallback":
                        err_cat = data.get("error_category", "SERVICE_UNAVAILABLE")
                        if err_cat == "SERVICE_UNAVAILABLE":
                            st.info("AI service is temporarily busy. We've switched to a fallback mode. Please try again shortly.")
                        elif err_cat == "QUOTA_EXCEEDED":
                            st.info("AI usage limit reached for the current API configuration. Switched to offline estimate.")
                        elif err_cat == "AUTH_ERROR":
                            st.info("Gemini API authentication failed. Switched to offline estimate. Please check your local API configuration.")
                        else:
                            st.info("Switched to offline estimate mode.")
                    else:
                        st.success("Personalized roadmap generated successfully!")
                except Exception as e:
                    st.error("Failed to parse analysis data. Switched to safe offline estimate.")
                    st.session_state.profile_data = None

    # Render Skill Gap Analysis & Roadmap when data is available
    if st.session_state.get("profile_data"):
        res = st.session_state.profile_data
        analysis = res.get("profile_analysis", {})
        roadmap_list = res.get("roadmap", [])
        if not isinstance(roadmap_list, list):
            roadmap_list = []

        is_fallback = res.get("source") == "fallback"

        if is_fallback:
            friendly_err = analysis.get("career_advice") or "AI service is currently operating in offline estimate mode."
            st.markdown(f"""
                <div class="banner-fallback">
                    <b>Notice:</b> {friendly_err}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ---------------- Section 3: Skill Gap Analysis ----------------
        st.markdown("### Step 2: Skill Gap & Market Readiness Audit")
        st.caption("Detailed diagnostics benchmarking your profile against current industry expectations.")

        # KPI Metrics Row
        readiness_score = int(analysis.get("readiness_score", 0))
        missing_skills = analysis.get("missing_skills", [])
        strengths = analysis.get("strengths", [])
        weaknesses = analysis.get("weaknesses", [])

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Market Readiness", f"{readiness_score}%", help="Skill overlap score against top market benchmarks")
        with m2:
            st.metric("Identified Skill Gaps", f"{len(missing_skills)} Critical", help="Crucial competencies needed for the target role")
        with m3:
            st.metric("Total Milestones", f"{len(roadmap_list)} Phases", help="Structured phases in your personalized path")

        # Two-Column Chips Display
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Identified Skill Gaps")
            if missing_skills:
                gaps_html = "".join(f'<span class="badge-chip badge-gap">{g}</span>' for g in missing_skills)
                st.markdown(gaps_html, unsafe_allow_html=True)
            else:
                st.markdown("_No critical gaps identified._")

        with c2:
            st.markdown("#### Verified Strengths")
            if strengths:
                strengths_html = "".join(f'<span class="badge-chip badge-strength">{s}</span>' for s in strengths)
                st.markdown(strengths_html, unsafe_allow_html=True)
            else:
                st.markdown("_No prior verified strengths submitted._")

        # Areas to watch / Bottlenecks
        if weaknesses:
            st.write("")
            st.markdown("#### Strategic Areas to Watch")
            for w in weaknesses:
                st.markdown(f"- ⚠️ {w}")

        # AI Mentor Executive Advice Card
        career_advice = analysis.get("career_advice", "")
        if career_advice and not is_fallback:
            st.markdown(f"""
                <div class="mentor-quote-card">
                    <b>✦ AI Mentor's Strategic Guidance:</b><br>
                    {career_advice}
                </div>
            """, unsafe_allow_html=True)

        # ---------------- Section 4: Recommended Resources ----------------
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Step 3: Curated Course Recommendations")
        st.caption("Precision-matched using our fuzzy-similarity catalog engine to address your identified skill gaps.")

        course_recs = rec.get_recommendations(missing_skills)
        if course_recs:
            # Modern SaaS Card Grid
            grid_cols = st.columns(min(len(course_recs), 3))
            for idx, course in enumerate(course_recs):
                col_target = grid_cols[idx % 3]
                with col_target:
                    platform_name = course.get("Platform", "Online")
                    st.markdown(f"""
                        <div class="resource-card">
                            <div>
                                <span class="hero-pill" style="font-size:0.74rem; margin-bottom: 0.5rem; display: inline-block;">
                                    {platform_name} • {course.get('Confidence', 'Matched')}
                                </span>
                                <h4 style="font-size: 1.02rem; margin: 0.3rem 0; line-height: 1.35;">{course.get('Course Title', '')}</h4>
                                <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 0.3rem;">
                                    <b>Target Skill:</b> <span style="color:#60a5fa;">{course.get('Skill Gap', '')}</span>
                                </div>
                                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">
                                    Provider: {course.get('Provider / Creator', 'Online Instructor')}
                                </div>
                            </div>
                            <div style="margin-top: 1rem;">
                                <a href="{course.get('Resource Link', '#')}" target="_blank" style="
                                    display: inline-flex; align-items: center; gap: 6px;
                                    font-size: 0.86rem; font-weight: 600; color: #3b82f6 !important;
                                    text-decoration: none; padding: 6px 12px; border-radius: 6px;
                                    background: rgba(37, 99, 235, 0.12); border: 1px solid rgba(59, 130, 246, 0.3);
                                ">
                                    Open Resource ↗
                                </a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.write("")

            # Optional Tabular View for deep sorting
            with st.expander("View Full Recommendations Table", expanded=False):
                df_recs = pd.DataFrame(course_recs)
                st.dataframe(
                    df_recs,
                    column_config={
                        "Skill Gap": "Target Skill",
                        "Matched Category": "Catalog Match",
                        "Confidence": "Match Confidence",
                        "Course Title": "Course Title",
                        "Platform": "Platform",
                        "Provider / Creator": "Provider",
                        "Resource Link": st.column_config.LinkColumn("Direct Link", display_text="Launch"),
                    },
                    hide_index=True,
                    use_container_width=True,
                )
        else:
            st.success("No critical skill gaps identified — your profile matches standard requirements.")

        # ---------------- Section 5: Week-by-Week Learning Roadmap ----------------
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Step 4: Week-by-Week Learning Timeline")
        st.caption("A sequential, milestone-driven curriculum engineered to build your mastery incrementally.")

        if roadmap_list:
            student_id = st.session_state.get("student_id")
            progress_map = db.get_week_progress(student_id) if student_id else {}

            completed_count = 0
            for idx, week in enumerate(roadmap_list):
                week_label = week.get("Week") or f"Week {idx + 1}"
                milestone_title = week.get("Core Milestone", "Technical Foundations")
                syllabus = week.get("Syllabus Breakup", "Concepts & hands-on exercises")
                daily_plan = week.get("Daily Allocation Plan", f"{study_time} hours hands-on coding")
                tasks = week.get("Tasks", f"Complete exercises for {milestone_title}")
                est_hours = week.get("Estimated Hours", f"{study_time * 7} hrs/week")
                project = week.get("Project", f"Milestone Capstone for {week_label}")

                is_done = st.checkbox(
                    f"**{week_label}** — {milestone_title} ({est_hours})",
                    value=progress_map.get(week_label, False),
                    key=f"chk_week_{week_label}_{idx}",
                )
                if is_done:
                    completed_count += 1
                if student_id and is_done != progress_map.get(week_label, False):
                    db.toggle_week_progress(student_id, week_label, is_done)

                # Milestone Detail Card
                with st.expander(f"Details & Tasks: {week_label}", expanded=False):
                    d_col1, d_col2 = st.columns([3, 2])
                    with d_col1:
                        st.markdown(f"**📚 Syllabus Breakdown:**")
                        st.write(syllabus)
                        st.markdown(f"**🎯 Actionable Tasks:**")
                        st.write(tasks)
                    with d_col2:
                        st.markdown(f"**⏱️ Daily Allocation:**")
                        st.write(daily_plan)
                        st.markdown(f"**🚀 Capstone Project:**")
                        st.info(project)

            # Progress Bar & Milestone Status Badge
            total_weeks = len(roadmap_list)
            pct = int((completed_count / total_weeks) * 100) if total_weeks else 0
            st.write("")
            pcol1, pcol2 = st.columns([3, 1])
            with pcol1:
                st.progress(pct / 100)
                st.caption(f"{completed_count} of {total_weeks} milestones completed ({pct}%)")
            with pcol2:
                if pct >= 100:
                    badge_label = "🏆 Curriculum Completed!"
                elif pct >= 75:
                    badge_label = "🔥 75%+ Advanced Milestone"
                elif pct >= 50:
                    badge_label = "⚡ 50%+ Halfway Milestone"
                elif pct >= 25:
                    badge_label = "🌱 25% Foundations Done"
                else:
                    badge_label = "🚀 Starting Journey"
                st.markdown(f"""
                    <div style="
                        text-align: center; font-weight: 700; font-size: 0.88rem;
                        background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(59, 130, 246, 0.35);
                        color: #93c5fd; padding: 0.6rem 0.8rem; border-radius: 8px;
                    ">
                        {badge_label}
                    </div>
                """, unsafe_allow_html=True)

            # Professional PDF Export
            st.markdown("<hr>", unsafe_allow_html=True)
            pdf_bytes = pdf_export.generate_roadmap_pdf(
                student_name=st.session_state.get("current_student", "Learner"),
                target_role=st.session_state.get("form_goal", target_role),
                analysis=analysis,
                roadmap=roadmap_list,
            )
            st.download_button(
                label="📄 Download Complete Roadmap as PDF",
                data=pdf_bytes,
                file_name=f"{st.session_state.get('current_student', 'career')}_roadmap.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        else:
            st.warning("Roadmap milestones missing from response. Please re-run analysis.")

# ----------------------------------------------------------------------------
# 5. TAB 2 — INTERACTIVE QUIZ GENERATOR
# ----------------------------------------------------------------------------
elif selected_menu == "Interactive Quiz":
    st.markdown("""
        <div class="hero-container">
            <span class="hero-badge">⚡ Practice & Self Assessment</span>
            <h1 class="hero-title">Interactive Technical Quiz</h1>
            <p class="hero-description">
                Challenge your concepts and test your real-time comprehension. Pick any technology or topic
                to generate dynamic, multi-tier evaluation questions.
            </p>
        </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)
    with q_col1:
        quiz_topic = st.text_input("Quiz Topic", value="Python Basics", placeholder="e.g. SQL Joins, Pandas DataFrames, Docker, Neural Networks")
    with q_col2:
        quiz_level = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

    st.session_state.setdefault("current_quiz", None)
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("user_answers", {})

    # Show Quiz History if available
    student_id = st.session_state.get("student_id")
    if student_id:
        try:
            history = db.get_quiz_history(student_id)
        except Exception:
            history = []
        if history:
            with st.expander("Past Quiz Performance", expanded=False):
                df_hist = pd.DataFrame(history)
                df_hist["Score %"] = (df_hist["score"] / df_hist["total"] * 100).round(0)
                st.dataframe(
                    df_hist,
                    column_config={
                        "topic": "Topic",
                        "score": "Score",
                        "total": "Total",
                        "date": "Date",
                        "Score %": st.column_config.ProgressColumn("Proficiency", min_value=0, max_value=100),
                    },
                    hide_index=True,
                    use_container_width=True,
                )

    if st.button("✦ Generate Assessment Quiz", use_container_width=True):
        with st.spinner(f"Generating questions for '{quiz_topic}'..."):
            quiz_result = gemini.get_quiz_questions(quiz_topic, quiz_level)
            if "error" in quiz_result:
                st.warning(f"{quiz_result['error']}")
                st.session_state.current_quiz = None
            else:
                st.session_state.current_quiz = quiz_result.get("quiz", [])
                st.session_state.quiz_submitted = False
                st.session_state.user_answers = {}

    if st.session_state.get("current_quiz"):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Select Your Answers & Submit")

        with st.form("quiz_display_form"):
            for idx, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"##### **Q{idx + 1}: {q.get('question', '')}**")
                options = q.get("options", [])
                user_choice = st.radio(
                    f"Options for Q{idx + 1}",
                    options=options,
                    key=f"quiz_opt_{idx}",
                    label_visibility="collapsed",
                    index=None,
                )
                st.session_state.user_answers[idx] = user_choice
                st.write("")

            submit_answers = st.form_submit_button("Submit Assessment", use_container_width=True)

        if submit_answers:
            unanswered = [i for i, v in st.session_state.user_answers.items() if v is None]
            if unanswered:
                st.warning(f"Please answer all questions before submitting (missing Q{', Q'.join(str(i+1) for i in unanswered)}).")
            else:
                st.session_state.quiz_submitted = True
                correct_count = sum(
                    1 for idx, q in enumerate(st.session_state.current_quiz)
                    if st.session_state.user_answers.get(idx) == q.get("correct_answer")
                )
                total = len(st.session_state.current_quiz)

                if st.session_state.get("student_id"):
                    db.save_quiz_score(st.session_state.student_id, quiz_topic, correct_count, total)

                st.markdown(f"### Final Score: **{correct_count} / {total}**")
                st.progress(correct_count / total)

                if correct_count == total:
                    st.success("🌟 Outstanding! Perfect score achieved.")
                elif correct_count >= total * 0.6:
                    st.info("👍 Good job! Review the explanations below to master the remaining concepts.")
                else:
                    st.warning("⚠️ Review the key concepts and try again to reinforce fundamentals.")

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("#### Answer Key & Explanations")
                for idx, q in enumerate(st.session_state.current_quiz):
                    u_ans = st.session_state.user_answers.get(idx)
                    c_ans = q.get("correct_answer")
                    if u_ans == c_ans:
                        st.markdown(f"**Q{idx + 1}: Correct!** Selected `{u_ans}`")
                    else:
                        st.markdown(f"**Q{idx + 1}: Incorrect.** You selected `{u_ans}`, correct answer is `{c_ans}`")
                    st.caption(f"Explanation: {q.get('explanation', '')}")

# ----------------------------------------------------------------------------
# 6. TAB 3 — AI DOUBTS CHATBOT
# ----------------------------------------------------------------------------
elif selected_menu == "AI Doubts Chatbot":
    st.markdown("""
        <div class="hero-container">
            <span class="hero-badge">💬 24/7 AI Technical Mentor</span>
            <h1 class="hero-title">Instant Doubt Clearing & Mock Prep</h1>
            <p class="hero-description">
                Ask architectural questions, get intuitive analogies for complex concepts, or practice mock interview
                prompts with your dedicated AI Career Mentor.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.setdefault("chat_messages", [])

    # Action Toolbar
    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    with b2:
        if st.session_state.chat_messages:
            chat_md = "\n\n".join(
                f"**{'You' if m['role']=='user' else 'AI Mentor'}:**\n{m['content']}"
                for m in st.session_state.chat_messages
            )
            st.download_button(
                "📥 Export Conversation (Markdown)",
                data=chat_md,
                file_name="ai_mentor_chat.md",
                mime="text/markdown",
                use_container_width=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Friendly empty state with starter prompts
    if not st.session_state.chat_messages:
        st.markdown("""
            <div style="text-align: center; padding: 2rem 1rem; color: #94a3b8;">
                <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">💡</div>
                <h4 style="color: #cbd5e1 !important;">What would you like to explore today?</h4>
                <p style="font-size: 0.9rem; max-width: 500px; margin: 0 auto 1.5rem auto;">
                    Ask anything about system design, Python algorithms, career transitions, or interview prep.
                </p>
            </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🔍 Explain Docker vs Virtual Machines with an analogy", use_container_width=True):
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": "Explain Docker vs Virtual Machines with a simple real-world analogy.",
                })
                with st.spinner("AI Mentor is drafting response..."):
                    reply = gemini.get_chatbot_reply(
                        "Explain Docker vs Virtual Machines with a simple real-world analogy.",
                        st.session_state.chat_messages,
                    )
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()
        with sc2:
            if st.button("📊 Top 5 SQL queries asked in Data Science interviews", use_container_width=True):
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": "What are the top 5 SQL queries or patterns most frequently tested in technical interviews?",
                })
                with st.spinner("AI Mentor is drafting response..."):
                    reply = gemini.get_chatbot_reply(
                        "What are the top 5 SQL queries or patterns most frequently tested in technical interviews?",
                        st.session_state.chat_messages,
                    )
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()

    # Conversation history rendering
    for msg in st.session_state.chat_messages:
        role = msg.get("role", "user")
        with st.chat_message(role):
            st.markdown(msg.get("content", ""))

    # Chat input
    if prompt := st.chat_input("Ask a doubt (e.g. How does gradient descent work? or Mock interview question on Pandas)"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("AI Mentor is thinking..."):
                response_text = gemini.get_chatbot_reply(prompt, st.session_state.chat_messages)
                st.markdown(response_text)

        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})