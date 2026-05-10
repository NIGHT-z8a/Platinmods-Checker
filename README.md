# Platinmods Checker

A CLI tool to check if Android games are already modded on [Platinmods](https://platinmods.com) before you start modding them.

## Features

- **Check by Game Name** - Search Platinmods for existing mods
- **Check by Play Store URL** - Paste a Google Play link, auto-extract package and check
- **Search APKPure** - Discover games and check their mod status
- **Auto-Scan** - Scan multiple categories and find available games to mod
- **Batch Check** - Load games from a file and check them all at once
- **Blacklist Detection** - Warns if game is on Platinmods blacklist
- **Caching** - Results cached for 1 hour to speed up repeated checks
- **Export Results** - Save checks as JSON, CSV, or text files
- **Rate Limiting** - Built-in delays and retries to avoid being blocked

## Requirements

- Python 3.8+
- Internet connection (scrapes Platinmods & APKPure live)
- No external dependencies needed

## Quick Start

### Run with Python
```bash
python3 main.py
```

### Run Binary (Linux)
```bash
./dist/Platinmods\ Checker
```

## Usage

### Menu Options

| Option | Description |
|--------|-------------|
| 1 | Check game on Platinmods |
| 2 | Check by Google Play URL |
| 3 | Search games on APKPure |
| 4 | Find moddable games (auto-scan) |
| 5 | Batch check from file |
| 6 | View blacklist |
| 7 | Cache settings |
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
Platinmods modded games apps/
├── main.py              # CLI entry point
├── config.py            # Blacklist + settings
├── core/
│   ├── cache.py         # JSON-based caching
│   ├── checker.py       # Game checking logic
│   └── export.py        # Export results (JSON/CSV/TXT)
├── scrapers/
│   ├── http_client.py   # HTTP with retry + rate limit
│   ├── platinmods.py    # Platinmods forum scraper
│   └── apkpure.py       # APKPure game discovery
├── utils/
│   └── progress.py      # Progress bars & spinners
├── dist/
│   └── Platinmods Checker  # Compiled binary (Linux)
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

## Blacklist

Games on the blacklist require permission from G-bo before posting. Includes:
- PUBG (all versions)
- COD (all versions)
- Minecraft + same publisher
- World of Tanks + Wargaming games
- BitLife (all versions)
- Stumble Guys, 8 Ball Pool
- And 120+ more...

See `config.py` for the full list.

## Build from Source

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build Binary
```bash
pyinstaller --onefile --name "Platinmods Checker" main.py
```

Output: `dist/Platinmods Checker`

## Platform Support

| Platform | Python | Binary |
|----------|--------|--------|
| Linux | Yes | Yes |
| Windows | Yes | Build on Windows |
| macOS | Yes | Build on macOS |

## License

For personal use only.

## Disclaimer

This tool is for checking purposes only. Always follow Platinmods forum rules and guidelines.
