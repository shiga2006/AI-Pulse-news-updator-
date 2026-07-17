"""
db/comments.py
Lets users leave their own opinion/note on an article. Unlike save/like,
this is NOT a toggle - a user can leave multiple comments over time.
"""
from db.database import get_connection


def add_comment(user_id: int, article_id: int, comment_text: str) -> bool:
    """Adds a comment. Returns False (and adds nothing) if the text is blank."""
    if not comment_text or not comment_text.strip():
        return False
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO article_comments (user_id, article_id, comment_text) VALUES (?, ?, ?)",
        (user_id, article_id, comment_text.strip()),
    )
    conn.commit()
    conn.close()
    return True


def get_comments(article_id: int) -> list[dict]:
    """Returns all comments for an article, newest first, joined with the commenter's username."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.comment_text, c.created_at, u.username, c.user_id
        FROM article_comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.article_id = ?
        ORDER BY c.created_at DESC
    """, (article_id,))
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "text": r[1], "created_at": r[2], "username": r[3], "user_id": r[4]}
        for r in rows
    ]


def delete_comment(comment_id: int, user_id: int) -> bool:
    """
    Deletes a comment, but only if it belongs to the requesting user -
    prevents one user from deleting another user's comment even if they
    somehow guess the comment_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM article_comments WHERE id = ? AND user_id = ?",
        (comment_id, user_id),
    )
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_comment_count(article_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM article_comments WHERE article_id = ?", (article_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count
