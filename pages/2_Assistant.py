"""
pages/2_Assistant.py
Chat interface for the AI assistant. Will be wired to the LLM API on Day 5.
"""
import streamlit as st

st.set_page_config(page_title="Assistant - AI Pulse", page_icon="🤖")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("🤖 Ask the AI Assistant")
st.info("Coming on Day 5: ask questions about any AI update and get a clear, "
        "simple explanation grounded in the actual stored articles.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask about a recent AI update...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        st.write("(Placeholder response — real LLM integration comes on Day 5.)")
