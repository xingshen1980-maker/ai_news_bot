#!/usr/bin/env python3
"""AI News Collector - Fetch latest AI news from multiple sources"""

import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# RSS Feed Sources
RSS_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("ArsTechnica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("OpenAI Blog", "https://openai.com/blog/rss/"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("NVIDIA Blog", "https://blogs.nvidia.com/feed/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
]

def fetch_rss_news():
    """Fetch news from RSS feeds"""
    news_items = []
    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                news_items.append({
                    'source': source_name,
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:500],
                    'date': pub_date,
                    'type': 'news'
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
    return news_items

def fetch_hacker_news_ai():
    """Fetch AI-related news from Hacker News"""
    news_items = []
    try:
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "query": "AI OR artificial intelligence OR LLM OR GPT OR machine learning OR Claude OR OpenAI",
            "tags": "story",
            "numericFilters": f"created_at_i>{int((datetime.now() - timedelta(days=1)).timestamp())}"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        for hit in data.get('hits', [])[:10]:
            news_items.append({
                'source': 'Hacker News',
                'title': hit.get('title', ''),
                'link': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                'summary': f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                'date': datetime.now(),
                'type': 'news'
            })
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
    return news_items

def fetch_github_trending():
    """Fetch trending AI/ML repositories from GitHub"""
    news_items = []
    try:
        # GitHub API for trending repos
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "topic:artificial-intelligence OR topic:machine-learning OR topic:llm OR topic:deep-learning created:>{}".format(
                (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            ),
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        headers = {"Accept": "application/vnd.github.v3+json"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        for repo in data.get('items', [])[:10]:
            news_items.append({
                'source': 'GitHub Trending',
                'title': f"⭐ {repo['full_name']} ({repo['stargazers_count']} stars)",
                'link': repo['html_url'],
                'summary': repo.get('description', '')[:200] if repo.get('description') else '',
                'date': datetime.now(),
                'type': 'github',
                'stars': repo['stargazers_count'],
                'language': repo.get('language', 'Unknown')
            })
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
    return news_items

def fetch_arxiv_papers():
    """Fetch latest AI papers from arXiv"""
    news_items = []
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": 10
        }
        resp = requests.get(url, params=params, timeout=10)
        feed = feedparser.parse(resp.text)
        for entry in feed.entries[:10]:
            news_items.append({
                'source': 'arXiv Papers',
                'title': entry.get('title', '').replace('\n', ' '),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', '')[:300].replace('\n', ' '),
                'date': datetime.now(),
                'type': 'paper'
            })
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
    return news_items

def fetch_product_hunt_ai():
    """Fetch AI products from Product Hunt (via RSS)"""
    news_items = []
    try:
        feed = feedparser.parse("https://www.producthunt.com/feed")
        ai_keywords = ['ai', 'gpt', 'llm', 'machine learning', 'artificial intelligence', 'chatbot', 'automation']
        for entry in feed.entries[:20]:
            title_lower = entry.get('title', '').lower()
            summary_lower = entry.get('summary', '').lower()
            if any(kw in title_lower or kw in summary_lower for kw in ai_keywords):
                news_items.append({
                    'source': 'Product Hunt',
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:200],
                    'date': datetime.now(),
                    'type': 'product'
                })
    except Exception as e:
        print(f"Error fetching Product Hunt: {e}")
    return news_items[:5]

def get_all_news():
    """Collect news from all sources"""
    all_news = []
    all_news.extend(fetch_rss_news())
    all_news.extend(fetch_hacker_news_ai())
    all_news.extend(fetch_github_trending())
    all_news.extend(fetch_arxiv_papers())
    all_news.extend(fetch_product_hunt_ai())

    # Sort by date (newest first)
    all_news.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)

    # Remove duplicates by title similarity
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title_key = item['title'].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_news.append(item)

    return unique_news[:50]  # Return top 50 news items

if __name__ == "__main__":
    news = get_all_news()
    print(f"Collected {len(news)} news items")
    for item in news[:10]:
        print(f"- [{item['source']}] {item['title']}")
