"""
resume_analyzer.py
-------------------
AI Module: Resume Analyzer.
Analyzes resume text and returns an ATS score, strengths, weaknesses,
and improvement suggestions.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import RESUME_ANALYZER_PROMPT
from ai.utils import build_user_prompt


def analyze_resume(resume_text: str) -> dict:
    """Run the resume through the LLM and return structured ATS analysis."""
    user_prompt = build_user_prompt({"resume_text": resume_text})
    raw = call_llm(RESUME_ANALYZER_PROMPT, user_prompt)
    return safe_json_parse(raw)
