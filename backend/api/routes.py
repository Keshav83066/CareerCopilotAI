"""
routes.py
---------
All API endpoints for the CareerCopilot AI backend.

Core endpoints:
  POST /signup, /login              - authentication
  POST /upload_resume                - parse + score a resume (deterministic + optional LLM commentary)
  POST /career_recommendation        - rank best-fit roles from a skills list
  POST /skill_gap                    - matched/missing skills for one target role
  POST /roadmap                      - month-by-month learning plan with real links
  POST /job_match                    - resume vs pasted job description
  POST /generate_report              - downloadable PDF summary
  GET  /user_profile                 - profile + resume history + activity log
  GET  /roles                        - list of supported roles (for dropdowns)
"""

import json
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from backend.database.db import get_connection
from backend.database.models import (
    CareerRecommendationRequest, SkillGapRequest, RoadmapRequest,
    JobMatchRequest, InterviewRequest, ChatRequest, UserCreateRequest,
    SignupRequest, LoginRequest,
)
from backend.parser.resume_parser import extract_text_from_pdf, parse_resume
from backend.reports.report_generator import generate_report, REPORTS_DIR
from backend.utils.helpers import log_action
from backend.utils.auth import hash_password, verify_password
from backend.data.skills_db import ROLES, extract_skills

from ai.ats_scorer import score_resume
from ai.role_matcher import rank_roles, skill_gap_for_role
from ai.roadmap_builder import build_roadmap, suggested_months
from ai.career_engine import recommend_careers
from ai.job_match import match_job
from ai.interview import evaluate_answer
from ai.chat import chat_reply
from ai.llm import MOCK_MODE

router = APIRouter()


# ---------------------------------------------------------------- Auth ----

@router.post("/signup")
def signup(payload: SignupRequest):
    """Create a new user account."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (payload.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already taken")

    cur.execute(
        "INSERT INTO users (username, password_hash, name, email, college, branch) VALUES (?, ?, ?, ?, ?, ?)",
        (payload.username, hash_password(payload.password), payload.name, payload.email, payload.college, payload.branch),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"user_id": user_id, "username": payload.username, "name": payload.name}


@router.post("/login")
def login(payload: LoginRequest):
    """Authenticate an existing user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (payload.username,))
    user = cur.fetchone()
    conn.close()

    if not user or not user["password_hash"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"user_id": user["id"], "username": user["username"], "name": user["name"]}


