#!/usr/bin/env python3
"""
AI情报官 - Entry point
Run with: python run.py
"""

import os
import sys
from pathlib import Path

# Load .env if present
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print("✅ Loaded .env configuration")
else:
    env_example = Path(__file__).parent / ".env.example"
    if env_example.exists():
        print("⚠️  No .env file found. Copy .env.example to .env and configure your API keys.")
        print("   The app will run in mock mode without real Twitter/AI data.\n")

# Defaults
host = os.getenv("APP_HOST", "0.0.0.0")
port = int(os.getenv("APP_PORT", "8000"))
mock = os.getenv("MOCK_MODE", "true").lower() == "true"
has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
has_twitter = bool(os.getenv("TWITTER_BEARER_TOKEN"))

print("=" * 60)
print("🔭 AI情报官 · Global AI Insights Tracker")
print("=" * 60)
print(f"   Mode:      {'Mock (demo)' if mock else 'Live'}")
print(f"   Claude AI: {'✅ Enabled' if has_anthropic else '⚠️  Not configured (using mock insights)'}")
print(f"   Twitter X: {'✅ Enabled' if has_twitter else '⚠️  Not configured (using mock tweets)'}")
print(f"   URL:       http://localhost:{port}")
print("=" * 60)
print()

import uvicorn
uvicorn.run(
    "backend.main:app",
    host=host,
    port=port,
    reload=False,
    log_level="info",
)
