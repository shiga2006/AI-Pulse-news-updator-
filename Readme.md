# 🧠 AI Pulse — Personalized AI News & Insights Platform

AI Pulse is a web platform that automatically aggregates the latest AI news from trusted sources, presents them as easy-to-scan highlights, and helps users go deeper with AI-generated summaries and a built-in AI assistant — all in one place.

Built as a final-year AIML project to solve a real problem: **staying updated with the fast-moving AI industry without spending hours browsing multiple sites.**

---

## ✨ Features

- 🔐 **User Authentication** — Sign up and log in to get a personalized feed
- 📰 **Auto-Fetched AI News** — Pulls updates from official sources (OpenAI, Anthropic, Google AI, Hugging Face, arXiv, etc.) every 1–2 days
- ⚡ **Highlight + Depth View** — Quick highlight cards, click to expand into a detailed AI-generated summary
- 🔗 **Official Source Links** — Every update links back to its original source for credibility
- 🎯 **Topic Preferences** — Filter news by interests like LLMs, Computer Vision, Robotics, Research Papers
- 🤖 **AI Assistant** — Chat with an integrated assistant to get updates explained in simple terms
- ⏰ **Scheduled Refresh** — Background job keeps the news feed current automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend + Backend | [Streamlit](https://streamlit.io/) |
| Database | SQLite |
| News Fetching | `feedparser` (RSS) + `requests` (APIs) |
| Summarization | LLM API (Anthropic / OpenAI) |
| AI Assistant | LLM API with context retrieval over stored articles |
| Scheduling | `APScheduler` |
| Deployment | Streamlit Community Cloud |

Pure Python stack — no separate frontend framework required.

---

## 📁 Project Structure

```
ai-pulse/
├── app.py                     # Main Streamlit app entry point
├── auth/
│   └── auth_utils.py          # Login/signup logic
├── fetcher/
│   ├── sources.py             # List of RSS feeds / API endpoints
│   ├── fetch_news.py          # Fetch + dedupe logic
│   └── scheduler.py           # APScheduler job for periodic fetch
├── summarizer/
│   └── summarize.py           # LLM calls for highlight + detailed summary
├── assistant/
│   └── chat_assistant.py      # AI assistant logic (context-aware chat)
├── db/
│   ├── models.py               # DB schema
│   └── database.db             # SQLite database (generated)
├── pages/                      # Streamlit multipage app pages
│   ├── 1_Feed.py
│   ├── 2_Article_Detail.py
│   ├── 3_Assistant.py
│   └── 4_Preferences.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- An API key from Anthropic or OpenAI

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
# Add your LLM API key inside .env
```

### Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🗺️ Roadmap

- [ ] User authentication
- [ ] RSS/API news fetcher with deduplication
- [ ] LLM-based highlight + detailed summary generation
- [ ] AI assistant chat over stored articles
- [ ] Topic-based preferences
- [ ] Scheduled auto-refresh (every 1–2 days)
- [ ] Deployment on Streamlit Community Cloud

**Future Enhancements:** Email digest, push notifications, mobile app, multi-language support.

---

## 📄 License

This project is developed for academic purposes as part of a final-year AIML curriculum.

---

## 🙋 Author

Built by [Your Name] as a final-year AIML project.