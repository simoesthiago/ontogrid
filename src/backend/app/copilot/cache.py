from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from threading import Lock

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class _MemoryCacheEntry:
    value: str
    expires_at: float


class CopilotCache:
    def __init__(self) -> None:
        self._client: Redis | None = None
        self._memory: dict[str, _MemoryCacheEntry] = {}
        self._lock = Lock()

    def get_json(self, key: str) -> dict[str, object] | None:
        client = self._client_or_none()
        if client is not None:
            try:
                payload = client.get(key)
            except RedisError as exc:
                logger.warning("copilot-cache-read-failed error=%s", exc)
            else:
                if payload:
                    return json.loads(payload)

        with self._lock:
            entry = self._memory.get(key)
            if entry is None or entry.expires_at < time.time():
                self._memory.pop(key, None)
                return None
            return json.loads(entry.value)

    def set_json(self, key: str, payload: dict[str, object], ttl_seconds: int) -> None:
        serialized = json.dumps(payload, ensure_ascii=True)
        client = self._client_or_none()
        if client is not None:
            try:
                client.setex(key, ttl_seconds, serialized)
                return
            except RedisError as exc:
                logger.warning("copilot-cache-write-failed error=%s", exc)

        with self._lock:
            self._memory[key] = _MemoryCacheEntry(
                value=serialized,
                expires_at=time.time() + ttl_seconds,
            )

    def _client_or_none(self) -> Redis | None:
        settings = get_settings()
        if not settings.redis_enabled:
            return None
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client


@lru_cache
def get_copilot_cache() -> CopilotCache:
    return CopilotCache()
