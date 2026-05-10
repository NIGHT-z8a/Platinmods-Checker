"""
Platinmods module - Search and parse Platinmods forum
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import html as html_module
import urllib.parse

from config import SEARCH_RESULTS_LIMIT
from scrapers.http_client import fetch_url
from core.cache import cache


def search(query, game_name=None):
    """Search Platinmods for game mods"""
    # Check cache first
    cache_key = f"platinmods_{query}_{game_name}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached, None
    
    url = f"https://platinmods.com/search/100660989/?q={urllib.parse.quote(query)}&o[date]=0"
    
    try:
        html = fetch_url(url)
        if not html:
            return None, "Failed to fetch page"
        
        results = parse_results(html, game_name)
        
        # Cache results
        cache.set(cache_key, results)
        
        return results, None
    except Exception as e:
        return None, str(e)


def normalize_url(url):
    """Normalize URL for deduplication"""
    url = url.split("/post-")[0]
    url = url.rstrip("/")
    return url


def is_relevant_result(title, game_name):
    """Check if search result is relevant to the game being searched"""
    if not game_name:
        return True
    
    title_lower = title.lower()
    game_lower = game_name.lower()
    
    # Exact match
    if game_lower in title_lower:
        return True
    
    # Filter generic words
    generic_words = {
        "mod", "apk", "menu", "ver", "the", "and", "for", "of", "in", "to",
        "is", "on", "a", "an", "game", "games", "shooter", "survival",
        "zombie", "war", "dead", "free", "online", "3d", "2d",
    }
    game_words = [w for w in game_lower.split() if w not in generic_words and len(w) > 2]
    
    if not game_words:
        return True
    
    # Short names: all words must match
    # Long names: at least 2 words must match
    required = len(game_words) if len(game_words) <= 3 else 2
    
    matches = sum(1 for word in game_words if word in title_lower)
    return matches >= required


def parse_results(html, game_name=None):
    """Parse Platinmods search results from HTML"""
    results = []
    seen = set()
    
    # Find thread titles
    pattern = r'<h3 class="contentRow-title">\s*<a href="(/threads/[^"]+)">(.*?)</a>\s*</h3>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for url, title_html in matches:
        # Clean title
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        title = html_module.unescape(title)
        title = re.sub(r"\s+", " ", title)
        
        # Normalize URL
        url = f"https://platinmods.com{normalize_url(url)}"
        
        if title and len(title) > 3 and url not in seen:
            seen.add(url)
            results.append({
                "url": url,
                "title": title,
                "id": url.rstrip("/").split(".")[-1],
            })
    
    # Filter to relevant results only
    if game_name:
        results = [r for r in results if is_relevant_result(r["title"], game_name)]
    
    return results[:SEARCH_RESULTS_LIMIT]


def check_game(game_name, package_name=None):
    """Check if a game has existing mods on Platinmods"""
    all_results = []
    
    # Priority 1: Search by package name
    if package_name:
        results, error = search(package_name, game_name)
        if not error and results:
            all_results.extend(results)
    
    # Priority 2: Search by game name
    if not all_results:
        results, error = search(game_name, game_name)
        if not error:
            all_results.extend(results)
    
    # Priority 3: Search by package app name
    if not all_results and package_name:
        parts = package_name.split(".")
        if len(parts) >= 2:
            app_name = parts[-1]
            spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", app_name)
            results, error = search(spaced, game_name)
            if not error:
                all_results.extend(results)
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_results.append(r)
    
    return unique_results, None
