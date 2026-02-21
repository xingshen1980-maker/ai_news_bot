#!/usr/bin/env python3
"""AI News Analyzer - Analyze news for Lenovo threats and opportunities"""

import os
import subprocess
import requests

ANALYSIS_PROMPT = """你是联想集团的战略分析师。请用中文分析以下AI新闻，提供：

1. **执行摘要** (3-5个最重要新闻的要点)

2. **技术趋势** - 关键AI技术发展

3. **竞争格局** - 竞争对手（戴尔、惠普、苹果、微软等）的动态

4. **硬件发展** - AI芯片、服务器、边缘设备、AI PC

5. **威胁分析** - 对联想的潜在风险和挑战
   - 每条威胁用以下格式：🔴 高风险 / 🟡 中风险 / 🟢 低风险 - 具体描述

6. **机遇分析** - 潜在增长领域
   - 每条机遇用以下格式：⭐⭐⭐ 高价值 / ⭐⭐ 中价值 / ⭐ 低价值 - 具体描述

7. **建议行动** - 对联想的具体建议

请简洁、可操作，聚焦商业影响。不要使用表格格式，使用列表格式。

---
新闻内容:
{news_content}
"""

def analyze_with_api(prompt):
    """Use OpenAI-compatible API via gateway"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://sky.tinyandbeautiful.com")

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
                {"role": "system", "content": "你是一位专业的商业战略分析师。请用中文提供详细分析。"},
                {"role": "user", "content": prompt}
            ]
        },
        timeout=300
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")

def analyze_with_cli(prompt):
    """Use Claude CLI for local execution"""
    result = subprocess.run(
        ['claude', '-p', prompt, '--model', 'sonnet'],
        capture_output=True, text=True, timeout=600
    )
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"Claude CLI error: {result.stderr}")

def analyze_news(news_items):
    """Analyze news for Lenovo impact"""
    news_items = news_items[:25]

    news_content = ""
    for i, item in enumerate(news_items, 1):
        news_content += f"\n{i}. [{item['source']}] {item['title']}\n"
        if item.get('summary'):
            summary = item['summary'].replace('<p>', '').replace('</p>', '')
            summary = summary[:200] + "..." if len(summary) > 200 else summary
            news_content += f"   {summary}\n"

    prompt = ANALYSIS_PROMPT.format(news_content=news_content)

    # Use API if ANTHROPIC_API_KEY is set, otherwise use CLI
    if os.environ.get("ANTHROPIC_API_KEY"):
        return analyze_with_api(prompt)
    else:
        return analyze_with_cli(prompt)

if __name__ == "__main__":
    print("Analyzer module loaded successfully")
