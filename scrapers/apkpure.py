"""
APKPure module - Search and discover games from APKPure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import urllib.parse

from config import USER_AGENT
from scrapers.http_client import fetch_url
from core.cache import cache


# Category search terms (APKPure category pages are blocked)
CATEGORY_SEARCH_TERMS = {
    "CASUAL": "casual offline",
    "ARCADE": "arcade offline",
    "PUZZLE": "puzzle offline",
    "STRATEGY": "strategy offline",
    "RPG": "rpg offline",
    "SIMULATION": "simulation offline",
    "RACING": "racing offline",
    "ADVENTURE": "adventure offline",
}


def search_games(query, limit=20):
    """Search for games on APKPure"""
    # Check cache
    cache_key = f"apkpure_search_{query}_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached, None
    
    url = f"https://apkpure.com/search?q={urllib.parse.quote(query)}&t=app"
    
    try:
        html = fetch_url(url)
        if not html:
            return None, "Failed to fetch page"
        
        results = parse_app_links(html, limit)
        cache.set(cache_key, results)
        
        return results, None
    except Exception as e:
        return None, str(e)


def parse_app_links(html, limit):
    """Parse APKPure app links from HTML"""
    results = []
    seen = set()
    
    # Pattern: https://apkpure.com/game-name/com.package.name
    pattern = r"https://apkpure\.com/([^/]+)/(com\.[a-zA-Z0-9_.]+)"
    matches = re.findall(pattern, html)
    
    for slug, package in matches:
        if package not in seen:
            seen.add(package)
            name = urllib.parse.unquote(slug)
            name = name.replace("-", " ").title()
            
            results.append({
                "name": name,
                "url": f"https://apkpure.com/{slug}/{package}",
                "package": package,
            })
    
    return results[:limit]


def get_trending_games(limit=20):
    """Get trending games"""
    return search_games("popular games 2024", limit)


def get_games_by_category(category_id, limit=20):
    """Get games by category search term"""
    search_term = CATEGORY_SEARCH_TERMS.get(category_id, category_id.lower())
    return search_games(search_term, limit)
