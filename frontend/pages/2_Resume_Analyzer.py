"""
2_Resume_Analyzer.py
---------------------
Upload a resume PDF and see a full, accurate breakdown:
ATS score (with a "why" breakdown + suggestions), extracted profile
(name, contact, education, skills, hobbies, achievements, certificates),
and which job roles the resume already matches.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login

st.set_page_config(page_title="Resume Analyzer", layout="wide")
load_css()
sidebar_nav("Resume Analyzer")
require_login()
user_id = get_user_id()

st.title("📄 Resume Analyzer")
st.write("Upload your resume as a PDF. Everything below — ATS score, your profile, and role matches — "
         "is generated from your actual resume content, and will auto-fill on every other page.")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file and st.button("Analyze Resume", type="primary"):
    with st.spinner("Reading and analyzing your resume..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        result = api_post("/upload_resume", data={"user_id": user_id}, files=files)

    if result:
        analysis = result.get("analysis", {})
        profile = result.get("profile", {})
        role_matches = result.get("role_matches", [])

        st.session_state["resume_text"] = result.get("resume_text", "")
        st.session_state["last_analysis"] = analysis
        st.session_state["full_profile"] = profile
        st.session_state["role_matches"] = role_matches
        st.session_state["extracted_skills"] = ", ".join(profile.get("skills", []))
        st.session_state["extracted_skills_list"] = profile.get("skills", [])
        st.session_state["extracted_education"] = profile.get("education", "")
        st.session_state["experience_summary"] = analysis.get("experience_summary", "")

        st.success("Analysis complete — this data will now auto-fill on other pages too.")

if st.session_state.get("last_analysis"):
    analysis = st.session_state["last_analysis"]
    profile = st.session_state.get("full_profile", {})
    role_matches = st.session_state.get("role_matches", [])

    # ---------------- ATS score ----------------
    st.markdown("## 🎯 ATS Score")
    score = analysis.get("ats_score", 0)
    col_score, col_bar = st.columns([1, 3])
    with col_score:
        st.metric("Your ATS Score", f"{score}/100")
    with col_bar:
        st.progress(min(score, 100) / 100)

    breakdown = analysis.get("score_breakdown", {})
    if breakdown:
        with st.expander("See exactly how this score was calculated"):
            for k, v in breakdown.items():
                st.write(f"- **{k.replace('_', ' ').title()}**: {v} points")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Strengths")
        for s in analysis.get("strengths", []):
            st.write(f"- {s}")
    with col2:
        st.markdown("#### ⚠️ Weaknesses")
        for w in analysis.get("weaknesses", []):
            st.write(f"- {w}")

    st.markdown("#### 💡 How to improve your ATS score")
    for s in analysis.get("suggestions", []):
        st.write(f"- {s}")

    st.markdown("---")

    # ---------------- Extracted profile ----------------
    st.markdown("## 🧩 Your Extracted Profile")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 👤 Personal Details")
            st.write(f"**Name:** {profile.get('name') or '—'}")
            st.write(f"**Email:** {profile.get('email') or '—'}")
            st.write(f"**Phone:** {profile.get('phone') or '—'}")
            st.write(f"**Address:** {profile.get('address') or '—'}")
            if profile.get("linkedin"):
                st.write(f"**LinkedIn:** {profile.get('linkedin')}")
            if profile.get("github"):
                st.write(f"**GitHub:** {profile.get('github')}")

        with st.container(border=True):
            st.markdown("#### 🎓 Education")
            st.write(profile.get("education") or "Not clearly detected — make sure your degree is under an 'Education' heading.")
            st.markdown("#### 💼 Experience")
            st.write(analysis.get("experience_summary", "—"))

    with c2:
        with st.container(border=True):
            st.markdown("#### 🛠️ Skills")
            skills = profile.get("skills", [])
            if skills:
                st.write(", ".join(skills))
            else:
                st.write("No recognizable skills found — list specific tools/technologies explicitly.")

        with st.container(border=True):
            st.markdown("#### 🏆 Achievements & 📜 Certifications")
            achievements = profile.get("achievements", [])
            certs = profile.get("certifications", [])
            if achievements:
                st.write("**Achievements:**")
                for a in achievements:
                    st.write(f"- {a}")
            if certs:
                st.write("**Certifications:**")
                for c in certs:
                    st.write(f"- {c}")
            if not achievements and not certs:
                st.write("None detected. Add an 'Achievements' or 'Certifications' section to strengthen your resume.")
            st.markdown("#### 🎨 Hobbies / Interests")
            hobbies = profile.get("hobbies", [])
            st.write(", ".join(hobbies) if hobbies else "None detected.")

    st.markdown("---")

    # ---------------- Role matches ----------------
    st.markdown("## 🎯 Which Roles Do You Already Match?")
    if role_matches:
        for r in role_matches[:5]:
            with st.container(border=True):
                st.markdown(f"### {r['role']} — {r['match_score']}% match")
                st.progress(min(r["match_score"], 100) / 100)
                if r["matched_skills"]:
                    st.write(f"**You already have:** {', '.join(r['matched_skills'])}")
                if r["missing_skills"]:
                    st.write(f"**Missing for this role:** {', '.join(r['missing_skills'])}")
    else:
        st.info("No skills detected yet to match against roles.")

    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📈 Go to Skill Gap for a Specific Role", use_container_width=True):
            st.switch_page("pages/4_Skill_Gap.py")
    with col_b:
        if st.button("🎯 See Full Career Recommendations", use_container_width=True):
            st.switch_page("pages/3_Career_Recommendation.py")
