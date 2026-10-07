# gemini.py
import os
import re
import json
import time
import logging
import warnings
import threading
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv

import prompts

# 1. Silence SDK internal logger warnings about thought_signature
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

# 2. Supported and Fallback Models
# Reliable primary model with fallback cascade for high-demand (503) scenarios
load_dotenv()
# You can override the main model without editing code: add GEMINI_MODEL=gemini-flash-lite-latest to .env
PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "").strip() or "gemini-flash-lite-latest"
logging.warning("gemini.py v8 loaded | primary model = %s", PRIMARY_MODEL)

FALLBACK_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
]  # PRIMARY_MODEL is always tried first; duplicates are removed automatically

# Shared state (lives for the whole Streamlit server process, so every user/request benefits)
_STATE_LOCK = threading.Lock()
_COOLDOWN_UNTIL = {}                      # model -> timestamp until which it is skipped after a 503
_NO_THINKING = {
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
}  # models that reject thinking_config (learned automatically too)
COOLDOWN_SECONDS = 60


def _model_order() -> list:
    """Models to try, skipping ones that recently returned 503. If all are cooling down, try all."""
    now = time.time()
    cascade = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    with _STATE_LOCK:
        available = [m for m in cascade if _COOLDOWN_UNTIL.get(m, 0) <= now]
    return available or cascade


def _mark_overloaded(model_name: str) -> None:
    with _STATE_LOCK:
        _COOLDOWN_UNTIL[model_name] = time.time() + COOLDOWN_SECONDS


def _mark_no_thinking(model_name: str) -> None:
    with _STATE_LOCK:
        _NO_THINKING.add(model_name)

def _get_api_key():
    """Retrieves API key from environment (.env / OS) or Streamlit secrets without exposing it."""
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key and key.strip():
        return key.strip()
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"].strip()
    except Exception:
        pass
    return None


def is_configured() -> bool:
    """Checks if a valid API key is present in environment or secrets."""
    return _get_api_key() is not None


def _get_client():
    """Initializes and returns a GenAI Client instance safely, or None if key is absent."""
    key = _get_api_key()
    if not key:
        return None
    try:
        # Timeout (seconds) so a busy/hanging model cannot block the app for a long time.
        # Change it with GEMINI_TIMEOUT_SEC in .env if needed.
        try:
            timeout_ms = int(float(os.getenv("GEMINI_TIMEOUT_SEC", "15")) * 1000)
            return genai.Client(api_key=key, http_options=types.HttpOptions(timeout=timeout_ms))
        except Exception:
            return genai.Client(api_key=key)
    except Exception as e:
        logging.error(f"Failed to initialize GenAI client: {e}")
        return None


def classify_error(err: Exception) -> tuple[str, str]:
    """Classifies an error into a machine category and a clear, polite user-facing message.
    Never exposes raw API keys, stack traces, or makes misleading assumptions.
    Returns: (category, user_friendly_message)
    """
    err_str = str(err).lower()
    
    # Check for authentication / API key errors
    if any(k in err_str for k in ["api_key_invalid", "api key not valid", "unauthenticated", "invalid api key", "permission_denied", "forbidden"]) or getattr(err, "code", None) in [401, 403]:
        return "AUTH_ERROR", "Gemini API authentication failed. Please check your local API configuration."
    
    # Check for high demand / temporary service unavailable (503 / 504 / deadline)
    if any(k in err_str for k in ["503", "504", "unavailable", "high demand", "overloaded", "deadline"]) or getattr(err, "code", None) in [503, 504] or isinstance(err, errors.ServerError):
        return "SERVICE_UNAVAILABLE", "AI service is temporarily busy. We've switched to a fallback mode. Please try again shortly."
    
    # Check for quota / rate-limiting (429)
    if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str or "rate limit" in err_str or getattr(err, "code", None) == 429:
        return "QUOTA_EXCEEDED", "AI usage limit reached for the current API configuration."
    
    # Check for network / connection errors
    if any(k in err_str for k in ["connection", "timeout", "timed out", "unreachable", "dns", "failed to resolve"]):
        return "NETWORK_ERROR", "Network connection issue. Please check your internet connection."
    
    # General API / parsing error
    return "GENERAL_ERROR", "AI service is currently unavailable. Switched to offline estimate."


