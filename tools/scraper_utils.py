"""
Shared utilities for scrapers.
Provides robust RSS fetching with retries, timeouts, and error handling.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import feedparser
from typing import Optional, Dict, Any

# Configure logger
logger = logging.getLogger("scraper_utils")

def get_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple = (500, 502, 503, 504, 429),
    timeout: int = 30
) -> requests.Session:
    """
    Creates a requests Session with retry logic and standard headers.
    
    Args:
        retries: Number of total retries
        backoff_factor: Backoff factor for exponential backoff
        status_forcelist: HTTP status codes to retry on
        timeout: Request timeout in seconds (not directly used in session, but good for doc)
        
    Returns:
        Configured requests.Session object
    """
    session = requests.Session()
    
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Standard User-Agent to avoid blocking
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AI-News-Scraper/1.0; +http://example.com)"
    })
    
    return session

def fetch_rss_feed(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Fetches and parses an RSS feed with robust error handling.
    
    Args:
        url: The URL of the RSS feed
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        Parsed feed object (dict-like) or None if fetching failed
    """
    try:
        session = get_session()
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse content
        # We pass response.content to feedparser to avoid it making its own requests
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            logger.warning(f"Feed parsed with potential errors (bozo=1): {feed.bozo_exception}")
            # We still return the feed as it might have usable data
            
        return feed
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching RSS feed {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching RSS feed {url}: {e}")
        return None
