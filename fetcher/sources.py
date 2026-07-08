"""
fetcher/sources.py
Central list of trusted AI news sources (RSS feeds).
Add/remove feeds here without touching the fetch logic.
"""

# Each source: name (shown as "Source" in UI), url (RSS feed), topic (default tag)
RSS_SOURCES = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "topic": "LLMs",
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "topic": "AI Research",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "topic": "AI Tools & Products",
    },
    {
        "name": "arXiv - AI (cs.AI)",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "topic": "AI Research Papers",
    },
    {
        "name": "MIT Technology Review - AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "topic": "AI Policy & Ethics",
    },
]

# Note: Anthropic does not currently publish a public RSS feed for its news page.
# If they add one later, just append it here in the same format:
# {"name": "Anthropic News", "url": "<feed_url>", "topic": "LLMs"}
