from __future__ import annotations

from datetime import datetime, timezone


def now() -> datetime:
    """
    Returns the current UTC time as an aware datetime.

    Returns:
        datetime: Current UTC time with timezone info set to UTC
    """
    return datetime.now(timezone.utc)
