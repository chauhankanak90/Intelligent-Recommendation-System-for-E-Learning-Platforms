# gemini.py
import os
import re
import json
import time
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

import prompts

# 1. Load environment variables (for local development)
load_dotenv()


def _get_api_key():
    """First checks .env / OS environment (for local dev), then falls back to
    st.secrets (for Streamlit Community Cloud deployment). This lets the same
    code run both locally and live without any changes."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()
    try:
        return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        return None


api_key = _get_api_key()
if not api_key:
    raise ValueError(
        "⚠️ ERROR: 'GEMINI_API_KEY' not found. Check your local .env file, "
        "or add the key under Streamlit Cloud → App Settings → Secrets."
    )

# 2. Client Initializer (google-genai unified SDK)
client = genai.Client(api_key=api_key)

# gemini-1.5-flash is SHUT DOWN by Google (returns 404). "gemini-flash-latest"
# is an auto-updating alias that always points at a currently-supported model,
# so this project won't silently break again on the next model retirement.
MODEL_NAME = "gemini-flash-latest"


def _extract_json(raw_text: str) -> dict:
    """Gemini sometimes wraps its response in markdown fences or adds extra
    text. This function safely extracts and parses the JSON block from it."""
    text = raw_text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    return json.loads(text)


def _call_model(prompt: str, retries: int = 2, temperature: float = 0.7) -> str:
    """Retry-wrapped Gemini call. Retries transient errors (rate limit,
    network issues) up to 2 times before declaring failure."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            if not response.text:
                raise ValueError("Received an empty response from Gemini.")
            return response.text
        except Exception as e:
            last_error = e
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Gemini API failed even after {retries + 1} attempts: {last_error}")


def generate_career_roadmap(user_name, target_role, current_skills, timeline_weeks,
                             year="N/A", branch="N/A", level="Beginner", study_time=2) -> str:
    """Calls 2 specialised prompts (profile analysis + roadmap architecture)
    and merges the results into a single combined JSON object."""
    try:
        analysis_prompt = prompts.PROFILE_ANALYSIS_PROMPT.format(
            name=user_name, year=year, branch=branch, skills=current_skills,
            goal=target_role, level=level, study_time=study_time,
        )
        roadmap_prompt = prompts.ROADMAP_PROMPT.format(
            goal=target_role, skills=current_skills, study_time=study_time,
        )

        analysis_json = _extract_json(_call_model(analysis_prompt, temperature=0.4))
        roadmap_json = _extract_json(_call_model(roadmap_prompt, temperature=0.6))

        missing = analysis_json.get("missing_skills", [])
        fallback_score = max(10, 100 - len(missing) * 12)

        combined = {
            "profile_analysis": {
                "readiness_score": analysis_json.get("readiness_score", fallback_score),
                "missing_skills": missing,
                "strengths": analysis_json.get("strengths", []),
                "weaknesses": analysis_json.get("weaknesses", []),
                "career_advice": analysis_json.get("career_advice", ""),
            },
            "roadmap": roadmap_json.get("roadmap", []),
            "source": "live",
        }
        return json.dumps(combined)

    except Exception as e:
        return json.dumps(_fallback_roadmap(target_role, current_skills, timeline_weeks, str(e)))


def _fallback_roadmap(target_role, current_skills, timeline_weeks, error_msg=""):
    """Offline safety net — only used when the live Gemini call fails, so the
    UI never crashes. The UI clearly labels this as an 'offline estimate'."""
    user_skills_list = [s.strip() for s in current_skills.split(",") if s.strip()]
    if "data" in target_role.lower() or "science" in target_role.lower():
        missing = ["Python", "SQL", "Machine Learning", "Pandas & NumPy"]
        score = 20
        full_roadmap = [
            {"Week": "Week 1-4", "Core Milestone": "Python & Data Libraries", "Syllabus Breakup": "Core syntax, data structures, Pandas, NumPy", "Daily Allocation Plan": "1 Hr Theory, 1 Hr Practice"},
            {"Week": "Week 5-8", "Core Milestone": "SQL & Statistics", "Syllabus Breakup": "Joins, aggregations, descriptive & inferential statistics", "Daily Allocation Plan": "1 Hr Theory, 1 Hr Practice"},
            {"Week": "Week 9-12", "Core Milestone": "Machine Learning Foundations", "Syllabus Breakup": "Regression, classification, Scikit-Learn", "Daily Allocation Plan": "1 Hr Theory, 1 Hr Practice"},
            {"Week": "Week 13-16", "Core Milestone": "Capstone & Deployment", "Syllabus Breakup": "End-to-end project, GitHub hosting", "Daily Allocation Plan": "2 Hr Project Work"},
        ]
    else:
        missing = ["Git", "Python Core", "Data Structures"]
        score = 40
        full_roadmap = [
            {"Week": "Week 1-4", "Core Milestone": "Core Programming Concepts", "Syllabus Breakup": "Variables, conditions, loops", "Daily Allocation Plan": "1 Hr Theory, 1 Hr Practice"},
            {"Week": "Week 5-8", "Core Milestone": "Version Control & Packages", "Syllabus Breakup": "Git, GitHub workflows, environments", "Daily Allocation Plan": "1 Hr Theory, 1 Hr Practice"},
        ]

    allowed_chunks = max(1, timeline_weeks // 4)
    return {
        "profile_analysis": {
            "readiness_score": score,
            "missing_skills": missing,
            "strengths": user_skills_list,
            "weaknesses": ["Live AI analysis is currently unavailable — this is an offline estimate."],
            "career_advice": f"⚠️ Could not connect to the AI engine ({str(error_msg)[:80]}). "
                              f"Please check your GEMINI_API_KEY and internet connection.",
        },
        "roadmap": full_roadmap[:allowed_chunks],
        "source": "fallback",
    }


def get_quiz_questions(topic: str, level: str) -> dict:
    try:
        prompt = prompts.QUIZ_PROMPT.format(topic=topic, level=level)
        data = _extract_json(_call_model(prompt, temperature=0.8))
        if not data.get("quiz"):
            raise ValueError("Received an empty quiz array.")
        return data
    except Exception as e:
        return {"error": str(e)}


def get_chatbot_reply(user_query: str, chat_history: list) -> str:
    try:
        system_instruction = (
            "You are an expert, encouraging AI Coding and Career Mentor. "
            "Explain technical topics simply using everyday real-world analogies. "
            "Keep answers concise, structured with bullet points, and always add "
            "1 technical interview question at the end related to the topic."
        )
        # Only send the last 8 messages — to stay within memory/token limits
        recent_history = chat_history[:-1][-8:]
        history_text = "".join(
            f"{m['role'].capitalize()}: {m['content']}\n" for m in recent_history
        )
        full_prompt = f"{system_instruction}\n\n{history_text}User: {user_query}\nAssistant:"

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)),
        )
        if not response.text:
            raise ValueError("Received an empty reply from Gemini.")
        return response.text.strip()

    except Exception as e:
        return (f"⚠️ Sorry, the AI mentor couldn't respond right now "
                f"(Error: {str(e)[:120]}). Please try again or check your API key.")