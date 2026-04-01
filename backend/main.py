"""
AI情报官 — FastAPI Backend
Tracks global AI thought leaders' tweets and generates daily insights.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .influencers import INFLUENCERS, CATEGORIES, get_influencers_by_category
from .twitter_client import get_twitter_client
from .ai_analyzer import get_analyzer
from .storage import save_tweets, load_tweets, save_daily_digest, load_daily_digest, list_digests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI情报官 API",
    description="Track global AI thought leaders on Twitter/X",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Serve frontend
if FRONTEND_DIR.exists():
    @app.get("/")
    async def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")


# ─── Background task: fetch all tweets ───────────────────────────────────────

def _fetch_and_analyze_all():
    """Fetch tweets from all influencers and analyze them with AI."""
    twitter = get_twitter_client()
    analyzer = get_analyzer()

    all_data = []
    for influencer in INFLUENCERS:
        try:
            tweets = twitter.fetch_user_tweets(
                twitter_id=influencer["twitter_id"],
                handle=influencer["handle"],
                max_results=3,
            )
            for tweet in tweets:
                analysis = analyzer.analyze_tweet(tweet, influencer)
                all_data.append({
                    "influencer": influencer,
                    "tweet": tweet,
                    "analysis": analysis,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            logger.error(f"Error fetching {influencer['handle']}: {e}")

    if all_data:
        save_tweets(all_data)
        logger.info(f"Fetched and analyzed {len(all_data)} tweets")

    return all_data


def _generate_digest(tweets_data: list[dict]):
    """Generate daily AI digest from tweet data."""
    analyzer = get_analyzer()
    # Sort by engagement
    sorted_data = sorted(
        tweets_data,
        key=lambda x: x["tweet"].get("likes", 0) + x["tweet"].get("retweets", 0) * 3,
        reverse=True,
    )
    digest = analyzer.generate_daily_digest(sorted_data)
    save_daily_digest(digest)
    return digest


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/influencers")
async def get_influencers(category: str = Query(default="all")):
    """Get list of tracked influencers, optionally filtered by category."""
    return {
        "influencers": get_influencers_by_category(category),
        "categories": CATEGORIES,
        "total": len(INFLUENCERS),
    }


@app.get("/api/tweets")
async def get_tweets(
    category: Optional[str] = Query(default=None),
    influencer_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    """Get cached tweet data with AI analysis."""
    cached = load_tweets()
    tweets = cached.get("tweets", [])

    # Filter by category
    if category and category != "all":
        tweets = [t for t in tweets if t["influencer"]["category"] == category]

    # Filter by influencer
    if influencer_id:
        tweets = [t for t in tweets if t["influencer"]["id"] == influencer_id]

    # Sort by engagement
    tweets = sorted(
        tweets,
        key=lambda x: x["tweet"].get("likes", 0) + x["tweet"].get("retweets", 0) * 3,
        reverse=True,
    )[:limit]

    return {
        "tweets": tweets,
        "total": len(tweets),
        "updated_at": cached.get("updated_at"),
    }


@app.get("/api/digest")
async def get_digest(date: Optional[str] = Query(default=None)):
    """Get the daily AI insights digest."""
    digest = load_daily_digest(date)
    if not digest:
        # Generate on-the-fly if not cached
        cached = load_tweets()
        if cached.get("tweets"):
            digest = _generate_digest(cached["tweets"])
        else:
            # No data yet, trigger refresh first
            data = _fetch_and_analyze_all()
            digest = _generate_digest(data)
    return digest or {}


@app.get("/api/digest/history")
async def get_digest_history():
    """Get list of available digest dates."""
    return {"dates": list_digests()}


@app.post("/api/refresh")
async def refresh_data(background_tasks: BackgroundTasks):
    """Trigger a data refresh in the background."""
    background_tasks.add_task(_do_full_refresh)
    return {"message": "数据刷新中，请稍候...", "status": "refreshing"}


async def _do_full_refresh():
    """Full refresh: fetch tweets + generate digest."""
    import asyncio
    import concurrent.futures

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        data = await loop.run_in_executor(pool, _fetch_and_analyze_all)
        if data:
            await loop.run_in_executor(pool, _generate_digest, data)


@app.get("/api/stats")
async def get_stats():
    """Get app statistics."""
    cached = load_tweets()
    tweets = cached.get("tweets", [])

    category_counts = {}
    for tweet in tweets:
        cat = tweet["influencer"]["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total_likes = sum(t["tweet"].get("likes", 0) for t in tweets)
    total_retweets = sum(t["tweet"].get("retweets", 0) for t in tweets)

    return {
        "total_tweets": len(tweets),
        "total_influencers": len(INFLUENCERS),
        "category_breakdown": category_counts,
        "total_engagement": total_likes + total_retweets,
        "last_updated": cached.get("updated_at"),
        "digests_available": len(list_digests()),
    }


# ─── Startup: load or fetch initial data ─────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """On startup, load cached data or fetch fresh data."""
    cached = load_tweets()
    if not cached.get("tweets"):
        logger.info("No cached data found, fetching initial data...")
        import asyncio
        import concurrent.futures

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            data = await loop.run_in_executor(pool, _fetch_and_analyze_all)
            if data:
                await loop.run_in_executor(pool, _generate_digest, data)
    else:
        logger.info(f"Loaded {len(cached['tweets'])} cached tweets")
