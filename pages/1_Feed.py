"""
pages/1_Feed.py
Displays the AI news feed as highlight cards, pulling real data from the DB.
Run fetcher/fetch_news.py and summarizer/summarize.py first to populate articles.
"""
import streamlit as st
from datetime import datetime
from db.database import get_connection
from db.preferences import get_user_preferences
from fetcher.fetch_news import fetch_all_sources
from summarizer.summarize import summarize_pending_articles

st.set_page_config(page_title="Feed - AI Pulse", page_icon="📰")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

header_col, button_col = st.columns([4, 1])
with header_col:
    st.title("📰 Latest AI Updates")
with button_col:
    st.write("")  # small vertical spacer to align button with title
    refresh_clicked = st.button("🔄 Refresh Now", use_container_width=True)

if refresh_clicked:
    with st.spinner("Fetching new articles..."):
        fetch_result = fetch_all_sources()
    with st.spinner("Summarizing new articles..."):
        # A few passes so backlog clears in one click, matching scheduler.py's approach
        total_summarized = 0
        for _ in range(4):
            sm_result = summarize_pending_articles()
            total_summarized += sm_result["succeeded"]
            if sm_result["total"] == 0:
                break
    st.success(
        f"Refreshed! {fetch_result['_total_new']} new article(s) fetched, "
        f"{total_summarized} summarized."
    )


def get_last_updated() -> str | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(fetched_at) FROM articles")
    result = cur.fetchone()[0]
    conn.close()
    return result


last_updated = get_last_updated()
if last_updated:
    st.caption(f"Last updated: {last_updated} · auto-refreshes every 48h while the app is running")


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


def count_all_summarized() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM articles WHERE ai_highlight IS NOT NULL")
    count = cur.fetchone()[0]
    conn.close()
    return count


user_prefs = get_user_preferences(st.session_state.user_id)

if user_prefs:
    st.caption(f"Filtered to: {', '.join(user_prefs)} · "
               f"[change in Preferences]")
else:
    st.caption("Showing all topics · set preferences to filter your feed")

articles = load_articles(user_prefs if user_prefs else None)

if not articles:
    total_summarized = count_all_summarized()
    if total_summarized == 0:
        st.info(
            "No summarized articles yet. Run these two commands from your terminal:\n\n"
            "```\npython -m fetcher.fetch_news\npython -m summarizer.summarize\n```"
        )
    else:
        st.warning(
            f"You have {total_summarized} summarized article(s) in total, but none "
            f"match your selected topic(s): **{', '.join(user_prefs)}**.\n\n"
            "This can happen if that topic's source hasn't published anything new, "
            "or hasn't been summarized yet. Try:\n"
            "- Clearing your filter in **Preferences** to see everything, or\n"
            "- Running `python -m summarizer.summarize` again to clear any backlog"
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
