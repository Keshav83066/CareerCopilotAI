"""
resume_parser.py
-----------------
Extracts raw text AND a structured profile from an uploaded resume PDF.

Structured extraction (name, contact info, education, skills, hobbies,
achievements, certifications, experience) is done with deterministic
regex/heuristics so it is accurate and consistent for every resume,
regardless of whether a live LLM API key is configured.
"""

import io
import re
from pypdf import PdfReader

from backend.data.skills_db import extract_skills

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?\d{10}\b|\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[^\s|,]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[^\s|,]+", re.IGNORECASE)

SECTION_HEADERS = {
    "education": ["education", "academic background", "academic qualification", "academics"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "internship"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "achievements": ["achievements", "accomplishments", "awards", "honors"],
    "hobbies": ["hobbies", "interests", "hobbies and interests", "extracurricular"],
    "summary": ["summary", "objective", "career objective", "profile"],
}

DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "be ", "bachelor", "b.sc", "bsc", "bca", "b.com", "bcom",
    "m.tech", "mtech", "m.e", "master", "msc", "m.sc", "mca", "mba", "phd", "ph.d",
    "diploma", "12th", "hsc", "10th", "ssc", "high school",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read a PDF's bytes in memory and return all extracted text."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n"
    return text.strip()


def _split_into_sections(lines):
    """Group resume lines into named sections based on common headers."""
    sections = {"header": []}
    current = "header"
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower().strip(":- ")
        matched_section = None
        for section, headers in SECTION_HEADERS.items():
            for h in headers:
                if lower == h or (len(lower) < 40 and lower.startswith(h)):
                    matched_section = section
                    break
            if matched_section:
                break
        if matched_section:
            current = matched_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _guess_name(header_lines):
    """The name is almost always the first substantial line of a resume that
    isn't an email, phone number, or link."""
    for line in header_lines[:6]:
        cleaned = line.strip()
        if not cleaned or len(cleaned) > 60:
            continue
        if EMAIL_RE.search(cleaned) or PHONE_RE.search(cleaned):
            continue
        if any(k in cleaned.lower() for k in ["resume", "curriculum vitae", "cv"]):
            continue
        # A plausible name: mostly letters/spaces, 2-4 words, no digits
        words = cleaned.split()
        if 1 <= len(words) <= 5 and not any(ch.isdigit() for ch in cleaned):
            if re.match(r"^[A-Za-z.\-' ]+$", cleaned):
                return cleaned.title() if cleaned.isupper() else cleaned
    return ""


def _guess_address(text, header_lines):
    """Look for a line containing common address indicators (city/state/pin)."""
    address_hint = re.compile(
        r"\b(street|road|nagar|colony|sector|city|state|pin\s?code|zip|india|"
        r"pradesh|maharashtra|delhi|karnataka|bengaluru|bangalore|mumbai|pune|"
        r"hyderabad|chennai|kolkata|jaipur|lucknow|patna|punjab|gujarat|rajasthan|"
        r"jammu|kashmir|noida|gurgaon|gurugram)\b",
        re.IGNORECASE,
    )
    for line in header_lines[:10]:
        if address_hint.search(line) and len(line) < 120:
            return line.strip()
    return ""


def _guess_education(section_lines, full_text):
    """Return the highest/most relevant qualification line(s) found."""
    candidates = []
    search_pool = section_lines if section_lines else full_text.split("\n")
    for line in search_pool:
        low = line.lower()
        if any(k in low for k in DEGREE_KEYWORDS):
            candidates.append(line.strip())
    # Prefer higher education over school-level entries
    priority = ["phd", "ph.d", "m.tech", "mtech", "mba", "mca", "m.sc", "msc", "master",
                "b.tech", "btech", "b.e", "bachelor", "bca", "b.sc", "bsc", "b.com", "bcom"]
    for p in priority:
        for c in candidates:
            if p in c.lower():
                return c, candidates
    return (candidates[0] if candidates else ""), candidates


def _guess_experience_years(full_text):
    """Estimate total years of experience from explicit mentions, else from
    date ranges like '2021 - 2023' or '2021 - Present'."""
    explicit = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(of\s+)?experience", full_text, re.IGNORECASE)
    if explicit:
        try:
            return float(explicit.group(1))
        except ValueError:
            pass

    ranges = re.findall(r"(20\d{2}|19\d{2})\s*[-–to]{1,3}\s*(20\d{2}|present|current)", full_text, re.IGNORECASE)
    total_months = 0
    import datetime
    this_year = datetime.datetime.now().year
    for start, end in ranges:
        start_y = int(start)
        end_y = this_year if end.lower() in ("present", "current") else int(end)
        if 1990 <= start_y <= this_year and end_y >= start_y:
            total_months += (end_y - start_y) * 12
    if total_months:
        return round(total_months / 12, 1)
    return 0.0


def _list_from_section(lines):
    """Turn a section's raw lines into a clean bullet list."""
    items = []
    for line in lines:
        cleaned = re.sub(r"^[•\-\*\u2022]\s*", "", line).strip()
        if cleaned and len(cleaned) < 200:
            items.append(cleaned)
    return items


def parse_resume(text: str) -> dict:
    """
    Deterministically extract a structured profile from resume text:
    name, email, phone, links, address, education, skills, experience,
    certifications, achievements, hobbies.
    """
    lines = text.split("\n")
    sections = _split_into_sections(lines)

    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)
    github_match = GITHUB_RE.search(text)

    name = _guess_name(sections.get("header", []))
    address = _guess_address(text, sections.get("header", []))
    top_education, all_education = _guess_education(sections.get("education", []), text)
    skills = extract_skills(text)
    experience_years = _guess_experience_years(text)
    certifications = _list_from_section(sections.get("certifications", []))
    achievements = _list_from_section(sections.get("achievements", []))
    hobbies = _list_from_section(sections.get("hobbies", []))
    projects = _list_from_section(sections.get("projects", []))
    summary = " ".join(sections.get("summary", []))[:400]

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "address": address,
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "github": github_match.group(0) if github_match else "",
        "education": top_education,
        "all_education": all_education,
        "skills": skills,
        "experience_years": experience_years,
        "certifications": certifications,
        "achievements": achievements,
        "hobbies": hobbies,
        "projects": projects,
        "summary": summary,
        "sections_found": [s for s in sections.keys() if s != "header" and sections[s]],
        "word_count": len(text.split()),
    }