def _clean_response_text(response) -> str:
    """Extracts text content cleanly from response parts without triggering logger warnings
    for metadata fields like thought_signature or thought parts."""
    if not response or not getattr(response, "candidates", None):
        return ""
    
    candidate = response.candidates[0]
    if not candidate or not candidate.content or not candidate.content.parts:
        return ""
    
    texts = []
    for part in candidate.content.parts:
        # Skip thoughts if present
        if getattr(part, "thought", False):
            continue
        text_val = getattr(part, "text", None)
        if isinstance(text_val, str) and text_val:
            texts.append(text_val)
            
    if texts:
        return "".join(texts).strip()
    
    # Fallback to response.text if direct extraction found nothing
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return (response.text or "").strip()
    except Exception:
        return ""


def _extract_json(raw_text: str) -> dict:
    """Safely extracts and parses JSON even with markdown fences or surrounding prose."""
    text = raw_text.strip()
    
    # Remove markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()
    
    # If not starting with { or [, locate the first { and last }
    if not text.startswith("{") and not text.startswith("["):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt trailing comma cleanup
        cleaned = re.sub(r",\s*([\]}])", r"\1", text)
        return json.loads(cleaned)


def _fit_roadmap_to_weeks(roadmap: list, total_weeks: int) -> list:
    """Guarantees the roadmap never runs past the requested number of weeks.
    Drops entries that start after total_weeks and clips ranges like 'Week 9-14' to 'Week 9-10'.
    Entries without parseable numbers are kept as-is."""
    fitted = []
    for item in roadmap:
        label = str(item.get("Week", ""))
        nums = [int(n) for n in re.findall(r"\d+", label)]
        if not nums:
            fitted.append(item)
            continue
        start, end = nums[0], nums[-1]
        if start > total_weeks:
            continue
        if end > total_weeks:
            item = dict(item)
            item["Week"] = f"Week {start}" if start == total_weeks else f"Week {start}-{total_weeks}"
        fitted.append(item)
    return fitted if fitted else roadmap[:1]


def _call_model(prompt: str, retries: int = 1, temperature: float = 0.7, json_mode: bool = True) -> str:
    """Calls Gemini with fast failover.
    - 503 (overloaded): the model is put on a 60s cooldown and the NEXT model is tried immediately
      (no pointless waiting on a model that is busy).
    - 400 (invalid argument): same model is retried once without thinking_config, and remembered.
    - 429 (quota): short wait, retry, then next model.
    - If every model was overloaded, the whole list is tried once more after a 3s pause.
    The real error is always logged to the terminal.
    """
    client = _get_client()
    if not client:
        raise ValueError("Gemini API authentication failed. Please check your local API configuration.")

    last_error = None
    start_time = time.time()
    # Stop trying new models after this many seconds so the app answers (offline) instead of hanging
    max_wait = float(os.getenv("GEMINI_MAX_WAIT_SEC", "35"))

    for round_no in range(2):
        saw_overload = False

        for model_name in _model_order():
            if last_error is not None and (time.time() - start_time) > max_wait:
                break
            use_thinking = ("lite" not in model_name.lower()) and (model_name not in _NO_THINKING)
            attempt = 0
            while attempt <= retries:
                try:
                    config_kwargs = {"temperature": temperature}
                    if use_thinking:
                        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
                    if json_mode:
                        config_kwargs["response_mime_type"] = "application/json"

                    _t0 = time.time()
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_kwargs),
                    )

                    extracted_text = _clean_response_text(response)
                    if not extracted_text:
                        raise ValueError(f"Received empty response from {model_name}.")
                    logging.warning("GEMINI OK | model=%s | %.1fs | %d chars", model_name, time.time() - _t0, len(extracted_text))
                    return extracted_text

                except Exception as e:
                    last_error = e
                    logging.error("GEMINI FAIL | model=%s | round=%s | attempt=%s | after %.1fs | %r", model_name, round_no, attempt, time.time() - _t0 if '_t0' in locals() else 0.0, e)
                    category, _ = classify_error(e)

                    if category == "AUTH_ERROR":
                        raise e

                    # 400: usually an unsupported thinking config -> retry without it and remember
                    if use_thinking and (getattr(e, "code", None) == 400 or "thinking" in str(e).lower()):
                        use_thinking = False
                        _mark_no_thinking(model_name)
                        continue

                    if category == "SERVICE_UNAVAILABLE":
                        saw_overload = True
                        _mark_overloaded(model_name)
                        break  # go to next model right away

                    if category == "QUOTA_EXCEEDED" and attempt < retries:
                        time.sleep(2.0)
                        attempt += 1
                        continue

                    break  # any other error: next model

        if saw_overload and round_no == 0 and (time.time() - start_time) <= max_wait:
            time.sleep(3)
            continue
        break

    raise last_error if last_error else RuntimeError("AI service failed across all available models.")


