"""
summarizer/summarize.py
Reads articles from the DB that don't have an AI summary yet, sends them to
Gemini (free tier), and stores back:
  - ai_highlight: 1 short sentence, for the Feed card
  - ai_detailed_summary: a short paragraph, shown when the user expands the card

Uses the current `google-genai` SDK (the older `google-generativeai` package
is fully deprecated as of 2026 - do not use it).

This is a separate step from fetch_news.py on purpose: fetching should never
fail because an LLM call failed, and vice versa. Run fetch first, then this.
"""
import os
import json
import time
from google import genai
from dotenv import load_dotenv

from db.database import get_connection

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"  # free tier model, good balance of speed/quality

_client = None


def _get_client():
    """Creates (once) and returns the Gemini client, using the key from .env."""
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


PROMPT_TEMPLATE = """You are helping a final-year AI/ML student stay updated on AI news.

Given the article title and raw summary/description below, produce:
1. "highlight": ONE short sentence (max 20 words) capturing the core update, in plain simple language.
2. "detailed_summary": A short paragraph (3-5 sentences) explaining what changed, why it matters, and who it affects. Avoid jargon where possible; explain any technical term you must use.

Respond with ONLY valid JSON in this exact format, no markdown fences, no extra text:
{{"highlight": "...", "detailed_summary": "..."}}

Article title: {title}
Raw summary/description: {raw_summary}
"""


def summarize_article(title: str, raw_summary: str) -> dict:
    """
    Calls Gemini to generate a highlight + detailed summary for one article.
    Returns {"highlight": str, "detailed_summary": str}.
    Raises on API failure - caller decides how to handle (retry/skip).
    """
    client = _get_client()

    prompt = PROMPT_TEMPLATE.format(
        title=title,
        raw_summary=raw_summary[:2000] if raw_summary else "(no description provided)",
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    text = response.text.strip()

    # Gemini sometimes wraps JSON in ```json fences despite instructions - strip them
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    parsed = json.loads(text)
    if "highlight" not in parsed or "detailed_summary" not in parsed:
        raise ValueError(f"Gemini response missing expected keys: {parsed}")

    return parsed


def get_unsummarized_articles(limit: int = 20, per_source: int = 4) -> list[dict]:
    """
    Fetches articles that haven't been summarized yet (ai_highlight IS NULL),
    picking evenly across sources (up to `per_source` from each) instead of
    just the newest overall. Without this, a high-volume source can crowd
    out every other source from the batch.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, raw_summary, source FROM (
            SELECT id, title, raw_summary, source, fetched_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY source ORDER BY fetched_at DESC
                   ) AS rn
            FROM articles
            WHERE ai_highlight IS NULL
        )
        WHERE rn <= ?
        ORDER BY fetched_at DESC
        LIMIT ?
    """, (per_source, limit))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "raw_summary": r[2], "source": r[3]} for r in rows]


def save_summary(article_id: int, highlight: str, detailed_summary: str):
    """Writes the generated summary back to the article's row."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE articles
        SET ai_highlight = ?, ai_detailed_summary = ?
        WHERE id = ?
    """, (highlight, detailed_summary, article_id))
    conn.commit()
    conn.close()


def summarize_pending_articles(limit: int = 25, per_source: int = 5, delay_seconds: float = 4.0) -> dict:
    """
    Main entry point: summarizes up to `limit` unsummarized articles, picking
    up to `per_source` from each source so no single feed dominates the batch.
    `delay_seconds` between calls respects Gemini free-tier rate limits
    (roughly 10-15 requests/minute - 4s spacing keeps us safely under that).
    Returns a summary dict with counts.
    """
    articles = get_unsummarized_articles(limit=limit, per_source=per_source)
    succeeded = 0
    failed = 0

    for i, art in enumerate(articles):
        try:
            result = summarize_article(art["title"], art["raw_summary"])
            save_summary(art["id"], result["highlight"], result["detailed_summary"])
            succeeded += 1
            print(f"[ok] Summarized: {art['title'][:60]}")
        except Exception as e:
            failed += 1
            print(f"[error] Failed to summarize article {art['id']}: {e}")

        # Don't sleep after the last one
        if i < len(articles) - 1:
            time.sleep(delay_seconds)

    return {"total": len(articles), "succeeded": succeeded, "failed": failed}


if __name__ == "__main__":
    # Run: python -m summarizer.summarize
    from dotenv import load_dotenv
    load_dotenv()
    from db.database import init_db
    init_db()
    result = summarize_pending_articles()
    print(f"\nDone. {result['succeeded']}/{result['total']} summarized, "
          f"{result['failed']} failed.")
