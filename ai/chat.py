"""
chat.py
-------
AI Module: AI Chat (Career Guidance).
Free-form conversational career guidance assistant.
"""

from ai.llm import call_llm, safe_json_parse
from ai.prompts import CHAT_PROMPT
from ai.utils import build_user_prompt


def chat_reply(message: str, history: list = None) -> dict:
    """Return an AI reply given the latest user message and prior chat history."""
    history = history or []
    context = "\n".join(f"{h.get('role')}: {h.get('content')}" for h in history)
    user_prompt = build_user_prompt({
        "conversation_history": context,
        "user_message": message,
    })
    raw = call_llm(CHAT_PROMPT, user_prompt)
    return safe_json_parse(raw)
