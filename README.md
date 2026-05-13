# Platinmods Checker v1.7.1

**Author:** NIGHT-z

A CLI tool to check if Android games are already modded on [Platinmods](https://platinmods.com) before you start modding them.

## Features

- **Check by Game Name** - Search Platinmods for existing mods
- **Check by Play Store URL** - Paste a Google Play link, auto-extract package and check
- **Search Play Store** - Search Google Play for games and check mod status
- **Auto-Scan** - Scan multiple categories (multi-query pooling for max results) and find available games to mod
- **Batch Check** - Load games from a file and check them all at once
- **Blacklist Detection** - Warns if game is on Platinmods blacklist (130+ entries)
- **Smart Filtering** - Remove big publishers and online-only games from results
- **Caching** - Results cached for 1 hour to speed up repeated checks
- **Export Results** - Save checks as JSON, CSV, or text files
- **Zero Dependencies** - Uses only Python standard library

## Requirements

- Python 3.8+
- Internet connection

## Quick Start

```bash
python main.py
```

## Usage

### Menu Options

| Option | Description |
|--------|-------------|
| 1 | Check game on Platinmods |
| 2 | Check by Google Play URL |
| 3 | Search games on Play Store |
| 4 | Find moddable games (auto-scan) |
| 5 | Batch check from file |
| 0 | Exit |

### Check by Play Store URL

```
Select ▶ 2
Google Play URL ▶ https://play.google.com/store/apps/details?id=com.kiloo.subwaysurfers

Extracted package: com.kiloo.subwaysurfers
Game name: Subway Surfers

⚠ Already modded on Platinmods
┌────────────────────────────────────────────────┐
│  Threads Found: 3                                │
├────────────────────────────────────────────────┤
│  [Request] Request Subway Surfers City          │
│    ID: 275815                                    │
│  [Fixing] Subway Surfers MEGA                   │
│    ID: 227410                                    │
│  [Free] MOD Subway Surfers City                 │
│    ID: 285210                                    │
└────────────────────────────────────────────────┘
```

### Batch Check from File

Create a text file with one game per line:

```
# games.txt
Subway Surfers,com.kiloo.subwaysurfers
Among Us,com.innersloth.spacemafia
Fireworks Arcade,com.bigduckgames.fireworksarcade
```

Then select option 5 and point to the file.

## Project Structure

```
Platinmods-Checker/
├── main.py              # CLI entry point
├── config.py            # Settings + version
├── core/
│   ├── cache.py         # JSON-based caching
│   ├── checker.py       # Game checking logic
│   └── export.py        # Export results (JSON/CSV/TXT)
├── scrapers/
│   ├── http_client.py   # HTTP with retry + rate limit
│   ├── platinmods.py    # Platinmods forum scraper
│   └── playstore.py     # Google Play Store game discovery
├── utils/
│   └── progress.py      # Progress bars
├── data/
│   └── blacklist.json   # 130+ forbidden games/publishers
└── .cache/              # Auto-generated cache
```

## How It Works

1. **Input** - You provide a game name, Play Store URL, or package name
2. **Blacklist Check** - Checks against 130+ forbidden games/publishers
3. **Platinmods Search** - Searches forum with 3-tier priority:
   - Package name (most accurate)
   - Game name
   - Package app name (fallback)
4. **Relevance Filtering** - Removes unrelated threads using smart word matching
5. **Results** - Shows available, modded, or blacklisted status

## Thread Types

| Type | Color | Meaning |
|------|-------|---------|
| `[PMT]` | Green | Platinmods Team official mod |
| `[Free]` | Cyan | Free mod available |
| `[Shared]` | Magenta | Shared by user |
| `[Request]` | Yellow | Open request |
| `[Fixing]` | Red | Needs fixing |
| `[Outdated]` | Gray | Outdated mod |
| `[Mod]` | White | General mod thread |

## Build from Source

```bash
pip install pyinstaller
pyinstaller --onefile --name "Platinmods Checker" main.py
```

Output: `dist/Platinmods Checker`

## License

For personal use only.

## Disclaimer

This tool is for checking purposes only. Always follow Platinmods forum rules and guidelines.