def generate_career_roadmap(
    user_name: str,
    target_role: str,
    current_skills: str,
    timeline_weeks: int = 12,
    year: str = "N/A",
    branch: str = "N/A",
    level: str = "Beginner",
    study_time: int = 2,
    **kwargs
) -> str:
    """Generates comprehensive profile analysis & week-by-week roadmap.
    Merges specialized prompts and normalizes response structure.
    Falls back gracefully to offline mode if the AI service is unavailable.
    """
    # Accept common alternate names for the duration, in case app.py uses one of them
    for _alias in ("weeks", "duration_weeks", "duration", "num_weeks", "timeline"):
        if kwargs.get(_alias):
            timeline_weeks = kwargs[_alias]
            break
    try:
        timeline_weeks = int(re.findall(r"\d+", str(timeline_weeks))[0])
    except Exception:
        timeline_weeks = 12
    timeline_weeks = max(1, timeline_weeks)

    try:
        analysis_prompt = prompts.PROFILE_ANALYSIS_PROMPT.format(
            name=user_name, year=year, branch=branch, skills=current_skills,
            goal=target_role, level=level, study_time=study_time,
        )
        roadmap_prompt = prompts.ROADMAP_PROMPT.format(
            goal=target_role, skills=current_skills, study_time=study_time,
        ) + (
            f"\n\nIMPORTANT CONSTRAINT: The roadmap must cover EXACTLY {timeline_weeks} weeks in total. "
            f"Plan the weeks so the last entry ends at Week {timeline_weeks}. "
            f"Never include any week beyond Week {timeline_weeks}."
        )

        # Both AI calls run at the same time (about 2x faster than one after the other)
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_analysis = pool.submit(_call_model, analysis_prompt, 1, 0.4, True)
            f_roadmap = pool.submit(_call_model, roadmap_prompt, 1, 0.6, True)
            analysis_text = f_analysis.result()
            roadmap_text = f_roadmap.result()
        analysis_json = _extract_json(analysis_text)
        roadmap_json = _extract_json(roadmap_text)

        missing = analysis_json.get("missing_skills", [])
        if not isinstance(missing, list):
            missing = [str(missing)] if missing else []

        fallback_score = max(10, min(95, 100 - len(missing) * 12))

        # Normalize roadmap entries
        raw_roadmap = roadmap_json.get("roadmap", [])
        normalized_roadmap = []
        for i, item in enumerate(raw_roadmap):
            week_label = item.get("Week") or f"Week {i+1}"
            milestone = item.get("Core Milestone") or item.get("milestone") or item.get("title") or "Technical Foundations"
            syllabus = item.get("Syllabus Breakup") or item.get("syllabus") or item.get("topics") or "Core technical concepts and hands-on drills"
            plan = item.get("Daily Allocation Plan") or item.get("daily_plan") or f"{study_time} hours hands-on coding & problem solving"
            tasks = item.get("Tasks") or item.get("tasks") or f"Implement practical mini-assignments covering {milestone}"
            project = item.get("Project") or item.get("project") or f"Hands-on Milestone Project for {week_label}"

            normalized_roadmap.append({
                "Week": week_label,
                "Core Milestone": milestone,
                "Syllabus Breakup": syllabus,
                "Daily Allocation Plan": plan,
                "Tasks": tasks,
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": project,
            })

        # Safety net: never exceed the requested number of weeks
        if not normalized_roadmap:
            raise ValueError("AI returned an empty roadmap.")
        normalized_roadmap = _fit_roadmap_to_weeks(normalized_roadmap, timeline_weeks)

        combined = {
            "profile_analysis": {
                "readiness_score": int(analysis_json.get("readiness_score", fallback_score)),
                "missing_skills": missing,
                "strengths": analysis_json.get("strengths", []),
                "weaknesses": analysis_json.get("weaknesses", []),
                "career_advice": analysis_json.get("career_advice", ""),
            },
            "roadmap": normalized_roadmap,
            "source": "live",
        }
        return json.dumps(combined)

    except Exception as e:
        logging.error("ROADMAP FALLBACK TRIGGERED | %r", e)
        category, friendly_message = classify_error(e)
        return json.dumps(_fallback_roadmap(
            target_role, current_skills, timeline_weeks, level, study_time,
            error_category=category, error_message=friendly_message
        ))


