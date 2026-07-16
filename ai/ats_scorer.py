"""
ats_scorer.py
-------------
Deterministic, rule-based ATS (Applicant Tracking System) scorer.

Unlike a pure LLM call, this always reflects the ACTUAL resume content, so
the same resume always gets the same score, and a genuinely stronger resume
always scores higher. This is the primary score shown to the user.
An LLM (when a real API key is configured) is used only to add extra
qualitative commentary on top of this score - never to replace it.
"""

import re

ACTION_VERBS = [
    "led", "built", "created", "developed", "designed", "managed", "improved",
    "increased", "decreased", "reduced", "optimized", "launched", "implemented",
    "achieved", "delivered", "automated", "analyzed", "coordinated", "spearheaded",
    "mentored", "streamlined", "engineered", "architected", "deployed",
]

WEAK_PHRASES = ["responsible for", "worked on", "helped with", "tasked with"]


def _has_quantified_results(text: str) -> bool:
    return bool(re.search(r"\d+%|\$\d|\d+\s?(x|times)\b|\d+\+", text))


def score_resume(resume_text: str, parsed: dict) -> dict:
    """
    Compute a 0-100 ATS score from concrete, explainable rules.
    Returns score plus a breakdown, strengths, weaknesses and suggestions.
    """
    text = resume_text or ""
    lower = text.lower()
    word_count = len(text.split())

    breakdown = {}
    strengths = []
    weaknesses = []
    suggestions = []

    # 1) Contact info completeness (15 pts)
    contact_pts = 0
    if parsed.get("email"):
        contact_pts += 6
    else:
        weaknesses.append("No email address detected — recruiters and ATS bots need this to reach you.")
        suggestions.append("Add a professional email address near the top of your resume.")
    if parsed.get("phone"):
        contact_pts += 5
    else:
        weaknesses.append("No phone number detected.")
        suggestions.append("Add a phone number so recruiters can contact you directly.")
    if parsed.get("linkedin") or parsed.get("github"):
        contact_pts += 4
    else:
        suggestions.append("Add your LinkedIn and/or GitHub profile link.")
    breakdown["contact_info"] = contact_pts
    if contact_pts >= 13:
        strengths.append("Contact details are complete and easy for recruiters/ATS to find.")

    # 2) Section completeness (25 pts)
    sections_found = set(parsed.get("sections_found", []))
    important_sections = ["education", "experience", "skills"]
    section_pts = 0
    for s in important_sections:
        if s in sections_found:
            section_pts += 6
        else:
            weaknesses.append(f"No clearly labeled '{s.title()}' section found.")
            suggestions.append(f"Add a clearly labeled '{s.title()}' section header so ATS software can parse it correctly.")
    if "projects" in sections_found or "certifications" in sections_found:
        section_pts += 7
    else:
        suggestions.append("Consider adding a 'Projects' or 'Certifications' section to strengthen your profile.")
    breakdown["structure"] = min(section_pts, 25)
    if breakdown["structure"] >= 18:
        strengths.append("Resume is well-structured with clearly labeled sections.")

    # 3) Skills detected (20 pts)
    skills = parsed.get("skills", [])
    skill_pts = min(len(skills) * 2, 20)
    breakdown["skills_detected"] = skill_pts
    if len(skills) >= 6:
        strengths.append(f"{len(skills)} relevant skills were clearly detectable in the resume text.")
    else:
        weaknesses.append("Very few recognizable skills were found in the resume text.")
        suggestions.append("List specific tools/technologies explicitly (e.g. 'Python', 'SQL') rather than only describing duties in prose.")

    # 4) Impact language: action verbs + quantified results (25 pts)
    action_verb_hits = sum(1 for v in ACTION_VERBS if re.search(r"\b" + v + r"\b", lower))
    action_pts = min(action_verb_hits * 2, 14)
    quant_pts = 11 if _has_quantified_results(text) else 0
    breakdown["impact_language"] = action_pts + quant_pts
    if action_verb_hits >= 4:
        strengths.append("Uses strong action verbs (led, built, improved, etc.) to describe work.")
    else:
        weaknesses.append("Limited use of strong action verbs.")
        suggestions.append("Start bullet points with action verbs like 'Built', 'Led', 'Improved' instead of 'Responsible for'.")
    if quant_pts:
        strengths.append("Includes quantified, measurable achievements (numbers/percentages).")
    else:
        weaknesses.append("No quantified/measurable achievements found (e.g. '%', numbers, results).")
        suggestions.append("Add measurable impact to bullet points, e.g. 'Improved load time by 30%' or 'Managed a team of 5'.")

    if any(p in lower for p in WEAK_PHRASES):
        suggestions.append("Replace passive phrases like 'responsible for' / 'worked on' with strong action verbs.")

    # 5) Length / density (15 pts)
    if 300 <= word_count <= 900:
        length_pts = 15
        strengths.append("Resume length is appropriate (not too short, not overloaded).")
    elif word_count < 300:
        length_pts = max(0, int(word_count / 300 * 15))
        weaknesses.append("Resume seems too short — ATS and recruiters may see it as incomplete.")
        suggestions.append("Expand on your projects/experience with 2-3 bullet points each.")
    else:
        length_pts = 10
        weaknesses.append("Resume is quite long — may be hard for recruiters to skim quickly.")
        suggestions.append("Trim to the most relevant 1-2 pages of content for best ATS + recruiter results.")
    breakdown["length_and_density"] = length_pts

    total = sum(breakdown.values())
    total = max(0, min(100, round(total)))

    # De-duplicate suggestion/weakness lists while preserving order
    def _dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {
        "ats_score": total,
        "score_breakdown": breakdown,
        "strengths": _dedupe(strengths) or ["Resume was successfully parsed."],
        "weaknesses": _dedupe(weaknesses) or ["No major issues detected."],
        "suggestions": _dedupe(suggestions) or ["Keep your resume updated with your latest achievements."],
    }
