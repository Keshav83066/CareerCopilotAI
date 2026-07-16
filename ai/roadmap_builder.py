"""
roadmap_builder.py
-------------------
Builds a month-by-month learning roadmap for a list of missing skills,
with real, curated learning resources (official docs, free courses,
YouTube search links) pulled from backend/data/skills_db.py.

This is fully deterministic - no LLM required - so it always produces a
concrete, usable plan, and it scales the number of months to how much
there actually is to learn if the user doesn't specify a timeframe.
"""

import math
from backend.data.skills_db import get_resources

# Rough weeks-to-working-proficiency per skill (used to size the roadmap)
DEFAULT_WEEKS_PER_SKILL = 3


def suggested_months(missing_skills: list) -> int:
    """Recommend a realistic timeframe based on how many skills are missing."""
    if not missing_skills:
        return 1
    total_weeks = len(missing_skills) * DEFAULT_WEEKS_PER_SKILL
    months = max(1, min(12, math.ceil(total_weeks / 4)))
    return months


def _resources_for(skill: str) -> list:
    return [f"{skill} — {label}: {url}" for label, url in get_resources(skill)[:2]]


def build_roadmap(missing_skills: list, months: int = None) -> dict:
    """
    Spread the given missing skills across `months` months (auto-computed
    if not provided), with real resources and a concrete milestone for
    each month. Always produces exactly `months` entries:

    - If there are at least as many skills as months, multiple skills are
      bucketed into each month (learn several things in parallel).
    - If there are MORE months than skills (a deliberately slower,
      user-chosen pace), each skill is spread across a block of consecutive
      months instead of being crammed into the first few months and leaving
      the rest of the requested timeframe empty: the first month covers the
      fundamentals (with resources), and any additional months for that
      skill are deepen/practice months.
    """
    missing_skills = [s for s in missing_skills if s]
    if not missing_skills:
        return {
            "roadmap": [],
            "total_months": 0,
            "note": "No missing skills to plan for — you already match the target role well!",
        }

    if not months or months < 1:
        months = suggested_months(missing_skills)

    n = len(missing_skills)
    roadmap = []

    if months <= n:
        # Distribute skills across months as evenly as possible (1+ skills/month).
        buckets = [[] for _ in range(months)]
        for i, skill in enumerate(missing_skills):
            buckets[i % months].append(skill)

        for month_idx, skills_this_month in enumerate(buckets, start=1):
            if not skills_this_month:
                continue
            resources = []
            for skill in skills_this_month:
                resources.extend(_resources_for(skill))
            roadmap.append({
                "month": month_idx,
                "focus": ", ".join(skills_this_month),
                "resources": resources,
                "milestone": f"Be able to confidently use {', '.join(skills_this_month)} in a small project "
                             f"or mock interview by the end of month {month_idx}.",
            })
    else:
        # More months than skills: give each skill a multi-month block so the
        # full requested timeframe is actually used, at a slower/deeper pace.
        base = months // n
        remainder = months - base * n
        month_idx = 1
        for i, skill in enumerate(missing_skills):
            span = base + (1 if i < remainder else 0)
            for j in range(span):
                if j == 0:
                    resources = _resources_for(skill)
                    milestone = (f"Learn the fundamentals of {skill} and build one small project "
                                 f"or exercise using it by the end of month {month_idx}.")
                else:
                    resources = [f"{skill} — revisit the resources from month {month_idx - j} "
                                 f"and apply {skill} in a slightly bigger project."]
                    milestone = (f"Deepen your {skill} skills with continued practice; be ready to "
                                 f"confidently discuss/use {skill} in an interview by the end of month {month_idx}.")
                roadmap.append({
                    "month": month_idx,
                    "focus": skill,
                    "resources": resources,
                    "milestone": milestone,
                })
                month_idx += 1

    return {
        "roadmap": roadmap,
        "total_months": len(roadmap),
        "note": "",
    }
