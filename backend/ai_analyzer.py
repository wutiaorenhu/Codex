"""
AI-powered tweet analysis using Claude API.
Generates Chinese-language summaries, key insights, and daily digests.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional
import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """你是AI情报官，专门追踪全球顶级AI科学家、创始人、意见领袖和播客在Twitter上的最新发言。

你的任务是：
1. 用中文总结英文推文的核心内容（简洁、准确、有洞察）
2. 提取关键主题标签（中英文）
3. 判断内容的重要性和影响力
4. 在生成每日洞察时，找出当天最重要的趋势和突破

输出风格：
- 专业简洁，像高质量的AI行业简报
- 避免翻译腔，用地道的中文表达
- 突出对AI行业的影响和意义
- 数据和事实要准确引用"""


class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set — AI analysis disabled")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)

    def analyze_tweet(self, tweet: dict, influencer: dict) -> dict:
        """Analyze a single tweet and return enriched data with Chinese summary."""
        if not self.client:
            return self._mock_analysis(tweet, influencer)

        prompt = f"""分析以下来自 {influencer['name']} ({influencer['title_zh']}) 的推文：

推文内容：
{tweet['text']}

请以JSON格式返回：
{{
  "summary_zh": "中文摘要（50-100字，突出核心观点和对AI行业的意义）",
  "key_points": ["要点1", "要点2", "要点3"],
  "tags": ["标签1", "标签2", "标签3"],
  "importance": "high/medium/low",
  "topic": "主要话题分类（如：模型能力/AI安全/商业进展/研究突破/行业观点）",
  "sentiment": "positive/neutral/negative/controversial"
}}"""

        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            text = next(
                (b.text for b in response.content if b.type == "text"), "{}"
            )
            # Extract JSON from response
            import re
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return self._mock_analysis(tweet, influencer)

        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return self._mock_analysis(tweet, influencer)

    def generate_daily_digest(self, all_tweets_data: list[dict]) -> dict:
        """Generate a comprehensive daily AI insights digest from all tweets."""
        if not self.client:
            return self._mock_daily_digest()

        # Prepare tweet summaries for context
        tweets_summary = []
        for item in all_tweets_data[:30]:  # Top 30 most engaging tweets
            tweets_summary.append(
                f"- [{item['influencer']['name']} / {item['influencer']['title_zh']}]: "
                f"{item['tweet']['text'][:200]}"
            )

        tweets_text = "\n".join(tweets_summary)

        prompt = f"""今天是 {datetime.now().strftime('%Y年%m月%d日')}。

以下是全球顶级AI思想领袖今天在Twitter上的最新发言摘要：

{tweets_text}

