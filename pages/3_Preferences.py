"""
pages/3_Preferences.py
Lets users pick which AI topics they care about. Saved to DB, read by the Feed page.
"""
import streamlit as st
from db.preferences import ALL_TOPICS, get_user_preferences, set_user_preferences

st.set_page_config(page_title="Preferences - AI Pulse", page_icon="⚙️")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("⚙️ Your Topic Preferences")
st.write("Pick the topics you care about. Your Feed will show only these "
         "(leave empty to see everything).")

user_id = st.session_state.user_id
current_prefs = get_user_preferences(user_id)

selected = st.multiselect(
    "Select topics you're interested in:",
    ALL_TOPICS,
    default=current_prefs,
)

if st.button("Save Preferences"):
    set_user_preferences(user_id, selected)
    st.success("Preferences saved! Head to the Feed to see it filtered.")
