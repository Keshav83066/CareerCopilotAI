"""
llm.py
------
Central LLM client wrapper for CareerCopilot AI.

Handles:
- Connecting to the LLM provider (Anthropic Claude by default)
- Sending prompts and receiving responses
- Falling back to a MOCK mode when no API key is configured, so the rest
  of the app can be built/tested without live API calls or billing.

To go live: add ANTHROPIC_API_KEY to a .env file (see .env.example) and
install `python-dotenv` + `anthropic` (already in requirements.txt).
"""

import os
import json

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None

# Loads .env into environment if python-dotenv is installed (optional).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------
# You are NOT locked into Anthropic. Set LLM_PROVIDER in your .env to pick
# which service to call. Every provider below except "anthropic" is called
# through the OpenAI-compatible chat-completions format (openai package),
# just pointed at a different base_url + api key + model, so switching
# providers is just an env-var change, no code change needed.
#
#   LLM_PROVIDER=anthropic   -> uses ANTHROPIC_API_KEY (Claude, native SDK)
#   LLM_PROVIDER=openai      -> uses OPENAI_API_KEY (gpt-4o-mini, etc.)
#   LLM_PROVIDER=groq        -> uses GROQ_API_KEY (fast, free-tier friendly)
#   LLM_PROVIDER=openrouter  -> uses OPENROUTER_API_KEY (100+ hosted models)
#   LLM_PROVIDER=gemini      -> uses GEMINI_API_KEY (Google, OpenAI-compat endpoint)
#
# If LLM_PROVIDER isn't set, we auto-detect: the first provider below whose
# API key is present in the environment is used. If none are present, the
# app runs in MOCK_MODE (deterministic placeholder JSON, no billing).

PROVIDERS = {
    "anthropic":  {"key_env": "ANTHROPIC_API_KEY", "base_url": None,
                   "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")},
    "openai":     {"key_env": "OPENAI_API_KEY", "base_url": "https://api.openai.com/v1",
                   "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")},
    "groq":       {"key_env": "GROQ_API_KEY", "base_url": "https://api.groq.com/openai/v1",
                   "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")},
    "openrouter": {"key_env": "OPENROUTER_API_KEY", "base_url": "https://openrouter.ai/api/v1",
                   "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")},
    "gemini":     {"key_env": "GEMINI_API_KEY", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                   "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash")},
}


def _detect_provider() -> str | None:
    forced = os.getenv("LLM_PROVIDER", "").strip().lower()
    if forced:
        return forced if forced in PROVIDERS else None
    for name, cfg in PROVIDERS.items():
        if os.getenv(cfg["key_env"]):
            return name
    return None


ACTIVE_PROVIDER = _detect_provider()
MOCK_MODE = ACTIVE_PROVIDER is None
MODEL_NAME = PROVIDERS[ACTIVE_PROVIDER]["model"] if ACTIVE_PROVIDER else None


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    """
    Send a system + user prompt to whichever LLM provider is configured
    (see PROVIDERS above) and return the raw text response.
    Falls back to a mock JSON response if no provider API key is set, or if
    the live call fails for any reason (bad key, no credits, network issue,
    etc.) - callers always get back valid JSON instead of an unhandled
    exception that would otherwise surface to the user as a raw 500 error.
    """
    if MOCK_MODE:
        return _mock_response(system_prompt, user_prompt)

    cfg = PROVIDERS[ACTIVE_PROVIDER]
    api_key = os.getenv(cfg["key_env"])

    try:
        if ACTIVE_PROVIDER == "anthropic":
            if anthropic is None:
                raise RuntimeError("The 'anthropic' package is not installed.")
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=cfg["model"],
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        else:
            # openai, groq, openrouter, gemini - all speak the OpenAI
            # chat-completions API, just with a different base_url/key/model.
            if openai is None:
                raise RuntimeError("The 'openai' package is not installed (needed for this provider).")
            client = openai.OpenAI(api_key=api_key, base_url=cfg["base_url"])
            try:
                # Ask the model to guarantee pure JSON output (supported by
                # OpenAI, Groq, and most OpenAI-compatible providers). This
                # stops the model from wrapping the JSON in extra prose like
                # "Sure! Here's the answer:" which would otherwise break
                # safe_json_parse().
                response = client.chat.completions.create(
                    model=cfg["model"],
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
            except Exception:
                # Some providers/models reject response_format - fall back
                # to a plain call without it; safe_json_parse's regex
                # fallback (below) will still try to salvage the JSON.
                response = client.chat.completions.create(
                    model=cfg["model"],
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
            return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "error": True,
            "note": f"Live AI call to '{ACTIVE_PROVIDER}' failed ({type(e).__name__}: {e}). Check that "
                     f"{cfg['key_env']} in .env is correct and that the account has available credits, then try again.",
            "summary": "Could not reach the AI service right now.",
            "reply": "Sorry, I couldn't reach the AI service just now - please check the API key/credits and try again.",
            "feedback": "Could not reach the AI service right now - please try again in a moment.",
            "score": 0,
            "improved_answer": "",
            "match_score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
        })


