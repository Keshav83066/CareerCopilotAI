"""
utils.py
--------
Shared helper functions for AI modules.
"""


def build_user_prompt(data: dict) -> str:
    """
    Convert a structured data dict into a clean text block to send to the LLM
    as the user-turn content, following the handbook's prompt workflow:
    receive structured input -> build prompt -> call LLM.
    """
    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
