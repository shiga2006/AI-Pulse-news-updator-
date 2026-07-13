"""
db/engagement.py
Handles "save for later" (bookmarks) and likes. Both use the same
toggle pattern: if the row exists, remove it (un-save/unlike); if not,
add it. UNIQUE constraints in the schema prevent double-saves/double-likes
even if a click somehow fires twice.
"""
from db.database import get_connection


# ---------- Save / Watch Later ----------

def is_saved(user_id: int, article_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM saved_articles WHERE user_id = ? AND article_id = ?",
        (user_id, article_id),
    )
    result = cur.fetchone() is not None
    conn.close()
    return result


def toggle_save(user_id: int, article_id: int) -> bool:
    """Saves if not saved, un-saves if already saved. Returns new saved state."""
    conn = get_connection()
    cur = conn.cursor()
    if is_saved(user_id, article_id):
        cur.execute(
            "DELETE FROM saved_articles WHERE user_id = ? AND article_id = ?",
            (user_id, article_id),
        )
        conn.commit()
        conn.close()
        return False
    else:
        cur.execute(
            "INSERT INTO saved_articles (user_id, article_id) VALUES (?, ?)",
            (user_id, article_id),
        )
        conn.commit()
        conn.close()
        return True


def get_saved_articles(user_id: int) -> list[dict]:
    """Returns full article details for everything this user has saved, most recent first."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.title, a.link, a.source, a.topic,
               a.ai_highlight, a.ai_detailed_summary, s.saved_at
        FROM saved_articles s
        JOIN articles a ON a.id = s.article_id
        WHERE s.user_id = ?
        ORDER BY s.saved_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "link": r[2], "source": r[3], "topic": r[4],
         "highlight": r[5], "detailed_summary": r[6], "saved_at": r[7]}
        for r in rows
    ]


# ---------- Likes ----------

def has_liked(user_id: int, article_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM article_likes WHERE user_id = ? AND article_id = ?",
        (user_id, article_id),
    )
    result = cur.fetchone() is not None
    conn.close()
    return result


def toggle_like(user_id: int, article_id: int) -> bool:
    """Likes if not liked, unlikes if already liked. Returns new liked state."""
    conn = get_connection()
    cur = conn.cursor()
    if has_liked(user_id, article_id):
        cur.execute(
            "DELETE FROM article_likes WHERE user_id = ? AND article_id = ?",
            (user_id, article_id),
        )
        conn.commit()
        conn.close()
        return False
    else:
        cur.execute(
            "INSERT INTO article_likes (user_id, article_id) VALUES (?, ?)",
            (user_id, article_id),
        )
        conn.commit()
        conn.close()
        return True


def get_like_count(article_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM article_likes WHERE article_id = ?", (article_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count
