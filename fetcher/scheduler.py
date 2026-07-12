"""
fetcher/scheduler.py
Background job that periodically fetches new articles and summarizes them,
so the Feed stays current without you manually running two commands.

IMPORTANT: this scheduler only runs while the Streamlit app process is
alive. If you close the app, nothing runs in the background - this is not
a system-level cron job. For a always-on version, you'd deploy the app
somewhere that stays running (e.g. Streamlit Community Cloud) or use a
separate cron job hitting a script. For this project, "runs while the app
is open" is a reasonable and honest scope for a week-1 build.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from db.database import init_db
from fetcher.fetch_news import fetch_all_sources
from summarizer.summarize import summarize_pending_articles

logger = logging.getLogger("ai_pulse.scheduler")

JOB_ID = "ai_pulse_refresh_job"

# How often to auto-refresh. Your mentor's advice was "check every 1-2 days" -
# 48 hours matches that. Change this single number to adjust the interval.
REFRESH_INTERVAL_HOURS = 48


def run_refresh_job():
    """
    The actual work: fetch new articles, then summarize whatever's pending.
    Runs multiple summarization passes so a big backlog doesn't get stuck
    waiting for the next scheduled run (see Day 4's per-source batching).
    """
    logger.info("Scheduled refresh starting...")
    try:
        init_db()
        fetch_result = fetch_all_sources()
        logger.info(f"Fetch complete: {fetch_result['_total_new']} new articles")

        # Run a few summarization passes back-to-back to clear backlog,
        # since each pass only takes ~5 articles per source (Day 4 fix)
        total_summarized = 0
        for _ in range(4):
            sm_result = summarize_pending_articles()
            total_summarized += sm_result["succeeded"]
            if sm_result["total"] == 0:
                break  # nothing left to summarize, stop early
        logger.info(f"Summarization complete: {total_summarized} articles summarized")

    except Exception as e:
        # A failed scheduled run should never crash the whole app -
        # just log it and let the next scheduled run try again
        logger.error(f"Scheduled refresh failed: {e}")


_scheduler = None


def start_scheduler() -> BackgroundScheduler:
    """
    Creates and starts the background scheduler exactly once.
    Safe to call multiple times - subsequent calls just return the existing
    scheduler instead of creating duplicate jobs (replace_existing=True as
    a second layer of protection against duplicate jobs on the same id).
    """
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_refresh_job,
        trigger="interval",
        hours=REFRESH_INTERVAL_HOURS,
        id=JOB_ID,
        replace_existing=True,
        next_run_time=None,  # don't fire immediately on startup - wait one full interval
    )
    _scheduler.start()
    logger.info(f"Scheduler started - refreshing every {REFRESH_INTERVAL_HOURS}h")
    return _scheduler


if __name__ == "__main__":
    # Manual one-off run, useful for testing without waiting for the schedule:
    # python -m fetcher.scheduler
    logging.basicConfig(level=logging.INFO)
    run_refresh_job()
