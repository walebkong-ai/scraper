#!/usr/bin/env python3
"""
Boston Consulting Group (BCG) Google News Scraper
Scrapes BCG news from Google News RSS feed as a reliable third-party source
Conforms to Scraper Output Schema
"""

import feedparser
import json
import sys
import re
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
from tools.scraper_utils import fetch_rss_feed
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.tmp/errors.log'),
        logging.StreamHandler()
    ]
)

# Search "Boston Consulting Group" over the last 7 days (to ensure we catch weekends)
RSS_URL = "https://news.google.com/rss/search?q=%22Boston+Consulting+Group%22+when:7d&hl=en-US&gl=US&ceid=US:en"
SOURCE_NAME = "bcg"
HOURS_FILTER = 48 # Filter down to recent business hours

def scrape_bcg():
    """
    Scrape Google News RSS for BCG Mentions over the last 48 hours.
    
    Returns:
        dict: Scraper Output Schema with articles, errors, success status
    """
    output = {
        "source": SOURCE_NAME,
        "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
        "articles": [],
        "errors": [],
        "success": False
    }

    try:
        logging.info(f"Fetching Google News RSS for BCG from {RSS_URL}")
        
        feed = fetch_rss_feed(RSS_URL)
        
        if feed is None:
            error_msg = "Failed to fetch RSS feed"
            output["errors"].append(error_msg)
            return output
            
        logging.info(f"Successfully parsed RSS feed. Found {len(feed.entries)} entries")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=HOURS_FILTER)
        
        for entry in feed.entries:
            try:
                # Parse publish date
                if hasattr(entry, 'published'):
                    pub_date = date_parser.parse(entry.published)
                elif hasattr(entry, 'updated'):
                    pub_date = date_parser.parse(entry.updated)
                else:
                    logging.warning(f"No date found for entry: {entry.get('title', 'Unknown')}")
                    continue
                
                # Ensure timezone-aware
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                
                # Ensure within last N hours
                if pub_date < cutoff_time:
                    continue
                
                title = entry.get('title', '').strip()
                
                # Extract clean title from Google News (often formatted as "Article Title - Publisher")
                if " - " in title:
                    title_parts = title.rsplit(" - ", 1)
                    title = title_parts[0].strip()
                    author = title_parts[1].strip()
                else:
                    author = getattr(entry, 'source', {}).get('title', 'Google News (BCG Mention)')
                
                article = {
                    "id": entry.get('id', entry.get('link', '')),
                    "source": SOURCE_NAME,
                    "title": title,
                    "url": entry.get('link', ''),
                    "summary": entry.get('summary', '').strip(),
                    "published_at": pub_date.isoformat(),
                    "author": author,
                    "is_saved": False
                }
                
                # Clean HTML
                if article["summary"]:
                    article["summary"] = re.sub(r'<[^>]+>', '', article["summary"])
                    article["summary"] = article["summary"].strip()
                
                output["articles"].append(article)
                logging.info(f"Added article: {article['title'][:50]}...")
                
            except Exception as e:
                error_msg = f"Error processing entry: {str(e)}"
                logging.error(error_msg)
                output["errors"].append(error_msg)
                continue
                
        output["success"] = True
        logging.info(f"Successfully scraped {len(output['articles'])} articles from last {HOURS_FILTER} hours")
        time.sleep(1)

    except Exception as e:
        error_msg = f"Fatal error scraping BCG: {str(e)}"
        logging.error(error_msg)
        output["errors"].append(error_msg)
        output["success"] = False

    return output


def main():
    try:
        result = scrape_bcg()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        error_output = {
            "source": SOURCE_NAME,
            "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
            "articles": [],
            "errors": [str(e)],
            "success": False
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
