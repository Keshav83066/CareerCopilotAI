"""
5_Learning_Roadmap.py
-----------------------
Generate a personalized, month-by-month learning roadmap for missing
skills, with real curated resources (official docs, free courses,
YouTube search links) for each one.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login

st.set_page_config(page_title="Learning Roadmap", layout="wide")
load_css()
sidebar_nav("Learning Roadmap")
require_login()
user_id = get_user_id()

st.title("🗺️ Learning Roadmap")

default_skills = st.session_state.get("missing_skills", "")
if default_skills:
    st.info("Missing skills below were auto-filled from your last Skill Gap analysis.")

missing_skills = st.text_area("Missing Skills (comma-separated)", value=default_skills,
                               placeholder="e.g. AWS, Docker, Data Visualization")
auto_timeframe = st.checkbox("Auto-suggest a realistic timeframe", value=True)
months = None
if not auto_timeframe:
    months = st.slider("Timeframe (months)", 1, 12, 3)

if st.button("Generate Roadmap", type="primary"):
    with st.spinner("Building your roadmap..."):
        result = api_post("/roadmap", json={
            "user_id": user_id,
            "missing_skills": missing_skills,
            "months": months or 0,
        })

    if result:
        if result.get("note"):
            st.success(result["note"])
        roadmap = result.get("roadmap", [])
        if roadmap:
            st.write(f"**Suggested timeframe: {result.get('total_months')} month(s)** "
                     "based on how many skills you need to learn.")
        for item in roadmap:
            with st.container(border=True):
                st.markdown(f"### Month {item.get('month')}: {item.get('focus')}")
                st.write("**Resources:**")
                for r in item.get("resources", []):
                    if " — " in r and ": http" in r:
                        label_part, url = r.rsplit(": ", 1)
                        st.markdown(f"- {label_part}: [{url}]({url})")
                    else:
                        st.write(f"- {r}")
                st.write(f"**Milestone:** {item.get('milestone')}")
