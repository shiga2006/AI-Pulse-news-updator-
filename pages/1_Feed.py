"""
pages/1_Feed.py
Displays the AI news feed as highlight cards, pulling real data from the DB.
Each card has: Save for later, Like, Share, and an inline "Ask about this"
AI helper scoped to just that article (like LeetCode's per-problem AI help,
or an IDE explaining the currently open file).
"""
import streamlit as st
from db.database import get_connection
from db.preferences import get_user_preferences
from db.engagement import toggle_save, is_saved, toggle_like, has_liked, get_like_count
from fetcher.fetch_news import fetch_all_sources
from summarizer.summarize import summarize_pending_articles
from assistant.chat_assistant import ask_about_article

st.set_page_config(page_title="Feed - AI Pulse", page_icon="📰")

if not st.session_state.get("logged_in"):
    st.warning("Please log in from the main page first.")
    st.stop()

user_id = st.session_state.user_id

header_col, button_col = st.columns([4, 1])
with header_col:
    st.title("📰 Latest AI Updates")
with button_col:
    st.write("")
    refresh_clicked = st.button("🔄 Refresh Now", use_container_width=True)

if refresh_clicked:
    with st.spinner("Fetching new articles..."):
        fetch_result = fetch_all_sources()
    with st.spinner("Summarizing new articles..."):
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
            SELECT id, title, link, source, topic, ai_highlight, ai_detailed_summary, published_at
            FROM articles
            WHERE ai_highlight IS NOT NULL AND topic IN ({placeholders})
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (*topics, limit))
    else:
        cur.execute("""
            SELECT id, title, link, source, topic, ai_highlight, ai_detailed_summary, published_at
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


user_prefs = get_user_preferences(user_id)

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
    for article_id, title, link, source, topic, highlight, detailed, published_at in articles:
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

            # --- Engagement row: Save, Like, Share ---
            save_col, like_col, share_col = st.columns(3)

            with save_col:
                saved = is_saved(user_id, article_id)
                label = "🔖 Saved" if saved else "🔖 Save for later"
                if st.button(label, key=f"save_{article_id}", use_container_width=True):
                    toggle_save(user_id, article_id)
                    st.rerun()

            with like_col:
                liked = has_liked(user_id, article_id)
                like_count = get_like_count(article_id)
                label = f"❤️ Liked ({like_count})" if liked else f"🤍 Like ({like_count})"
                if st.button(label, key=f"like_{article_id}", use_container_width=True):
                    toggle_like(user_id, article_id)
                    st.rerun()

            with share_col:
                with st.popover("🔗 Share", use_container_width=True):
                    st.caption("Copy this link to share:")
                    st.code(link, language=None)

            # --- Inline AI helper, scoped to just this article ---
            with st.expander("🤖 Ask AI about this update"):
                article_ctx = {
                    "title": title, "source": source, "topic": topic,
                    "detailed_summary": detailed,
                }
                q_key = f"article_q_{article_id}"
                a_key = f"article_a_{article_id}"

                question = st.text_input(
                    "Ask a question about this specific update",
                    key=q_key,
                    placeholder="e.g. Why does this matter for developers?",
                )
                if st.button("Ask", key=f"ask_btn_{article_id}"):
                    if question.strip():
                        with st.spinner("Thinking..."):
                            try:
                                answer = ask_about_article(article_ctx, question)
                                st.session_state[a_key] = answer
                            except RuntimeError as e:
                                st.session_state[a_key] = f"⚠️ {e}"
                    else:
                        st.session_state[a_key] = "⚠️ Please type a question first."

                if st.session_state.get(a_key):
                    st.markdown(f"**Answer:** {st.session_state[a_key]}")
