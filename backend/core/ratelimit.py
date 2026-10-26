"""Limitador de solicitudes en memoria (un solo proceso).
Con varios workers o servidores, usa Redis o el rate limiting de tu proxy."""
import os
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    # Detrás de un proxy inverso esto será la IP del proxy: configura uvicorn con --proxy-headers.
    return request.client.host if request.client else "unknown"


class RateLimiter:
    def __init__(self, max_hits: int, window_seconds: int):
        self.max_hits = max_hits
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def hit(self, key: str) -> None:
        if os.getenv("DISABLE_RATE_LIMIT") == "1":  # solo para pruebas automáticas; nunca en producción
            return
        now = time.time()
        if len(self._hits) > 10000:  # limpieza para que la memoria no crezca sin límite
            for k in [k for k, q in self._hits.items() if not q or now - q[-1] > self.window]:
                del self._hits[k]
        q = self._hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max_hits:
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos. Inténtalo más tarde.",
                headers={"Retry-After": str(self.window)},
            )
        q.append(now)