def _fallback_roadmap(
    target_role: str,
    current_skills: str,
    timeline_weeks: int = 12,
    level: str = "Beginner",
    study_time: int = 2,
    error_category: str = "SERVICE_UNAVAILABLE",
    error_message: str = "AI service is temporarily busy. We've switched to a fallback mode. Please try again shortly."
) -> dict:
    """Offline safety net when live Gemini call fails. Returns a structured,
    role-aligned roadmap labeled clearly as an offline estimate with polite error classification.
    """
    user_skills_list = [s.strip() for s in current_skills.split(",") if s.strip()]
    role_lower = target_role.lower()

    if any(k in role_lower for k in ["data", "science", "ml", "machine learning", "ai"]):
        missing = ["Python Core & OOP", "SQL & Relational Databases", "Pandas & NumPy", "Machine Learning (Scikit-Learn)"]
        score = 25
        full_roadmap = [
            {
                "Week": "Week 1-4",
                "Core Milestone": "Python & Data Libraries",
                "Syllabus Breakup": "Core syntax, data structures, Pandas, NumPy, Data Cleaning",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Theory, {max(1, study_time - (study_time // 2))} Hr Coding Practice",
                "Tasks": "Solve 10 LeetCode Python problems, build Pandas data pipeline",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Automated CSV Data Cleaning & EDA Report Tool",
            },
            {
                "Week": "Week 5-8",
                "Core Milestone": "SQL & Statistical Foundations",
                "Syllabus Breakup": "Complex Joins, Window Functions, Inferential Statistics, Hypothesis Testing",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Theory, {max(1, study_time - (study_time // 2))} Hr Query Writing",
                "Tasks": "Practice 25 SQL interview questions on HackerRank",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "E-Commerce Database Schema Design & Analytics Dashboard",
            },
            {
                "Week": "Week 9-12",
                "Core Milestone": "Machine Learning Foundations",
                "Syllabus Breakup": "Regression, Classification, Cross-Validation, Scikit-Learn Pipelines",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Algorithmic Theory, {max(1, study_time - (study_time // 2))} Hr Model Tuning",
                "Tasks": "Implement Linear & Logistic Regression from scratch, train Random Forest",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Customer Churn Prediction Model with FastAPI Endpoint",
            },
            {
                "Week": "Week 13-16",
                "Core Milestone": "Capstone Deployment & Portfolio",
                "Syllabus Breakup": "Model Serialization, Docker Containerization, Streamlit UI, GitHub Portfolio",
                "Daily Allocation Plan": f"{study_time} Hr Full Project Development & Documentation",
                "Tasks": "Deploy containerized ML app to cloud, write technical blog post",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "End-to-End Predictive SaaS Application on Cloud",
            },
        ]
    elif any(k in role_lower for k in ["web", "full stack", "frontend", "backend", "software"]):
        missing = ["Modern JavaScript / TypeScript", "React Framework", "Node.js / Express or Python Backend", "Database Architecture & Git"]
        score = 30
        full_roadmap = [
            {
                "Week": "Week 1-4",
                "Core Milestone": "Web Fundamentals & Modern JS",
                "Syllabus Breakup": "Semantic HTML, Modern CSS Grid/Flexbox, ES6+ JavaScript, DOM Manipulation",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Concepts, {max(1, study_time - (study_time // 2))} Hr UI Building",
                "Tasks": "Build 3 responsive landing pages, practice JS array methods",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Interactive Task Management & Analytics Web App",
            },
            {
                "Week": "Week 5-8",
                "Core Milestone": "Frontend Framework (React)",
                "Syllabus Breakup": "React Components, State & Hooks, Routing, Tailwind CSS, API Integration",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Documentation, {max(1, study_time - (study_time // 2))} Hr Component Labs",
                "Tasks": "Convert static designs into modular reusable React components",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Full-Featured SaaS Dashboard with Live REST API Integration",
            },
            {
                "Week": "Week 9-12",
                "Core Milestone": "Backend APIs & Database Design",
                "Syllabus Breakup": "RESTful API Design, Express/Node.js or FastAPI, PostgreSQL/MongoDB, Auth (JWT)",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Architecture, {max(1, study_time - (study_time // 2))} Hr API Building",
                "Tasks": "Implement user authentication, secure JWT cookies, CRUD endpoints",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Secure Multi-User E-Learning Management API",
            },
            {
                "Week": "Week 13-16",
                "Core Milestone": "Full-Stack Deployment & CI/CD",
                "Syllabus Breakup": "Docker, GitHub Actions, Cloud Hosting (Vercel/Render/AWS), Testing",
                "Daily Allocation Plan": f"{study_time} Hr System Integration & Deployment",
                "Tasks": "Set up CI/CD pipeline, write unit tests for critical endpoints",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Production-Ready Full-Stack Web Platform with CI/CD",
            },
        ]
    else:
        missing = ["Version Control (Git)", "Core Programming Logic", "Data Structures & Algorithms", "System Architecture"]
        score = 35
        full_roadmap = [
            {
                "Week": "Week 1-4",
                "Core Milestone": "Foundational Computer Science & Logic",
                "Syllabus Breakup": "Data Types, Control Flow, Modular Functions, OOP Principles, Git Workflows",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Theory, {max(1, study_time - (study_time // 2))} Hr Practice",
                "Tasks": "Solve 20 fundamental logic challenges, setup GitHub profile",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Command-Line Productivity Suite with Version Control",
            },
            {
                "Week": "Week 5-8",
                "Core Milestone": "Data Structures & Problem Solving",
                "Syllabus Breakup": "Arrays, Hash Maps, Linked Lists, Stacks, Queues, Big-O Complexity",
                "Daily Allocation Plan": f"{max(1, study_time // 2)} Hr Algorithm Analysis, {max(1, study_time - (study_time // 2))} Hr Coding",
                "Tasks": "Implement core data structures from scratch",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": "Custom Search & Indexing Engine with Performance Benchmarks",
            },
            {
                "Week": "Week 9-12",
                "Core Milestone": "Specialization & Applied Project",
                "Syllabus Breakup": "Role-specific frameworks, API consumption, practical architecture patterns",
                "Daily Allocation Plan": f"{study_time} Hr Hands-on Project Implementation",
                "Tasks": "Integrate 3rd-party APIs, write comprehensive documentation",
                "Estimated Hours": f"{int(study_time) * 7} hrs/week",
                "Project": f"Production-Grade Showcase Project for {target_role}",
            },
        ]

    try:
        timeline_weeks = max(1, int(timeline_weeks))
    except Exception:
        timeline_weeks = 12
    return {
        "profile_analysis": {
            "readiness_score": score,
            "missing_skills": missing,
            "strengths": user_skills_list if user_skills_list else ["Demonstrated initiative to set targeted career goals"],
            "weaknesses": ["Analysis generated in offline estimate mode — full live AI diagnosis will resume once service stabilizes."],
            "career_advice": error_message,
            "error_category": error_category,
        },
        "roadmap": _fit_roadmap_to_weeks(full_roadmap, timeline_weeks),
        "source": "fallback",
        "error_category": error_category,
        "error_message": error_message,
    }


def get_quiz_questions(topic: str, level: str) -> dict:
    """Generates interactive quiz questions with robust error categorization."""
    try:
        prompt = prompts.QUIZ_PROMPT.format(topic=topic, level=level)
        data = _extract_json(_call_model(prompt, temperature=0.7, json_mode=True))
        if not data.get("quiz"):
            raise ValueError("Received an empty quiz array.")
        return data
    except Exception as e:
        logging.error("QUIZ FAIL | %r", e)
        category, friendly_message = classify_error(e)
        return {"error": friendly_message, "category": category}


def get_chatbot_reply(user_query: str, chat_history: list) -> str:
    """Handles chatbot conversational turns with polite categorized fallbacks."""
    try:
        system_instruction = (
            "You are an elite, inspiring AI Coding & Career Mentor. "
            "Explain technical concepts intuitively using memorable real-world analogies. "
            "Structure responses cleanly with bullet points, code snippets when relevant, "
            "and end with exactly 1 insightful interview challenge question."
        )
        recent_history = chat_history[:-1][-8:] if len(chat_history) > 1 else []
        history_text = "".join(
            f"{m['role'].capitalize()}: {m['content']}\n" for m in recent_history
        )
        full_prompt = f"{system_instruction}\n\n{history_text}User: {user_query}\nMentor:"

        if not is_configured():
            return "Gemini API authentication failed. Please check your local API configuration."

        return _call_model(full_prompt, retries=1, temperature=0.7, json_mode=False)

    except Exception as e:
        logging.error("CHATBOT FAIL | %r", e)
        _, friendly_msg = classify_error(e)
        return friendly_msg