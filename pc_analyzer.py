#!/usr/bin/env python3
"""PC Market Analyzer - Competitive analysis for Dell, HP, Lenovo vs Apple"""

import os
import time
import requests

ANALYSIS_PROMPT = """你是一位资深的PC行业分析师。请用中文基于以下一周的行业新闻和市场信息，提供专业的竞争分析报告：

## 分析要求

### 1. 执行摘要
- 本周PC市场3-5个最重要的动态

### 2. 主流价位段产品对比分析（$800-$1500）

请对比分析 Dell、HP、Lenovo 三大品牌的主流产品线：

**Dell（XPS、Inspiron、Latitude系列）**
- 产品定位与目标用户
- 性能表现（CPU/GPU配置）
- 续航能力
- 设计与做工
- 性价比评估

**HP（Spectre、Envy、EliteBook系列）**
- 产品定位与目标用户
- 性能表现（CPU/GPU配置）
- 续航能力
- 设计与做工
- 性价比评估

**Lenovo（ThinkPad、Yoga、IdeaPad系列）**
- 产品定位与目标用户
- 性能表现（CPU/GPU配置）
- 续航能力
- 设计与做工
- 性价比评估

**综合对比结论**
- 各品牌优势领域
- 各品牌短板
- 不同用户群体推荐

### 3. Apple威胁分析（重点章节）

**Apple Silicon的竞争优势**
- M系列芯片性能与能效比
- macOS生态系统粘性
- 品牌溢价能力

**对Windows PC厂商的威胁**
- 🔴 高威胁 / 🟡 中威胁 / 🟢 低威胁 - 具体描述
- 市场份额影响
- 利润率压力
- 高端市场蚕食

**应对策略建议**

### 4. PC业态发展趋势
- AI PC发展方向
- ARM架构Windows PC前景
- 续航与性能平衡趋势
- 轻薄化与散热挑战

### 5. 下一代产品建议

**硬件配置建议**
- 处理器选择（Intel/AMD/Qualcomm）
- 内存与存储配置
- 显示屏规格
- 电池容量与快充

**差异化方向**
- AI功能集成
- 企业安全特性
- 可持续发展（环保材料、可维修性）

**定价策略建议**

### 6. 风险与机遇

**威胁分析**
- 每条用格式：🔴 高风险 / 🟡 中风险 / 🟢 低风险 - 描述

**机遇分析**
- 每条用格式：⭐⭐⭐ 高价值 / ⭐⭐ 中价值 / ⭐ 低价值 - 描述

请基于专业知识和市场数据提供深度分析，不要使用表格格式，使用列表格式。

---
本周行业新闻:
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
                    "max_tokens": 8192,
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
