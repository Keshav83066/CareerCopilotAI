"""
role_matcher.py
----------------
Deterministic matching between a candidate's extracted skills and a
database of common job roles (backend/data/skills_db.py).

Used for:
- "Which roles fit me best" (Career Recommendation page)
- "What am I missing for role X" (Skill Gap page)
"""

from backend.data.skills_db import ROLES


def _match_pct(candidate_skills: set, required: list, nice_to_have: list) -> dict:
    required_set = set(required)
    nice_set = set(nice_to_have)

    matched_required = sorted(candidate_skills & required_set)
    missing_required = sorted(required_set - candidate_skills)
    matched_nice = sorted(candidate_skills & nice_set)
    missing_nice = sorted(nice_set - candidate_skills)

    # required skills weigh 75% of the score, nice-to-have 25%
    req_score = (len(matched_required) / len(required_set) * 75) if required_set else 75
    nice_score = (len(matched_nice) / len(nice_set) * 25) if nice_set else 25
    match_score = round(req_score + nice_score)

    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_nice_to_have": matched_nice,
        "missing_nice_to_have": missing_nice,
        "match_score": min(match_score, 100),
    }


def rank_roles(candidate_skills: list, top_n: int = 5) -> list:
    """Return the top_n best-fit roles for a set of candidate skills."""
    cs = set(candidate_skills)
    results = []
    for role, spec in ROLES.items():
        info = _match_pct(cs, spec["required"], spec["nice_to_have"])
        results.append({
            "role": role,
            "match_score": info["match_score"],
            "matched_skills": info["matched_required"] + info["matched_nice_to_have"],
            "missing_skills": info["missing_required"],
            "missing_nice_to_have": info["missing_nice_to_have"],
        })
    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:top_n]


def skill_gap_for_role(candidate_skills: list, target_role: str) -> dict:
    """Return matched/missing skills + a priority order for one specific role.
    If the role isn't in the database, do a best-effort fuzzy match on name."""
    cs = set(candidate_skills)

    spec = ROLES.get(target_role)
    if spec is None:
        # fuzzy: case-insensitive partial match
        for role_name, role_spec in ROLES.items():
            if target_role.strip().lower() in role_name.lower() or role_name.lower() in target_role.strip().lower():
                spec = role_spec
                target_role = role_name
                break

    if spec is None:
        return {
            "target_role": target_role,
            "matched_skills": sorted(cs),
            "missing_skills": [],
            "priority_order": [],
            "match_score": None,
            "note": "This role isn't in our built-in database yet, so we can only show your current skills. "
                    "Try one of the supported roles for a full gap analysis, or paste a job description "
                    "into the Job Matcher for a custom comparison.",
        }

    info = _match_pct(cs, spec["required"], spec["nice_to_have"])
    # Priority: missing required skills first (most critical), then missing nice-to-haves
    priority_order = info["missing_required"] + info["missing_nice_to_have"]

    return {
        "target_role": target_role,
        "matched_skills": info["matched_required"] + info["matched_nice_to_have"],
        "missing_skills": info["missing_required"] + info["missing_nice_to_have"],
        "priority_order": priority_order,
        "match_score": info["match_score"],
        "note": "",
    }
