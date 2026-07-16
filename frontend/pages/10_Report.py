"""
10_Report.py
-------------
Generate and download a consolidated PDF career report combining the
resume analysis, extracted profile, and role matches from this session.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import requests
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login, API_BASE_URL, get_resume_profile
import json

st.set_page_config(page_title="Report", layout="wide")
load_css()
sidebar_nav("Report")
require_login()
user_id = get_user_id()

st.title("📥 Career Report")
st.write("Generate a downloadable PDF summary of your resume analysis, profile, and career matches.")

analysis = st.session_state.get("last_analysis")
full_profile = get_resume_profile().get("full_profile", {})

if not analysis:
    st.warning("No resume analyzed yet. Analyze your resume first for a complete report.")
    if st.button("📄 Go to Resume Analyzer"):
        st.switch_page("pages/2_Resume_Analyzer.py")

if st.button("Generate Report", type="primary"):
    report_data = {
        "ats_score": analysis.get("ats_score") if analysis else "N/A",
        "strengths": ", ".join(analysis.get("strengths", [])) if analysis else "",
        "weaknesses": ", ".join(analysis.get("weaknesses", [])) if analysis else "",
        "suggestions": ", ".join(analysis.get("suggestions", [])) if analysis else "",
        "skills": ", ".join(full_profile.get("skills", [])),
        "education": full_profile.get("education", ""),
        "certifications": ", ".join(full_profile.get("certifications", [])),
        "achievements": ", ".join(full_profile.get("achievements", [])),
        "top_role_matches": ", ".join(
            f"{r['role']} ({r['match_score']}%)" for r in st.session_state.get("role_matches", [])[:5]
        ),
    }
    with st.spinner("Generating report..."):
        result = api_post(
            "/generate_report",
            data={"user_id": user_id, "data": json.dumps(report_data)},
        )

    if result:
        st.success("Report generated!")
        try:
            pdf_resp = requests.get(f"{API_BASE_URL}/download_report", params={"path": result["report_path"]}, timeout=30)
            pdf_resp.raise_for_status()
            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_resp.content,
                file_name=f"CareerCopilot_Report_user_{user_id}.pdf",
                mime="application/pdf",
            )
        except requests.exceptions.RequestException:
            st.info(f"Report saved on the server at: `{result.get('report_path')}`")
