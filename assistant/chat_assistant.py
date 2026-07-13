"""
assistant/chat_assistant.py
A simple retrieval-augmented assistant: finds relevant stored articles for
the user's question, and asks Gemini to answer using ONLY that context.

This is intentionally NOT a general-purpose chatbot - if we don't have
relevant articles stored, it should say so rather than making things up
from the model's own training data (which could be stale or wrong about
"latest" AI news).
"""
import os
import re
from google import genai
from dotenv import load_dotenv

from db.database import get_connection

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY not set. Copy .env.example to .env and add your "
            "free key from https://aistudio.google.com/apikey"
        )
    _client = genai.Client(api_key=api_key)
    return _client


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "what", "which", "who",
    "how", "why", "when", "where", "did", "does", "do", "in", "on", "of",
    "for", "to", "and", "or", "about", "tell", "me", "explain", "please",
}


def _extract_keywords(question: str) -> list[str]:
    """Pulls meaningful words out of the question to search article text with."""
    words = re.findall(r"[a-zA-Z0-9]+", question.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def find_relevant_articles(question: str, limit: int = 5) -> list[dict]:
    """
    Simple keyword search over title + ai_detailed_summary + raw_summary.
    Good enough for a week-1 project; could be upgraded to embeddings later.
    Falls back to the most recent articles if no keyword matches, so the
    assistant still has *something* relevant to reason about.
    """
    keywords = _extract_keywords(question)
    conn = get_connection()
    cur = conn.cursor()

    if keywords:
        conditions = []
        params = []
        for kw in keywords:
            conditions.append(
                "(title LIKE ? OR ai_detailed_summary LIKE ? OR raw_summary LIKE ?)"
            )
            params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
        where_clause = " OR ".join(conditions)
        cur.execute(f"""
            SELECT title, source, topic, ai_highlight, ai_detailed_summary, link
            FROM articles
            WHERE ai_highlight IS NOT NULL AND ({where_clause})
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (*params, limit))
        rows = cur.fetchall()
    else:
        rows = []

    if not rows:
        # Fallback: no keyword matches - just grab the most recent articles
        cur.execute("""
            SELECT title, source, topic, ai_highlight, ai_detailed_summary, link
            FROM articles
            WHERE ai_highlight IS NOT NULL
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()

    conn.close()
    return [
        {"title": r[0], "source": r[1], "topic": r[2],
         "highlight": r[3], "detailed_summary": r[4], "link": r[5]}
        for r in rows
    ]


ASSISTANT_PROMPT_TEMPLATE = """You are an AI news assistant helping a student understand recent AI updates.

Answer the user's question using ONLY the article context below. If the context
doesn't actually contain an answer to their question, say so honestly instead
of guessing or using outside knowledge - do not invent facts.

Keep your answer clear, simple, and a few sentences long unless the question
needs more detail.

--- ARTICLE CONTEXT ---
{context}
--- END CONTEXT ---

User question: {question}
"""


def _format_context(articles: list[dict]) -> str:
    if not articles:
        return "(No articles are currently stored in the database.)"
    blocks = []
    for a in articles:
        blocks.append(
            f"Title: {a['title']}\n"
            f"Source: {a['source']} | Topic: {a['topic']}\n"
            f"Summary: {a['detailed_summary']}\n"
            f"Link: {a['link']}"
        )
    return "\n\n".join(blocks)


def ask_assistant(question: str) -> dict:
    """
    Main entry point. Finds relevant articles, asks Gemini to answer grounded
    in them, and returns both the answer and which articles were used (so the
    UI can show sources).
    """
    articles = find_relevant_articles(question)
    context = _format_context(articles)

    client = _get_client()
    prompt = ASSISTANT_PROMPT_TEMPLATE.format(context=context, question=question)

    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)

    return {
        "answer": response.text.strip(),
        "sources": articles,
    }


ARTICLE_SCOPED_PROMPT_TEMPLATE = """You are helping a student understand ONE specific AI news article.
Answer the user's question using ONLY the article below - like an inline
"explain this" helper (similar to how LeetCode explains a problem, or an
IDE explains the currently open file). Do not pull in outside knowledge or
other AI news you might know about; stick to this article.

If the question can't be answered from this article's content, say so
honestly rather than guessing.

--- ARTICLE ---
Title: {title}
Source: {source} | Topic: {topic}
Summary: {detailed_summary}
--- END ARTICLE ---

User question: {question}
"""


def ask_about_article(article: dict, question: str) -> str:
    """
    Scoped Q&A for a single article - this is the "per-article assistant"
    (LeetCode/VSCode-style: help scoped to what the user is currently
    looking at, not a search across everything). Unlike ask_assistant(),
    this never does a DB-wide search - the article is passed in directly
    by the caller (the Feed card that's already showing it), so context is
    guaranteed correct and this stays fast and cheap.

    Expects `article` dict with keys: title, source, topic, detailed_summary.
    Returns the answer text directly (no sources list needed - there's only
    ever one source: the article itself).
    """
    client = _get_client()
    prompt = ARTICLE_SCOPED_PROMPT_TEMPLATE.format(
        title=article["title"],
        source=article.get("source", "Unknown"),
        topic=article.get("topic", "Unknown"),
        detailed_summary=article.get("detailed_summary", "(no summary available)"),
        question=question,
    )
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()
