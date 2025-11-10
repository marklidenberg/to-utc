from __future__ import annotations  # delay type hint evaluation

from datetime import date, datetime, timezone
from typing import Union
import numbers
from dateutil.parser import parse as parse_date

try:
    import pendulum

    HAS_PENDULUM = True
except ImportError:
    HAS_PENDULUM = False

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
    import arrow

    HAS_ARROW = True
except ImportError:
    HAS_ARROW = False


COMMON_DATETIME_PATTERNS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y%m%d",
    "%Y%m%d%H%M%S",
    "%Y-%m-%d %H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S%z",
]


DatetimeLike = Union[
    datetime,
    str,
    int,
    float,
    date,
    # Optional libs (kept as Any to avoid hard deps in type hints)
    "pendulum.DateTime",  # if pendulum installed
    "pd.Timestamp",  # if pandas available
    "np.datetime64",  # if numpy available
    "arrow.Arrow",  # if arrow available
]


def _ensure_utc(
    dt: datetime,
) -> datetime:
    """Return UTC-aware datetime."""
    if dt.tzinfo:
        return dt.astimezone(timezone.utc)
    else:
        return dt.replace(tzinfo=timezone.utc)


def _from_epoch_like(
    val: int | float,
) -> datetime:
    """Accept seconds, ms, or μs since epoch. Try in that order."""
    for div in (1, 1_000, 1_000_000):
        try:
            return datetime.fromtimestamp(
                float(val) / div,
                tz=timezone.utc,
            )
        except (ValueError, OSError, OverflowError):
            continue
    raise ValueError(
        f"Numeric value {val} is out of valid datetime range "
        f"(tried as seconds, milliseconds, and microseconds)"
    )


def to_utc(
    value: DatetimeLike,
) -> datetime:
    """Converts any datetime-like value to a UTC-aware datetime."""

    # - Pendulum

    if HAS_PENDULUM and isinstance(value, pendulum.DateTime):
        # Convert to stdlib datetime with timezone.utc
        return _ensure_utc(value.in_timezone("UTC"))

    # - Builtin datetime/date

    if isinstance(value, datetime):
        return _ensure_utc(value)
    if isinstance(value, date):
        return datetime(
            year=value.year,
            month=value.month,
            day=value.day,
            tzinfo=timezone.utc,
        )

    # - Arrow

    if HAS_ARROW and isinstance(value, arrow.Arrow):
        # Arrow's .to("UTC").datetime already returns timezone-aware datetime
        return _ensure_utc(value.to("UTC").datetime)

    # - Pandas.Timestamp

    if HAS_PANDAS and isinstance(value, pd.Timestamp):
        if value.tz is not None:
            return value.tz_convert("UTC").to_pydatetime()
        if value is pd.NaT:
            raise ValueError("pandas.NaT is not a valid datetime")
        return value.to_pydatetime().replace(tzinfo=timezone.utc)  # naive, add UTC

    # - Numpy.datetime64

    if HAS_NUMPY and isinstance(value, np.datetime64):
        if str(value) == "NaT":
            raise ValueError("numpy.datetime64('NaT') is not a valid datetime")

        # Use pandas for robust conversion if available
        if HAS_PANDAS:
            return pd.to_datetime(
                value,
                utc=True,
            ).to_pydatetime()

        # Fallback via ISO string
        return to_utc(str(value))

    # - Numpy scalar integers/floats (epoch)

    if HAS_NUMPY and isinstance(value, (np.integer, np.floating)):
        return _from_epoch_like(float(value))

    # - Plain numbers

    if isinstance(value, numbers.Real):
        return _from_epoch_like(float(value))

    # - Strings

    if isinstance(value, str):
        # - Lower

        s = value.strip().lower()

        # - Try common patterns first

        for pattern in COMMON_DATETIME_PATTERNS:
            try:
                return _ensure_utc(datetime.strptime(s, pattern))
            except Exception:
                continue

        # - Fallback: dateutil

        try:
            return _ensure_utc(parse_date(s))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Unable to parse datetime string: {value}") from e

    raise TypeError(f"Cannot convert type {type(value).__name__} to datetime")


def test():
    # - Strings

    assert to_utc("2020.01.01") == datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert to_utc("2022-09-05T15:00:00") == datetime(
        2022, 9, 5, 15, 0, 0, tzinfo=timezone.utc
    )
    assert to_utc("2022-09-05T18:00:00+03:00") == datetime(
        2022, 9, 5, 15, 0, 0, tzinfo=timezone.utc
    )
    assert to_utc("2025-08-11T14:23:45Z") == datetime(
        2025, 8, 11, 14, 23, 45, tzinfo=timezone.utc
    )

    # - Datetime/date

    aware = datetime(
        2024,
        1,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )
    assert to_utc(aware) == datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    naive = datetime(2024, 1, 1, 12, 0)
    assert to_utc(naive) == datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert to_utc(date(2024, 1, 1)) == datetime(2024, 1, 1, tzinfo=timezone.utc)

    # - Pendulum

    pdt = pendulum.datetime(
        2024,
        1,
        1,
        15,
        tz="Europe/Luxembourg",
    )
    assert to_utc(pdt) == datetime(2024, 1, 1, 14, 0, tzinfo=timezone.utc)

    # - Epoch numbers

    assert to_utc(1_700_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    )
    assert to_utc(1_700_000_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    )  # ms
    assert to_utc(1_700_000_000_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    )  # μs

    # - Pandas

    ts_naive = pd.Timestamp(2024, 2, 1, 10, 30, 5)
    assert to_utc(ts_naive) == datetime(2024, 2, 1, 10, 30, 5, tzinfo=timezone.utc)
    ts_aware = pd.Timestamp(
        "2024-02-01T10:30:05",
        tz="Europe/Luxembourg",
    )
    assert to_utc(ts_aware) == datetime(2024, 2, 1, 9, 30, 5, tzinfo=timezone.utc)
    try:
        to_utc(pd.NaT)  # should raise
        assert False, "Expected exception for pandas.NaT"
    except Exception:
        pass

    # - Numpy

    dt64 = np.datetime64("2024-03-01T12:00:00")
    assert to_utc(dt64) == datetime(2024, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    dt64_local = np.datetime64("2024-03-01T12:00:00")  # treated as naive

    # dateutil will treat as naive local then _ensure_utc adds UTC
    assert to_utc(dt64_local) == datetime(2024, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert to_utc(np.int64(1_700_000_000)) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    )
    try:
        to_utc(np.datetime64("NaT"))
        assert False, "Expected exception for numpy NaT"
    except Exception:
        pass

    # - Arrow

    arw = arrow.get("2024-04-01T10:00:00+02:00")
    assert to_utc(arw) == datetime(2024, 4, 1, 8, 0, 0, tzinfo=timezone.utc)


if __name__ == "__main__":
    test()
