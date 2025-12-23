# D:\Projects\OmniTask_AI\UI\app.py

import streamlit as st
import uuid
import requests

st.set_page_config(page_title="OmniTask AI", layout="centered")
st.title("OmniTask AI Agent")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

BACKEND_URL = "http://localhost:8000/chat"

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Area
user_text = st.chat_input("How can I help you today?")
uploaded_file = st.file_uploader(
    "Upload Image / PDF / Audio (Optional)",
    type=["png", "jpg", "jpeg", "pdf", "mp3", "wav", "m4a"]
)

if user_text or uploaded_file:
    # Display User Message
    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        if uploaded_file:
            st.caption(f"📎 {uploaded_file.name}")

    st.session_state.messages.append({
        "role": "user",
        "content": user_text or uploaded_file.name
    })

    # Call Backend with Error Handling
    with st.spinner("Processing..."):
        try:
            response = requests.post(
                BACKEND_URL,
                data={
                    "thread_id": st.session_state.thread_id,
                    "text": user_text or ""
                },
                files={"file": uploaded_file} if uploaded_file else None
            )
            
            if response.status_code == 200:
                try:
                    bot_reply = response.json().get("message", "No content returned.")
                except requests.exceptions.JSONDecodeError:
                    bot_reply = f"Error: Backend returned invalid format. Raw: {response.text[:100]}"
            else:
                # Handle 500 errors gracefully
                try:
                    bot_reply = response.json().get("message", f"Server Error {response.status_code}")
                except:
                    bot_reply = f"Critical Server Error ({response.status_code})"

        except requests.exceptions.ConnectionError:
            bot_reply = "Connection Error: Please ensure `main.py` is running."

    # Display Bot Response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })