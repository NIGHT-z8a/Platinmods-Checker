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


def get_game_metadata(package):
    """Get basic metadata for a game"""
    cache_key = f"apkpure_meta_{package}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached, None
    
    metadata = {
        "package": package,
        "downloads": 0,
        "rating": 0.0,
        "last_update": "",
        "has_iap": False,
        "is_online": False,
        "size": "",
        "version": "",
        "is_indie": True,
    }
    
    # Check if from known big publisher
    big_publishers = [
        "com.ea", "com.activision", "com.ubisoft", "com.square",
        "com.supercell", "com.king", "com.gameloft", "com.netmarble",
        "com.ncsoft", "com.nexon", "com.pubg", "com.garena",
        "com.tencent", "com.miHoYo", "com.lilith", "com.epicgames",
    ]
    
    for pub in big_publishers:
        if package.startswith(pub):
            metadata["is_indie"] = False
            break
    
    # Check if likely online game
    online_keywords = ["multiplayer", "online", "pvp", "battle", "war"]
    for keyword in online_keywords:
        if keyword in package.lower():
            metadata["is_online"] = True
            break
    
    cache.set(cache_key, metadata)
    
    return metadata, None


def parse_game_metadata(html, package):
    """Extract game metadata from APKPure HTML"""
    metadata = {
        "package": package,
        "downloads": 0,
        "rating": 0.0,
        "last_update": "",
        "has_iap": False,
        "is_online": False,
        "size": "",
        "version": "",
    }
    
    # Extract downloads count
    dl_match = re.search(r'(\d[\d,]*)\s*(downloads|K|M|B)', html, re.IGNORECASE)
    if dl_match:
        dl_str = dl_match.group(1).replace(",", "")
        suffix = dl_match.group(2).upper()
        try:
            dl_num = float(dl_str)
            if suffix == "K":
                dl_num *= 1000
            elif suffix == "M":
                dl_num *= 1000000
            elif suffix == "B":
                dl_num *= 1000000000
            metadata["downloads"] = int(dl_num)
        except ValueError:
            pass
    
    # Extract rating
    rating_match = re.search(r'(\d\.\d)', html)
    if rating_match:
        try:
            metadata["rating"] = float(rating_match.group(1))
        except ValueError:
            pass
    
    # Check for IAP
    if re.search(r'in-app purchases|iap|contains ads', html, re.IGNORECASE):
        metadata["has_iap"] = True
    
    # Check for online features
    if re.search(r'online multiplayer|requires internet|online only', html, re.IGNORECASE):
        metadata["is_online"] = True
    
    # Extract last update date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\w+ \d+, \d{4})', html)
    if date_match:
        metadata["last_update"] = date_match.group(1)
    
    # Extract size
    size_match = re.search(r'(\d+\.?\d*\s*(MB|GB))', html, re.IGNORECASE)
    if size_match:
        metadata["size"] = size_match.group(1)
    
    # Extract version
    version_match = re.search(r'Version\s*([\d.]+)', html, re.IGNORECASE)
    if version_match:
        metadata["version"] = version_match.group(1)
    
    return metadata


def filter_games(games, filters=None):
    """Filter games based on criteria"""
    if filters is None:
        filters = {
            "exclude_big_publishers": True,
            "exclude_online": True,
            "keywords_include": [],
            "keywords_exclude": ["multiplayer", "online", "pvp"],
        }
    
    filtered = []
    
    for game in games:
        metadata, _ = get_game_metadata(game["package"])
        if metadata:
            game["metadata"] = metadata
            
            # Filter out big publishers
            if filters.get("exclude_big_publishers", True) and not metadata.get("is_indie", True):
                continue
            
            # Filter out online games
            if filters.get("exclude_online", True) and metadata.get("is_online", False):
                continue
            
            # Check excluded keywords
            name_lower = game["name"].lower()
            pkg_lower = game["package"].lower()
            
            skip = False
            for keyword in filters.get("keywords_exclude", []):
                if keyword in name_lower or keyword in pkg_lower:
                    skip = True
                    break
            
            if skip:
                continue
            
            # Check included keywords (if specified)
            include_keywords = filters.get("keywords_include", [])
            if include_keywords:
                match = any(kw in name_lower or kw in pkg_lower for kw in include_keywords)
                if not match:
                    continue
        
        filtered.append(game)
    
    return filtered


def get_trending_games(limit=20):
    """Get trending games"""
    return search_games("popular games 2024", limit)


def get_games_by_category(category_id, limit=20):
    """Get games by category search term"""
    search_term = CATEGORY_SEARCH_TERMS.get(category_id, category_id.lower())
    return search_games(search_term, limit)
