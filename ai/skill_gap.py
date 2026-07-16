"""
skill_gap.py
------------
AI Module: Skill Gap Analysis.
Compares a candidate's current skills against a target role's requirements.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import SKILL_GAP_PROMPT
from ai.utils import build_user_prompt


def analyze_skill_gap(current_skills: str, target_role: str) -> dict:
    """Return matched skills, missing skills, and a priority order to learn them."""
    user_prompt = build_user_prompt({
        "current_skills": current_skills,
        "target_role": target_role,
    })
    raw = call_llm(SKILL_GAP_PROMPT, user_prompt)
    return safe_json_parse(raw)
