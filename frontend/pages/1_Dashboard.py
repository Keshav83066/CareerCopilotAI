"""
1_Dashboard.py
--------------
Overview dashboard: resume score, career match, skill readiness, quick
actions, and recent activity.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_get, sidebar_nav, require_login, get_resume_profile

st.set_page_config(page_title="Dashboard - CareerCopilot AI", layout="wide")
load_css()
sidebar_nav("Dashboard")
require_login()
user_id = get_user_id()

st.title("📊 Dashboard")

profile = api_get("/user_profile", params={"user_id": user_id}, silent_404=True)
resume_profile = get_resume_profile()

resume_score = 0
if profile and profile.get("resumes"):
    resume_score = profile["resumes"][-1].get("resume_score", 0)

top_role_score = 0
role_matches = st.session_state.get("role_matches", [])
if role_matches:
    top_role_score = role_matches[0].get("match_score", 0)

skill_readiness = "—"
if resume_profile["skills_list"]:
    skill_readiness = f"{len(resume_profile['skills_list'])} skills"

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric("Resume ATS Score", f"{resume_score}/100")
with col2:
    with st.container(border=True):
        st.metric("Best Career Match", f"{top_role_score}/100" if role_matches else "—")
with col3:
    with st.container(border=True):
        st.metric("Skills Detected", skill_readiness)

if not resume_profile["resume_text"]:
    st.info("👋 Start by uploading your resume — every other page (Career Match, Skill Gap, Roadmap) "
            "will auto-fill from it.")

st.write("")
st.subheader("Quick Actions")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📄 Analyze Resume", use_container_width=True):
        st.switch_page("pages/2_Resume_Analyzer.py")
with c2:
    if st.button("🎯 Career Match", use_container_width=True):
        st.switch_page("pages/3_Career_Recommendation.py")
with c3:
    if st.button("📈 Skill Gap", use_container_width=True):
        st.switch_page("pages/4_Skill_Gap.py")
with c4:
    if st.button("🔍 Job Matcher", use_container_width=True):
        st.switch_page("pages/6_Job_Matcher.py")

if profile and profile.get("history"):
    st.write("")
    st.subheader("Recent Activity")
    for h in reversed(profile["history"][-5:]):
        st.write(f"• {h['action']} — {h['timestamp']}")
