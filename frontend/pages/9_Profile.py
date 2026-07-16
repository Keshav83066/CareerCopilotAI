"""
9_Profile.py
-------------
View your account details and your resume history/scores over time.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, sidebar_nav, require_login, api_get, get_resume_profile

st.set_page_config(page_title="Profile", layout="wide")
load_css()
sidebar_nav("Profile")
require_login()
user_id = get_user_id()

st.title("👤 Profile")

profile = api_get("/user_profile", params={"user_id": user_id}, silent_404=True)

if profile:
    user = profile["user"]
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Account Details")
            st.write(f"**Name:** {user.get('name') or '—'}")
            st.write(f"**Username:** {user.get('username') or '—'}")
            st.write(f"**Email:** {user.get('email') or '—'}")
            st.write(f"**College:** {user.get('college') or '—'}")

    with col2:
        with st.container(border=True):
            st.markdown("#### Resume History")
            resumes = profile.get("resumes", [])
            if resumes:
                for r in resumes:
                    st.write(f"- **{r.get('file_path')}** — ATS Score: {r.get('resume_score')}/100")
            else:
                st.write("No resumes uploaded yet.")

full_profile = get_resume_profile().get("full_profile", {})
if full_profile:
    st.markdown("---")
    st.markdown("### 🧩 Latest Extracted Resume Profile")
    st.write(f"**Skills:** {', '.join(full_profile.get('skills', [])) or '—'}")
    st.write(f"**Education:** {full_profile.get('education') or '—'}")
    st.write(f"**Certifications:** {', '.join(full_profile.get('certifications', [])) or '—'}")
    st.write(f"**Achievements:** {', '.join(full_profile.get('achievements', [])) or '—'}")
    st.write(f"**Hobbies:** {', '.join(full_profile.get('hobbies', [])) or '—'}")

if st.button("📄 Upload / Re-analyze Resume"):
    st.switch_page("pages/2_Resume_Analyzer.py")
