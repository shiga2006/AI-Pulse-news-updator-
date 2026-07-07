"""
auth/auth_utils.py
Handles user signup, login, and password hashing using bcrypt.
"""
import bcrypt
import sqlite3
from db.database import get_connection


def hash_password(password: str) -> str:
    """Hashes a plaintext password for safe storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Checks a plaintext password against a stored hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Attempts to create a new user.
    Returns (success, message).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        password_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """
    Verifies login credentials.
    Returns (success, message, user_id).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "No account found with that username.", None

    user_id, password_hash = row
    if verify_password(password, password_hash):
        return True, "Login successful.", user_id
    else:
        return False, "Incorrect password.", None
