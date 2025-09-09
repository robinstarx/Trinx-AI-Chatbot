import streamlit as st
import requests
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from langchain_core.messages import AIMessage, HumanMessage

# ---- Config ----
API_URL = "{}/api/chat-premium"  # replace dynamically each run

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Chatbot", layout="centered")
st.title("🤖 TrinX AI Chatbot")

SESSION_TIMEOUT = timedelta(minutes=10)
now = datetime.now()

if "thread_id" not in st.session_state or "last_active" not in st.session_state:
    st.session_state.thread_id = str(uuid4())
    st.session_state.messages = []
    st.session_state.last_active = now
    logger.info(f"New session started: {st.session_state.thread_id}")
elif now - st.session_state.last_active > SESSION_TIMEOUT:
    st.session_state.thread_id = str(uuid4())
    st.session_state.messages = []
    st.session_state.last_active = now
    logger.info(f"Session reset: {st.session_state.thread_id}")

st.session_state.last_active = now

# Show history
for msg in st.session_state.messages:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

# User input
user_input = st.chat_input("Ask a question…")
ngrok_url = st.sidebar.text_input('Enter the ngrok url')
if user_input and ngrok_url:
    st.chat_message("user").markdown(user_input)
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)

    try:
        resp = requests.post(
            API_URL.format(ngrok_url),
            json={"session_id": st.session_state.thread_id,"prompt": user_input},
            timeout=60
        )
        data = resp.json()
        ai_msg = AIMessage(content=data["messages"])

        st.chat_message("assistant").markdown(ai_msg.content)
        st.session_state.messages.append(ai_msg)

    except Exception as e:
        st.chat_message("assistant").markdown(f"❌ Error: `{e}`")
else:
    if ngrok_url =="":
        st.chat_message("assistant").markdown("Enter the Ngrok url")
    elif user_input == "" :
        st.chat_message("assistant").markdown("Empty User Input")
