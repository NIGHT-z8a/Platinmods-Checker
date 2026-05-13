"""
Play Store module - Search and discover games via Google Play Store
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import html as html_module
import urllib.parse

from config import USER_AGENT
from scrapers.http_client import fetch_url
from core.cache import cache


NON_GAME_PACKAGES = [
    "com.android", "com.google.android", "com.example",
    "com.security", "com.antivirus", "com.launcher",
    "com.keyboard", "com.wallpaper", "com.theme",
]


def clean_name(name):
    """Clean up a game name"""
    name = html_module.unescape(name)
    name = re.sub(r"[\uFFFD\u00AE\u2122\u00A0\u2022\u2026\u2013\u2014]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def extract_game_name(card_html):
    """Extract game name from a Play Store card"""
    aria_match = re.search(r'aria-label="Play ([^"]+)"', card_html)
    if aria_match:
        name = clean_name(aria_match.group(1))
        if name.lower() not in ("trailer", "video", "play"):
            return name

    text = re.sub(r'<script[^>]*>.*?</script>', "", card_html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', "", text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', "\n", text)
    text = re.sub(r'\n+', "\n", text).strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    skip_words = {"trailer", "video", "screenshot", "screenshot image", "play"}
    for line in lines:
        if line.lower() not in skip_words and len(line) > 1:
            return clean_name(line)

    return "Unknown Game"


def parse_app_cards(html, limit):
    """Parse Google Play Store app cards from HTML"""
    results = []
    seen = set()

    for match in re.finditer(r'<a class="Si6A0c Gy4nib" href="/store/apps/details\?id=([^"&]+)', html):
        package = match.group(1)
        if package in seen:
            continue
        seen.add(package)

        for prefix in NON_GAME_PACKAGES:
            if package.startswith(prefix):
                break
        else:
            card_start = match.start()
            card_end = min(len(html), card_start + 2000)
            card_html = html[card_start:card_end]

            name = extract_game_name(card_html)
            if name and name != "Unknown Game":
                results.append({
                    "name": name,
                    "url": f"https://play.google.com/store/apps/details?id={package}",
                    "package": package,
                })

        if len(results) >= limit:
            break

    return results


def search_games(query, limit=30):
    """Search for games on Google Play Store"""
    cache_key = f"playstore_search_{query}_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached, None

    url = f"https://play.google.com/store/search?q={urllib.parse.quote(query)}&c=apps"

    try:
        html = fetch_url(url)
        if not html:
            return None, "Failed to fetch page"

        results = parse_app_cards(html, limit)
        cache.set(cache_key, results)

        return results, None
    except Exception as e:
        return None, str(e)


def search_games_batch(queries, limit=30):
    """Search multiple queries and merge results (deduplicated)"""
    seen = set()
    all_games = []

    for query in queries:
        games, error = search_games(query, limit=limit)
        if not games:
            continue

        for game in games:
            if game["package"] not in seen:
                seen.add(game["package"])
                all_games.append(game)

    return all_games, None


CATEGORY_SEARCH_TERMS = {
    "CASUAL": ["casual offline", "time killer games", "relaxing games"],
    "ARCADE": ["arcade offline", "endless runner", "classic arcade"],
    "PUZZLE": ["puzzle offline", "brain games", "logic puzzle"],
    "STRATEGY": ["strategy offline", "tower defense", "city builder offline"],
    "RPG": ["rpg offline", "action rpg", "adventure rpg"],
    "SIMULATION": ["simulation offline", "tycoon games", "life simulator"],
    "RACING": ["racing offline", "car games", "driving simulator"],
    "ADVENTURE": ["adventure offline", "platformer", "open world"],
}


def get_games_by_category(category_id, limit=30):
    """Get games by category using multiple search terms"""
    terms = CATEGORY_SEARCH_TERMS.get(category_id, [category_id.lower()])
    return search_games_batch(terms, limit=limit)


def get_game_metadata(package):
    """Get basic metadata for a game"""
    cache_key = f"playstore_meta_{package}"
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

    big_publishers = [
        "com.ea", "com.activision", "com.ubisoft", "com.square",
        "com.supercell", "com.king", "com.gameloft", "com.netmarble",
        "com.ncsoft", "com.nexon", "com.pubg", "com.garena",
        "com.tencent", "com.miHoYo", "com.lilith", "com.epicgames",
        "com.nintendo", "com.sega", "com.capcom", "com.konami",
        "com.bandai", "com.rockstar", "com.take2", "com.zynga",
        "com.playrix", "com.rovio", "com.outfit7", "com.mojang",
        "com.disney", "com.wb", "com.warnerbros", "com.marvel",
        "com.lego", "com.hasbro", "com.mattel", "com.nickelodeon",
        "com.cartoonnetwork", "com.miniclip", "com.innogames",
        "com.goodgamestudios", "com.wooga", "com.socialpoint",
        "com.machinezone", "com.midasplayer", "com.scopely",
        "com.jamcity", "com.glu", "com.mobilegaming", "com.gree",
        "com.decknine", "com.f5", "com.kabam", "com.pocketgems",
        "com.sgn", "com.ngmoco", "com.ouya", "com.mplay",
        "com.gameinsight", "com.plarium", "com.funplus",
        "com.igames", "com.epicwar", "com.gaijin", "com.wargaming",
        "com.paradox", "com.asmodee", "com.focusentertainment",
        "com.deepsilver", "com.thq", "com.madfinger",
        "com.creativemobile", "com.appquantum", "com.direxdigital",
        "com.sanzaru", "com.naturalmotion", "com.spaceape",
        "com.tekken", "com.square-enix", "com.segaplus",
    ]

    for pub in big_publishers:
        if package.startswith(pub):
            metadata["is_indie"] = False
            break

    online_keywords = ["multiplayer", "online", "pvp", "battle", "war"]
    for keyword in online_keywords:
        if keyword in package.lower():
            metadata["is_online"] = True
            break

    cache.set(cache_key, metadata)

    return metadata, None


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

            if filters.get("exclude_big_publishers", True) and not metadata.get("is_indie", True):
                continue

            if filters.get("exclude_online", True) and metadata.get("is_online", False):
                continue

            name_lower = game["name"].lower()
            pkg_lower = game["package"].lower()

            skip = False
            for keyword in filters.get("keywords_exclude", []):
                if keyword in name_lower or keyword in pkg_lower:
                    skip = True
                    break

            if skip:
                continue

            include_keywords = filters.get("keywords_include", [])
            if include_keywords:
                match = any(kw in name_lower or kw in pkg_lower for kw in include_keywords)
                if not match:
                    continue

        filtered.append(game)

    return filtered
