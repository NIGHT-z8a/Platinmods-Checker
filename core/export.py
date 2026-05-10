"""
Export module - Save check results to files
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path


def export_json(results, filepath=None):
    """Export results to JSON file"""
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"results_{timestamp}.json"
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "available": len([r for r in results if r.get("status") == "available"]),
        "modded": len([r for r in results if r.get("status") == "modded"]),
        "blacklisted": len([r for r in results if r.get("status") == "blacklisted"]),
        "results": results,
    }
    
    with open(filepath, "w") as f:
        json.dump(export_data, f, indent=2)
    
    return filepath


def export_csv(results, filepath=None):
    """Export results to CSV file"""
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"results_{timestamp}.csv"
    
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "Game Name",
            "Package",
            "Status",
            "Thread Count",
            "Thread IDs",
            "Reason",
        ])
        
        # Data rows
        for r in results:
            thread_ids = ",".join([t.get("id", "") for t in r.get("threads", [])])
            writer.writerow([
                r.get("name", ""),
                r.get("package", ""),
                r.get("status", ""),
                len(r.get("threads", [])),
                thread_ids,
                r.get("reason", ""),
            ])
    
    return filepath


def export_text(results, filepath=None):
    """Export results to readable text file"""
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"results_{timestamp}.txt"
    
    with open(filepath, "w") as f:
        f.write(f"Platinmods Checker - Game Check Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 60}\n\n")
        
        # Available games
        available = [r for r in results if r.get("status") == "available"]
        f.write(f"AVAILABLE FOR MODDING ({len(available)})\n")
        f.write(f"{'-' * 40}\n")
        for r in available:
            f.write(f"  ✓ {r['name']} ({r['package']})\n")
        f.write("\n")
        
        # Already modded
        modded = [r for r in results if r.get("status") == "modded"]
        f.write(f"ALREADY MODDED ({len(modded)})\n")
        f.write(f"{'-' * 40}\n")
        for r in modded:
            f.write(f"  ✗ {r['name']} ({r['package']}) - {len(r['threads'])} threads\n")
        f.write("\n")
        
        # Blacklisted
        blacklisted = [r for r in results if r.get("status") == "blacklisted"]
        f.write(f"BLACKLISTED ({len(blacklisted)})\n")
        f.write(f"{'-' * 40}\n")
        for r in blacklisted:
            f.write(f"  ⛔ {r['name']} - {r['reason']}\n")
    
    return filepath


def save_last_check(results):
    """Save results as the last check (overwrites previous)"""
    filepath = Path(__file__).parent.parent / ".cache" / "last_check.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }
    
    with open(filepath, "w") as f:
        json.dump(export_data, f, indent=2)


def load_last_check():
    """Load the last check results"""
    filepath = Path(__file__).parent.parent / ".cache" / "last_check.json"
    
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
