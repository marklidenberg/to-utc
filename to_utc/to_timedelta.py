from __future__ import annotations  # delay type hint evaluation

import re
import numbers
from datetime import timedelta
from typing import Union

# Optional libs
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pendulum

    HAS_PENDULUM = True
except ImportError:
    HAS_PENDULUM = False


TimedeltaLike = Union[
    list,
    int,
    float,
    str,
    timedelta,
    "pd.Timedelta",  # if pandas available
    "np.timedelta64",  # if numpy available
    "pendulum.Duration",  # if pendulum available
]


def to_timedelta(
    value: TimedeltaLike,
) -> timedelta:
    """Convert many timedelta-like values to datetime.timedelta."""

    # - Datetime.timedelta passthrough (check first to avoid any edge cases)

    if isinstance(value, timedelta):
        return value

    # - Numbers -> seconds (but make sure we don't catch timedelta objects)

    if isinstance(value, numbers.Real) and (
        not HAS_NUMPY or not isinstance(value, np.timedelta64)
    ):
        return timedelta(
            seconds=float(value),
        )

    # - Strings

    if isinstance(value, str):
        # Try compact units then word units
        try:
            _UNIT_SECONDS = {
                "d": 86400,
                "h": 3600,
                "m": 60,
                "s": 1,
            }

            s = value.replace(" ", "").lower()

            # Try frequency (d/h/m/s) or pandas-like order-free combos
            m = re.fullmatch(
                r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?",
                s,
            )
            if m:
                d, h, mi, se = (int(x) if x else 0 for x in m.groups())
                return timedelta(
                    days=d,
                    hours=h,
                    minutes=mi,
                    seconds=se,
                )

            # Accept order-free sequences like "2h30m15s" already covered above
            # Also accept single unit like "90s" or "48h" via a simple scan
            m = re.fullmatch(r"(\d+)([dhms])", s)
            if m:
                n = int(m.group(1))
                u = m.group(2)
                return timedelta(
                    seconds=n * _UNIT_SECONDS[u],
                )

            raise ValueError(f"Unknown timedelta string format: {value}")

        except ValueError:
            # Fallback: words

            _WORD_UNITS = {
                "days": 86400,
                "day": 86400,
                "hours": 3600,
                "hour": 3600,
                "mins": 60,
                "minutes": 60,
                "minute": 60,
                "min": 60,
                "seconds": 1,
                "second": 1,
                "sec": 1,
                "s": 1,
            }

            # e.g., "2 hours 30 minutes", "1 day", "5min 10sec"
            tokens = re.findall(r"(\d+)\s*([a-zA-Z]+)", value.lower())
            if not tokens:
                raise ValueError(f"Invalid timedelta string format: {value}")
            total = 0
            for num, unit in tokens:
                if unit not in _WORD_UNITS:
                    raise ValueError(f"Unknown time unit '{unit}' in string: {value}")
                total += int(num) * _WORD_UNITS[unit]
            return timedelta(
                seconds=total,
            )

    # - Pandas Timedelta

    if HAS_PANDAS and isinstance(value, pd.Timedelta):
        if value is pd.NaT:
            raise ValueError("pandas.NaT is not a valid timedelta")
        return value.to_pytimedelta()

    # - Numpy timedelta64

    if HAS_NUMPY and isinstance(value, np.timedelta64):
        if str(value) == "NaT":
            raise ValueError("numpy.timedelta64('NaT') is not a valid timedelta")

        # Prefer pandas if present for edge units
        if HAS_PANDAS:
            # pd.to_timedelta returns Timedelta; .to_pytimedelta -> datetime.timedelta
            return pd.to_timedelta(value).to_pytimedelta()

        # Fallback: normalize to nanoseconds then build timedelta
        # Works for time-based units. Month/Year are not supported
        # Convert to ns
        try:
            ns = value.astype("timedelta64[ns]").astype("int64")
        except (ValueError, TypeError):
            raise ValueError("Unsupported numpy timedelta64 unit (likely months/years)")

        # Convert ns -> seconds + microseconds precisely
        seconds, nanos_rem = divmod(int(ns), 1_000_000_000)
        microseconds = nanos_rem // 1_000
        return timedelta(
            seconds=seconds,
            microseconds=microseconds,
        )

    # - Numpy numeric scalars

    if HAS_NUMPY and isinstance(value, (np.integer, np.floating)):
        return timedelta(
            seconds=float(value),
        )

    # - Pendulum Duration

    if HAS_PENDULUM and isinstance(value, pendulum.Duration):
        return timedelta(
            seconds=float(value.total_seconds()),
        )

    raise TypeError(f"Cannot convert type {type(value).__name__} to timedelta")


def test():
    assert to_timedelta("2m") == timedelta(
        minutes=2,
    )
    assert to_timedelta("1h30m15s") == timedelta(
        hours=1,
        minutes=30,
        seconds=15,
    )
    assert to_timedelta("2 hours 5 minutes") == timedelta(
        hours=2,
        minutes=5,
    )
    assert to_timedelta(2.5) == timedelta(
        seconds=2.5,
    )

    assert to_timedelta(np.timedelta64(90, "s")) == timedelta(
        seconds=90,
    )
    assert to_timedelta(np.timedelta64(2, "h")) == timedelta(
        hours=2,
    )

    assert to_timedelta(pd.Timedelta("1D")) == timedelta(
        days=1,
    )

    dur = pendulum.duration(
        days=1,
        hours=2,
        minutes=3,
        seconds=4,
    )
    assert to_timedelta(dur) == timedelta(
        days=1,
        hours=2,
        minutes=3,
        seconds=4,
    )


if __name__ == "__main__":
    test()
