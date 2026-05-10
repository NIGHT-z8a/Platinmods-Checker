"""
Configuration file - All settings for the script
"""

# Blacklist from Platinmods official spreadsheet
# These games require permission from G-boy before posting
BLACKLIST = [
    # PUBG variants
    "pubg",
    "pubg mobile",
    "pubg new state",
    "playerunknown battlegrounds",
    "pubg mobile vn",
    "pubg mobile kr",
    "pubg mobile india",
    # COD variants
    "call of duty",
    "cod mobile",
    "codm",
    "call of duty warzone",
    "call of duty mobile vn",
    "call of duty mobile garena",
    # Wargaming
    "world of tanks",
    "world of warships",
    "wargaming",
    # Battle Royale / FPS
    "stumble guys",
    "8 ball pool",
    "guns of boom",
    "modern strike",
    "world war heroes",
    "1v1.lol",
    "hunt royale",
    "darts club",
    # Survival / Strategy
    "state of survival",
    "king of avalon",
    "frost flame king of avalon",
    # Life simulators
    "bitlife",
    "bitlife dogs",
    "bitlife go",
    "bitlife espanol",
    "doglife",
    # Gacha / RPG
    "blue archive",
    "seven deadly sins",
    "grand cross",
    "gran cross",
    "lyssa",
    "ex astris",
    "auto brawl chess",
    "mighty party",
    "monster trainer",
    "dungeon maker",
    "dungeon squad",
    "combat quest",
    "eterspire",
    "octopath traveler",
    # Casual / Puzzle
    "coin master",
    "candy crush soda",
    "bubble pop",
    "word cookies",
    "jewels magic",
    "lollipop sweet heroes",
    "brick out",
    "avatar world",
    "masha and the bear",
    "monster hunter puzzles",
    "muse dash",
    # Streaming / TV apps (No-Go)
    "flix vision",
    "flixoid",
    "cricfy tv",
    "cricz tv",
    "magis tv",
    # Social / Messaging (No-Go)
    "whatsapp",
    "telegram",
    # AutoResponder (No-Go)
    "autoresponder",
    # ChatGPT / AI (No-Go)
    "chatgpt",
    # VPN / Privacy
    "expressvpn",
    "private internet access",
    "strava",
    # Other apps
    "wattpad",
    "grammarly",
    "truecaller",
    "picsart",
    "vSCO",
    "canva",
    "flipaclip",
    "notewise",
    "hiPER calc",
    "macrorify",
    "voxbox",
    "flo period",
    # Anime / Adult (Nutaku)
    "virtual succubus",
    "faynet",
    "amikin survival",
    "episode choose your story",
    "sifting thyme",
    # Minecraft
    "minecraft",
    # Roblox
    "roblox",
    # Free Fire
    "free fire",
    "garena free fire",
    # Hitman
    "hitman blood money",
    # XCOM
    "xcom 2",
    # Total War
    "total war",
    # GRID
    "grid legends",
    # Company of Heroes
    "company of heroes",
    # Avakin Life
    "avakin life",
    # Crunchyroll
    "crunchyroll",
    # Dawn of Ages
    "dawn of ages",
    # Flying High
    "flying high",
    # Rally Fury
    "rally fury",
    # Cooking Live
    "cooking live",
    # Rainbow Survivor
    "rainbow survivor",
    # Torrent Search
    "torrent search",
]

# APKPure categories for game discovery
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
