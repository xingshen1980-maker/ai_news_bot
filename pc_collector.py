#!/usr/bin/env python3
"""PC Market Collector - Fetch PC industry news and product information"""

import requests
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote

# PC brands and keywords
PC_BRANDS = ['dell', 'hp', 'lenovo', 'apple', 'macbook', 'thinkpad', 'xps', 'spectre', 'pavilion']
PC_KEYWORDS = ['laptop', 'notebook', 'pc', 'computer', 'ultrabook', 'workstation']

def fetch_google_news_pc():
    """Fetch PC news via Google News RSS"""
    news_items = []
    search_terms = [
        'Dell XPS laptop',
        'HP Spectre laptop',
        'Lenovo ThinkPad',
        'Apple MacBook',
        'laptop review 2026',
        'PC market analysis'
    ]

    for term in search_terms:
        try:
            encoded_term = quote(term)
            url = f"https://news.google.com/rss/search?q={encoded_term}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                news_items.append({
                    'source': f'Google News',
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:500],
                    'date': datetime.now(),
                    'type': 'news'
                })
        except Exception as e:
            print(f"Error fetching Google News for {term}: {e}")
    return news_items

def fetch_tech_reviews():
    """Fetch PC reviews from tech sites"""
    news_items = []
    feeds = [
        ("Tom's Hardware", "https://www.tomshardware.com/feeds/all"),
        ("NotebookCheck", "https://www.notebookcheck.net/News.152.100.html"),
        ("PCMag", "https://www.pcmag.com/feeds/all"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
        ("AnandTech", "https://www.anandtech.com/rss/"),
        ("CNET", "https://www.cnet.com/rss/all/"),
    ]

    keywords = ['dell', 'hp', 'lenovo', 'thinkpad', 'xps', 'spectre', 'macbook',
                'laptop', 'notebook', 'battery life', 'benchmark', 'review',
                'intel', 'amd', 'ryzen', 'core ultra', 'snapdragon', 'apple silicon', 'm3', 'm4']

    for source_name, feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:
                title_lower = entry.get('title', '').lower()
                summary_lower = entry.get('summary', '').lower()
                if any(kw in title_lower or kw in summary_lower for kw in keywords):
                    news_items.append({
                        'source': source_name,
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '')[:500],
                        'date': datetime.now(),
                        'type': 'review'
                    })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
    return news_items

def fetch_hacker_news_pc():
    """Fetch PC-related discussions from Hacker News"""
    news_items = []
    try:
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "query": "laptop OR ThinkPad OR MacBook OR Dell XPS OR HP Spectre OR notebook review",
            "tags": "story",
            "numericFilters": f"created_at_i>{int((datetime.now() - timedelta(days=7)).timestamp())}"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        for hit in data.get('hits', [])[:15]:
            news_items.append({
                'source': 'Hacker News',
                'title': hit.get('title', ''),
                'link': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                'summary': f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                'date': datetime.now(),
                'type': 'discussion'
            })
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
    return news_items

def fetch_reddit_pc():
    """Fetch PC discussions from Reddit"""
    news_items = []
    subreddits = ['laptops', 'thinkpad', 'Dell', 'Hewlett_Packard', 'Lenovo', 'mac', 'hardware']

    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            params = {"limit": 10}
            headers = {"User-Agent": "PCMarketBot/1.0"}
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            for post in data.get('data', {}).get('children', [])[:5]:
                post_data = post.get('data', {})
                news_items.append({
                    'source': f'Reddit r/{subreddit}',
                    'title': post_data.get('title', ''),
                    'link': f"https://reddit.com{post_data.get('permalink', '')}",
                    'summary': f"Score: {post_data.get('score', 0)} | Comments: {post_data.get('num_comments', 0)}",
                    'date': datetime.now(),
                    'type': 'social'
                })
        except Exception as e:
            print(f"Error fetching Reddit r/{subreddit}: {e}")
    return news_items

def get_all_pc_news():
    """Collect PC-related news from all sources"""
    all_news = []
    all_news.extend(fetch_google_news_pc())
    all_news.extend(fetch_tech_reviews())
    all_news.extend(fetch_hacker_news_pc())
    all_news.extend(fetch_reddit_pc())

    # Sort by date
    all_news.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)

    # Remove duplicates
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title_key = item['title'].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_news.append(item)

    return unique_news[:60]

if __name__ == "__main__":
    news = get_all_pc_news()
    print(f"Collected {len(news)} PC-related news items")
    for item in news[:10]:
        print(f"- [{item['source']}] {item['title']}")
