#!/usr/bin/env python3
"""
Platinmods Checker
Main CLI entry point
"""

import sys
import os
import re
import urllib.parse

from scrapers.platinmods import check_game as platinmods_check
from scrapers.apkpure import search_games, get_trending_games, get_games_by_category
from core.checker import check_single_game, find_moddable_games
from config import BLACKLIST, GAME_CATEGORIES
from core.cache import cache
from utils.progress import Progress, Spinner
from core.export import export_json, export_csv, export_text, save_last_check

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

# ASCII Art Banner - Rainbow
BANNER = f"""
{RED}|$$$$$$$  |$$        /$$$$$$  /$$$$$$$$ /$$$$$$ /$$    /$$ /$$      /$$  /$$$$$$  /$$$$$$$   /$$$$$$
{YELLOW}| $$__  $$| $$      |$$__  $$ |__  $$__/|_  $$_/| $$$ | $$| $$$    /$$$ /$$__  $$| $$__  $$ /$$__  $$
{GREEN}| $$  \\ $$| $$      | $$  \\ $$   | $$     | $$  | $$$$| $$| $$$$  /$$$$| $$  \\ $$| $$  \\ $$| $$  \\__/
{CYAN}| $$$$$$$/| $$      | $$$$$$$$   | $$     | $$  | $$ $$ $$| $$ $$/$$ $$| $$  | $$| $$  | $$|  $$$$$$ 
{BLUE}| $$____/ | $$      | $$__  $$   | $$     | $$  | $$  $$$$| $$  $$$| $$| $$  | $$| $$  | $$ \\____  $$
{MAGENTA}| $$      | $$      | $$  | $$   | $$     | $$  | $$\\  $$$| $$\\  $ | $$| $$  | $$| $$  | $$ /$$  \\ $$
{RED}| $$      | $$$$$$$$| $$  | $$   | $$    /$$$$$$| $$ \\  $$| $$ \\/  | $$|  $$$$$$/| $$$$$$$/|  $$$$$$/ 
{YELLOW}|__/      |________/|__/  |__/   |__/   |______/|__/  \\__/|__/     |__/ \\______/ |_______/  \\______/{RESET}
{DIM}                    Platinmods Game Checker & Finder{RESET}"""

# Menu border style
MENU_WIDTH = 60


def print_banner():
    """Print the ASCII art banner"""
    print(BANNER)
    print()


def print_menu():
    """Print styled menu"""
    print(f"{BOLD}{BLUE}┌{'─' * MENU_WIDTH}┐{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {BOLD}{CYAN}Main Menu{RESET}{' ' * (MENU_WIDTH - 11)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}├{'─' * MENU_WIDTH}┤{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}1.{RESET} Check game on Platinmods{' ' * (MENU_WIDTH - 29)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}2.{RESET} Check by Google Play URL{' ' * (MENU_WIDTH - 29)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}3.{RESET} Search games on APKPure{' ' * (MENU_WIDTH - 28)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}4.{RESET} Find moddable games (auto-scan){' ' * (MENU_WIDTH - 34)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}5.{RESET} Batch check from file{' ' * (MENU_WIDTH - 26)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}6.{RESET} View blacklist{' ' * (MENU_WIDTH - 19)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {GREEN}7.{RESET} Cache settings{' ' * (MENU_WIDTH - 19)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}├{'─' * MENU_WIDTH}┤{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {RED}0.{RESET} Exit{' ' * (MENU_WIDTH - 9)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}└{'─' * MENU_WIDTH}┘{RESET}")


def print_section(title):
    """Print a styled section header"""
    print(f"\n{BOLD}{CYAN}{'─' * 50}{RESET}")
    print(f"{BOLD}{CYAN} {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 50}{RESET}\n")


def print_status_bar():
    """Print status bar at bottom"""
    stats = cache.get_stats()
    status = f"Cache: {stats['files']} files | {stats['size'] / 1024:.1f} KB"
    print(f"\n{GRAY}{'─' * 50}{RESET}")
    print(f"{GRAY} {status}{RESET}")


def print_success(msg):
    """Print success message"""
    print(f"\n  {GREEN}✓{RESET} {msg}")


def print_error(msg):
    """Print error message"""
    print(f"\n  {RED}✗{RESET} {msg}")


def print_warning(msg):
    """Print warning message"""
    print(f"\n  {YELLOW}⚠{RESET} {msg}")


def print_info(msg):
    """Print info message"""
    print(f"\n  {CYAN}ℹ{RESET} {msg}")