# Field names build_user_prompt() is actually called with across the app's
# LIVE (wired-into-routes.py) AI modules: job_match.py, interview.py, chat.py.
# Used by _parse_user_prompt below to tell "this line starts a new field"
# apart from "this line is part of a multi-line field's value".
_KNOWN_PROMPT_FIELDS = {
    "resume_text", "job_description",       # job_match.py
    "question", "candidate_answer",          # interview.py
    "conversation_history", "user_message",  # chat.py
}


def _parse_user_prompt(user_prompt: str) -> dict:
    """Reverse ai/utils.py:build_user_prompt's 'key: value' lines back into a dict.

    build_user_prompt joins a dict into 'key: value' lines, but values such as
    resume_text or conversation_history are themselves multi-line - a naive
    'split every line on its first colon' parser would treat each line inside
    those values as its own new key, truncating them to just their first line.
    Instead, only a line whose key is a recognized top-level field name starts
    a new field; every other line (including ones that happen to contain a
    colon, e.g. a resume's own 'Email:' label) is appended to whichever field
    is currently being accumulated, so multi-line values survive intact.
    """
    data = {}
    current_key = None
    for line in user_prompt.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            if k in _KNOWN_PROMPT_FIELDS:
                data[k] = v.strip()
                current_key = k
                continue
        if current_key is not None:
            data[current_key] = (data[current_key] + "\n" + line).rstrip()
    return data


def _mock_response(system_prompt: str, user_prompt: str) -> str:
    """
    MOCK MODE fallback used only when no ANTHROPIC_API_KEY is configured.
    NOTE: this is a rough, keyword-based stand-in so the app is testable
    without billing - it is NOT a substitute for the real model. Set
    ANTHROPIC_API_KEY in .env for real, accurate AI output.
    Each branch below at least reacts to the actual input instead of
    returning one frozen answer for every question.
    """
    from backend.data.skills_db import extract_skills

    data = _parse_user_prompt(user_prompt)
    sp = system_prompt.lower()

    if "resume-to-job-description" in sp:
        resume_skills = set(extract_skills(data.get("resume_text", "")))
        jd_skills = set(extract_skills(data.get("job_description", "")))
        matched = sorted(resume_skills & jd_skills)
        missing = sorted(jd_skills - resume_skills)
        score = round(len(matched) / len(jd_skills) * 100) if jd_skills else 50
        summary = (
            f"Your resume covers {len(matched)} of the {len(jd_skills)} skills this job description mentions."
            if jd_skills else
            "Couldn't detect specific skills in the job description text — paste the full JD for a real comparison."
        )
        return json.dumps({
            "mock_mode": True,
            "note": "MOCK MODE: this is a simple keyword-overlap estimate, not an LLM answer. Set an API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, etc.) in .env for a real comparison.",
            "match_score": score, "matched_keywords": matched, "missing_keywords": missing, "summary": summary,
        })

    if "mock interview evaluator" in sp:
        question = data.get("question", "this question")
        answer = data.get("candidate_answer", "")
        wc = len(answer.split())
        if wc == 0:
            score, feedback = 0, "You haven't written an answer yet — add a few sentences so there's something to evaluate."
        elif wc < 15:
            score, feedback = 4, f"Your answer is quite short ({wc} words). Add a specific example or measurable result."
        elif wc < 40:
            score, feedback = 6, "Decent start — expand with one concrete example (a project, number, or outcome)."
        else:
            score, feedback = 8, "Good level of detail — keep it focused and end with a clear takeaway."
        return json.dumps({
            "mock_mode": True,
            "note": "MOCK MODE: score is based on answer length only, not real content quality. Set an API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, etc.) in .env for real grading.",
            "score": score, "feedback": feedback,
            "improved_answer": f"For \"{question}\", use the STAR method: describe the Situation, your Task, the Action you took, "
                                f"and the measurable Result — specific to your own experience.",
        })

    if "career guidance assistant" in sp:
        message = data.get("user_message", "")
        return json.dumps({
            "mock_mode": True,
            "reply": f"(MOCK MODE — no live answer yet) You asked: \"{message}\". "
                     f"Set an API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, etc.) in .env to get a real, tailored reply to this specific question.",
        })

    # Fallback for any other prompt type
    return json.dumps({
        "mock_mode": True,
        "note": "Set an API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, etc.) in a .env file to get real AI output.",
        "summary": "MOCK MODE placeholder response.",
    })


def safe_json_parse(raw_text: str) -> dict:
    """
    Safely parse LLM output into JSON, stripping markdown code fences if present.
    Falls back to an error dict rather than crashing the app.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Some models (especially smaller/free ones) wrap the JSON in extra
    # prose despite instructions ("Sure! Here's the answer: {...}"). Try to
    # salvage the JSON object embedded in the text before giving up.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return {"error": "Failed to parse LLM response as JSON", "raw": raw_text}