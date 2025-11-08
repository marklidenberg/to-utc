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


def _ensure_naive_utc(
    dt: datetime,
) -> datetime:
    """Return naive datetime in UTC."""
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(
            tzinfo=None,
        )
    return dt


def _from_epoch_like(
    val: int | float,
) -> datetime:
    """Accept seconds, ms, or μs since epoch. Try in that order."""
    for div in (1, 1_000, 1_000_000):
        try:
            return datetime.fromtimestamp(
                float(val) / div,
                tz=timezone.utc,
            ).replace(
                tzinfo=None,
            )
        except Exception:
            continue
    raise Exception(f"Numeric out of bounds for datetime: {val}")


def to_naive_utc(
    value: DatetimeLike,
) -> datetime:
    """Converts any datetime-like value to a naive UTC datetime."""

    # - Pendulum

    if HAS_PENDULUM and isinstance(value, pendulum.DateTime):
        return value.in_timezone(pendulum.UTC).naive()

    # - Builtin datetime/date

    if isinstance(value, datetime):
        return _ensure_naive_utc(value)
    if isinstance(value, date):
        return datetime(
            year=value.year,
            month=value.month,
            day=value.day,
        )

    # - Arrow

    if HAS_ARROW and isinstance(value, arrow.Arrow):
        return value.to("UTC").naive

    # - Pandas.Timestamp

    if HAS_PANDAS and isinstance(value, pd.Timestamp):
        if value.tz is not None:
            return (
                value.tz_convert("UTC")
                .to_pydatetime()
                .replace(
                    tzinfo=None,
                )
            )
        if value is pd.NaT:
            raise Exception("pandas.NaT is not a valid datetime")
        return value.to_pydatetime()  # naive already

    # - Numpy.datetime64

    if HAS_NUMPY and isinstance(value, np.datetime64):
        if str(value) == "NaT":
            raise Exception("numpy.datetime64('NaT') is not a valid datetime")

        # Use pandas for robust conversion if available
        if HAS_PANDAS:
            return (
                pd.to_datetime(
                    value,
                    utc=True,
                )
                .to_pydatetime()
                .replace(
                    tzinfo=None,
                )
            )

        # Fallback via ISO string
        return to_naive_utc(str(value))

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

        # - Now

        if s == "now":
            return datetime.now(timezone.utc).replace(
                tzinfo=None,
            )

        # - Try common patterns first

        for pattern in COMMON_DATETIME_PATTERNS:
            try:
                return _ensure_naive_utc(datetime.strptime(s, pattern))
            except Exception:
                continue

        # - Fallback: dateutil

        try:
            return _ensure_naive_utc(parse_date(s))
        except Exception:
            raise Exception(f"Unknown string datetime format: {value}")

    raise Exception(f"Unknown datetime type: {type(value)!r}")


def test():
    # - Strings

    assert to_naive_utc("2020.01.01") == datetime(2020, 1, 1)
    assert to_naive_utc("2022-09-05T15:00:00") == datetime(2022, 9, 5, 15, 0, 0)
    assert to_naive_utc("2022-09-05T18:00:00+03:00") == datetime(2022, 9, 5, 15, 0, 0)
    assert to_naive_utc("2025-08-11T14:23:45Z") == datetime(2025, 8, 11, 14, 23, 45)
    assert isinstance(to_naive_utc("now"), datetime)

    # - Datetime/date

    aware = datetime(
        2024,
        1,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )
    assert to_naive_utc(aware) == datetime(2024, 1, 1, 12, 0)
    naive = datetime(2024, 1, 1, 12, 0)
    assert to_naive_utc(naive) == naive
    assert to_naive_utc(date(2024, 1, 1)) == datetime(2024, 1, 1)

    # - Pendulum

    pdt = pendulum.datetime(
        2024,
        1,
        1,
        15,
        tz="Europe/Luxembourg",
    )
    assert to_naive_utc(pdt) == datetime(2024, 1, 1, 14, 0)

    # - Epoch numbers

    assert to_naive_utc(1_700_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    ).replace(
        tzinfo=None,
    )
    assert to_naive_utc(1_700_000_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    ).replace(
        tzinfo=None,
    )  # ms
    assert to_naive_utc(1_700_000_000_000_000) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    ).replace(
        tzinfo=None,
    )  # μs

    # - Pandas

    ts_naive = pd.Timestamp(2024, 2, 1, 10, 30, 5)
    assert to_naive_utc(ts_naive) == datetime(2024, 2, 1, 10, 30, 5)
    ts_aware = pd.Timestamp(
        "2024-02-01T10:30:05",
        tz="Europe/Luxembourg",
    )
    assert to_naive_utc(ts_aware) == datetime(2024, 2, 1, 9, 30, 5)
    try:
        to_naive_utc(pd.NaT)  # should raise
        assert False, "Expected exception for pandas.NaT"
    except Exception:
        pass

    # - Numpy

    dt64 = np.datetime64("2024-03-01T12:00:00Z")
    assert to_naive_utc(dt64) == datetime(2024, 3, 1, 12, 0, 0)
    dt64_local = np.datetime64("2024-03-01T12:00:00")  # treated as naive

    # dateutil will treat as naive local then _ensure_naive_utc keeps naive
    assert to_naive_utc(dt64_local) == datetime(2024, 3, 1, 12, 0, 0)
    assert to_naive_utc(np.int64(1_700_000_000)) == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    ).replace(
        tzinfo=None,
    )
    try:
        to_naive_utc(np.datetime64("NaT"))
        assert False, "Expected exception for numpy NaT"
    except Exception:
        pass

    # - Arrow

    arw = arrow.get("2024-04-01T10:00:00+02:00")
    assert to_naive_utc(arw) == datetime(2024, 4, 1, 8, 0, 0)


if __name__ == "__main__":
    test()
