# AI News Bot 🤖

每日自动收集AI新闻，使用Claude AI分析对联想的威胁与机遇，生成精美图片报告并发送邮件。

## 功能特点

- 📰 多源新闻收集：TechCrunch、Wired、MIT Tech Review、Hacker News、GitHub Trending、arXiv论文、Product Hunt
- 🧠 Claude AI智能分析：识别技术趋势、竞争态势、威胁与机遇
- 🎨 精美图片报告：卡片式设计，渐变背景，专业排版
- 📧 自动邮件发送：支持QQ邮箱SMTP

## 安装

```bash
pip install feedparser requests pillow
```

## 配置

设置环境变量：

```bash
export QQ_EMAIL="your_email@qq.com"
export QQ_AUTH_CODE="your_qq_auth_code"
export RECIPIENT_EMAIL="recipient@qq.com"
```

## 使用

```bash
python main.py
```

## 定时任务

添加crontab实现每日8点自动运行：

```bash
0 8 * * * cd /path/to/ai_news_bot && /path/to/python main.py
```

## 项目结构

```
ai_news_bot/
├── main.py           # 主程序入口
├── news_collector.py # 新闻收集模块
├── analyzer.py       # Claude AI分析模块
├── image_generator.py# 图片报告生成
├── email_sender.py   # 邮件发送模块
└── run_bot.sh        # 运行脚本
```

## 依赖

- Python 3.8+
- Claude CLI
- feedparser
- requests
- Pillow