请生成一份专业的AI每日洞察报告，以JSON格式返回：
{{
  "headline": "今日最重要的AI动态（一句话标题）",
  "executive_summary": "执行摘要（150-200字，概括今天AI领域最重要的3-5个动态）",
  "top_trends": [
    {{
      "trend": "趋势名称",
      "description": "趋势描述（50字）",
      "evidence": "相关人物/事件"
    }}
  ],
  "key_developments": [
    {{
      "title": "发展标题",
      "detail": "详细说明（80字）",
      "importance": "high/medium"
    }}
  ],
  "hot_debates": ["争议话题1", "争议话题2"],
  "watch_list": ["值得关注的技术/公司/趋势1", "值得关注的技术/公司/趋势2"],
  "market_signal": "今日AI行业信号（积极/谨慎/混合）及简短理由"
}}"""

        try:
            with self.client.messages.stream(
                model=MODEL,
                max_tokens=2048,
                thinking={"type": "adaptive"},
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                final = stream.get_final_message()

            text = next(
                (b.text for b in final.content if b.type == "text"), "{}"
            )
            import re
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                result = json.loads(json_match.group())
                result["generated_at"] = datetime.now(timezone.utc).isoformat()
                result["date"] = datetime.now().strftime("%Y-%m-%d")
                return result

        except Exception as e:
            logger.error(f"Daily digest generation error: {e}")

        return self._mock_daily_digest()

    def batch_analyze_tweets(self, tweets_with_influencers: list[tuple]) -> list[dict]:
        """Analyze multiple tweets efficiently."""
        results = []
        for tweet, influencer in tweets_with_influencers:
            analysis = self.analyze_tweet(tweet, influencer)
            results.append(analysis)
        return results

    # ─── Mock data for when API key is not available ──────────────────────────

    def _mock_analysis(self, tweet: dict, influencer: dict) -> dict:
        """Return a mock analysis based on tweet content."""
        text = tweet["text"].lower()

        # Simple keyword-based topic detection
        if any(w in text for w in ["safety", "alignment", "risk", "constitutional"]):
            topic = "AI安全"
            tags = ["AI安全", "对齐研究", "风险"]
        elif any(w in text for w in ["model", "training", "benchmark", "capability"]):
            topic = "模型能力"
            tags = ["模型训练", "技术突破", "基准测试"]
        elif any(w in text for w in ["company", "raise", "fund", "invest", "billion"]):
            topic = "商业进展"
            tags = ["融资", "商业化", "市场"]
        elif any(w in text for w in ["research", "paper", "arxiv", "study"]):
            topic = "研究突破"
            tags = ["学术研究", "论文", "新发现"]
        else:
            topic = "行业观点"
            tags = ["AI趋势", "观点", "洞察"]

        # Generate importance based on likes
        likes = tweet.get("likes", 0)
        importance = "high" if likes > 8000 else "medium" if likes > 2000 else "low"

        return {
            "summary_zh": f"{influencer['name']}就{topic}分享了重要观点：{tweet['text'][:80]}...",
            "key_points": [
                tweet["text"][:60] + "...",
                f"来自{influencer['title_zh']}的专业视角",
                "值得持续关注的AI行业动态",
            ],
            "tags": tags,
            "importance": importance,
            "topic": topic,
            "sentiment": "neutral",
        }

    def _mock_daily_digest(self) -> dict:
        return {
            "headline": "AI模型能力竞赛加速，安全与商业化议题引发广泛讨论",
            "executive_summary": (
                "今日AI领域焦点：OpenAI、Anthropic、DeepMind三大巨头同步发力，"
                "新模型能力显著提升。Sam Altman暗示AGI时间线大幅提前；"
                "Yann LeCun继续倡导世界模型路线；多位研究者警告AI风险被低估。"
                "商业化方面，企业AI采纳率创历史新高，Copilot用户突破4亿。"
                "学术界聚焦小模型高效训练，数据质量再次成为核心议题。"
            ),
            "top_trends": [
                {
                    "trend": "AGI时间线提前",
                    "description": "多位领袖认为AGI将在2-3年内到来",
                    "evidence": "Sam Altman, Greg Brockman",
                },
                {
                    "trend": "AI企业应用爆发",
                    "description": "企业级AI工具采纳率大幅提升，生产力数据显著",
                    "evidence": "Mustafa Suleyman, Ethan Mollick",
                },
                {
                    "trend": "开源vs闭源博弈",
                    "description": "AI基础设施集中化引发治理担忧",
                    "evidence": "Timnit Gebru, Gary Marcus",
                },
            ],
            "key_developments": [
                {
                    "title": "新一代模型训练取得突破",
                    "detail": "多家实验室报告训练效率大幅提升，涌现能力出现在意料之外的规模",
                    "importance": "high",
                },
                {
                    "title": "AI辅助科研加速",
                    "detail": "AlphaFold3覆盖所有已知生物体蛋白质结构，药物发现进入新纪元",
                    "importance": "high",
                },
            ],
            "hot_debates": [
                "LLM能否实现真正的推理还是只是模式匹配？",
                "AI安全监管的时机是否已经到来？",
            ],
            "watch_list": [
                "Ilya Sutskever的SSI进展",
                "欧盟AI法案实施细则",
                "开源小模型突破闭源大模型性能",
            ],
            "market_signal": "积极 — 技术突破频出，商业化加速，但监管不确定性上升需关注",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }


# Singleton instance
_analyzer: Optional[AIAnalyzer] = None


def get_analyzer() -> AIAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = AIAnalyzer()
    return _analyzer
