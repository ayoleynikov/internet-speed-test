"""URL validation for http/https targets."""

from __future__ import annotations

from urllib.parse import urlparse


def validate_target_url(url: str) -> str:
    """Return normalized URL or raise ValueError."""
    url = url.strip()
    if not url:
        raise ValueError("URL не может быть пустым")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Допустимы только схемы http и https")
    if not parsed.netloc:
        raise ValueError("В URL должны быть хост и, при необходимости, порт")
    if parsed.params or parsed.query or parsed.fragment:
        # query/fragment allowed by spec example; only reject oddities if needed
        pass

    return url