"""
8_AI_Chat.py
-------------
Simple chat interface for career guidance conversation with the AI.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
from components.ui_helpers import load_css, get_user_id, api_post, sidebar_nav, require_login

st.set_page_config(page_title="AI Chat", layout="wide")
load_css()
sidebar_nav("AI Chat")
require_login()
user_id = get_user_id()

st.title("💬 AI Career Chat")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_message = st.chat_input("Ask me anything about your career...")

if user_message:
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)

    with st.spinner("Thinking..."):
        result = api_post("/ai_chat", json={
            "user_id": user_id,
            "message": user_message,
            "history": st.session_state.chat_history,
        })

    reply = result.get("reply", "Sorry, I couldn't generate a response.") if result else "Backend unavailable."
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
