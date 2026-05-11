"""
Checker module - Core logic for checking games against Platinmods
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.platinmods import check_game as platinmods_check
from scrapers.apkpure import get_game_metadata
from config import BLACKLIST


def is_blacklisted(game_name, package_name=None):
    """Check if game is on blacklist"""
    game_lower = game_name.lower()
    package_lower = package_name.lower() if package_name else ""
    
    for item in BLACKLIST:
        if item in game_lower or item in package_lower:
            return True, item
    return False, None


def check_single_game(game_name, package_name=None):
    """Check a single game against Platinmods"""
    blacklisted, reason = is_blacklisted(game_name, package_name)
    if blacklisted:
        return {
            "name": game_name,
            "package": package_name,
            "status": "blacklisted",
            "reason": reason,
            "threads": [],
        }
    
    threads, error = platinmods_check(game_name, package_name)
    if error:
        return {
            "name": game_name,
            "package": package_name,
            "status": "error",
            "error": error,
            "threads": [],
        }
    
    if threads:
        return {
            "name": game_name,
            "package": package_name,
            "status": "modded",
            "threads": threads,
        }
    
    return {
        "name": game_name,
        "package": package_name,
        "status": "available",
        "threads": [],
    }


def pre_filter_games(games, exclude_big_publishers=True, exclude_online=True):
    """Filter out unworthy games BEFORE checking Platinmods (saves time)"""
    filtered = []
    seen_packages = set()
    
    for game in games:
        package = game.get("package", "")
        if package in seen_packages:
            continue
        seen_packages.add(package)
        
        metadata, _ = get_game_metadata(package)
        if metadata:
            game["metadata"] = metadata
            
            if exclude_big_publishers and not metadata.get("is_indie", True):
                continue
            if exclude_online and metadata.get("is_online", False):
                continue
        
        filtered.append(game)
    
    return filtered


def find_moddable_games(games_list, max_checks=10, progress_callback=None):
    """Check multiple games and return categorized results"""
    available = []
    modded = []
    blacklisted = []
    
    for i, game in enumerate(games_list[:max_checks]):
        name = game.get("name", "")
        package = game.get("package", "")
        
        if progress_callback:
            progress_callback(i + 1, len(games_list[:max_checks]), game)
        
        result = check_single_game(name, package)
        
        if result["status"] == "available":
            available.append(result)
        elif result["status"] == "modded":
            modded.append(result)
        elif result["status"] == "blacklisted":
            blacklisted.append(result)
    
    return {
        "available": available,
        "modded": modded,
        "blacklisted": blacklisted,
    }
