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
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ----------------------------------------------------------------------------
# 2. GLOBAL STYLING — "Bluish-Black" Theme + Highlighting Key Features
# ----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #0b0e14;
        --bg-raised: #111723;
        --bg-card: #161f30;
        --border: #233148;
        --border-soft: #1b263b;
        --text: #f1f5f9;
        --text-dim: #94a3b8;
        --text-faint: #64748b;
        --accent: #3b82f6;
        --accent-strong: #2563eb;
        --accent-glow: rgba(59, 130, 246, 0.4);
        --accent-ink: #ffffff;
        --accent-soft: rgba(59, 130, 246, 0.15);
        --highlight-gold: #f59e0b;
        --highlight-gold-soft: rgba(245, 158, 11, 0.15);
        --clay: #f43f5e;
        --clay-soft: rgba(244, 63, 94, 0.15);
        --sage: #10b981;
        --sage-soft: rgba(16, 185, 129, 0.15);
        --radius-lg: 14px;
        --radius-md: 10px;
        --radius-sm: 7px;
        --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    p, span, label, h3, h4, h5, .stMarkdown {
        color: var(--text) !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-faint) !important;
    }

    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; font-weight: 600; letter-spacing: -0.02em; }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    a { color: var(--accent) !important; }
    *:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

    /* ---------------- Sidebar ---------------- */
    [data-testid="stSidebar"] {
        background-color: var(--bg-raised) !important;
        border-right: 1px solid var(--border);
    }
    .sidebar-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 0.15rem; }
    .sidebar-logo-mark {
        width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #ffffff; font-size: 1rem;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
    }
    .sidebar-logo-text { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.05rem; color: #fff; line-height: 1.2; }
    .sidebar-logo-sub { font-size: 0.75rem; color: var(--text-faint); margin-top: 1px; }
    .sidebar-tip {
        background: var(--accent-soft); border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: var(--radius-sm); padding: 0.75rem 0.9rem; font-size: 0.85rem;
        color: var(--text-dim) !important; line-height: 1.55;
    }

    /* ---------------- Hero Banner with Dynamic Accent Lighting ---------------- */
    .hero-banner {
        position: relative;
        background: linear-gradient(135deg, #111a2e 0%, #16243d 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 2.1rem 2.2rem;
        margin-bottom: 1.7rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 180px; height: 180px;
        background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Highlight Labels */
    .hero-label-highlight {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.82rem; font-weight: 700; 
        color: #60a5fa !important;
        background: rgba(59, 130, 246, 0.18);
        border: 1px solid rgba(59, 130, 246, 0.4);
        padding: 4px 12px;
        border-radius: 999px;
        text-transform: uppercase; 
        letter-spacing: 0.06em;
        margin-bottom: 0.8rem;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
    }

    /* ---------------- Metrics ---------------- */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.05rem 1.25rem;
        box-shadow: var(--shadow-card);
    }
    div[data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif !important; font-size: 1.8rem; font-weight: 700; color: #60a5fa !important; }
    div[data-testid="stMetricLabel"] { color: var(--text-faint) !important; font-size: 0.82rem !important; }

    /* ---------------- Forms & Inputs ---------------- */
    div.stForm {
        border-radius: var(--radius-lg);
        background: var(--bg-card);
        padding: 1.8rem;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--border);
    }
    .stTextInput label, .stSelectbox label, .stTextArea label, .stSlider label, .stRadio label {
        color: var(--text-dim) !important; font-size: 0.85rem !important; font-weight: 500 !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
        background: var(--bg-raised) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius-sm) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }
    div[data-baseweb="slider"] div[role="slider"] { background-color: var(--accent) !important; }
    div[data-testid="stSlider"] > div > div > div > div { background: var(--accent) !important; }

    /* ---------------- Buttons ---------------- */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        border-radius: var(--radius-sm);
        border: none;
        padding: 0.65rem 0;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    .stButton > button p { color: #ffffff !important; font-weight: 600; }
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-radius: var(--radius-sm);
        font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 600;
    }
    .stDownloadButton > button:hover { background: var(--accent-soft) !important; }
    .stDownloadButton > button p { color: var(--accent) !important; }

    /* ---------------- Cards, Chips & Banners ---------------- */
    .info-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: var(--radius-md);
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        line-height: 1.65;
        color: var(--text-dim) !important;
    }
    .info-card b { color: #60a5fa !important; }

    .chip {
        display: inline-flex; align-items: center; gap: 7px;
        border-radius: 999px; padding: 5px 13px; margin: 3px 4px 3px 0;
        font-size: 0.85rem; font-weight: 500; border: 1px solid;
    }
    .chip::before { content: ''; width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .gap-pill { background: var(--clay-soft); color: #fca5a5 !important; border-color: rgba(244, 63, 94, 0.3); }
    .gap-pill::before { background: var(--clay); }
    .strength-pill { background: var(--sage-soft); color: #6ee7b7 !important; border-color: rgba(16, 185, 129, 0.3); }
    .strength-pill::before { background: var(--sage); }

    .fallback-banner {
        background: var(--clay-soft);
        border: 1px solid rgba(244, 63, 94, 0.3);
        color: #fca5a5 !important;
        padding: 0.9rem 1.1rem;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .milestone-badge {
        font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1.05rem;
        text-align: center; color: #60a5fa !important;
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.7rem 0.5rem;
    }

    /* ---------------- Native Component Polish ---------------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }
    div[data-testid="stProgress"] div[role="progressbar"] > div { background-color: var(--accent) !important; }
    div[data-testid="stExpander"] {
        background: var(--bg-card); border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important; overflow: hidden;
    }
    div[data-testid="stAlert"] {
        border-radius: var(--radius-md) !important; border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
    }
    [data-testid="stChatMessage"] {
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: var(--radius-md); padding: 0.4rem 0.2rem;
    }
    hr { border-color: var(--border-soft) !important; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-mark">AI</div>
            <div>
                <div class="sidebar-logo-text">Learning & Career Studio</div>
                <div class="sidebar-logo-sub">Your ongoing academic mentor</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.write("---")

    selected_menu = option_menu(
        menu_title=None,
        options=["Dashboard & Roadmap", "Interactive Quiz", "AI Doubts Chatbot"],
        icons=["speedometer2", "patch-question", "chat-dots"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "0.95rem"},
            "nav-link": {
                "font-size": "0.92rem", "border-radius": "7px", "margin": "3px 0",
                "color": "#94a3b8", "font-family": "Plus Jakarta Sans", "font-weight": "500",
                "--hover-color": "#161f30",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)", 
                "color": "#ffffff", 
                "font-weight": "600",
                "box-shadow": "0 4px 12px rgba(59, 130, 246, 0.3)"
            },
        },
    )
    st.write("---")
    st.markdown(
        """<div class="sidebar-tip">Update your profile anytime from the Dashboard to regenerate your roadmap.</div>""",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# 4. TAB 1 — DASHBOARD & ROADMAP (Skill Gap Highlighted)
# ----------------------------------------------------------------------------
if selected_menu == "Dashboard & Roadmap":
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-label-highlight"> Core Feature • Skill Gap Analysis</span>
            <h1>Your Learning Dashboard</h1>
            <p>Tell us about yourself and we'll build a personalized skill-gap analysis, a
            structured roadmap, and a shortlist of free courses targeted directly at your gap areas.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Full name", value="Aman Kumar")
            target_role = st.text_input("Target career goal", value="Data Scientist")
            level = st.selectbox("Current level", ["Beginner", "Intermediate", "Advanced"])
        with col2:
            current_skills = st.text_area("Your current skills (comma separated)", value="Python, Basic SQL, Excel")
            timeline_weeks = st.slider("Roadmap duration (weeks)", min_value=4, max_value=16, value=12)
            study_time = st.slider("Daily study hours", min_value=1, max_value=8, value=2)

        st.session_state.setdefault("profile_data", None)
        submit_profile = st.form_submit_button("Generate learning path")

    if submit_profile:
        with st.spinner("Analyzing your profile against current industry standards..."):
            raw_response = gemini.generate_career_roadmap(
                user_name, target_role, current_skills, timeline_weeks,
                level=level, study_time=study_time,
            )
            try:
                data = json.loads(raw_response)
                st.session_state.profile_data = data
                st.session_state.current_student = user_name

                # Persist to SQLite
                student_id = db.save_student_profile(
                    user_name, "N/A", "N/A", current_skills, target_role, level, study_time
                )
                db.save_roadmap(student_id, json.dumps(data.get("profile_analysis", {})), json.dumps(data.get("roadmap", [])))
                st.session_state.student_id = student_id

                if data.get("source") == "fallback":
                    st.warning("Live AI engine unavailable right now — showing an offline estimate. See details below.")
                else:
                    st.success("Learning path generated.")
            except Exception as e:
                st.error(f"Failed to parse AI response ({e}). Please click the button to try again.")
                st.session_state.profile_data = None

    if st.session_state.get("profile_data"):
        res = st.session_state.profile_data
        analysis = res.get("profile_analysis", {})

        if res.get("source") == "fallback":
            st.markdown(f"""<div class="fallback-banner">{analysis.get('career_advice','')}</div>""", unsafe_allow_html=True)

        st.write("---")
        st.subheader("Skill Gap Analysis")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Readiness score", f"{analysis.get('readiness_score', 0)}%")
        with m2:
            st.metric("Identified gaps", f"{len(analysis.get('missing_skills', []))} core skills")
        with m3:
            st.metric("Est. commitment", f"{sum(1 for _ in res.get('roadmap', []))} milestones")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Identified skill gaps")
            gaps_html = "".join(f'<span class="chip gap-pill">{g}</span>' for g in analysis.get("missing_skills", []))
            st.markdown(gaps_html or "_None found_", unsafe_allow_html=True)
        with c2:
            st.markdown("##### Verified strengths")
            strengths_html = "".join(f'<span class="chip strength-pill">{s}</span>' for s in analysis.get("strengths", []))
            st.markdown(strengths_html or "_None found_", unsafe_allow_html=True)

        if analysis.get("weaknesses"):
            st.markdown("##### Areas to watch")
            for w in analysis["weaknesses"]:
                st.markdown(f"- {w}")

        if analysis.get("career_advice") and res.get("source") != "fallback":
            st.markdown(f"""<div class="info-card"><b>Mentor's advice:</b><br>{analysis['career_advice']}</div>""", unsafe_allow_html=True)

        # ---- Course Recommendations ----
        st.write("---")
        st.markdown("### Recommended resources")
        st.caption("Matched using a fuzzy-similarity engine — shorthand skills like 'ML' or typos still map correctly.")

        missing_skills_list = analysis.get("missing_skills", [])
        course_recs = rec.get_recommendations(missing_skills_list)

        if course_recs:
            df_recs = pd.DataFrame(course_recs)
            st.dataframe(
                df_recs,
                column_config={
                    "Skill Gap": "Skill focus",
                    "Matched Category": "Matched to",
                    "Confidence": "Match confidence",
                    "Course Title": "Course title",
                    "Platform": "Platform",
                    "Provider / Creator": "Instructor / creator",
                    "Resource Link": st.column_config.LinkColumn("Course", display_text="Open resource"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("No critical skill gaps found — no immediate courses needed.")

        # ---- Roadmap with Progress Tracker ----
        st.write("---")
        st.markdown("### Your week-by-week roadmap")
        roadmap_list = res.get("roadmap", [])

        if roadmap_list:
            student_id = st.session_state.get("student_id")
            progress_map = db.get_week_progress(student_id) if student_id else {}

            completed_count = 0
            for week in roadmap_list:
                week_label = week.get("Week", "")
                is_done = st.checkbox(
                    f"**{week_label}** — {week.get('Core Milestone', '')}",
                    value=progress_map.get(week_label, False),
                    key=f"week_done_{week_label}",
                )
                if is_done:
                    completed_count += 1
                if student_id and is_done != progress_map.get(week_label, False):
                    db.toggle_week_progress(student_id, week_label, is_done)
                with st.expander("Details", expanded=False):
                    st.write(f"**Syllabus:** {week.get('Syllabus Breakup', '-')}")
                    st.write(f"**Daily plan:** {week.get('Daily Allocation Plan', '-')}")

            # ---- Progress % + Badge ----
            total_weeks = len(roadmap_list)
            pct = int((completed_count / total_weeks) * 100) if total_weeks else 0
            st.write("---")
            pcol1, pcol2 = st.columns([3, 1])
            with pcol1:
                st.progress(pct / 100)
                st.caption(f"{completed_count} / {total_weeks} weeks completed ({pct}%)")
            with pcol2:
                if pct >= 100:
                    badge_text = "Roadmap complete"
                elif pct >= 75:
                    badge_text = "75%+ milestone"
                elif pct >= 50:
                    badge_text = "50%+ milestone"
                elif pct >= 25:
                    badge_text = "25%+ milestone"
                else:
                    badge_text = "Just getting started"
                st.markdown(f'<div class="milestone-badge">{badge_text}</div>', unsafe_allow_html=True)

            # ---- PDF Export ----
            st.write("---")
            pdf_bytes = pdf_export.generate_roadmap_pdf(
                st.session_state.get("current_student", "Student"),
                target_role, analysis, roadmap_list,
            )
            st.download_button(
                "Download roadmap as PDF",
                data=pdf_bytes,
                file_name=f"{st.session_state.get('current_student', 'student')}_roadmap.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Roadmap structure missing from the AI response — try regenerating.")

# ----------------------------------------------------------------------------
# 5. TAB 2 — INTERACTIVE QUIZ GENERATOR (Practice Mode Highlighted)
# ----------------------------------------------------------------------------
elif selected_menu == "Interactive Quiz":
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-label-highlight">⚡ Practice Mode • Self Assessment</span>
            <h1>Interactive Quiz Generator</h1>
            <p>Test your real-time understanding. Pick any custom topic and challenge your concepts instantly.</p>
        </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)
    with q_col1:
        quiz_topic = st.text_input("Enter topic (e.g., Python Lists, SQL Joins, Pandas)", value="Python Basics")
    with q_col2:
        quiz_level = st.selectbox("Select difficulty", ["Beginner", "Intermediate", "Advanced"])

    st.session_state.setdefault("current_quiz", None)
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("user_answers", {})

    if st.session_state.get("student_id"):
        with st.expander("Quiz history", expanded=False):
            history = db.get_quiz_history(st.session_state.student_id)
            if history:
                df_hist = pd.DataFrame(history)
                df_hist["Score %"] = (df_hist["score"] / df_hist["total"] * 100).round(0)
                st.dataframe(
                    df_hist,
                    column_config={
                        "topic": "Topic", "score": "Score", "total": "Total",
                        "date": "Date", "Score %": st.column_config.ProgressColumn("Score %", min_value=0, max_value=100),
                    },
                    hide_index=True, use_container_width=True,
                )
            else:
                st.caption("No quiz attempts yet — generate a quiz below and give it a try.")

    if st.button("Generate new quiz"):
        with st.spinner("Drafting analytical questions..."):
            quiz_data = gemini.get_quiz_questions(quiz_topic, quiz_level)
            if "error" in quiz_data:
                st.error(f"The AI engine couldn't generate a quiz right now.\n\nDetails: `{quiz_data['error']}`\n\nPlease check your GEMINI_API_KEY / internet connection and try again.")
                st.session_state.current_quiz = None
            else:
                st.session_state.current_quiz = quiz_data["quiz"]
                st.session_state.quiz_submitted = False
                st.session_state.user_answers = {}

    if st.session_state.current_quiz:
        st.write("---")
        st.info("Select your answers and click Submit at the bottom.")

        with st.form("quiz_display_form"):
            for idx, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"##### **Q{idx + 1}: {q['question']}**")
                user_choice = st.radio(
                    f"Select option for Q{idx + 1}:",
                    options=q["options"],
                    key=f"q_radio_{idx}",
                    label_visibility="collapsed",
                    index=None,
                )
                st.session_state.user_answers[idx] = user_choice
                st.write("")

            submit_answers = st.form_submit_button("Submit answers")

        if submit_answers:
            unanswered = [i for i, v in st.session_state.user_answers.items() if v is None]
            if unanswered:
                st.warning(f"Please answer all questions before submitting (missing Q{', Q'.join(str(i+1) for i in unanswered)}).")
            else:
                st.session_state.quiz_submitted = True
                correct_count = sum(
                    1 for idx, q in enumerate(st.session_state.current_quiz)
                    if st.session_state.user_answers[idx] == q["correct_answer"]
                )
                total = len(st.session_state.current_quiz)

                if st.session_state.get("student_id"):
                    db.save_quiz_score(st.session_state.student_id, quiz_topic, correct_count, total)

                st.markdown(f"### Final result: **{correct_count} / {total}**")
                st.progress(correct_count / total)

                if correct_count == total:
                    st.success("Perfect score! Advanced proficiency achieved.")
                elif correct_count >= total * 0.6:
                    st.success("Good job — keep learning to plug the remaining gaps.")
                else:
                    st.warning("Needs improvement. Re-watch the tutorials and try again.")

                st.write("---")
                st.markdown("#### Answer key")
                for idx, q in enumerate(st.session_state.current_quiz):
                    u_ans = st.session_state.user_answers[idx]
                    c_ans = q["correct_answer"]
                    if u_ans == c_ans:
                        st.markdown(f"**Q{idx + 1} — Correct.** You selected `{u_ans}`.")
                    else:
                        st.markdown(f"**Q{idx + 1} — Incorrect.** You selected `{u_ans}`, correct is `{c_ans}`.")
                    st.caption(f"Explanation: {q['explanation']}")

# ----------------------------------------------------------------------------
# 6. TAB 3 — AI DOUBTS CHATBOT (Live Chat Highlighted)
# ----------------------------------------------------------------------------
elif selected_menu == "AI Doubts Chatbot":
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-label-highlight">💬 Live Chat • AI Mentor</span>
            <h1>Instant Mentor Chatbot</h1>
            <p>Ask technical doubts, conceptual queries, or mock interview questions with instant 24/7 AI assistance.</p>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.setdefault("chat_messages", [])

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.chat_messages = []
            # for testing
            #st.rerun()
    with btn_col2:
        if st.session_state.chat_messages:
            chat_md = "\n\n".join(
                f"**{'You' if m['role']=='user' else 'Mentor'}:** {m['content']}"
                for m in st.session_state.chat_messages
            )
            st.download_button(
                "Download chat", data=chat_md, file_name="ai_mentor_chat.md",
                mime="text/markdown", use_container_width=True,
            )

    st.write("---")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a doubt (e.g., Explain standard deviation in plain English)"):
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = gemini.get_chatbot_reply(user_query, st.session_state.chat_messages)
                st.markdown(ai_response)

        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