def extract_package_from_play_url(url):
    """Extract package name from Google Play URL"""
    match = re.search(r"id=([a-zA-Z0-9_.]+)", url)
    if match:
        return match.group(1)
    return None


def get_game_name_from_playstore(package_name):
    """Get game name by searching APKPure"""
    games, error = search_games(package_name, limit=5)
    if games:
        for game in games:
            if game["package"] == package_name:
                return game["name"]
        return games[0]["name"]
    
    parts = package_name.split(".")
    return parts[-1].replace("_", " ").title()


def clean_game_name(name):
    """Clean game name for better search results"""
    name = re.sub(r"\s*\b(202[0-9])\b\s*$", "", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def get_thread_type(title):
    """Extract thread type from title"""
    title_upper = title.upper()
    if "PMT" in title_upper:
        return "PMT"
    if "SHARED" in title_upper:
        return "Shared"
    if "FREE MOD" in title_upper or "FREE" in title_upper:
        return "Free"
    if "REQUEST" in title_upper:
        return "Request"
    if "OUTDATED" in title_upper:
        return "Outdated"
    if "NEEDS FIXING" in title_upper:
        return "Fixing"
    return "Mod"


def format_thread(title):
    """Format thread title for display"""
    title = re.sub(r"^(PMT|FREE|SHARED|OPEN|FILLED|NEEDS FIXING|OUTDATED)\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*Ver\.\s*[\d.]+[a-z]?\s*", " ", title)
    title = re.sub(r"\s*MOD\s*(MENU)?\s*APK.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\[[^\]]+\]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:70]


def display_threads(threads):
    """Display thread list in clean format"""
    print(f"\n{BOLD}{BLUE}┌{'─' * 48}┐{RESET}")
    print(f"{BOLD}{BLUE}│{RESET}  {BOLD}Threads Found: {len(threads)}{' ' * (48 - len(str(len(threads))) - 15)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}├{'─' * 48}┤{RESET}")
    
    for i, t in enumerate(threads):
        thread_type = get_thread_type(t["title"])
        clean_title = format_thread(t["title"])
        thread_id = t.get("id", t["url"].rstrip("/").split(".")[-1])
        
        type_colors = {
            "PMT": GREEN,
            "Free": CYAN,
            "Shared": MAGENTA,
            "Request": YELLOW,
            "Outdated": GRAY,
            "Fixing": RED,
            "Mod": WHITE,
        }
        color = type_colors.get(thread_type, WHITE)
        
        print(f"{BOLD}{BLUE}│{RESET}  {color}[{thread_type}]{RESET} {clean_title[:40]}{' ' * max(0, 40 - len(clean_title))}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET}    {GRAY}ID: {thread_id}{' ' * 38}{BOLD}{BLUE}│{RESET}")
        if i < len(threads) - 1:
            print(f"{BOLD}{BLUE}│{RESET}{' ' * 48}{BOLD}{BLUE}│{RESET}")
    
    print(f"{BOLD}{BLUE}└{'─' * 48}┘{RESET}")


def menu_check_game():
    """Check game by name"""
    print_section("Check Game on Platinmods")
    
    game = input(f"  {CYAN}Game name {GREEN}▶{RESET} ").strip()
    if not game:
        return
    
    pkg = input(f"  {CYAN}Package name (optional) {GREEN}▶{RESET} ").strip() or None
    
    progress = Progress(1, prefix="Checking")
    progress.start()
    
    result = check_single_game(game, pkg)
    progress.finish()
    
    if result["status"] == "blacklisted":
        print_error(f"BLACKLISTED - {result['reason']}")
    elif result["status"] == "error":
        print_error(f"Error: {result['error']}")
    elif result["status"] == "modded":
        print_warning(f"Found {len(result['threads'])} thread(s)")
        display_threads(result["threads"])
    else:
        print_success("No existing mods found - Game is available!")


def menu_check_playstore_url():
    """Check game by Google Play URL"""
    print_section("Check by Google Play URL")
    
    url = input(f"  {CYAN}Google Play URL {GREEN}▶{RESET} ").strip()
    if not url:
        return
    
    package = extract_package_from_play_url(url)
    if not package:
        print_error("Invalid Google Play URL.")
        print_info(f"Example: https://play.google.com/store/apps/details?id=com.example.game")
        return
    
    print_info(f"Extracted package: {package}")
    
    progress = Progress(2, prefix="Checking")
    progress.start()
    
    game_name = get_game_name_from_playstore(package)
    game_name = clean_game_name(game_name)
    progress.update()
    print_info(f"Game name: {game_name}")
    
    result = check_single_game(game_name, package)
    progress.finish()
    
    if result["status"] == "blacklisted":
        print_error(f"BLACKLISTED - {result['reason']}")
        print(f"  {RED}This game is FORBIDDEN to mod on Platinmods.{RESET}")
    elif result["status"] == "error":
        print_error(f"Error: {result['error']}")
    elif result["status"] == "modded":
        print_warning("Already modded on Platinmods")
        display_threads(result["threads"])
    else:
        print_success("Not blacklisted")
        print_success("No existing mods found")
        print(f"\n{BOLD}{GREEN}✓ Game is available for modding!{RESET}")


def menu_search_apkpure():
    """Search games on APKPure"""
    print_section("Search Games on APKPure")
    
    query = input(f"  {CYAN}Search APKPure {GREEN}▶{RESET} ").strip()
    if not query:
        return
    
    progress = Progress(1, prefix="Searching")
    progress.start()
    
    games, error = search_games(query)
    progress.finish()
    
    if error or not games:
        print_error("No results found.")
        return
    
    print(f"\n{BOLD}{GREEN}Found {len(games)} games:{RESET}\n")
    for i, game in enumerate(games, 1):
        print(f"  {GREEN}{i}.{RESET} {game['name']}")
        print(f"     {GRAY}{game['package']}{RESET}")
    
    choice = input(f"\n  {CYAN}Check a game on Platinmods? (number or 0 to skip) {GREEN}▶{RESET} ").strip()
    if choice.isdigit() and int(choice) > 0 and int(choice) <= len(games):
        game = games[int(choice) - 1]
        print(f"\n{YELLOW}Checking {game['name']} on Platinmods...{RESET}")
        result = check_single_game(game["name"], game["package"])
        
        if result["status"] == "available":
            print_success("Available for modding!")
        elif result["status"] == "modded":
            print_warning(f"Already modded ({len(result['threads'])} threads)")
            display_threads(result["threads"])
        else:
            print_error(result.get('reason', result.get('error', 'Unknown')))


def menu_find_moddable():
    """Auto-scan for moddable games"""
    print_section("Find Moddable Games (Auto-Scan)")
    
    print(f"{YELLOW}Fetching games from APKPure...{RESET}")
    
    games = []
    for cat in GAME_CATEGORIES[:3]:
        cat_games, error = get_games_by_category(cat["id"], limit=10)
        if cat_games:
            games.extend(cat_games)
    
    if not games:
        print_error("Could not fetch games. Check your internet connection.")
        return
    
    print(f"{YELLOW}Found {len(games)} games. Checking against Platinmods...{RESET}")
    
    all_results = []
    progress = Progress(len(games[:15]), prefix="Checking")
    
    def on_progress(current, total, result):
        all_results.append(result)
        progress.update()
    
    results = find_moddable_games(games, max_checks=15, progress_callback=on_progress)
    progress.finish()
    
    print(f"\n{BOLD}{GREEN}Available for modding ({len(results['available'])}):{RESET}")
    for r in results["available"]:
        print(f"  {GREEN}✓{RESET} {r['name']} {GRAY}({r['package']}){RESET}")
    
    print(f"\n{BOLD}{RED}Already modded ({len(results['modded'])}):{RESET}")
    for r in results["modded"]:
        print(f"  {RED}✗{RESET} {r['name']} {GRAY}({len(r['threads'])} threads){RESET}")
    
    if results["blacklisted"]:
        print(f"\n{BOLD}{RED}Blacklisted ({len(results['blacklisted'])}):{RESET}")
        for r in results["blacklisted"]:
            print(f"  {RED}⛔{RESET} {r['name']} {GRAY}({r['reason']}){RESET}")
    
    # Export option
    if all_results:
        print(f"\n{YELLOW}Save results?{RESET}")
        print(f"  {GREEN}1.{RESET} Export as JSON")
        print(f"  {GREEN}2.{RESET} Export as CSV")
        print(f"  {GREEN}3.{RESET} Export as text")
        print(f"  {GREEN}0.{RESET} Skip")
        
        choice = input(f"\n  {BOLD}Select {GREEN}▶{RESET} ").strip()
        if choice == "1":
            filepath = export_json(all_results)
            print_success(f"Saved to {filepath}")
        elif choice == "2":
            filepath = export_csv(all_results)
            print_success(f"Saved to {filepath}")
        elif choice == "3":
            filepath = export_text(all_results)
            print_success(f"Saved to {filepath}")


def menu_batch_check():
    """Batch check games from file"""
    print_section("Batch Check from File")
    
    print(f"{GRAY}Format: One game per line (name,package){RESET}")
    print(f"{GRAY}Example: Subway Surfers,com.kiloo.subwaysurfers{RESET}")
    
    filepath = input(f"\n  {CYAN}File path {GREEN}▶{RESET} ").strip()
    if not filepath:
        return
    
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return
    
    games = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(",")
                name = parts[0].strip()
                package = parts[1].strip() if len(parts) > 1 else None
                if name:
                    games.append({"name": name, "package": package})
    
    if not games:
        print_error("No valid games found in file.")
        return
    
    print(f"\n{YELLOW}Found {len(games)} games. Checking...{RESET}\n")
    
    all_results = []
    progress = Progress(len(games), prefix="Checking")
    
    for i, game in enumerate(games):
        result = check_single_game(game["name"], game["package"])
        all_results.append(result)
        progress.update()
    
    progress.finish()
    
    # Display results
    available = [r for r in all_results if r["status"] == "available"]
    modded = [r for r in all_results if r["status"] == "modded"]
    blacklisted = [r for r in all_results if r["status"] == "blacklisted"]
    
    print(f"\n{BOLD}{GREEN}Available ({len(available)}):{RESET}")
    for r in available:
        print(f"  {GREEN}✓{RESET} {r['name']} {GRAY}({r['package']}){RESET}")
    
    print(f"\n{BOLD}{RED}Modded ({len(modded)}):{RESET}")
    for r in modded:
        print(f"  {RED}✗{RESET} {r['name']} {GRAY}({len(r['threads'])} threads){RESET}")
    
    if blacklisted:
        print(f"\n{BOLD}{RED}Blacklisted ({len(blacklisted)}):{RESET}")
        for r in blacklisted:
            print(f"  {RED}⛔{RESET} {r['name']} {GRAY}({r['reason']}){RESET}")
    
    # Export option
    if all_results:
        print(f"\n{YELLOW}Save results?{RESET}")
        print(f"  {GREEN}1.{RESET} Export as JSON")
        print(f"  {GREEN}2.{RESET} Export as CSV")
        print(f"  {GREEN}3.{RESET} Export as text")
        print(f"  {GREEN}0.{RESET} Skip")
        
        choice = input(f"\n  {BOLD}Select {GREEN}▶{RESET} ").strip()
        if choice == "1":
            filepath = export_json(all_results)
            print_success(f"Saved to {filepath}")
        elif choice == "2":
            filepath = export_csv(all_results)
            print_success(f"Saved to {filepath}")
        elif choice == "3":
            filepath = export_text(all_results)
            print_success(f"Saved to {filepath}")


def menu_view_blacklist():
    """Display full blacklist"""
    print_section("Blacklist - Forbidden to Mod")
    
    for item in BLACKLIST:
        print(f"  {RED}✗{RESET} {item.title()}")


def menu_cache_info():
    """Show cache information"""
    print_section("Cache Settings")
    
    stats = cache.get_stats()
    print(f"  {CYAN}Enabled:{RESET} {cache.enabled}")
    print(f"  {CYAN}TTL:{RESET} {cache.ttl}s ({cache.ttl // 3600}h)")
    print(f"  {CYAN}Files:{RESET} {stats['files']}")
    print(f"  {CYAN}Size:{RESET} {stats['size'] / 1024:.1f} KB")
    print(f"  {CYAN}Directory:{RESET} {stats['dir']}")
    
    print(f"\n  {GREEN}1.{RESET} Clear cache")
    print(f"  {GREEN}0.{RESET} Back")
    
    choice = input(f"\n  {BOLD}Select {GREEN}▶{RESET} ").strip()
    if choice == "1":
        cache.clear()
        print_success("Cache cleared")


def main():
    """Main menu loop"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input(f"\n  {BOLD}Select {GREEN}▶{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{YELLOW}Goodbye!{RESET}\n")
            break
        
        if choice == "1":
            menu_check_game()
        elif choice == "2":
            menu_check_playstore_url()
        elif choice == "3":
            menu_search_apkpure()
        elif choice == "4":
            menu_find_moddable()
        elif choice == "5":
            menu_batch_check()
        elif choice == "6":
            menu_view_blacklist()
        elif choice == "7":
            menu_cache_info()
        elif choice == "0":
            print(f"\n  {GREEN}Good luck modding!{RESET}\n")
            break
        else:
            print_error("Invalid option.")
            continue
        
        print_status_bar()
        
        try:
            input(f"\n  {DIM}Press Enter to continue...{RESET}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{YELLOW}Goodbye!{RESET}\n")
            break


if __name__ == "__main__":
    main()
