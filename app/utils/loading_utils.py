import sys
import threading
import itertools
import time
from typing import Optional

class LoadingAnimation:
    """
    Displays a loading animation in the console while a task is running.
    Usage:
        with LoadingAnimation("Loading data..."):
            # do some long task
        # animation automatically stops when context exits
    """
    
    def __init__(self, message: str = "Processing", animation_type: str = "dots"):
        self.message = message
        self.animation_type = animation_type
        self.is_running = False
        self.animation_thread = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def start(self):
        """Start the loading animation in a separate thread"""
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
    def stop(self):
        """Stop the loading animation"""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        # Clear the animation line
        sys.stdout.write("\r" + " " * (len(self.message) + 20) + "\r")
        sys.stdout.flush()
    
    def _animate(self):
        """Animation loop that runs in a separate thread"""
        if self.animation_type == "dots":
            chars = itertools.cycle([".  ", ".. ", "..."])
        elif self.animation_type == "spinner":
            chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        elif self.animation_type == "bar":
            chars = itertools.cycle(["|", "/", "-", "\\"])
        else:  # Default to dots
            chars = itertools.cycle([".  ", ".. ", "..."])
            
        while self.is_running:
            char = next(chars)
            sys.stdout.write(f"\r{self.message} {char}")
            sys.stdout.flush()
            time.sleep(0.1)


def timed_action(message: str, animation_type: str = "dots"):
    """
    Decorator to show loading animation during function execution
    
    Example:
        @timed_action("Fetching data")
        def fetch_data():
            # do something that takes time
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with LoadingAnimation(message, animation_type):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
