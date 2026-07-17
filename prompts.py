# prompts.py

PROFILE_ANALYSIS_PROMPT = """
You are a Senior Technical Career Consultant. Analyze the following student attributes and identify their career potential and critical skill gaps.

Student Attributes:
- Name: {name}
- Academic Stage: {year}
- Stream/Branch: {branch}
- Known Technologies: {skills}
- Ultimate Career Target: {goal}
- Professional Standing: {level}
- Allocation Capacity: {study_time} Hours/Day

Evaluate their profile against current top-tier market standards for the target role.
Return your output strictly as a valid raw JSON object matching the schema below. Do not wrap it in markdown block fences.

JSON Schema:
{{
  "readiness_score": 0,
  "missing_skills": ["A list of 4-6 crucial technical skills or frameworks the student completely lacks to achieve the target role"],
  "strengths": ["2-3 positive indicators based on their existing branch, current level, or tech skills"],
  "weaknesses": ["2-3 areas of concern or bottlenecks they must overcome"],
  "career_advice": "A precise, customized 3-sentence action-plan guidance summary addressing the student directly by their name."
}}

Notes on "readiness_score": an integer from 0-100 representing how ready the student currently is for the target role, based on skill overlap.
"""

ROADMAP_PROMPT = """
Act as an industry-standard technical curriculum architect.
Design a thorough, highly effective sequential learning program targeting the role: '{goal}'.

Student Prerequisites:
- Current Knowledge: {skills}
- Time Commitment Available: {study_time} hours every single day

Map out exactly what they must cover week-by-week. Ensure early weeks strengthen fundamentals if required, middle weeks focus on frameworks, and later weeks target project deployment and interview prep.
Return your output strictly as a valid raw JSON object matching the schema below. Do not wrap it in markdown block fences.

JSON Schema:
{{
  "roadmap": [
    {{
      "Week": "Week 1",
      "Core Milestone": "High-level topic title",
      "Syllabus Breakup": "Concepts or tools to learn this week separated by commas",
      "Daily Allocation Plan": "Clear tactical routine utilizing their daily {study_time} hours (e.g., '1 Hr Video, 1 Hr Lab Work')"
    }}
  ]
}}
"""

QUIZ_PROMPT = """
You are an advanced technical interviewer. Generate an interactive multiple-choice quiz of exactly 5 questions based on the topic: "{topic}" at a {level} level.

Return your output strictly as a valid raw JSON object matching the schema below. Do not wrap it in markdown block fences (like ```json).

JSON Schema:
{{
  "quiz": [
    {{
      "id": 1,
      "question": "Clear and conceptual question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Exact text of the correct option",
      "explanation": "A short 1-sentence explanation of why this option is correct."
    }}
  ]
}}
"""