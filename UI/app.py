import streamlit as st
import uuid
import requests

st.set_page_config(page_title="Chatbot (MVP)", layout="centered")
st.title("Chatbot (MVP)")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

BACKEND_URL = "http://localhost:8000/chat"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_text = st.chat_input("Say something...")
uploaded_file = st.file_uploader(
    "Upload Image / PDF / Audio",
    type=["png", "jpg", "jpeg", "pdf", "mp3", "wav", "m4a"]
)

if user_text or uploaded_file:
    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        if uploaded_file:
            st.caption(f"📎 {uploaded_file.name}")

    st.session_state.messages.append({
        "role": "user",
        "content": user_text or uploaded_file.name
    })

    response = requests.post(
        BACKEND_URL,
        data={
            "thread_id": st.session_state.thread_id,
            "text": user_text or ""
        },
        files={"file": uploaded_file} if uploaded_file else None
    )

    bot_reply = response.json()["message"]

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
