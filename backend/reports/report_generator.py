"""
report_generator.py
--------------------
Generates a downloadable PDF report summarizing a user's AI results,
following the "Report generation" responsibility from the Backend Handbook.
"""

from fpdf import FPDF
import os
import re

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(REPORTS_DIR, exist_ok=True)

# The core Helvetica font only supports Latin-1. Resume text copy-pasted from
# Word/LinkedIn often contains smart quotes, em-dashes, bullets, or emoji,
# which used to crash PDF generation. Map the common ones to safe equivalents,
# then drop anything else that still doesn't fit instead of erroring out.
_CHAR_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2022": "-", "\u2026": "...",
}


def _sanitize(text: str) -> str:
    for bad, good in _CHAR_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_report(user_id: int, data: dict) -> str:
    """Render a simple PDF report from a dict of section -> content and save it."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "CareerCopilot AI - Career Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 12)
    for section, content in data.items():
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, _sanitize(str(section).replace("_", " ").title()), ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _sanitize(str(content)))
        pdf.ln(3)

    file_path = os.path.join(REPORTS_DIR, f"report_user_{user_id}.pdf")
    pdf.output(file_path)
    return file_path
