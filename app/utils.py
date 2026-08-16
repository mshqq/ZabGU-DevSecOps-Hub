from datetime import datetime, timezone
from urllib.parse import ParseResult, urlparse

ALLOWED_HOSTS = ("github.com", "gitlab.com")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def is_allowed_url(url: str) -> bool:
    if not url:
        return False

    parsed: ParseResult = urlparse(url)
    if parsed.scheme in ("http", "https"):
        host: str | None = parsed.hostname

        return host is not None and host.lower() in ALLOWED_HOSTS

    if url.startswith("git@"):
        rest: str = url[len("git@") :]
        host, sep, path = rest.partition(":")

        return bool(sep) and bool(host) and bool(path) and host.lower() in ALLOWED_HOSTS

    return False
