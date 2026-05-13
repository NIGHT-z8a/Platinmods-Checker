"""
Configuration file - All settings for the script
"""

__version__ = "1.7.1"
__author__ = "NIGHT-z"

import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BLACKLIST_FILE = DATA_DIR / "blacklist.json"


def load_blacklist():
    """Load blacklist from JSON file"""
    if not BLACKLIST_FILE.exists():
        return []
    
    try:
        with open(BLACKLIST_FILE, "r") as f:
            data = json.load(f)
        
        # Flatten all categories into a single list
        blacklist = []
        for category, items in data.get("categories", {}).items():
            blacklist.extend(items)
        
        return blacklist
    except (json.JSONDecodeError, IOError):
        return []


# Blacklist (loaded from external file)
BLACKLIST = load_blacklist()

# Game categories for auto-scan discovery
GAME_CATEGORIES = [
    {"id": "CASUAL", "name": "Casual"},
    {"id": "ARCADE", "name": "Arcade"},
    {"id": "PUZZLE", "name": "Puzzle"},
    {"id": "STRATEGY", "name": "Strategy"},
    {"id": "RPG", "name": "RPG"},
    {"id": "SIMULATION", "name": "Simulation"},
    {"id": "RACING", "name": "Racing"},
    {"id": "ADVENTURE", "name": "Adventure"},
]

# Search settings
SEARCH_RESULTS_LIMIT = 50
REQUEST_TIMEOUT = 10

# User-Agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Cache settings
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour

# Rate limiting
REQUEST_DELAY = 0.5  # Seconds between requests
MAX_RETRIES = 3
