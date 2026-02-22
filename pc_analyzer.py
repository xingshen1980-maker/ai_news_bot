#!/usr/bin/env python3
"""PC Market Analyzer - Competitive analysis for Dell, HP, Lenovo vs Apple"""

import os
import time
import requests

ANALYSIS_PROMPT = """你是PC行业分析师。请用中文分析以下新闻，提供：

1. **执行摘要** - 本周3-5个最重要动态

2. **品牌对比**（$800-$1500价位）
- Dell（XPS/Latitude）：性能、续航、性价比
- HP（Spectre/EliteBook）：性能、续航、性价比
- Lenovo（ThinkPad/Yoga）：性能、续航、性价比

3. **Apple威胁分析**（重点）
- M系列芯片优势
- 对Windows PC厂商的威胁：🔴高/🟡中/🟢低 - 描述
- 应对策略

4. **趋势与建议**
- AI PC发展方向
- 下一代产品建议

5. **威胁分析**
- 🔴 高风险 / 🟡 中风险 / 🟢 低风险 - 描述

6. **机遇分析**
- ⭐⭐⭐ 高价值 / ⭐⭐ 中价值 / ⭐ 低价值 - 描述

请简洁，使用列表格式。

---
新闻:
{news_content}
"""

def analyze_with_api(prompt, max_retries=3):
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
                        {"role": "system", "content": "你是一位资深PC行业分析师，拥有20年行业经验。请提供专业、深度、可操作的分析报告。用中文回答。"},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=600
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code >= 500 or "timeout" in response.text.lower():
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(10)
                continue
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out, retrying...")
            time.sleep(10)
            continue

    raise Exception("API failed after max retries")

def analyze_pc_market(news_items):
    """Analyze PC market competitive landscape"""
    news_items = news_items[:40]

    news_content = ""
    for i, item in enumerate(news_items, 1):
        news_content += f"\n{i}. [{item['source']}] {item['title']}\n"
        if item.get('summary'):
            summary = item['summary'].replace('<p>', '').replace('</p>', '')
            summary = summary[:250] + "..." if len(summary) > 250 else summary
            news_content += f"   {summary}\n"

    prompt = ANALYSIS_PROMPT.format(news_content=news_content)
    return analyze_with_api(prompt)

if __name__ == "__main__":
    print("PC Market Analyzer module loaded successfully")
