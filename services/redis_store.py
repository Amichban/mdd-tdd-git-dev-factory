"""
Redis-based state management for production.

Provides caching, session storage, and pub/sub for events.
"""

import os
import json
from typing import Any, Optional
from datetime import timedelta

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None


class RedisStore:
    """Redis-backed state store with pub/sub support."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: str = None,
        prefix: str = "devplatform:"
    ):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package not installed. "
                "Install with: pip install redis"
            )

        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.prefix = prefix

        self._client: Optional[Redis] = None
        self._pubsub = None

    @property
    def client(self) -> Redis:
        """Get Redis client, connecting if needed."""
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
        return self._client

    def _key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"

    # Basic key-value operations
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        value = self.client.get(self._key(key))
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value with optional TTL in seconds."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl:
            return self.client.setex(self._key(key), ttl, serialized)
        return self.client.set(self._key(key), serialized)

    def delete(self, key: str) -> int:
        """Delete a key."""
        return self.client.delete(self._key(key))

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.client.exists(self._key(key)) > 0

    def expire(self, key: str, seconds: int) -> bool:
        """Set TTL on existing key."""
        return self.client.expire(self._key(key), seconds)

    def ttl(self, key: str) -> int:
        """Get TTL of key in seconds."""
        return self.client.ttl(self._key(key))

    # Hash operations for complex objects
    def hget(self, name: str, key: str) -> Optional[str]:
        """Get field from hash."""
        return self.client.hget(self._key(name), key)

    def hset(self, name: str, key: str, value: Any) -> int:
        """Set field in hash."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        return self.client.hset(self._key(name), key, serialized)

    def hgetall(self, name: str) -> dict:
        """Get all fields from hash."""
        data = self.client.hgetall(self._key(name))
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except json.JSONDecodeError:
                result[k] = v
        return result

    def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from hash."""
        return self.client.hdel(self._key(name), *keys)

    # List operations for queues
    def lpush(self, key: str, *values: Any) -> int:
        """Push to left of list."""
        serialized = [
            json.dumps(v) if not isinstance(v, str) else v
            for v in values
        ]
        return self.client.lpush(self._key(key), *serialized)

    def rpush(self, key: str, *values: Any) -> int:
        """Push to right of list."""
        serialized = [
            json.dumps(v) if not isinstance(v, str) else v
            for v in values
        ]
        return self.client.rpush(self._key(key), *serialized)

    def lpop(self, key: str) -> Optional[Any]:
        """Pop from left of list."""
        value = self.client.lpop(self._key(key))
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def rpop(self, key: str) -> Optional[Any]:
        """Pop from right of list."""
        value = self.client.rpop(self._key(key))
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list."""
        values = self.client.lrange(self._key(key), start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except json.JSONDecodeError:
                result.append(v)
        return result

    def llen(self, key: str) -> int:
        """Get list length."""
        return self.client.llen(self._key(key))

    # Pub/Sub for events
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        serialized = json.dumps(message) if not isinstance(message, str) else message
        return self.client.publish(self._key(channel), serialized)

    def subscribe(self, *channels: str):
        """Subscribe to channels."""
        if self._pubsub is None:
            self._pubsub = self.client.pubsub()
        prefixed = [self._key(c) for c in channels]
        self._pubsub.subscribe(*prefixed)

    def listen(self):
        """Listen for messages on subscribed channels."""
        if self._pubsub is None:
            return
        for message in self._pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                except json.JSONDecodeError:
                    data = message["data"]
                yield {
                    "channel": message["channel"].replace(self.prefix, ""),
                    "data": data
                }

    # Session management
    def create_session(
        self,
        session_id: str,
        data: dict,
        ttl: int = 3600
    ) -> bool:
        """Create a session with TTL."""
        key = f"session:{session_id}"
        return self.set(key, data, ttl=ttl)

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        return self.get(f"session:{session_id}")

    def update_session(self, session_id: str, data: dict) -> bool:
        """Update session data, preserving TTL."""
        key = f"session:{session_id}"
        current_ttl = self.ttl(key)
        if current_ttl > 0:
            return self.set(key, data, ttl=current_ttl)
        return self.set(key, data)

    def delete_session(self, session_id: str) -> int:
        """Delete a session."""
        return self.delete(f"session:{session_id}")

    # Signal/Event stream
    def emit_signal(self, signal: dict) -> int:
        """Emit a signal to the events channel."""
        return self.publish("signals", signal)

    def get_recent_signals(self, count: int = 100) -> list:
        """Get recent signals from history."""
        return self.lrange("signal_history", 0, count - 1)

    def store_signal(self, signal: dict, max_history: int = 1000):
        """Store signal in history."""
        self.lpush("signal_history", signal)
        # Trim to max size
        self.client.ltrim(self._key("signal_history"), 0, max_history - 1)

    # Cache helpers
    def cache(self, key: str, ttl: int = 300):
        """Decorator for caching function results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                cache_key = f"cache:{key}:{hash(str(args) + str(kwargs))}"
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl)
                return result
            return wrapper
        return decorator

    def invalidate_cache(self, pattern: str = "cache:*"):
        """Invalidate cached items matching pattern."""
        keys = self.client.keys(self._key(pattern))
        if keys:
            return self.client.delete(*keys)
        return 0

    # Health check
    def ping(self) -> bool:
        """Check Redis connection."""
        try:
            return self.client.ping()
        except Exception:
            return False

    def close(self):
        """Close connections."""
        if self._pubsub:
            self._pubsub.close()
        if self._client:
            self._client.close()


# Global store instance
_store = None


def get_redis_store() -> RedisStore:
    """Get the global Redis store instance."""
    global _store
    if _store is None:
        _store = RedisStore()
    return _store


def get_or_create_store() -> Optional[RedisStore]:
    """Get Redis store if available, or None."""
    if not REDIS_AVAILABLE:
        return None
    try:
        store = get_redis_store()
        if store.ping():
            return store
    except Exception:
        pass
    return None
