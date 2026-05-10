"""
Progress indicators for batch operations
"""

import sys
import time

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"


class Progress:
    """Simple progress indicator for batch operations"""
    
    def __init__(self, total, prefix="Progress", show_bar=True):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.show_bar = show_bar
        self.start_time = time.time()
        self.bar_width = 30
    
    def _get_bar(self):
        """Generate progress bar string"""
        if self.total == 0:
            return ""
        
        filled = int(self.bar_width * self.current / self.total)
        bar = "█" * filled + "░" * (self.bar_width - filled)
        return bar
    
    def _get_elapsed(self):
        """Get elapsed time string"""
        elapsed = time.time() - self.start_time
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        return f"{elapsed/60:.1f}m"
    
    def update(self, step=1):
        """Update progress by step"""
        self.current += step
        self._display()
    
    def _display(self):
        """Display progress"""
        if not self.show_bar:
            return
        
        if self.total == 0:
            print(f"\r{YELLOW}{self.prefix}: 0/0{RESET}", end="", flush=True)
            return
        
        pct = int(100 * self.current / self.total)
        bar = self._get_bar()
        elapsed = self._get_elapsed()
        
        # Estimate remaining time
        if self.current > 0:
            rate = self.current / (time.time() - self.start_time)
            remaining = (self.total - self.current) / rate
            eta = f"{remaining:.0f}s" if remaining < 60 else f"{remaining/60:.1f}m"
        else:
            eta = "??"
        
        line = f"\r{YELLOW}{self.prefix}{RESET} [{bar}] {CYAN}{self.current}/{self.total}{RESET} ({pct}%) {DIM}ETA: {eta}{RESET}"
        
        # Clear to end of line
        sys.stdout.write(line)
        sys.stdout.flush()
    
    def finish(self):
        """Mark progress as complete"""
        self.current = self.total
        elapsed = self._get_elapsed()
        print(f"\r{GREEN}{self.prefix}{RESET} [{self._get_bar()}] {GREEN}{self.total}/{self.total}{RESET} (100%) {DIM}Done in {elapsed}{RESET}")
        print()


class Spinner:
    """Simple spinner for single operations"""
    
    def __init__(self, message="Working"):
        self.message = message
        self.chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.idx = 0
        self.running = False
    
    def _display(self):
        char = self.chars[self.idx % len(self.chars)]
        self.idx += 1
        sys.stdout.write(f"\r{YELLOW}{char}{RESET} {self.message}...")
        sys.stdout.flush()
    
    def start(self):
        """Start spinner"""
        self.running = True
        self._display()
    
    def step(self):
        """Update spinner animation"""
        if self.running:
            self._display()
    
    def stop(self, success=True):
        """Stop spinner"""
        self.running = False
        icon = "✓" if success else "✗"
        color = GREEN if success else "\033[91m"
        sys.stdout.write(f"\r{color}{icon}{RESET} {self.message}")
        sys.stdout.write(" " * 20)  # Clear rest of line
        sys.stdout.write("\n")
        sys.stdout.flush()
