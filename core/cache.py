"""
Cache module - JSON-based caching for search results
"""

import json
import os
import time
from pathlib import Path

# Default cache settings
CACHE_DIR = Path(__file__).parent.parent / ".cache"
CACHE_TTL = 3600  # 1 hour in seconds
CACHE_ENABLED = True


class Cache:
    """Simple JSON-based cache for storing search results"""
    
    def __init__(self, cache_dir=None, ttl=None, enabled=None):
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.ttl = ttl if ttl is not None else CACHE_TTL
        self.enabled = enabled if enabled is not None else CACHE_ENABLED
        
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key):
        """Get cache file path for a key"""
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key):
        """Get cached result if exists and not expired"""
        if not self.enabled:
            return None
        
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() - data.get("timestamp", 0) > self.ttl:
                cache_path.unlink()
                return None
            
            return data.get("result")
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(self, key, result):
        """Cache a result"""
        if not self.enabled:
            return
        
        cache_path = self._get_cache_path(key)
        try:
            data = {
                "timestamp": time.time(),
                "result": result,
            }
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    def clear(self):
        """Clear all cached data"""
        if not self.enabled:
            return
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except IOError:
                pass
    
    def clean_expired(self):
        """Remove all expired cache files"""
        if not self.enabled:
            return 0

        removed = 0
        now = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                if now - data.get("timestamp", 0) > self.ttl:
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, IOError):
                cache_file.unlink()
                removed += 1

        return removed

    def get_stats(self):
        """Get cache statistics"""
        if not self.enabled:
            return {"files": 0, "size": 0}
        
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files if f.exists())
        
        return {
            "files": len(files),
            "size": total_size,
            "dir": str(self.cache_dir),
        }


# Global cache instance
cache = Cache()
