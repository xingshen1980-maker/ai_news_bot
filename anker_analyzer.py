#!/usr/bin/env python3
"""Anker News Analyzer - Analyze news for Anker competitive intelligence"""

import os
import time
import requests

ANALYSIS_PROMPT = """你是安克创新(Anker Innovations)的战略分析师。请用中文分析以下一周的行业新闻，提供：

1. **执行摘要** (3-5个最重要的要点)

2. **安克动态** - 安克及其子品牌(Soundcore、Eufy、Nebula、AnkerMake)的最新动态

3. **竞争格局** - 竞争对手（Belkin、Baseus、绿联、RAVPower等）的动态

4. **市场趋势** - 充电技术、智能家居、音频设备等领域的发展趋势

5. **威胁分析** - 对安克的潜在风险和挑战
   - 每条威胁用以下格式：🔴 高风险 / 🟡 中风险 / 🟢 低风险 - 具体描述

6. **机遇分析** - 潜在增长领域
   - 每条机遇用以下格式：⭐⭐⭐ 高价值 / ⭐⭐ 中价值 / ⭐ 低价值 - 具体描述

7. **建议行动** - 对安克的具体建议

请简洁、可操作，聚焦商业影响。不要使用表格格式，使用列表格式。

---
本周新闻内容:
{news_content}
"""

def analyze_with_api(prompt, max_retries=10):
    """Use OpenAI-compatible API via gateway with retry"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://sky.tinyandbeautiful.com")

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-opus-4-5-20251101",
                    "max_tokens": 4096,
                    "messages": [
                        {"role": "system", "content": "你是一位专业的消费电子行业战略分析师。请用中文提供详细分析。"},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=300
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Attempt {attempt + 1} failed: {response.status_code} - {response.text[:200]}")
                time.sleep(20)
                continue
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out, retrying...")
            time.sleep(20)
            continue

    raise Exception("API failed after max retries")

def analyze_anker_news(news_items):
    """Analyze news for Anker impact"""
    news_items = news_items[:30]

    news_content = ""
    for i, item in enumerate(news_items, 1):
        news_content += f"\n{i}. [{item['source']}] {item['title']}\n"
        if item.get('summary'):
            summary = item['summary'].replace('<p>', '').replace('</p>', '')
            summary = summary[:200] + "..." if len(summary) > 200 else summary
            news_content += f"   {summary}\n"

    prompt = ANALYSIS_PROMPT.format(news_content=news_content)
    return analyze_with_api(prompt)

if __name__ == "__main__":
    print("Anker Analyzer module loaded successfully")
