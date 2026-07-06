"""Shared slowapi rate limiter, keyed by client IP.

Defined in its own module so both the FastAPI app (app/main.py, which wires
the limiter into app.state and registers the 429 handler) and individual
routers can import it without circular imports. Works identically locally
and on Modal since it is pure in-process middleware.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def client_ip(request: Request) -> str:
    """Rate-limit key: the originating client IP.

    In production every request arrives via the Vercel /api proxy (and
    Modal's ingress), so the direct peer address is the proxy — keying on
    it alone would give all users one shared bucket. Both hops append the
    real client to X-Forwarded-For; use its first entry when present.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip)
