"""
Twitter/X API client with mock data fallback.
Uses Twitter API v2 via tweepy when TWITTER_BEARER_TOKEN is set,
otherwise returns realistic mock data for demo/development.
"""

import os
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Mock tweet data for demo mode ───────────────────────────────────────────

MOCK_TWEETS = {
    "karpathy": [
        {
            "text": "Spending the day reading papers on mixture-of-experts. The scaling laws for MoE are surprisingly different from dense models. Some counterintuitive results around compute-optimal training.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
            "likes": 4823,
            "retweets": 891,
            "replies": 156,
            "url": "https://twitter.com/karpathy/status/mock1",
        },
        {
            "text": "The most underrated skill in ML engineering: being able to quickly debug a training run. Loss spikes, NaN gradients, learning rate issues — learning to diagnose these fast is worth 10x any specific algorithm knowledge.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
            "likes": 7234,
            "retweets": 1456,
            "replies": 234,
            "url": "https://twitter.com/karpathy/status/mock2",
        },
    ],
    "ylecun": [
        {
            "text": "Interesting paper on world models from DeepMind. But I still maintain that LLMs alone cannot achieve true human-level intelligence. We need grounded, embodied learning with persistent world models. The path is JEPA.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
            "likes": 3421,
            "retweets": 723,
            "replies": 445,
            "url": "https://twitter.com/ylecun/status/mock1",
        },
        {
            "text": "New META FAIR paper on self-supervised learning for video understanding. We're getting closer to machines that can learn from watching the world like children do.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=22)).isoformat(),
            "likes": 2198,
            "retweets": 456,
            "replies": 89,
            "url": "https://twitter.com/ylecun/status/mock2",
        },
    ],
    "sama": [
        {
            "text": "We are on the verge of something extraordinary. AGI may be closer than most people think. The key question is no longer if but how we navigate this transition responsibly.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "likes": 15234,
            "retweets": 3891,
            "replies": 2156,
            "url": "https://twitter.com/sama/status/mock1",
        },
        {
            "text": "GPT-5 training is going well. Seeing emergent capabilities we didn't anticipate. The scaling continues to surprise us.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=14)).isoformat(),
            "likes": 28934,
            "retweets": 7234,
            "replies": 4523,
            "url": "https://twitter.com/sama/status/mock2",
        },
    ],
    "dario_amodei": [
        {
            "text": "Claude 3.7 is now available. The improvements in reasoning and code generation are substantial. We've made major strides on the alignment front — the model is more honest and less prone to hallucination.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "likes": 8934,
            "retweets": 2134,
            "replies": 987,
            "url": "https://twitter.com/dario_amodei/status/mock1",
        },
        {
            "text": "Constitutional AI + RLHF together is proving to be a powerful combination. We're seeing significantly better alignment without sacrificing capability. Safety and capability are not fundamentally at odds.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=28)).isoformat(),
            "likes": 5678,
            "retweets": 1234,
            "replies": 456,
            "url": "https://twitter.com/dario_amodei/status/mock2",
        },
    ],
    "emollick": [
        {
            "text": "I ran an experiment: gave 200 MBA students the same strategic analysis task with and without Claude. The AI-assisted group outperformed on every metric. But more interesting: the distribution of outcomes COMPRESSED. AI is narrowing skill gaps.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
            "likes": 6234,
            "retweets": 1823,
            "replies": 342,
            "url": "https://twitter.com/emollick/status/mock1",
        },
        {
            "text": "New paper in Nature: AI now writes 25% of code at major tech companies. The productivity implications are staggering — but so are the workforce implications. We need much better education policies for the AI era.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=20)).isoformat(),
            "likes": 9123,
            "retweets": 2987,
            "replies": 678,
            "url": "https://twitter.com/emollick/status/mock2",
        },
    ],
    "lexfridman": [
        {
            "text": "Just finished a 5-hour conversation with Ilya Sutskever about the nature of intelligence, consciousness, and the path to superintelligence. One of the most profound conversations I've had. Coming soon.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "likes": 12456,
            "retweets": 2345,
            "replies": 1234,
            "url": "https://twitter.com/lexfridman/status/mock1",
        },
    ],
    "drfeifei": [
        {
            "text": "World Labs just released our first spatial intelligence model. We can now reason about 3D structure from 2D images in a way that generalizes across domains. This is a foundational step toward machines that understand physical space.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "likes": 7845,
            "retweets": 1923,
            "replies": 456,
            "url": "https://twitter.com/drfeifei/status/mock1",
        },
    ],
    "demishassabis": [
        {
            "text": "AlphaFold 3 has now predicted protein structures for virtually every known organism. We're using this to accelerate drug discovery across 50+ diseases. Science is about to change fundamentally.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat(),
            "likes": 11234,
            "retweets": 3456,
            "replies": 789,
            "url": "https://twitter.com/demishassabis/status/mock1",
        },
    ],
    "mustafasuleyman": [
        {
            "text": "Copilot is now used by 400M people monthly. We're seeing the productivity data and it's remarkable — knowledge workers are completing complex tasks 40% faster. This is just the beginning of the AI-augmented workforce.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
            "likes": 4567,
            "retweets": 987,
            "replies": 234,
            "url": "https://twitter.com/mustafasuleyman/status/mock1",
        },
    ],
    "ilyasut": [
        {
            "text": "The pre-training paradigm still has a lot left to give. We're nowhere near the limits of what can be learned from next-token prediction at scale. But the next frontier is teaching models to reason about their own uncertainty.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
            "likes": 8934,
            "retweets": 2123,
            "replies": 567,
            "url": "https://twitter.com/ilyasut/status/mock1",
        },
    ],
    "dwarkesh_sp": [
        {
            "text": "New episode: 3 hours with Dario Amodei on Claude's capabilities, Anthropic's roadmap, and what happens when AI can do most cognitive work. One of the most interesting conversations I've had on the show.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=9)).isoformat(),
            "likes": 5678,
            "retweets": 1456,
            "replies": 345,
            "url": "https://twitter.com/dwarkesh_sp/status/mock1",
        },
    ],
    "saranormous": [
        {
            "text": "Hot take: the AI companies will be the most valuable companies in history, but the biggest winners will be the vertical application builders who deeply understand specific domains. Infrastructure vs application debate is already being settled by revenue.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=11)).isoformat(),
            "likes": 3456,
            "retweets": 876,
            "replies": 234,
            "url": "https://twitter.com/saranormous/status/mock1",
        },
    ],
    "garymarcus": [
        {
            "text": "Three new papers out this week all showing that LLMs fail systematically on compositional generalization tasks that 4-year-olds handle easily. The gap between benchmark performance and true understanding remains massive.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=15)).isoformat(),
            "likes": 2345,
            "retweets": 678,
            "replies": 456,
            "url": "https://twitter.com/garymarcus/status/mock1",
        },
    ],
    "paulg": [
        {
            "text": "The companies that figure out how to use AI to 10x their engineering velocity will dominate their markets within 3 years. This is the most important operational question for startups right now.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=16)).isoformat(),
            "likes": 8923,
            "retweets": 2134,
            "replies": 567,
            "url": "https://twitter.com/paulg/status/mock1",
        },
    ],
    "timnitgebru": [
        {
            "text": "The concentration of AI power in 4-5 companies is deeply concerning. We need antitrust action and open-source alternatives. The infrastructure of intelligence should not be controlled by a handful of Silicon Valley firms.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=13)).isoformat(),
            "likes": 4567,
            "retweets": 1234,
            "replies": 789,
            "url": "https://twitter.com/timnitgebru/status/mock1",
        },
    ],
    "danielaamodei": [
        {
            "text": "Thrilled to announce Anthropic's partnership with AWS to bring Claude to 100,000+ enterprise customers. Constitutional AI at enterprise scale — this is how we deploy powerful AI responsibly.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=17)).isoformat(),
            "likes": 3456,
            "retweets": 892,
            "replies": 234,
            "url": "https://twitter.com/danielaamodei/status/mock1",
        },
    ],
    "gdb": [
        {
            "text": "The thing nobody talks about enough: the compounding effect of AI on AI research. Models that are better at reasoning are faster at generating new AI research insights. We may be entering a period of super-exponential progress.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=19)).isoformat(),
            "likes": 5678,
            "retweets": 1456,
            "replies": 345,
            "url": "https://twitter.com/gdb/status/mock1",
        },
    ],
    "rasbt": [
        {
            "text": "Just published a deep dive on how to train small LLMs from scratch with only 10B tokens. Key finding: data quality matters MORE than quantity below 100B tokens. A carefully curated 10B dataset beats a noisy 100B one.",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=21)).isoformat(),
            "likes": 4321,
            "retweets": 1098,
            "replies": 234,
            "url": "https://twitter.com/rasbt/status/mock1",
        },
    ],
}

