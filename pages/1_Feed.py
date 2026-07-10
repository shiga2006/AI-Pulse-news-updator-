"""
pages/1_Feed.py
Displays the AI news feed as highlight cards, pulling real data from the DB.
Run fetcher/fetch_news.py and summarizer/summarize.py first to populate articles.
"""
import streamlit as st
from db.database import get_connection
from db.preferences import get_user_preferences

st.set_page_config(page_title="Feed - AI Pulse", page_icon="📰")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

st.title("📰 Latest AI Updates")


def load_articles(topics: list[str] | None, limit: int = 30):
    conn = get_connection()
    cur = conn.cursor()
    if topics:
        placeholders = ",".join("?" for _ in topics)
        cur.execute(f"""
            SELECT title, link, source, topic, ai_highlight, ai_detailed_summary, published_at
            FROM articles
            WHERE ai_highlight IS NOT NULL AND topic IN ({placeholders})
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (*topics, limit))
    else:
        cur.execute("""
            SELECT title, link, source, topic, ai_highlight, ai_detailed_summary, published_at
            FROM articles
            WHERE ai_highlight IS NOT NULL
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


user_prefs = get_user_preferences(st.session_state.user_id)

if user_prefs:
    st.caption(f"Filtered to: {', '.join(user_prefs)} · "
               f"[change in Preferences]")
else:
    st.caption("Showing all topics · set preferences to filter your feed")

articles = load_articles(user_prefs if user_prefs else None)

if not articles:
    st.info(
        "No summarized articles yet. Run these two commands from your terminal:\n\n"
        "```\npython -m fetcher.fetch_news\npython -m summarizer.summarize\n```"
    )
else:
    for title, link, source, topic, highlight, detailed, published_at in articles:
        with st.container(border=True):
            st.subheader(highlight)
            meta = f"Source: {source}"
            if topic:
                meta += f" · {topic}"
            if published_at:
                meta += f" · {published_at[:10]}"
            st.caption(meta)
            with st.expander("Read more"):
                st.write(detailed)
                st.markdown(f"[Official source →]({link})")
