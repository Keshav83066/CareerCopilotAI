"""
7_Mock_Interview.py
---------------------
Practice interview questions and get AI feedback: question, answer, evaluation.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login

st.set_page_config(page_title="Mock Interview", layout="wide")
load_css()
sidebar_nav("Mock Interview")
require_login()
user_id = get_user_id()

st.title("🎤 Mock Interview")

sample_questions = [
    "Tell me about yourself.",
    "What are your greatest strengths?",
    "Describe a challenging project you worked on.",
    "Why do you want this role?",
    "Where do you see yourself in 5 years?",
]

question = st.selectbox("Choose a question", sample_questions)
answer = st.text_area("Your Answer", height=150)

if st.button("Evaluate Answer"):
    with st.spinner("Evaluating your answer..."):
        result = api_post("/mock_interview", json={
            "user_id": user_id,
            "question": question,
            "answer": answer,
        })

    if result:
        st.metric("Score", f"{result.get('score', 0)}/10")
        st.markdown("#### Feedback")
        st.write(result.get("feedback", ""))
        st.markdown("#### Improved Answer")
        st.write(result.get("improved_answer", ""))
