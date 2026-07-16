# 🧭 CareerCopilot AI

An AI-powered career guidance platform. Log in, upload your resume once, and
get: an accurate ATS score with an exact points breakdown, a full extracted
profile (name, contact, education, skills, hobbies, achievements,
certificates), which job roles you already match and by how much, a skill
gap analysis for any target role, and a month-by-month learning roadmap with
real course/YouTube links — all flowing from a clean left sidebar, the same
way Claude's interface works.

**Important — how scoring works:** ATS scoring, resume field extraction,
and role/skill matching are all done with deterministic rules and a
built-in skills/roles database (`backend/data/skills_db.py`), **not** by an
LLM. This means the same resume always produces the same, explainable score
— it does not depend on having an Anthropic API key configured. The LLM
(`ai/llm.py`) is only used for the optional Job Matcher, Mock Interview, and
AI Chat pages, which fall back to MOCK MODE without an API key.

Built around the three team handbooks:
- **Team Member 1 — AI Engineer**: `ai/` (LLM integration, prompts, recommendation logic)
- **Team Member 2 — Frontend/UI-UX**: `frontend/` (Streamlit app + pages)
- **Team Member 3 — Backend & Integration**: `backend/` (FastAPI, parser, database, reports)

---

## 📁 Project Structure

```
CareerCopilotAI/
├── ai/                        # AI Engineer's module (Team Member 1)
│   ├── llm.py                 # LLM client wrapper (Anthropic Claude + MOCK MODE)
│   ├── prompts.py             # All system prompts, centralized
│   ├── resume_analyzer.py     # ATS score, strengths, weaknesses
│   ├── career_engine.py       # Career recommendations
│   ├── skill_gap.py           # Current vs target-role skills
│   ├── roadmap.py             # Monthly learning roadmap
│   ├── job_match.py           # Resume vs job description
│   ├── interview.py           # Mock interview evaluation
│   ├── chat.py                # AI career chat
│   └── utils.py
│
├── backend/                   # Backend & Integration (Team Member 3)
│   ├── main.py                # FastAPI app entry point
│   ├── api/routes.py          # All API endpoints (incl. /signup, /login)
│   ├── data/skills_db.py      # Skills taxonomy, roles DB, real learning resources
│   ├── database/              # SQLite models + connection (users, resumes, etc.)
│   ├── parser/resume_parser.py # PDF text extraction + structured field extraction
│   ├── reports/                # PDF report generator
│   └── utils/auth.py          # Password hashing for login/signup
│
├── ai/ats_scorer.py           # Deterministic, explainable ATS scoring engine
├── ai/role_matcher.py         # Deterministic skill-to-role matching
├── ai/roadmap_builder.py      # Deterministic roadmap with real resource links
│
├── frontend/                  # Frontend & UI/UX (Team Member 2)
│   ├── app.py                 # Landing page + Login / Sign Up
│   ├── pages/                 # 1 file per page (Dashboard, Resume Analyzer, ...)
│   ├── components/ui_helpers.py  # Left sidebar nav, auth helpers, API wrappers
│   └── assets/style.css       # Dark blue theme
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Enable real AI output:**
   Copy `.env.example` to `.env` and add your Anthropic API key:
   ```bash
   cp .env.example .env
   # then edit .env and set ANTHROPIC_API_KEY=sk-ant-...
   ```
   Without a key, the app runs in **MOCK MODE** — every AI module still
   returns realistic placeholder JSON, so the full app works end-to-end
   for demos/testing without any billing.

---

## ▶️ Running the App

You need **two terminals** — one for the backend API, one for the frontend UI.

**Terminal 1 — Backend (FastAPI):**
```bash
uvicorn backend.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

**Terminal 2 — Frontend (Streamlit):**
```bash
streamlit run frontend/app.py
```
Visit `http://localhost:8501` in your browser.

---

## 🧠 AI Flow (per the AI Engineer Handbook)

```
User Input → Backend structures data → Prompt Builder → LLM API
→ Structured JSON Response → Backend Validation → Frontend Display
```

Every AI module (`ai/*.py`) follows the same pattern:
1. Build a clean prompt from structured input (`ai/utils.py`)
2. Call the LLM with a role-specific system prompt (`ai/prompts.py`)
3. Parse and validate the JSON response (`ai/llm.py: safe_json_parse`)

---

## 🔌 API Endpoints (per the Backend Handbook)

| Method | Endpoint                  | Description                          |
|--------|----------------------------|---------------------------------------|
| POST   | `/signup`                  | Create a user account (username/password) |
| POST   | `/login`                   | Log in and get a `user_id`            |
| POST   | `/upload_resume`           | Parse + deterministically score a resume PDF, return full profile |
| GET    | `/roles`                   | List all roles in the built-in database |
| POST   | `/career_recommendation`   | Rank best-fit roles from a skills list |
| POST   | `/skill_gap`               | Matched/missing skills for one target role |
| POST   | `/roadmap`                 | Month-by-month roadmap with real resource links |
| POST   | `/job_match`                | Compare resume vs a pasted job description (LLM) |
| POST   | `/mock_interview`           | Evaluate a mock interview answer (LLM) |
| POST   | `/ai_chat`                  | AI career guidance chat (LLM)         |
| POST   | `/generate_report`          | Generate a downloadable PDF report    |
| GET    | `/download_report`          | Download a previously generated PDF   |
| GET    | `/user_profile`             | Get profile, resumes, and history     |

---

## 🗄️ Database Schema (SQLite)

```
users(id, username, password_hash, name, email, college, branch)
resumes(id, user_id, resume_score, file_path, parsed_profile_json)
reports(id, user_id, report_path)
history(id, user_id, action, timestamp)
```

SQLite file is created automatically at `backend/database/careercopilot.db`
on first run — no manual setup needed.

---

## 🎨 Frontend Flow

Login/Sign Up → Dashboard → Resume Analyzer (full profile + ATS score) →
Career Match → Skill Gap → Learning Roadmap → Job Matcher → Mock Interview →
AI Chat → Profile → Report

Navigation is a **persistent left sidebar** (`sidebar_nav()` in
`ui_helpers.py`), not a row of buttons — the same pattern as Claude's own
interface. Every protected page starts with `require_login()`, which sends
unauthenticated visitors back to the login screen on `app.py`.

Theme: dark blue background, white cards, blue buttons, progress bars —
implemented in `frontend/assets/style.css` and `.streamlit/config.toml`.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI + Uvicorn
- **Database:** SQLite
- **AI:** Anthropic Claude API (with offline MOCK MODE fallback)
- **PDF Parsing:** pypdf
- **PDF Report Generation:** fpdf2

---

## 🚀 Next Steps / Future Improvements

- Swap SQLite for Postgres/Firebase for multi-user production use
- Add password reset / email verification to the auth flow
- Stream AI chat responses instead of waiting for the full reply
- Add resume history comparison (score over time, on the Profile page)
- Deploy backend (Render/Railway) + frontend (Streamlit Community Cloud)
- Expand `backend/data/skills_db.py` with more roles/skills as needed —
  it's a plain Python dict, easy to extend without touching any logic
