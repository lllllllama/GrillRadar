"""Simple sliding window rate limiter middleware."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict, Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Limit incoming requests per client IP within a fixed window."""

    def __init__(
        self,
        app,
        *,
        max_requests: int,
        window_seconds: int,
        exempt_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exempt_paths = set(exempt_paths or [])
        self._buckets: DefaultDict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self._buckets[client_ip]

        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please retry later.",
                    "rate_limit": {
                        "max_requests": self.max_requests,
                        "window_seconds": self.window_seconds,
                    },
                },
            )

        bucket.append(now)
        return await call_next(request)
