from __future__ import annotations

from datetime import datetime

from to_utc.to_utc import DatetimeLike, to_utc


def to_naive_utc(
    value: DatetimeLike,
) -> datetime:
    """Converts any datetime-like value to a naive UTC datetime."""
    return to_utc(value).replace(tzinfo=None)
