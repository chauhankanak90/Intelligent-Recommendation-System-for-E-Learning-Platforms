# recommendation.py
import difflib

# Predefined trusted course catalog mapped against popular skills
COURSE_CATALOG = {
    "Python": [
        {"title": "Python for Everybody Specialization", "platform": "Coursera (Free Audit)", "provider": "University of Michigan", "url": "https://www.coursera.org/specializations/python"},
        {"title": "Python for Beginners", "platform": "YouTube", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
    ],
    "SQL": [
        {"title": "SQL for Data Science", "platform": "Coursera (Free Audit)", "provider": "UC Davis", "url": "https://www.coursera.org/learn/sql-for-data-science"},
        {"title": "SQL Tutorial for Beginners", "platform": "YouTube", "provider": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization", "platform": "Coursera (Free Audit)", "provider": "Andrew Ng (DeepLearning.AI)", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
        {"title": "Intro to Machine Learning", "platform": "Kaggle Learn", "provider": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
    ],
    "Deep Learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera (Free)", "provider": "Andrew Ng", "url": "https://www.coursera.org/specializations/deep-learning"},
        {"title": "Practical Deep Learning for Coders", "platform": "Fast.ai", "provider": "Jeremy Howard", "url": "https://www.fast.ai/"},
    ],
    "Pandas": [
        {"title": "Pandas Micro-Course", "platform": "Kaggle Learn", "provider": "Kaggle", "url": "https://www.kaggle.com/learn/pandas"},
        {"title": "Data Analysis with Python (Pandas)", "platform": "YouTube", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=r-uOLxNrNk8"},
    ],
    "NumPy": [
        {"title": "NumPy Tutorial", "platform": "W3Schools", "provider": "W3Schools", "url": "https://www.w3schools.com/python/numpy_intro.asp"},
        {"title": "NumPy Completely Beginner Course", "platform": "YouTube", "provider": "Keith Galli", "url": "https://www.youtube.com/watch?v=GB9Byg7Wygg"},
    ],
    "TensorFlow": [
        {"title": "Intro to TensorFlow for Deep Learning", "platform": "Udacity", "provider": "TensorFlow / Google", "url": "https://www.udacity.com/course/intro-to-tensorflow-for-deep-learning--ud187"},
    ],
    "Git": [
        {"title": "Git & GitHub Crash Course", "platform": "YouTube", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
    ],
    "Docker": [
        {"title": "Docker for Beginners", "platform": "YouTube", "provider": "TechWorld with Nana", "url": "https://www.youtube.com/watch?v=3c-iQQ23VvU"},
    ],
    "JavaScript": [
        {"title": "JavaScript Algorithms and Data Structures", "platform": "freeCodeCamp", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
    ],
    "React": [
        {"title": "React Course - Beginner's Tutorial", "platform": "YouTube", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"},
    ],
    "Data Structures": [
        {"title": "Data Structures & Algorithms", "platform": "YouTube", "provider": "Abdul Bari", "url": "https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O"},
    ],
    "Statistics": [
        {"title": "Statistics and Probability", "platform": "Khan Academy", "provider": "Khan Academy", "url": "https://www.khanacademy.org/math/statistics-probability"},
    ],
    "Cloud Computing": [
        {"title": "AWS Cloud Practitioner Essentials", "platform": "AWS Skill Builder", "provider": "Amazon", "url": "https://skillbuilder.aws/"},
    ],
    "UI/UX Design": [
        {"title": "Google UX Design Certificate", "platform": "Coursera (Free Audit)", "provider": "Google", "url": "https://www.coursera.org/professional-certificates/google-ux-design"},
    ],
}

# Common shorthand/abbreviations students actually type, mapped to catalog keys
SKILL_ALIASES = {
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "ai": "Machine Learning",
    "js": "JavaScript",
    "reactjs": "React",
    "react.js": "React",
    "dsa": "Data Structures",
    "ds": "Data Structures",
    "stats": "Statistics",
    "aws": "Cloud Computing",
    "gcp": "Cloud Computing",
    "azure": "Cloud Computing",
    "ux": "UI/UX Design",
    "ui": "UI/UX Design",
    "tf": "TensorFlow",
}

# Match confidence ke fuzzy-matching cutoffs
_STRONG_MATCH_CUTOFF = 0.72
_WEAK_MATCH_CUTOFF = 0.5


def _best_catalog_match(skill: str):
    """Pehle alias table check karta hai (ML, DSA, JS jaisi shorthand ke liye),
    phir substring match, phir difflib fuzzy match (typos ke liye) — isse
    sirf brittle substring matching se kahin zyada robust matching milti hai."""
    skill_lower = skill.lower().strip()
    catalog_keys = list(COURSE_CATALOG.keys())

    # 1. Alias table (handles abbreviations like "ML", "DSA", "JS")
    if skill_lower in SKILL_ALIASES:
        return SKILL_ALIASES[skill_lower], "Exact Match"

    # 2. Direct substring match (fast path)
    for key in catalog_keys:
        if skill_lower in key.lower() or key.lower() in skill_lower:
            return key, "Exact Match"

    # 3. Fuzzy match fallback (handles typos)
    close = difflib.get_close_matches(skill_lower, [k.lower() for k in catalog_keys], n=1, cutoff=_WEAK_MATCH_CUTOFF)
    if close:
        matched_key = next(k for k in catalog_keys if k.lower() == close[0])
        ratio = difflib.SequenceMatcher(None, skill_lower, close[0]).ratio()
        confidence = "Strong Match" if ratio >= _STRONG_MATCH_CUTOFF else "Related Match"
        return matched_key, confidence

    return None, None


def get_recommendations(missing_skills_list):
    """Student ki missing skills list ke base par intelligent fuzzy-matching
    se course suggestions nikalta hai."""
    recommendations = []
    seen = set()

    for skill in missing_skills_list:
        matched_skill, confidence = _best_catalog_match(skill)
        if not matched_skill:
            continue
        for course in COURSE_CATALOG[matched_skill]:
            dedupe_key = (skill, course["title"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            recommendations.append({
                "Skill Gap": skill,
                "Matched Category": matched_skill,
                "Confidence": confidence,
                "Course Title": course["title"],
                "Platform": course["platform"],
                "Provider / Creator": course["provider"],
                "Resource Link": course["url"],
            })

    if not recommendations:
        recommendations.append({
            "Skill Gap": "General",
            "Matched Category": "General",
            "Confidence": "Default",
            "Course Title": "Google IT Support Professional Certificate",
            "Platform": "Coursera",
            "Provider / Creator": "Google",
            "Resource Link": "https://www.coursera.org/professional-certificates/google-it-support",
        })

    return recommendations