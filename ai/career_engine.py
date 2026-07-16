"""
career_engine.py
-----------------
AI Module: Career Recommendation Engine.
Suggests best-fit career roles based on skills, education and interests.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import CAREER_RECOMMENDATION_PROMPT
from ai.utils import build_user_prompt


def recommend_careers(skills: str, education: str, interests: str) -> dict:
    """Return a ranked list of recommended career roles with reasons."""
    user_prompt = build_user_prompt({
        "skills": skills,
        "education": education,
        "interests": interests,
    })
    raw = call_llm(CAREER_RECOMMENDATION_PROMPT, user_prompt)
    return safe_json_parse(raw)
