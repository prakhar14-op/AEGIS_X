import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class TokenBucket:

    def __init__(self, rate: float, capacity: int):
        self._rate = rate
        self._capacity = capacity
        self._tokens: Dict[str, float] = defaultdict(lambda: float(capacity))
        self._last_refill: Dict[str, float] = defaultdict(time.time)

    def consume(self, key: str, tokens: int = 1) -> Tuple[bool, float]:
        now = time.time()
        elapsed = now - self._last_refill[key]
        self._last_refill[key] = now
        self._tokens[key] = min(
            self._capacity,
            self._tokens[key] + elapsed * self._rate,
        )
        if self._tokens[key] >= tokens:
            self._tokens[key] -= tokens
            return True, self._tokens[key]
        return False, self._tokens[key]


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, requests_per_second: float = 50, burst: int = 100):
        super().__init__(app)
        self._bucket = TokenBucket(rate=requests_per_second, capacity=burst)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        allowed, remaining = self._bucket.consume(client_ip)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": "1", "X-RateLimit-Remaining": "0"},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(int(remaining))
        return response
