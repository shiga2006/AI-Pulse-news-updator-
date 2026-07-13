"""
pages/4_Saved.py
Shows everything the logged-in user has saved for later.
"""
import streamlit as st
from db.engagement import get_saved_articles, toggle_save

st.set_page_config(page_title="Saved - AI Pulse", page_icon="🔖")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

user_id = st.session_state.user_id

st.title("🔖 Saved for Later")

saved = get_saved_articles(user_id)

if not saved:
    st.info("You haven't saved anything yet. Save articles from the Feed page to see them here.")
else:
    st.caption(f"{len(saved)} saved article(s)")
    for art in saved:
        with st.container(border=True):
            st.subheader(art["highlight"])
            meta = f"Source: {art['source']}"
            if art["topic"]:
                meta += f" · {art['topic']}"
            meta += f" · saved {art['saved_at'][:10]}"
            st.caption(meta)

            with st.expander("Read more"):
                st.write(art["detailed_summary"])
                st.markdown(f"[Official source →]({art['link']})")

            if st.button("🗑️ Remove from saved", key=f"unsave_{art['id']}"):
                toggle_save(user_id, art["id"])
                st.rerun()
