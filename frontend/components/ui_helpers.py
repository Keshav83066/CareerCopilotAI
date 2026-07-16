"""
ui_helpers.py
-------------
Shared frontend helpers: backend API base URL, request wrappers, the
dark-blue theme CSS loader, the left sidebar navigation, and login/session
helpers used across every page.
"""

import requests
import streamlit as st
import os

API_BASE_URL = "http://localhost:8000"


def load_css():
    """Inject the shared dark-blue theme stylesheet into the current page."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def api_post(endpoint: str, json=None, data=None, files=None):
    """POST to the backend and return parsed JSON, or None + an error message."""
    try:
        resp = requests.post(f"{API_BASE_URL}{endpoint}", json=json, data=data, files=files, timeout=60)
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.error(detail)
            return None
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Backend request failed — is the FastAPI server running on port 8000? ({e})")
        return None


def api_get(endpoint: str, params=None, silent_404=False):
    """GET from the backend and return parsed JSON, or None on failure."""
    try:
        resp = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=30)
        if silent_404 and resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Backend request failed — is the FastAPI server running on port 8000? ({e})")
        return None


# --------------------------------------------------------------- Auth -----

def is_logged_in() -> bool:
    return bool(st.session_state.get("user_id")) and bool(st.session_state.get("username"))


def get_user_id():
    """Return the logged-in user's id. Falls back to demo user 1 only if
    no login system is in use yet (keeps old flows from crashing)."""
    return st.session_state.get("user_id", 1)


def require_login():
    """Call at the top of every protected page. Sends the user back to the
    login screen on app.py if they aren't authenticated yet."""
    if not is_logged_in():
        st.warning("Please log in first to use CareerCopilot AI.")
        if st.button("Go to Login"):
            st.switch_page("app.py")
        st.stop()


def logout_button():
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        for key in ["user_id", "username", "user_name"]:
            st.session_state.pop(key, None)
        st.switch_page("app.py")


# ---------------------------------------------------------- Sidebar nav ---

NAV_PAGES = [
    ("🏠", "Home", "app.py"),
    ("📊", "Dashboard", "pages/1_Dashboard.py"),
    ("📄", "Resume Analyzer", "pages/2_Resume_Analyzer.py"),
    ("🎯", "Career Match", "pages/3_Career_Recommendation.py"),
    ("📈", "Skill Gap", "pages/4_Skill_Gap.py"),
    ("🗺️", "Learning Roadmap", "pages/5_Learning_Roadmap.py"),
    ("🔍", "Job Matcher", "pages/6_Job_Matcher.py"),
    ("🎤", "Mock Interview", "pages/7_Mock_Interview.py"),
    ("💬", "AI Chat", "pages/8_AI_Chat.py"),
    ("👤", "Profile", "pages/9_Profile.py"),
    ("📥", "Report", "pages/10_Report.py"),
]


def sidebar_nav(current: str = ""):
    """
    A clean, always-visible left sidebar menu (Claude-style) instead of a
    row of buttons across the top of the page.
    """
    with st.sidebar:
        st.markdown(
            "<h2 style='margin-bottom:0;'>🧭 CareerCopilot</h2>"
            "<p style='color:#5F6368;margin-top:0;font-size:13px;'>AI Career Companion</p>"
            "<div class='gc-accent-bar'></div>",
            unsafe_allow_html=True,
        )
        if is_logged_in():
            st.markdown(f"**👋 Hi, {st.session_state.get('user_name') or st.session_state.get('username')}**")
        st.markdown("<hr style='margin:6px 0 10px 0;border-color:#E8EAED;'>", unsafe_allow_html=True)

        for icon, label, target in NAV_PAGES:
            is_current = (label == current)
            btn_label = f"{icon}  {label}"
            if st.button(
                btn_label,
                key=f"nav_{target}",
                use_container_width=True,
                disabled=is_current,
                type="primary" if is_current else "secondary",
            ):
                st.switch_page(target)

        st.markdown("<hr style='margin:10px 0;border-color:#E8EAED;'>", unsafe_allow_html=True)
        if is_logged_in():
            logout_button()


def get_resume_profile():
    """
    Return whatever the Resume Analyzer has extracted so far (full structured
    profile), so other pages can auto-fill from a single resume upload
    instead of asking the user to retype everything.
    """
    return {
        "skills": st.session_state.get("extracted_skills", ""),
        "skills_list": st.session_state.get("extracted_skills_list", []),
        "education": st.session_state.get("extracted_education", ""),
        "experience_summary": st.session_state.get("experience_summary", ""),
        "resume_text": st.session_state.get("resume_text", ""),
        "full_profile": st.session_state.get("full_profile", {}),
    }