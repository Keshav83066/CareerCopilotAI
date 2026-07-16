"""
roadmap.py
----------
AI Module: Learning Roadmap Generator.
Builds a personalized monthly learning plan to close identified skill gaps.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import ROADMAP_PROMPT
from ai.utils import build_user_prompt


def generate_roadmap(missing_skills: str, months: int = 3) -> dict:
    """Return a month-by-month roadmap covering the given missing skills."""
    user_prompt = build_user_prompt({
        "missing_skills": missing_skills,
        "timeframe_months": months,
    })
    raw = call_llm(ROADMAP_PROMPT, user_prompt)
    return safe_json_parse(raw)
