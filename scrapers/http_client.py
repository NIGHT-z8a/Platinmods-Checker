"""
HTTP client module - Handles requests with retry and rate limiting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.parse
import ssl
import time
from config import REQUEST_TIMEOUT, USER_AGENT


# Rate limiting settings
REQUEST_DELAY = 0.5  # Seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2  # Seconds before retry


def get_ssl_context():
    """Create SSL context that ignores certificate errors"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_url(url, headers=None, timeout=None):
    """Fetch URL content with retry and rate limiting"""
    if headers is None:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    if timeout is None:
        timeout = REQUEST_TIMEOUT
    
    # Rate limiting
    if hasattr(fetch_url, "_last_request"):
        elapsed = time.time() - fetch_url._last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
    
    for attempt in range(MAX_RETRIES):
        try:
            ctx = get_ssl_context()
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                fetch_url._last_request = time.time()
                return response.read().decode("utf-8", errors="ignore")
        
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait_time = RETRY_DELAY * (attempt + 1)
                time.sleep(wait_time)
                continue
            raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (attempt + 1)
                time.sleep(wait_time)
                continue
            raise
    
    return None


def fetch_json(url, headers=None, timeout=None):
    """Fetch and parse JSON response"""
    html = fetch_url(url, headers, timeout)
    if html:
        import json
        try:
            return json.loads(html)
        except json.JSONDecodeError:
            return None
    return None
