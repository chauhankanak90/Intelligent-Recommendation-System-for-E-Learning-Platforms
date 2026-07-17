<div align="center">

# 🧠 Intelligent Recommendation System for E-Learning Platforms

### An AI-Powered Personal Career & Learning Mentor

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://intelligent-recommendation-system-for-e-learning-platforms-gt5.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[🔗 Try the Live App](https://intelligent-recommendation-system-for-e-learning-platforms-gt5.streamlit.app/)**

</div>

---

## 📖 Overview

Traditional e-learning platforms show every student the same courses, the same content, and the same generic advice — regardless of their background or goals.

**This project is different.** It acts as a personal AI mentor that analyzes each student's current skills against their target career goal, identifies exactly what they're missing, and builds a custom week-by-week learning roadmap — backed by trusted, free course recommendations, an AI-generated quiz system, and a 24/7 doubt-solving chatbot.

Built using **Google Gemini AI** for intelligent reasoning and **Streamlit** for an interactive, zero-frontend-code web interface.

---

## 🔗 Live Demo

> ### 🌐 **[intelligent-recommendation-system-for-e-learning-platforms-gt5.streamlit.app](https://intelligent-recommendation-system-for-e-learning-platforms-gt5.streamlit.app/)**

No installation needed — open the link above and try it directly in your browser.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Getting Started (Local Setup)](#-getting-started-local-setup)
- [Deployment](#️-deployment-streamlit-community-cloud)
- [Future Scope](#-future-scope)
- [Author](#-author)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Skill-Gap Analysis** | AI compares your current skills against your target role to identify strengths and missing skills |
| 🗺️ **Personalized Roadmap** | Auto-generated week-by-week learning plan tailored to your available study time |
| 📚 **Smart Course Recommendations** | Fuzzy-matching engine maps skill gaps to trusted, free courses — even handles typos and shorthand like "ML" or "DSA" |
| ✍️ **AI Quiz Generator** | Instantly generates topic-specific MCQs with explanations and scoring |
| 💬 **24/7 AI Doubts Chatbot** | Conversational AI mentor that explains concepts with real-world analogies |
| ✅ **Progress Tracker** | Mark roadmap weeks as complete and track your overall progress |
| 🏅 **Milestone Badges** | Earn 🥉🥈🥇 badges as you complete your learning roadmap |
| 📊 **Quiz History Dashboard** | Track your quiz performance and improvement over time |
| 📥 **PDF Export** | Download your personalized roadmap as a PDF report |
| 💾 **Persistent Storage** | Student profiles, roadmaps, and progress saved via SQLite |

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) — pure Python, no HTML/CSS/JS required
- **AI Engine:** [Google Gemini API](https://ai.google.dev/) (`google-genai` SDK) — powers skill analysis, roadmap generation, quizzes, and chat
- **Database:** SQLite — lightweight persistence for student data
- **PDF Generation:** `fpdf2`
- **Data Handling:** `pandas`
- **Config Management:** `python-dotenv`

---

## ⚙️ How It Works

```
[Student Profile Input]
        ↓
[Gemini AI — Skill Gap Analysis]  →  Strengths & Missing Skills identified
        ↓
[Structured Roadmap Generator]    →  Week-by-week learning plan
        ↓
[Fuzzy-Matching Recommendation Engine]  →  Trusted free courses per skill gap
        ↓
[Interactive Tools]  →  AI Quiz Generator · Doubts Chatbot · Progress Tracker
```

1. **Input** — Student enters their name, current skills, target career role, and available study time
2. **Analysis** — Gemini AI evaluates the profile against real industry requirements for that role
3. **Roadmap** — A structured, week-by-week study plan is generated automatically
4. **Recommendations** — Missing skills are matched to trusted free courses using a fuzzy-matching engine
5. **Practice** — Students can generate quizzes and track their scores over time
6. **Support** — An AI chatbot is available anytime to resolve doubts
7. **Tracking** — Students mark weeks complete, earn badges, and can export their roadmap as a PDF

---

## 📂 Project Structure

```
├── app.py               # Streamlit UI — all pages/tabs
├── gemini.py             # Google Gemini API integration & prompt handling
├── prompts.py            # Structured AI prompt templates
├── recommendation.py     # Fuzzy-matching course recommendation engine
├── database.py           # SQLite persistence layer
├── pdf_export.py         # PDF roadmap generation
├── requirements.txt      # Python dependencies
├── runtime.txt            # Python version pin for deployment
├── .env.example           # Template for local environment variables
└── README.md
```

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Python 3.11+
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. Create and activate a virtual environment
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and add your API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### Run

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Community Cloud)

This app is deployed on **Streamlit Community Cloud**:

1. Push the repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account
3. Select the repository, branch `main`, and entry point `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
5. Deploy — the app will be live within minutes

> **Note:** SQLite data on Streamlit Cloud is not permanently persistent across app restarts. For production use at scale, migrating to a managed database (e.g., PostgreSQL/Supabase) is recommended.

---

## 🔮 Future Scope

- 📄 Resume/LinkedIn analyzer for automatic skill extraction
- 🎤 Mock interview simulator with real-time AI feedback
- 🗣️ Voice-based doubt solving
- 🏆 Peer comparison and gamified leaderboards
- 🔗 Live integration with YouTube/Coursera APIs for real-time course discovery
- 🌐 Multi-language support (Hindi + English)
- 🔐 User authentication for secure multi-user access

---

## 👤 Author

**[kanak chauhan]**
[B.tech Cse(AI/ML)] 

📧 [your.email@example.com](chauhankanak822@gmail.com) · 🔗 [LinkedIn](www.linkedin.com/in/kanak-chauhan-7ba173366) · 💻 [GitHub](https://github.com/chauhankanak90)

---

<div align="center">

⭐ If you found this project useful, consider giving it a star!

</div>