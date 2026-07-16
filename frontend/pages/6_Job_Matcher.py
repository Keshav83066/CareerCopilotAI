"""
6_Job_Matcher.py
-----------------
Paste a job description and compare it against the (auto-filled) resume text.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login

st.set_page_config(page_title="Job Matcher", layout="wide")
load_css()
sidebar_nav("Job Matcher")
require_login()
user_id = get_user_id()

st.title("🔍 Job Matcher")

resume_text = st.text_area(
    "Resume Text",
    value=st.session_state.get("resume_text", ""),
    height=200,
    help="Auto-filled if you already analyzed a resume on the Resume Analyzer page.",
)
job_description = st.text_area("Paste Job Description", height=200)

if st.button("Match Job"):
    with st.spinner("Comparing resume to job description..."):
        result = api_post("/job_match", json={
            "user_id": user_id,
            "resume_text": resume_text,
            "job_description": job_description,
        })

    if result:
        st.metric("Match Score", f"{result.get('match_score', 0)}/100")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ Matched Keywords")
            for k in result.get("matched_keywords", []):
                st.write(f"- {k}")
        with col2:
            st.markdown("#### ❌ Missing Keywords")
            for k in result.get("missing_keywords", []):
                st.write(f"- {k}")
        st.markdown("#### Summary")
        st.write(result.get("summary", ""))
