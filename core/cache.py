import time
import threading
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    """Simple thread-safe TTL cache for API responses."""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str):
        """Get value from cache. Returns None if not found or expired."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self._cache[key]
        return None

    def set(self, key: str, value, ttl: int = None):
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        with self._lock:
            # Evict if over max size
            if len(self._cache) >= self.max_size:
                self._evict_expired()
                if len(self._cache) >= self.max_size:
                    # Remove oldest entry
                    oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
                    del self._cache[oldest_key]
            self._cache[key] = (value, time.time() + ttl)

    def _evict_expired(self):
        """Remove all expired entries."""
        now = time.time()
        expired = [k for k, (v, exp) in self._cache.items() if exp <= now]
        for k in expired:
            del self._cache[k]

    def clear(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()


if __name__ == '__main__':
    cache = TTLCache(default_ttl=5)
    cache.set('test', 'value')
    print(cache.get('test'))
