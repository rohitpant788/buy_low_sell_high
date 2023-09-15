import streamlit as st

def get_log_messages():
    log_messages = st.session_state.get("log_messages", "")
    return log_messages

def update_log_messages(log_message):
    log_messages = get_log_messages()
    log_messages += "\n" + log_message
    st.session_state.log_messages = log_messages
