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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ----------------------------------------------------------------------------
# 2. GLOBAL STYLING — premium dark/black theme
# ----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
    }

    /* Core Dark Backgrounds */
    .stApp {
        background-color: #0d0e12;
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #161920 !important;
    }

    /* Hero Banner Dark Mode Adjustments */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 55%, #4c1d95 100%);
        padding: 2.2rem 2rem;
        border-radius: 18px;
        color: #f8fafc;
        margin-bottom: 1.6rem;
        border: 1px solid #3b0764;
        box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.7);
    }
    .hero-banner h1 { margin: 0; font-weight: 800; font-size: 1.9rem; color: #ffffff; }
    .hero-banner p { margin: 0.35rem 0 0 0; opacity: 0.85; color: #cbd5e1; }

    /* Metrics Blocks */
    div[data-testid="stMetric"] {
        background: #161920;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 14px -6px rgba(0, 0, 0, 0.5);
        border: 1px solid #272c38;
    }
    div[data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 800; color: #818cf8; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }

    /* Forms and Inputs */
    div.stForm {
        border-radius: 16px; 
        background: #161920; 
        padding: 1.8rem;
        box-shadow: 0 6px 20px -8px rgba(0, 0, 0, 0.6);
        border: 1px solid #272c38;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white; border-radius: 10px; font-weight: 600;
        width: 100%; border: none; padding: 0.6rem 0;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 8px 18px -8px rgba(99, 102, 241, 0.6); 
        color: white;
    }

    /* Info Cards & Badges */
    .info-card {
        background: #1e222b; border-radius: 14px; padding: 1.2rem 1.4rem;
        border-left: 4px solid #8b5cf6; margin-bottom: 0.8rem;
        box-shadow: 0 4px 14px -8px rgba(0,0,0,0.5);
        color: #e2e8f0;
    }
    .gap-pill {
        display:inline-block; background:#450a0a; color:#fca5a5;
        border-radius:999px; padding:4px 12px; margin:3px; font-size:0.85rem; font-weight:600;
        border: 1px solid #7f1d1d;
    }
    .strength-pill {
        display:inline-block; background:#064e3b; color:#6ee7b7;
        border-radius:999px; padding:4px 12px; margin:3px; font-size:0.85rem; font-weight:600;
        border: 1px solid #065f46;
    }
    .fallback-banner {
        background:#78350f; border:1px solid #92400e; color:#fef3c7;
        padding:0.8rem 1rem; border-radius:10px; margin-bottom:1rem; font-size:0.9rem;
    }
    
    /* Global element text overrides to match dark mode */
    p, span, label, h3, h4, h5 {
        color: #e2e8f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("AI Learning & Career Studio")
    st.caption("Your 24/7 Personal Academic & Career Mentor")
    st.write("---")

    selected_menu = option_menu(
        menu_title=None,
        options=["Dashboard & Roadmap", "Interactive Quiz", "AI Doubts Chatbot"],
        icons=["speedometer2", "patch-question", "chat-dots"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "nav-link": {"font-size": "0.95rem", "border-radius": "8px", "margin": "3px 0", "color": "#cbd5e1"},
            "nav-link-selected": {"background-color": "#6366f1", "color": "#ffffff"},
        },
    )
    st.write("---")
    st.info("💡 Pro-Tip: Update your profile anytime in the Dashboard to regenerate your roadmap.")

# ----------------------------------------------------------------------------
# 4. TAB 1 — DASHBOARD & ROADMAP
# ----------------------------------------------------------------------------
if selected_menu == "Dashboard & Roadmap":
    st.markdown("""
        <div class="hero-banner">
            <h1>🚀 Intelligent E-Learning Dashboard</h1>
            <p>Tell us about yourself — our AI mentor builds a skill-gap analysis,
            a personalised roadmap, and maps trusted free courses to your gaps.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Full Name", value="Aman Kumar")
            target_role = st.text_input("Target Career Goal", value="Data Scientist")
            level = st.selectbox("Current Level", ["Beginner", "Intermediate", "Advanced"])
        with col2:
            current_skills = st.text_area("Your Current Skills (comma separated)", value="Python, Basic SQL, Excel")
            timeline_weeks = st.slider("Roadmap Duration (Weeks)", min_value=4, max_value=16, value=12)
            study_time = st.slider("Daily Study Hours", min_value=1, max_value=8, value=2)

        st.session_state.setdefault("profile_data", None)
        submit_profile = st.form_submit_button("🎯 Generate Personalized Learning Path")

    if submit_profile:
        with st.spinner("🧠 Analyzing your profile against current industry standards..."):
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
                    st.warning("⚠️ Live AI engine unavailable right now — showing an offline estimate. See details below.")
                else:
                    st.success("✨ Learning path successfully generated by Gemini!")
            except Exception as e:
                st.error(f"⚠️ Failed to parse AI response ({e}). Please click the button to try again.")
                st.session_state.profile_data = None

    if st.session_state.get("profile_data"):
        res = st.session_state.profile_data
        analysis = res.get("profile_analysis", {})

        if res.get("source") == "fallback":
            st.markdown(f"""<div class="fallback-banner">{analysis.get('career_advice','')}</div>""", unsafe_allow_html=True)

        st.write("---")
        st.subheader("📊 Skill Gap Analysis & Diagnostics")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Readiness Score", f"{analysis.get('readiness_score', 0)}%")
        with m2:
            st.metric("Identified Gaps", f"{len(analysis.get('missing_skills', []))} Core Skills")
        with m3:
            st.metric("Est. Commitment", f"{sum(1 for _ in res.get('roadmap', []))} Milestones")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🔍 Identified Skill Gaps")
            gaps_html = "".join(f'<span class="gap-pill">🔴 {g}</span>' for g in analysis.get("missing_skills", []))
            st.markdown(gaps_html or "_None found_", unsafe_allow_html=True)
        with c2:
            st.markdown("##### ✅ Verified Strengths")
            strengths_html = "".join(f'<span class="strength-pill">🟢 {s}</span>' for s in analysis.get("strengths", []))
            st.markdown(strengths_html or "_None found_", unsafe_allow_html=True)

        if analysis.get("weaknesses"):
            st.markdown("##### ⚠️ Areas to Watch")
            for w in analysis["weaknesses"]:
                st.markdown(f"- {w}")

        if analysis.get("career_advice") and res.get("source") != "fallback":
            st.markdown(f"""<div class="info-card">💬 <b>Mentor's Advice:</b><br>{analysis['career_advice']}</div>""", unsafe_allow_html=True)

        # ---- Course Recommendations ----
        st.write("---")
        st.markdown("### 📚 Recommended Free Trusted Resources")
        st.caption("Matched using a fuzzy-similarity engine — so even shorthand skills like 'ML' or typos still map correctly.")

        missing_skills_list = analysis.get("missing_skills", [])
        course_recs = rec.get_recommendations(missing_skills_list)

        if course_recs:
            df_recs = pd.DataFrame(course_recs)
            st.dataframe(
                df_recs,
                column_config={
                    "Skill Gap": "Skill Focus",
                    "Matched Category": "Matched To",
                    "Confidence": "Match Confidence",
                    "Course Title": "Course Title",
                    "Platform": "Platform",
                    "Provider / Creator": "Instructor / Creator",
                    "Resource Link": st.column_config.LinkColumn("Go to Course 🚀", display_text="Open Resource"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("🎉 You don't have any critical skill gaps! No immediate courses needed.")

        # ---- Roadmap with Progress Tracker ----
        st.write("---")
        st.markdown("### 📅 Your Personalized Week-by-Week Learning Roadmap")
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
                    st.write(f"**Daily Plan:** {week.get('Daily Allocation Plan', '-')}")

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
                    st.markdown("### 🥇 100% Complete!")
                elif pct >= 75:
                    st.markdown("### 🥈 75%+ Milestone")
                elif pct >= 50:
                    st.markdown("### 🥈 50%+ Milestone")
                elif pct >= 25:
                    st.markdown("### 🥉 25%+ Milestone")
                else:
                    st.markdown("### 🔰 Just Getting Started")

            # ---- PDF Export ----
            st.write("---")
            pdf_bytes = pdf_export.generate_roadmap_pdf(
                st.session_state.get("current_student", "Student"),
                target_role, analysis, roadmap_list,
            )
            st.download_button(
                "📥 Download Roadmap as PDF",
                data=pdf_bytes,
                file_name=f"{st.session_state.get('current_student', 'student')}_roadmap.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Roadmap structure missing from the AI response — try regenerating.")

# ----------------------------------------------------------------------------
# 5. TAB 2 — INTERACTIVE QUIZ GENERATOR
# ----------------------------------------------------------------------------
elif selected_menu == "Interactive Quiz":
    st.markdown("""
        <div class="hero-banner">
            <h1>✍️ Practice Quiz Generator</h1>
            <p>Test your real-time understanding. Pick a topic and let the AI mentor challenge you.</p>
        </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)
    with q_col1:
        quiz_topic = st.text_input("Enter Topic (e.g., Python Lists, SQL Joins, Pandas)", value="Python Basics")
    with q_col2:
        quiz_level = st.selectbox("Select Difficulty", ["Beginner", "Intermediate", "Advanced"])

    st.session_state.setdefault("current_quiz", None)
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("user_answers", {})

    if st.session_state.get("student_id"):
        with st.expander("📈 My Quiz History", expanded=False):
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
                st.caption("No quiz attempts yet — generate a quiz below and give it a try!")

    if st.button("🎲 Generate Fresh Quiz"):
        with st.spinner("🧠 Gemini is drafting analytical questions..."):
            quiz_data = gemini.get_quiz_questions(quiz_topic, quiz_level)
            if "error" in quiz_data:
                st.error(f"⚠️ AI engine couldn't generate a quiz right now.\n\nDetails: `{quiz_data['error']}`\n\nPlease check your GEMINI_API_KEY / internet connection and try again.")
                st.session_state.current_quiz = None
            else:
                st.session_state.current_quiz = quiz_data["quiz"]
                st.session_state.quiz_submitted = False
                st.session_state.user_answers = {}

    if st.session_state.current_quiz:
        st.write("---")
        st.info("💡 Select your answers and click Submit at the bottom.")

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

            submit_answers = st.form_submit_button("🏁 Submit Answers")

        if submit_answers:
            unanswered = [i for i, v in st.session_state.user_answers.items() if v is None]
            if unanswered:
                st.warning(f"⚠️ Please answer all questions before submitting (missing Q{', Q'.join(str(i+1) for i in unanswered)}).")
            else:
                st.session_state.quiz_submitted = True
                correct_count = sum(
                    1 for idx, q in enumerate(st.session_state.current_quiz)
                    if st.session_state.user_answers[idx] == q["correct_answer"]
                )
                total = len(st.session_state.current_quiz)

                if st.session_state.get("student_id"):
                    db.save_quiz_score(st.session_state.student_id, quiz_topic, correct_count, total)

                st.markdown(f"### 📊 Final Result: **{correct_count} / {total}**")
                st.progress(correct_count / total)

                if correct_count == total:
                    st.balloons()
                    st.success("🎖️ Perfect score! Advanced proficiency achieved.")
                elif correct_count >= total * 0.6:
                    st.success("👍 Good job! Keep learning to plug the remaining gaps.")
                else:
                    st.warning("⚠️ Needs improvement. Re-watch the tutorials and try again!")

                st.write("---")
                st.markdown("#### 🔍 Answer Key & Explanations")
                for idx, q in enumerate(st.session_state.current_quiz):
                    u_ans = st.session_state.user_answers[idx]
                    c_ans = q["correct_answer"]
                    if u_ans == c_ans:
                        st.markdown(f"🟢 **Q{idx + 1}**: Correct! You selected `{u_ans}`.")
                    else:
                        st.markdown(f"🔴 **Q{idx + 1}**: Incorrect. You selected `{u_ans}`, correct is `{c_ans}`.")
                    st.caption(f"💡 *Explanation:* {q['explanation']}")

# ----------------------------------------------------------------------------
# 6. TAB 3 — AI DOUBTS CHATBOT
# ----------------------------------------------------------------------------
elif selected_menu == "AI Doubts Chatbot":
    st.markdown("""
        <div class="hero-banner">
            <h1>💬 24/7 Instant AI Mentor Chatbot</h1>
            <p>Ask technical doubts, conceptual queries, or mock interview questions.</p>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.setdefault("chat_messages", [])

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    with btn_col2:
        if st.session_state.chat_messages:
            chat_md = "\n\n".join(
                f"**{'You' if m['role']=='user' else 'AI Mentor'}:** {m['content']}"
                for m in st.session_state.chat_messages
            )
            st.download_button(
                "📥 Download Chat", data=chat_md, file_name="ai_mentor_chat.md",
                mime="text/markdown", use_container_width=True,
            )

    st.write("---")

    for message in st.session_state.chat_messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🧠"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a doubt (e.g., Explain standard deviation in plain English)"):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_query)
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("🧠 Thinking..."):
                ai_response = gemini.get_chatbot_reply(user_query, st.session_state.chat_messages)
                st.markdown(ai_response)

        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})