@router.post("/create_user")
def create_user(payload: UserCreateRequest):
    """Legacy quick-profile creation (kept for backward compatibility)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, college, branch) VALUES (?, ?, ?)",
        (payload.name, payload.college, payload.branch),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"user_id": user_id}


# ------------------------------------------------------------- Resume -----

@router.post("/upload_resume")
async def upload_resume(user_id: int = Form(...), file: UploadFile = File(...)):
    """Validate + parse an uploaded resume PDF, score it deterministically,
    and return the full structured profile."""
    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text or len(resume_text.split()) < 15:
        raise HTTPException(
            status_code=400,
            detail="Could not extract readable text from this PDF. Please upload a text-based PDF resume (not a scanned image).",
        )

    parsed = parse_resume(resume_text)
    ats_result = score_resume(resume_text, parsed)
    role_matches = rank_roles(parsed["skills"], top_n=5)

    analysis = {
        **ats_result,
        "extracted_skills": parsed["skills"],
        "extracted_education": parsed["education"],
        "experience_summary": (
            f"{parsed['experience_years']} year(s) of experience detected." if parsed["experience_years"]
            else "Experience duration could not be confidently detected."
        ),
        "mock_mode": MOCK_MODE,
    }

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (user_id, resume_score, file_path, parsed_profile_json) VALUES (?, ?, ?, ?)",
        (user_id, ats_result["ats_score"], file.filename, json.dumps(parsed)),
    )
    conn.commit()
    log_action(conn, user_id, "upload_resume")
    conn.close()

    return {
        "resume_text": resume_text,
        "analysis": analysis,
        "profile": parsed,
        "role_matches": role_matches,
    }


# ------------------------------------------------------------- Careers ----

@router.get("/roles")
def list_roles():
    """Return all roles supported by the built-in matching database."""
    return {"roles": sorted(ROLES.keys())}


@router.post("/career_recommendation")
def career_recommendation(payload: CareerRecommendationRequest):
    """Return ranked career roles from the candidate's skills (deterministic),
    enriched with an LLM-written reason for each when a live API key is set."""
    candidate_skills = extract_skills(payload.skills) or [s.strip() for s in payload.skills.split(",") if s.strip()]
    ranked = rank_roles(candidate_skills, top_n=5)

    recommendations = []
    for r in ranked:
        reason = (
            f"You already have {len(r['matched_skills'])} of the key skills for this role"
            + (f" — missing: {', '.join(r['missing_skills'][:3])}." if r["missing_skills"] else ".")
        )
        recommendations.append({
            "role": r["role"],
            "match_score": r["match_score"],
            "reason": reason,
            "matched_skills": r["matched_skills"],
            "missing_skills": r["missing_skills"],
        })

    conn = get_connection()
    log_action(conn, payload.user_id, "career_recommendation")
    conn.close()
    return {"recommendations": recommendations}


@router.post("/skill_gap")
def skill_gap(payload: SkillGapRequest):
    """Return matched/missing skills for a target role (deterministic DB match)."""
    candidate_skills = extract_skills(payload.current_skills) or [s.strip() for s in payload.current_skills.split(",") if s.strip()]
    result = skill_gap_for_role(candidate_skills, payload.target_role.strip())

    conn = get_connection()
    log_action(conn, payload.user_id, "skill_gap")
    conn.close()
    return result


@router.post("/roadmap")
def roadmap(payload: RoadmapRequest):
    """Return a personalized, resource-linked monthly learning roadmap."""
    missing = [s.strip() for s in payload.missing_skills.split(",") if s.strip()]
    result = build_roadmap(missing, payload.months)

    conn = get_connection()
    log_action(conn, payload.user_id, "roadmap")
    conn.close()
    return result


@router.get("/suggested_months")
def get_suggested_months(missing_skills: str):
    skills = [s.strip() for s in missing_skills.split(",") if s.strip()]
    return {"months": suggested_months(skills)}


@router.post("/job_match")
def job_match(payload: JobMatchRequest):
    """Compare resume text against a job description."""
    result = match_job(payload.resume_text, payload.job_description)
    conn = get_connection()
    log_action(conn, payload.user_id, "job_match")
    conn.close()
    return result


@router.post("/mock_interview")
def mock_interview(payload: InterviewRequest):
    """Evaluate a mock interview answer and return score + feedback."""
    result = evaluate_answer(payload.question, payload.answer)
    conn = get_connection()
    log_action(conn, payload.user_id, "mock_interview")
    conn.close()
    return result


@router.post("/ai_chat")
def ai_chat(payload: ChatRequest):
    """Return a conversational AI reply for the career chat page."""
    result = chat_reply(payload.message, payload.history)
    conn = get_connection()
    log_action(conn, payload.user_id, "ai_chat")
    conn.close()
    return result


@router.post("/generate_report")
def report(user_id: int = Form(...), data: str = Form(...)):
    """Generate a downloadable PDF report from a JSON-encoded results dict."""
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in 'data' field")

    file_path = generate_report(user_id, data_dict)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reports (user_id, report_path) VALUES (?, ?)",
        (user_id, file_path),
    )
    conn.commit()
    log_action(conn, user_id, "generate_report")
    conn.close()

    return {"report_path": file_path}


@router.get("/download_report")
def download_report(path: str):
    """Stream a previously generated PDF report back to the client.
    Only files inside backend/reports/generated are ever served, to prevent
    path traversal (e.g. ?path=/etc/passwd or ?path=../../.env)."""
    requested = os.path.realpath(path)
    allowed_root = os.path.realpath(REPORTS_DIR)
    if os.path.commonpath([requested, allowed_root]) != allowed_root:
        raise HTTPException(status_code=400, detail="Invalid report path.")
    if not os.path.isfile(requested):
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(requested, media_type="application/pdf", filename=os.path.basename(requested))


@router.get("/user_profile")
def user_profile(user_id: int):
    """Return a user's profile, resume history, and activity history."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cur.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
    resumes = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM history WHERE user_id = ?", (user_id,))
    history = [dict(h) for h in cur.fetchall()]

    conn.close()
    return {"user": dict(user), "resumes": resumes, "history": history}
