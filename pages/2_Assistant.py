"""
pages/2_Assistant.py
Chat interface for the AI assistant. Answers are grounded in stored articles
(see assistant/chat_assistant.py) - it won't make up "recent" AI news that
isn't actually in your database.
"""
import streamlit as st
from assistant.chat_assistant import ask_assistant

st.set_page_config(page_title="Assistant - AI Pulse", page_icon="🤖")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("🤖 Ask the AI Assistant")
st.caption("Answers are grounded in the articles stored in your Feed - "
           "if nothing relevant is stored yet, it'll tell you honestly.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources used"):
                for s in msg["sources"]:
                    st.markdown(f"- [{s['title']}]({s['link']}) · {s['source']}")

prompt = st.chat_input("Ask about a recent AI update...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = ask_assistant(prompt)
                st.write(result["answer"])
                if result["sources"]:
                    with st.expander("Sources used"):
                        for s in result["sources"]:
                            st.markdown(f"- [{s['title']}]({s['link']}) · {s['source']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                })
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")
