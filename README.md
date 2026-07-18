# 🧠 AI Pulse — Personalized AI News & Insights Platform

AI Pulse is a web platform that automatically aggregates the latest AI news from trusted sources, presents them as easy-to-scan highlights, and helps users go deeper with AI-generated summaries and a built-in AI assistant — all in one place.

Built as a final-year AIML project to solve a real problem: **staying updated with the fast-moving AI industry without spending hours browsing multiple sites.**

Try the demo here !!!
https://ai-pulse-news-updator.streamlit.app/
---

## ✨ Features

- 🔐 **User Authentication** — Sign up and log in to get a personalized feed
- 📰 **Auto-Fetched AI News** — Pulls updates from official sources (OpenAI, Google AI, Hugging Face, arXiv, MIT Tech Review) via RSS
- ⚡ **Highlight + Depth View** — Quick highlight cards, click to expand into a detailed AI-generated summary
- 🔗 **Official Source Links** — Every update links back to its original source for credibility
- 🎯 **Topic Preferences** — Filter news by interests like LLMs, AI Research, Research Papers, Policy & Ethics
- 🤖 **AI Assistant (whole-feed search)** — Ask questions across all stored articles; answers are grounded in retrieved articles, not hallucinated
- 💬 **Per-Article AI Helper** — Ask a question about one specific update, right inside its card (like LeetCode's problem helper or an IDE's "explain this file") — answers are scoped to that article only
- 🔖 **Save for Later** — Bookmark any article to revisit from the dedicated Saved page
- ❤️ **Like** — Like/unlike articles, with a live like count
- 🔗 **Share** — Copy a shareable link straight from any card
- ⏰ **Scheduled Auto-Refresh** — Background job refreshes the feed every 48h while the app is running, plus a manual "Refresh Now" button for on-demand updates

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend + Backend | [Streamlit](https://streamlit.io/) |
| Database | SQLite |
| News Fetching | `feedparser` (RSS) + `requests` (APIs) |
| Summarization & Assistant | Google Gemini API (`google-genai`) — free tier, no credit card required |
| Scheduling | `APScheduler` |
| Deployment | Streamlit Community Cloud |

Pure Python stack — no separate frontend framework required.

---

## 📁 Project Structure

```
ai-pulse/
├── app.py                     # Main Streamlit app entry point (login/signup, starts scheduler)
├── auth/
│   └── auth_utils.py          # Signup/login logic, bcrypt password hashing
├── fetcher/
│   ├── sources.py             # RSS feed list (name, url, topic, max_items per source)
│   ├── fetch_news.py          # Fetch + parse + dedupe logic
│   └── scheduler.py           # APScheduler background job (auto-refresh every 48h)
├── summarizer/
│   └── summarize.py           # Gemini calls: raw article -> highlight + detailed summary
├── assistant/
│   └── chat_assistant.py      # Whole-feed search assistant + per-article scoped assistant
├── db/
│   ├── database.py             # SQLite schema: users, articles, preferences, saves, likes
│   ├── preferences.py          # Get/set user topic preferences
│   ├── engagement.py           # Save/unsave and like/unlike toggle logic
│   └── database.db             # SQLite database (generated, gitignored)
├── pages/                      # Streamlit multipage app pages
│   ├── 1_Feed.py                # Main feed: highlights, save/like/share, per-article AI helper
│   ├── 2_Assistant.py           # Whole-feed chat assistant
│   ├── 3_Preferences.py         # Topic preference picker
│   └── 4_Saved.py               # Saved / Watch Later page
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free Gemini API key

### Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/ai-pulse.git
cd ai-pulse

# Create virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

Get a **free** Gemini API key (no credit card required) from **https://aistudio.google.com/apikey**, then add it to `.env`:
```
GEMINI_API_KEY=your_key_here
```

### Populate the database (first run)

```bash
python -m fetcher.fetch_news       # pulls articles from RSS sources
python -m summarizer.summarize     # generates AI highlights + detailed summaries
```

### Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`. From then on, the Feed page's **🔄 Refresh Now** button (or the background scheduler, every 48h while the app runs) keeps things current.

---

## 🗺️ Roadmap

- [x] User authentication
- [x] RSS/API news fetcher with deduplication and per-source caps
- [x] LLM-based highlight + detailed summary generation
- [x] AI assistant chat over stored articles (whole-feed search)
- [x] Topic-based preferences with Feed filtering
- [x] Scheduled auto-refresh (every 48h) + manual refresh button
- [x] Per-article AI helper (contextual, scoped to one update)
- [x] Save for later / Watch Later page
- [x] Like + Share buttons
- [ ] Comments (personal notes on articles)
- [ ] Deployment on Streamlit Community Cloud

**Future Enhancements:** Comments/personal notes, email digest, push notifications, mobile app, multi-language support, embeddings-based retrieval for the assistant (currently keyword-based).

---

## ⚠️ Known Scope Notes

- The auto-refresh scheduler only runs while the Streamlit app process is alive — it is not a system-level cron job. A production deployment would use an always-on worker or the hosting platform's scheduled jobs feature.
- The whole-feed AI assistant uses simple keyword search (not embeddings) to find relevant articles before answering — sufficient for this project's scale, upgradeable later.

---

## 📄 License

This project is developed for academic purposes as part of a final-year AIML curriculum.

---

## 🙋 Author

Built by Shivashiga A.M as a final-year AIML project.
