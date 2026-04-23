"""Reusable utilities for common application tasks."""

import hashlib

from rest_framework.request import Request

__all__ = [
    'hash_token',
    'resolve_client_ip',
]

# Headers that commonly carry the real client IP when the application sits
# behind a reverse proxy or load balancer, listed in priority order.
_FORWARDED_FOR_HEADERS = (
    'HTTP_X_FORWARDED_FOR',
    'HTTP_X_REAL_IP',
    'REMOTE_ADDR',
)


def hash_token(raw: str) -> str:
    """Return the SHA-256 hex digest of a raw token string.

    Args:
        raw: The plaintext token value supplied by the caller.

    Returns:
        A 64-character lowercase hex string.
    """

    return hashlib.sha256(raw.encode()).hexdigest()


def resolve_client_ip(request: Request) -> str:
    """Return the best-guess client IP address from request metadata.

    Args:
        request: An incoming HTTP request.

    Returns:
        The first usable IP string found across forwarded-for headers.
    """

    for header in _FORWARDED_FOR_HEADERS:
        value = request.META.get(header, '').strip()
        if value:
            # X-Forwarded-For may be a comma-separated list.
            # The leftmost entry is the original client.
            return value.split(',')[0].strip()

    return '0.0.0.0'
