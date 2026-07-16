"""
interview.py
------------
AI Module: Mock Interview Evaluation.
Scores a candidate's answer to an interview question and gives feedback.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import INTERVIEW_PROMPT
from ai.utils import build_user_prompt


def evaluate_answer(question: str, answer: str) -> dict:
    """Return a 0-10 score, feedback, and an improved example answer."""
    user_prompt = build_user_prompt({
        "question": question,
        "candidate_answer": answer,
    })
    raw = call_llm(INTERVIEW_PROMPT, user_prompt)
    return safe_json_parse(raw)
