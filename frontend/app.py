"""
app.py
------
CareerCopilot AI - Landing page, login and signup.
Run with: streamlit run frontend/app.py
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from components.ui_helpers import load_css, api_post, sidebar_nav, is_logged_in

st.set_page_config(page_title="CareerCopilot AI", page_icon="🧭", layout="wide")
load_css()
sidebar_nav("Home")

st.markdown("<h1 style='text-align:center;'>🧭 CareerCopilot AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Upload your resume once. Get your ATS score, "
    "a full profile breakdown, career matches, a skill-gap analysis, and a real learning roadmap — "
    "all in one flow.</p>",
    unsafe_allow_html=True,
)
st.write("")

if is_logged_in():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.success(f"You're logged in as **{st.session_state.get('user_name') or st.session_state.get('username')}**.")
        if st.button("🚀 Go to Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
else:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # NOTE: this used to be st.markdown("<div class='css-card'>...</div>")
        # wrapped around the tabs below. That does NOT actually work in
        # Streamlit — a raw HTML markdown call renders as its own separate
        # element and can't wrap widgets created *after* it, so the opening
        # <div> showed up as its own empty rounded box above the tabs (the
        # bug in the screenshot). st.container(border=True) is the real,
        # supported way to get a bordered card that contains the widgets.
        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["🔑 Log In", "🆕 Sign Up"])

            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Log In", use_container_width=True)
                if submitted:
                    result = api_post("/login", json={"username": username, "password": password})
                    if result:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = result["username"]
                        st.session_state.user_name = result.get("name", result["username"])
                        st.success("Logged in! Redirecting to your dashboard...")
                        st.switch_page("pages/1_Dashboard.py")

            with tab_signup:
                with st.form("signup_form"):
                    su_name = st.text_input("Full Name")
                    su_username = st.text_input("Choose a Username")
                    su_email = st.text_input("Email (optional)")
                    su_college = st.text_input("College / University (optional)")
                    su_password = st.text_input("Choose a Password", type="password")
                    su_submitted = st.form_submit_button("Create Account", use_container_width=True)
                if su_submitted:
                    if not su_name or not su_username or not su_password:
                        st.error("Name, username and password are required.")
                    else:
                        result = api_post("/signup", json={
                            "username": su_username, "password": su_password,
                            "name": su_name, "email": su_email, "college": su_college, "branch": "",
                        })
                        if result:
                            st.session_state.user_id = result["user_id"]
                            st.session_state.username = result["username"]
                            st.session_state.user_name = result.get("name", result["username"])
                            st.success("Account created! Redirecting to your dashboard...")
                            st.switch_page("pages/1_Dashboard.py")

st.write("")
st.markdown("### What CareerCopilot AI helps you do")
features = [
    "📄 Parse your resume into a full profile — name, contact, education, skills, hobbies, achievements & certificates",
    "📊 Get an accurate ATS score with a clear breakdown of exactly why, and how to improve it",
    "🎯 See which job roles you already match, and by how much",
    "📈 Find the exact skills you're missing for any target role",
    "🗺️ Get a month-by-month learning roadmap with real course/YouTube links for each missing skill",
    "🔍 Match your resume against a specific job description",
    "🎤 Practice with an AI mock interviewer",
    "💬 Chat with an AI career guide",
]
for f in features:
    st.markdown(f"- {f}")
