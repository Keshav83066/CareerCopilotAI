"""
4_Skill_Gap.py
--------------
Compare current (auto-filled) skills vs a target role's actual required
skill set from the built-in role database, with matched/missing skills
and a priority order for what to learn first.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, api_get, sidebar_nav, require_login, get_resume_profile

st.set_page_config(page_title="Skill Gap", layout="wide")
load_css()
sidebar_nav("Skill Gap")
require_login()
user_id = get_user_id()

st.title("📈 Skill Gap Analysis")

profile = get_resume_profile()
if profile["skills"]:
    st.info("Current skills below were auto-filled from your uploaded resume. Feel free to edit them.")

current_skills = st.text_area("Current Skills", value=profile["skills"], placeholder="e.g. Python, Excel, SQL")

roles_resp = api_get("/roles") or {"roles": []}
role_options = roles_resp.get("roles", [])
choice = st.selectbox("Target Role", options=role_options + ["Other (type below)"])
target_role = choice
if choice == "Other (type below)":
    target_role = st.text_input("Type your target role")

if st.button("Analyze Gap", type="primary"):
    with st.spinner("Comparing your skills to this role's requirements..."):
        result = api_post("/skill_gap", json={
            "user_id": user_id,
            "current_skills": current_skills,
            "target_role": target_role,
        })

    if result:
        st.session_state["missing_skills"] = ", ".join(result.get("missing_skills", []))
        st.session_state["skill_gap_role"] = result.get("target_role", target_role)

        if result.get("match_score") is not None:
            st.metric(f"Fit for {result.get('target_role')}", f"{result['match_score']}/100")

        if result.get("note"):
            st.info(result["note"])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ Matched Skills")
            matched = result.get("matched_skills", [])
            for s in matched:
                st.write(f"- {s}")
            if not matched:
                st.write("None yet.")
        with col2:
            st.markdown("#### ❌ Missing Skills")
            missing = result.get("missing_skills", [])
            for s in missing:
                st.write(f"- {s}")
            if not missing:
                st.write("None! You already cover the key skills for this role. 🎉")

        if result.get("priority_order"):
            st.markdown("#### 📌 Priority Order to Learn Next")
            for i, s in enumerate(result["priority_order"], 1):
                st.write(f"{i}. {s}")

        st.write("")
        if st.button("🗺️ Next: Build a Learning Roadmap"):
            st.switch_page("pages/5_Learning_Roadmap.py")
