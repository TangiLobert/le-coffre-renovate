"""X-Forwarded-For-aware client IP resolution.

Rate limiting needs a correct client IP to key buckets against.  Reading
``X-Forwarded-For`` blindly lets any client forge an IP per request by setting
the header themselves, which defeats IP-based rate limiting entirely.

The rule encoded here: only trust ``X-Forwarded-For`` when the direct TCP
peer is a known proxy (``trusted_proxies``); and within that header, only
trust the rightmost ``hops`` entries — each one was appended by a link in the
proxy chain we control, so the entry at position ``len(xff) - hops`` is the
nearest hop we trust to have written an authentic value.
"""

from __future__ import annotations

from typing import Protocol


class _HasClientAndHeaders(Protocol):
    client: object | None
    headers: dict[str, str]


def resolve_client_ip(
    request: _HasClientAndHeaders,
    *,
    trusted_proxies: set[str],
    hops: int,
) -> str:
    """Return the caller's client IP, honoring XFF only for trusted peers."""
    client = getattr(request, "client", None)
    peer = getattr(client, "host", None) or "unknown"

    if hops <= 0 or peer not in trusted_proxies:
        return peer

    raw = request.headers.get("X-Forwarded-For", "")
    entries = [p.strip() for p in raw.split(",") if p.strip()]
    if len(entries) < hops:
        return peer
    return entries[-hops]
