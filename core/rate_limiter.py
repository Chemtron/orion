import time
import threading
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self):
        self._requests = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        with self._lock:
            # Clean old entries
            self._requests[key] = [t for t in self._requests[key] if t > now - window_seconds]
            if not self._requests[key]:
                del self._requests[key]
            if len(self._requests.get(key, [])) >= max_requests:
                return False
            self._requests[key].append(now)
            return True