# Default tweets for influencers not in MOCK_TWEETS
DEFAULT_MOCK_TWEETS = [
    {
        "text": "Exciting times in AI. New research directions are emerging every week. The field is moving faster than ever before.",
        "created_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))).isoformat(),
        "likes": random.randint(500, 5000),
        "retweets": random.randint(100, 1000),
        "replies": random.randint(50, 500),
        "url": "https://twitter.com/status/mock_default",
    }
]


class TwitterClient:
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
        self._client = None

        if self.bearer_token and not self.mock_mode:
            try:
                import tweepy
                self._client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("Twitter API client initialized")
            except ImportError:
                logger.warning("tweepy not installed, using mock mode")
                self.mock_mode = True
        else:
            logger.info("Running in mock mode (no Twitter API key)")
            self.mock_mode = True

    def fetch_user_tweets(
        self,
        twitter_id: str,
        handle: str,
        max_results: int = 5,
    ) -> list[dict]:
        """Fetch recent tweets for a user. Falls back to mock data."""
        if self.mock_mode or not self._client:
            return self._get_mock_tweets(handle)

        try:
            import tweepy
            response = self._client.get_users_tweets(
                id=twitter_id,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "entities"],
                expansions=["author_id"],
            )

            if not response.data:
                return []

            tweets = []
            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                tweets.append({
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "url": f"https://twitter.com/{handle}/status/{tweet.id}",
                })
            return tweets

        except Exception as e:
            logger.error(f"Twitter API error for {handle}: {e}")
            return self._get_mock_tweets(handle)

    def _get_mock_tweets(self, handle: str) -> list[dict]:
        tweets = MOCK_TWEETS.get(handle, DEFAULT_MOCK_TWEETS)
        # Add slight randomness to timestamps each call
        result = []
        for t in tweets:
            tweet = t.copy()
            result.append(tweet)
        return result


# Singleton instance
_client: Optional[TwitterClient] = None


def get_twitter_client() -> TwitterClient:
    global _client
    if _client is None:
        _client = TwitterClient()
    return _client
