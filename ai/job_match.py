"""
job_match.py
------------
AI Module: Job Description Match.
Compares resume text against a pasted job description.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import JOB_MATCH_PROMPT
from ai.utils import build_user_prompt


def match_job(resume_text: str, job_description: str) -> dict:
    """Return a match score plus matched/missing keywords and a summary."""
    user_prompt = build_user_prompt({
        "resume_text": resume_text,
        "job_description": job_description,
    })
    raw = call_llm(JOB_MATCH_PROMPT, user_prompt)
    return safe_json_parse(raw)
