"""
fetcher/fetch_news.py
Fetches articles from all configured RSS sources, deduplicates against
what's already in the DB (by article link), and inserts new ones.

This module does NOT call any LLM - it's pure fetch + store.
Summarization (Day 3) reads from the `articles` table afterward and fills
in ai_highlight / ai_detailed_summary for rows that don't have them yet.
"""
import feedparser
import sqlite3
from datetime import datetime
from time import mktime

from fetcher.sources import RSS_SOURCES
from db.database import get_connection


def parse_published_date(entry) -> str | None:
    """
    feedparser gives a time.struct_time in entry.published_parsed (if present).
    Convert it to an ISO string for consistent storage. Some feeds don't set
    this field, so we fall back to None and let SQLite default handle it.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime.fromtimestamp(mktime(entry.published_parsed))
        return dt.isoformat()
    return None


def fetch_source(source: dict) -> list[dict]:
    """
    Fetches and parses a single RSS source.
    Returns a list of plain dicts ready for DB insertion.
    Never raises - a broken feed just returns an empty list, so one bad
    source doesn't stop the others from being fetched.
    """
    articles = []
    try:
        feed = feedparser.parse(source["url"])

        # feedparser sets bozo=1 if the feed XML was malformed. It may still
        # have usable entries, so we only warn, not skip.
        if feed.bozo:
            print(f"[warn] Feed may be malformed: {source['name']} ({feed.bozo_exception})")

        for entry in feed.entries:
            title = entry.get("title", "Untitled")
            link = entry.get("link")
            if not link:
                continue  # can't dedupe or link back without a URL, skip

            summary = entry.get("summary", "") or entry.get("description", "")

            articles.append({
                "title": title,
                "link": link,
                "source": source["name"],
                "topic": source["topic"],
                "published_at": parse_published_date(entry),
                "raw_summary": summary,
            })

    except Exception as e:
        print(f"[error] Failed to fetch {source['name']}: {e}")

    return articles


def save_articles(articles: list[dict]) -> int:
    """
    Inserts articles into the DB, skipping duplicates (same link = same article).
    Returns the count of NEWLY inserted articles.
    """
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0

    for art in articles:
        try:
            cur.execute("""
                INSERT INTO articles (title, link, source, topic, published_at, raw_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                art["title"], art["link"], art["source"],
                art["topic"], art["published_at"], art["raw_summary"],
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # link already exists (UNIQUE constraint) - already have this article
            continue

    conn.commit()
    conn.close()
    return inserted


def fetch_all_sources() -> dict:
    """
    Main entry point: fetches every configured source and saves new articles.
    Returns a summary dict, e.g. {"OpenAI Blog": 5, "Hugging Face Blog": 3, ...}
    plus a "_total_new" key with the combined count.
    """
    summary = {}
    total_new = 0

    for source in RSS_SOURCES:
        articles = fetch_source(source)
        new_count = save_articles(articles)
        summary[source["name"]] = {
            "fetched": len(articles),
            "new": new_count,
        }
        total_new += new_count

    summary["_total_new"] = total_new
    return summary


if __name__ == "__main__":
    # Lets you run: python -m fetcher.fetch_news  to manually trigger a fetch
    from db.database import init_db
    init_db()
    result = fetch_all_sources()
    print("\n--- Fetch Summary ---")
    for name, stats in result.items():
        if name == "_total_new":
            continue
        print(f"{name}: fetched {stats['fetched']}, {stats['new']} new")
    print(f"\nTotal new articles saved: {result['_total_new']}")
