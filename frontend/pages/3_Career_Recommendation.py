"""
3_Career_Recommendation.py
----------------------------
Shows which job roles best fit the candidate's (auto-filled) skills,
ranked by an accurate, deterministic match score against a role database.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login, get_resume_profile

st.set_page_config(page_title="Career Recommendation", layout="wide")
load_css()
sidebar_nav("Career Match")
require_login()
user_id = get_user_id()

st.title("🎯 Career Recommendation")

profile = get_resume_profile()
if profile["skills"]:
    st.info("Skills below were auto-filled from your uploaded resume. Feel free to edit them.")
else:
    st.warning("No resume analyzed yet — upload one on the Resume Analyzer page for the most accurate results, "
               "or just type your skills below.")

with st.form("career_form"):
    skills = st.text_area("Your Skills (comma-separated)", value=profile["skills"],
                           placeholder="e.g. Python, SQL, Communication")
    education = st.text_input("Education", value=profile["education"], placeholder="e.g. B.Tech Computer Science")
    interests = st.text_area("Interests (optional)", placeholder="e.g. Data, Design, Product")
    submitted = st.form_submit_button("Get Recommendations", type="primary")

if submitted:
    with st.spinner("Finding the best-fit roles for you..."):
        result = api_post("/career_recommendation", json={
            "user_id": user_id,
            "skills": skills,
            "education": education,
            "interests": interests,
        })

    if result:
        st.session_state["role_matches"] = result.get("recommendations", [])
        for rec in result.get("recommendations", []):
            with st.container(border=True):
                st.markdown(f"### {rec.get('role')} — {rec.get('match_score')}% match")
                st.progress(min(int(rec.get("match_score", 0)), 100) / 100)
                st.write(rec.get("reason"))
                if rec.get("missing_skills"):
                    st.write(f"**To improve your fit, learn:** {', '.join(rec['missing_skills'])}")

        st.write("")
        if st.button("📈 Next: Check Skill Gap for a Specific Role"):
            st.switch_page("pages/4_Skill_Gap.py")
