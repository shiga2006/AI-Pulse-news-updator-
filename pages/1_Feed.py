"""
pages/1_Feed.py
Displays the AI news feed as highlight cards.
Will be connected to real fetched data starting Day 2-3.
"""
import streamlit as st

st.set_page_config(page_title="Feed - AI Pulse", page_icon="📰")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("📰 Latest AI Updates")
st.info("Coming on Day 2-3: live articles fetched from RSS/APIs, "
        "summarized by AI into highlights and expandable detail views.")

# Placeholder example of what a highlight card will look like
with st.container(border=True):
    st.subheader("Example: New model release announced")
    st.caption("Source: OpenAI Blog · 2 days ago")
    st.write("This is a placeholder highlight. Real AI-generated summaries land on Day 3.")
    with st.expander("Read more"):
        st.write("Detailed AI-generated explanation will appear here.")
        st.markdown("[Official source →](https://openai.com)")
