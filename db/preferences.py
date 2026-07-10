"""
db/preferences.py
Handles reading/writing a user's topic preferences.
Kept separate from auth_utils.py since this is article-domain logic, not auth.
"""
from db.database import get_connection

# Master topic list - must match the `topic` values used in fetcher/sources.py
ALL_TOPICS = [
    "LLMs",
    "AI Research",
    "AI Tools & Products",
    "AI Research Papers",
    "AI Policy & Ethics",
]


def get_user_preferences(user_id: int) -> list[str]:
    """Returns the list of topics this user has selected. Empty list = no filter (show all)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT topic FROM user_preferences WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def set_user_preferences(user_id: int, topics: list[str]):
    """
    Replaces the user's preferences with the given topic list.
    Simplest correct approach: delete all existing rows for this user, then
    insert the new selection. Wrapped in one transaction so a failure can't
    leave the user with a half-updated preference set.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
        cur.executemany(
            "INSERT INTO user_preferences (user_id, topic) VALUES (?, ?)",
            [(user_id, topic) for topic in topics],
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
