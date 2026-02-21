#!/usr/bin/env python3
"""AI News Analyzer - Analyze news for Lenovo threats and opportunities"""

import os
import requests

ANALYSIS_PROMPT = """You are a strategic analyst for Lenovo Group. Analyze the following AI news and provide:

1. **Executive Summary** (3-5 bullet points of the most important news)

2. **Technology Trends** - Key AI technology developments

3. **Competitive Landscape** - What competitors (Dell, HP, Apple, Microsoft, etc.) are doing

4. **Hardware Developments** - AI chips, servers, edge devices, AI PCs

5. **Threats to Lenovo** - Potential risks and challenges
   - Rate each threat: 🔴 High | 🟡 Medium | 🟢 Low

6. **Opportunities for Lenovo** - Potential growth areas
   - Rate each opportunity: ⭐⭐⭐ High | ⭐⭐ Medium | ⭐ Low

7. **Recommended Actions** - Specific suggestions for Lenovo

Please be concise and actionable. Focus on business impact.

---
NEWS ITEMS:
{news_content}
"""

def analyze_news(news_items):
    """Use Anthropic API to analyze news for Lenovo impact"""
    news_items = news_items[:25]

    news_content = ""
    for i, item in enumerate(news_items, 1):
        news_content += f"\n{i}. [{item['source']}] {item['title']}\n"
        if item.get('summary'):
            summary = item['summary'].replace('<p>', '').replace('</p>', '')
            summary = summary[:200] + "..." if len(summary) > 200 else summary
            news_content += f"   {summary}\n"

    prompt = ANALYSIS_PROMPT.format(news_content=news_content)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception("ANTHROPIC_API_KEY not set")

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=300
    )

    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Analyzer module loaded successfully")
