#!/usr/bin/env python3
"""AI News Analyzer - Analyze news for Lenovo threats and opportunities"""

import os
import subprocess

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
    """Use Claude CLI to analyze news for Lenovo impact"""
    news_items = news_items[:25]

    news_content = ""
    for i, item in enumerate(news_items, 1):
        news_content += f"\n{i}. [{item['source']}] {item['title']}\n"
        if item.get('summary'):
            summary = item['summary'].replace('<p>', '').replace('</p>', '')
            summary = summary[:200] + "..." if len(summary) > 200 else summary
            news_content += f"   {summary}\n"

    prompt = ANALYSIS_PROMPT.format(news_content=news_content)

    result = subprocess.run(
        ['claude', '-p', prompt, '--model', 'sonnet'],
        capture_output=True, text=True, timeout=600
    )

    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"Claude CLI error: {result.stderr}")

if __name__ == "__main__":
    print("Analyzer module loaded successfully")
