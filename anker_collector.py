#!/usr/bin/env python3
"""Anker News Collector - Fetch Anker related news from multiple sources"""

import requests
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote

# Anker related keywords
ANKER_KEYWORDS = [
    'anker', 'soundcore', 'eufy', 'nebula', 'ankermake',
    '安克', '安克创新', 'anker innovations'
]

# Competitor keywords for context
COMPETITOR_KEYWORDS = [
    'belkin', 'baseus', 'ugreen', 'ravpower', 'aukey',
    'charging', 'power bank', 'portable charger', 'wireless charger',
    'usb-c', 'gan charger', 'fast charging'
]

def fetch_google_news_anker():
    """Fetch Anker news via Google News RSS"""
    news_items = []
    search_terms = ['Anker', 'Anker Innovations', 'Soundcore', 'Eufy', 'AnkerMake']

    for term in search_terms:
        try:
            encoded_term = quote(term)
            url = f"https://news.google.com/rss/search?q={encoded_term}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                news_items.append({
                    'source': f'Google News ({term})',
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:500],
                    'date': datetime.now(),
                    'type': 'news'
                })
        except Exception as e:
            print(f"Error fetching Google News for {term}: {e}")
    return news_items

def fetch_hacker_news_anker():
    """Fetch Anker-related news from Hacker News"""
    news_items = []
    try:
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "query": "Anker OR Soundcore OR Eufy OR portable charger OR power bank OR GaN charger",
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
                'type': 'news'
            })
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
    return news_items

def fetch_reddit_anker():
    """Fetch Anker discussions from Reddit"""
    news_items = []
    subreddits = ['anker', 'UsbCHardware', 'ChargingTech', 'gadgets', 'technology']

    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                "q": "anker OR soundcore OR eufy",
                "sort": "new",
                "t": "week",
                "limit": 10
            }
            headers = {"User-Agent": "AnkerNewsBot/1.0"}
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

def fetch_tech_news_charging():
    """Fetch charging/power tech news from tech sites"""
    news_items = []
    feeds = [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("9to5Mac", "https://9to5mac.com/feed/"),
        ("Android Authority", "https://www.androidauthority.com/feed/"),
    ]

    keywords = ['anker', 'charger', 'charging', 'power bank', 'usb-c', 'gan',
                'soundcore', 'eufy', 'wireless charging', 'fast charging']

    for source_name, feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title_lower = entry.get('title', '').lower()
                summary_lower = entry.get('summary', '').lower()
                if any(kw in title_lower or kw in summary_lower for kw in keywords):
                    news_items.append({
                        'source': source_name,
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '')[:500],
                        'date': datetime.now(),
                        'type': 'news'
                    })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
    return news_items

def fetch_amazon_bestsellers():
    """Note: Amazon scraping may be blocked, this is a placeholder"""
    # In production, use Amazon Product API or similar
    return []

def get_all_anker_news():
    """Collect Anker-related news from all sources"""
    all_news = []
    all_news.extend(fetch_google_news_anker())
    all_news.extend(fetch_hacker_news_anker())
    all_news.extend(fetch_reddit_anker())
    all_news.extend(fetch_tech_news_charging())

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

    return unique_news[:50]

if __name__ == "__main__":
    news = get_all_anker_news()
    print(f"Collected {len(news)} Anker-related news items")
    for item in news[:10]:
        print(f"- [{item['source']}] {item['title']}")
