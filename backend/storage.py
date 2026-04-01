"""
Simple JSON-based storage for tweet data and AI insights.
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
INSIGHTS_DIR = DATA_DIR / "insights"
TWEETS_FILE = DATA_DIR / "tweets.json"


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    INSIGHTS_DIR.mkdir(exist_ok=True)


def save_tweets(tweets_data: list[dict]):
    """Save fetched tweets to disk."""
    _ensure_dirs()
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "tweets": tweets_data,
    }
    with open(TWEETS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(tweets_data)} tweets")


def load_tweets() -> dict:
    """Load cached tweets from disk."""
    _ensure_dirs()
    if not TWEETS_FILE.exists():
        return {"updated_at": None, "tweets": []}
    try:
        with open(TWEETS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tweets: {e}")
        return {"updated_at": None, "tweets": []}


def save_daily_digest(digest: dict, date: str = None):
    """Save daily digest to disk."""
    _ensure_dirs()
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    path = INSIGHTS_DIR / f"{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved daily digest for {date}")


def load_daily_digest(date: str = None) -> dict | None:
    """Load daily digest for a specific date."""
    _ensure_dirs()
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    path = INSIGHTS_DIR / f"{date}.json"
    if not path.exists():
        # Try to find most recent digest
        digests = sorted(INSIGHTS_DIR.glob("*.json"), reverse=True)
        if digests:
            path = digests[0]
        else:
            return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading digest: {e}")
        return None


def list_digests() -> list[str]:
    """List all available digest dates."""
    _ensure_dirs()
    return sorted(
        [p.stem for p in INSIGHTS_DIR.glob("*.json")],
        reverse=True,
    )
