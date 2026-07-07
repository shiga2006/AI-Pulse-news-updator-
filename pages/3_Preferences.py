"""
pages/3_Preferences.py
Lets users pick which AI topics they care about. Wired to DB on Day 4.
"""
import streamlit as st

st.set_page_config(page_title="Preferences - AI Pulse", page_icon="⚙️")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("⚙️ Your Topic Preferences")
st.info("Coming on Day 4: choose topics below and your Feed will filter to match.")

topics = ["Large Language Models", "Computer Vision", "Robotics",
          "AI Research Papers", "AI Tools & Products", "AI Policy & Ethics"]

selected = st.multiselect("Select topics you're interested in:", topics)

if st.button("Save Preferences"):
    st.success("Preferences saved (placeholder — DB wiring comes Day 4).")
