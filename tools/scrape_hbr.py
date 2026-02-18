#!/usr/bin/env python3
"""
Harvard Business Review Strategy Scraper
Scrapes strategy and consulting articles from HBR RSS feed
Conforms to Scraper Output Schema in gemini.md
"""

import feedparser
import json
import sys
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
import time
import logging
from tools.scraper_utils import fetch_rss_feed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.tmp/errors.log'),
        logging.StreamHandler()
    ]
)

# Constants
RSS_URL = "https://hbr.org/topic/strategy/feed"
SOURCE_NAME = "hbr"
HOURS_FILTER = 48  # HBR publishes regularly but not as frequently as news

def scrape_hbr():
    """
    Scrape HBR Strategy RSS feed for articles from last 48 hours
    
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
        logging.info(f"Fetching HBR RSS feed from {RSS_URL}")
        
        # Parse RSS feed
        feed = fetch_rss_feed(RSS_URL)
         
        if feed is None:
             error_msg = "Failed to fetch RSS feed"
             output["errors"].append(error_msg)
             return output

        if feed.bozo:
            error_msg = f"RSS feed parsing error: {feed.bozo_exception}"
            logging.error(error_msg)
            output["errors"].append(error_msg)
            return output
        
        logging.info(f"Successfully parsed RSS feed. Found {len(feed.entries)} entries")
        
        # Calculate cutoff time (48 hours ago)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=HOURS_FILTER)
        
        # Process each entry
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
                
                # Filter to last 48 hours
                if pub_date < cutoff_time:
                    continue
                
                # Extract article data
                article = {
                    "id": entry.get('id', entry.get('link', '')),
                    "source": SOURCE_NAME,
                    "title": entry.get('title', '').strip(),
                    "url": entry.get('link', ''),
                    "summary": entry.get('summary', entry.get('description', '')).strip(),
                    "published_at": pub_date.isoformat(),
                    "author": entry.get('author', 'Harvard Business Review'),
                    "is_saved": False
                }
                
                # Clean HTML from summary if present
                if article["summary"]:
                    # Simple HTML tag removal
                    import re
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
        
        # Rate limiting - be respectful
        time.sleep(1)
        
    except Exception as e:
        error_msg = f"Fatal error scraping HBR: {str(e)}"
        logging.error(error_msg)
        output["errors"].append(error_msg)
        output["success"] = False
    
    return output

def main():
    """Main execution"""
    try:
        result = scrape_hbr()
        
        # Output JSON to stdout
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
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
