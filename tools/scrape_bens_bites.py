#!/usr/bin/env python3
"""
Ben's Bites Newsletter Scraper (RSS Version)
Follows architecture SOP: architecture/scraper_bens_bites.md
Conforms to schemas defined in: gemini.md
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict

import feedparser
from dateutil import parser as date_parser


# Constants
RSS_URL = "https://bensbites.substack.com/feed/"
TMP_DIR = Path(__file__).parent.parent / ".tmp"
ERROR_LOG = TMP_DIR / "errors.log"


def log_error(message: str) -> None:
    """Log error to .tmp/errors.log"""
    TMP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(ERROR_LOG, "a") as f:
        f.write(f"[{timestamp}] [BensBites] {message}\n")


from tools.scraper_utils import fetch_rss_feed


def fetch_rss() -> Dict:
    """Fetch and parse RSS feed"""
    # Use robust fetcher with retries and timeout
    return fetch_rss_feed(RSS_URL)


def parse_articles(feed: Dict) -> List[Dict]:
    """Extract articles from RSS feed"""
    articles = []
    
    if not feed or "entries" not in feed:
        return articles
    
    for entry in feed.entries:
        try:
            # Extract title
            title = entry.get("title", "").strip()
            if not title:
                continue
            
            # Extract URL
            url = entry.get("link", "").strip()
            if not url:
                continue
            
            # Extract publish date
            pub_date_str = entry.get("published", "")
            if not pub_date_str:
                log_error(f"Article missing publish date: {url}")
                continue
            
            # Parse publish date
            try:
                pub_date = date_parser.parse(pub_date_str)
            except Exception as e:
                log_error(f"Failed to parse date '{pub_date_str}' for {url}: {e}")
                continue
            
            # Ensure timezone-aware
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            
            # Extract summary/description
            summary = entry.get("summary", "").strip()
            
            # Extract author
            author = entry.get("author", "Ben Tossell")
            
            articles.append({
                "title": title,
                "url": url,
                "published_at": pub_date.isoformat(),
                "summary": summary,
                "author": author
            })
        except Exception as e:
            log_error(f"Failed to parse RSS entry: {e}")
            continue
    
    return articles


def filter_24h(articles: List[Dict]) -> List[Dict]:
    """Filter articles to last 24 hours"""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    filtered = []
    
    for article in articles:
        try:
            pub_date = datetime.fromisoformat(article["published_at"])
            
            if pub_date >= cutoff:
                filtered.append(article)
        except Exception as e:
            log_error(f"Failed to filter article {article.get('url', 'unknown')}: {e}")
            continue
    
    return filtered


def scrape_bens_bites() -> Dict:
    """Main scraper function - returns Scraper Output Schema"""
    result = {
        "source": "bens_bites",
        "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
        "articles": [],
        "errors": [],
        "success": True
    }
    
    # Fetch RSS feed
    feed = fetch_rss()
    if feed is None:
        result["success"] = False
        result["errors"].append("Unable to fetch RSS feed")
        return result
    
    # Parse articles
    try:
        articles = parse_articles(feed)
    except Exception as e:
        log_error(f"Failed to parse articles: {e}")
        result["success"] = False
        result["errors"].append(f"Failed to parse articles: {e}")
        return result
    
    # Filter to 24 hours
    try:
        filtered = filter_24h(articles)
        result["articles"] = filtered
    except Exception as e:
        log_error(f"Failed to filter articles: {e}")
        result["success"] = False
        result["errors"].append(f"Failed to filter articles: {e}")
        return result
    
    return result


if __name__ == "__main__":
    output = scrape_bens_bites()
    print(json.dumps(output, indent=2))
