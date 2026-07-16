"""
models.py
---------
Pydantic models describing API request bodies for FastAPI validation.
"""

from pydantic import BaseModel
from typing import Optional, List


class UserCreateRequest(BaseModel):
    name: str
    college: str
    branch: str


class SignupRequest(BaseModel):
    username: str
    password: str
    name: str
    email: Optional[str] = ""
    college: Optional[str] = ""
    branch: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class CareerRecommendationRequest(BaseModel):
    user_id: int
    skills: str
    education: str
    interests: str


class SkillGapRequest(BaseModel):
    user_id: int
    current_skills: str
    target_role: str


class RoadmapRequest(BaseModel):
    user_id: int
    missing_skills: str
    months: int = 3


class JobMatchRequest(BaseModel):
    user_id: int
    resume_text: str
    job_description: str


class InterviewRequest(BaseModel):
    user_id: int
    question: str
    answer: str


class ChatRequest(BaseModel):
    user_id: int
    message: str
    history: Optional[List[dict]] = []
