🧠 AI Pulse — Personalized AI News & Insights Platform

AI Pulse is a web platform that automatically aggregates the latest AI news from trusted sources, presents them as easy-to-scan highlights, and helps users go deeper with AI-generated summaries and a built-in AI assistant — all in one place.

Built as a final-year AIML project to solve a real problem: staying updated with the fast-moving AI industry without spending hours browsing multiple sites.


✨ Features


🔐 User Authentication — Sign up and log in to get a personalized feed

📰 Auto-Fetched AI News — Pulls updates from official sources (OpenAI, Anthropic, Google AI, Hugging Face, arXiv, etc.) every 1–2 days

⚡ Highlight + Depth View — Quick highlight cards, click to expand into a detailed AI-generated summary

🔗 Official Source Links — Every update links back to its original source for credibility

🎯 Topic Preferences — Filter news by interests like LLMs, Computer Vision, Robotics, Research Papers

🤖 AI Assistant — Chat with an integrated assistant to get updates explained in simple terms

⏰ Scheduled Refresh — Background job keeps the news feed current automatically

🛠️ Tech Stack


Frontend + Backend   ->    Streamlit

Database           ->      SQLiteNews 

Fetching             ->    feedparser (RSS) + requests (APIs)

Summarization         ->   LLM API (Gemini)

AI Assistant   ->          LLM API with context retrieval over stored articles

Scheduling        ->       APScheduler

Deployment          ->     Streamlit Community Cloud

Pure Python stack — no separate frontend framework required.
