---
name: ai-twitter-voices-tracker
description: Track and summarize the latest Twitter/X posts from global AI scientists, AI tech company founders, AI thought leaders, and top AI podcast accounts. Use when the user asks to monitor, watchlist, digest, or compare recent posts, topics, sentiment, links, and trends from these AI voices.
---

# AI Twitter Voices Tracker

## Define tracking scope first

Always confirm or infer these parameters before collecting posts:

1. Time window (default: last 24 hours; alternatives: 3 days, 7 days).
2. Target groups (scientists / founders / thought leaders / podcasts; allow all).
3. Language preference (default: Chinese summary, preserve key English terms).
4. Output depth (flash digest vs detailed briefing).
5. Whether to include only original posts or include replies/quotes.

If the user gives no constraints, use defaults and proceed directly.

## Maintain a dynamic watchlist

Build and maintain four account buckets:

- **AI Scientists**: researchers known for influential AI papers, labs, benchmarks, or safety work.
- **AI Founders**: founders/co-founders/CEOs of AI-native companies or major AI model/product companies.
- **AI Thought Leaders**: practitioners, investors, strategists, policy experts with recurring AI commentary.
- **Top AI Podcasts**: official podcast accounts and hosts focused on AI interviews, news, and technical discussions.

For each account, store:

- Handle and display name.
- Bucket label.
- Why included (1 short reason).
- Priority tier (P1 core / P2 active / P3 optional).

When uncertain whether an account fits, include it temporarily as P3 and mark as “待确认”.

## Collect latest posts reliably

When gathering updates:

1. Prioritize the newest posts within the requested window.
2. Capture post timestamp in UTC and user-local readable time.
3. Keep original links for every cited post.
4. De-duplicate near-identical cross-posted content.
5. Separate:
   - Original insights
   - News sharing/reposts
   - Product announcements
   - Hiring/community posts

If data source coverage is incomplete, explicitly state what is missing.

## Analyze content with a consistent schema

For each selected post, extract:

- **Who**: account + bucket.
- **What**: one-sentence summary.
- **Type**: research / product / policy / market / tooling / other.
- **Signal strength**: high / medium / low (based on novelty and downstream impact).
- **Sentiment**: optimistic / neutral / cautious / critical.
- **Actionability**: what the reader should monitor next.

Then produce cross-account synthesis:

- Top 3 recurring themes.
- Contradictions or debates between voices.
- Early signals (topics showing sudden acceleration).
- Notable absences (expected topic not discussed).

## Output format

Use this exact structure unless user asks otherwise:

### 1) Executive Snapshot

- Time window.
- Number of accounts scanned.
- Number of posts analyzed.
- 3–5 bullet key takeaways.

### 2) Bucket Highlights

#### AI Scientists
- `@handle` — summary | signal | link

#### AI Founders
- `@handle` — summary | signal | link

#### AI Thought Leaders
- `@handle` — summary | signal | link

#### AI Podcasts
- `@handle` — summary | signal | link

### 3) Theme & Trend Synthesis

- Theme A/B/C with evidence bullets.
- Diverging viewpoints.
- Potential next-7-day watch items.

### 4) Suggested Follow-up

Provide 3 concrete options, for example:

1. “只看高优先级(P1)账号，给我每日早报模板”
2. “按研究/产品/政策分栏追踪一周趋势”
3. “新增/移除关注名单并解释原因”

## Quality bar

Always:

- Prefer factual summaries over hype.
- Distinguish facts vs interpretation.
- Keep claims traceable to links.
- Flag uncertainty explicitly.
- Avoid inventing posts, metrics, or quotes.

Never:

- Present stale posts as “latest”.
- Mix unverified rumors into key takeaways without warning.
- Omit timestamps when discussing fast-moving topics.
