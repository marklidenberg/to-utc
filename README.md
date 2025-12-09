# to-utc

Timezones are error-prone. The safest approach is to store and process datetimes in **UTC** consistently.

```python
def to_utc(value) -> datetime:
    """Converts any datetime-like value to a UTC-aware datetime."""
    ...

def to_naive_utc(value) -> datetime:
    """Converts any datetime-like value to a naive UTC datetime."""

def now() -> datetime:
    """Returns the current UTC time as a UTC-aware datetime."""

def to_timedelta(value) -> timedelta:
    """Converts any timedelta-like value to datetime.timedelta."""
```

## API Reference

```python
def to_utc(value: Union[
    datetime,
    str,
    int,
    float,
    date,
    "pendulum.DateTime", # if pendulum installed
    "pd.Timestamp",      # if pandas installed
    "np.datetime64",     # if numpy installed
    "arrow.Arrow",       # if arrow installed
]) -> datetime:
    """
    Converts any datetime-like value to a UTC-aware datetime.

      - Numbers are handled as timestamps (try seconds → milliseconds → microseconds)
      - Strings are converted as follows:
        1. Try fixed patterns first: ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", ...)
        2. Fallback to dateutil.parser.parse
      - Common datetime-like objects are converted as expected (datetime, date, pd.Timestamp, ...)
      - Naive datetimes are assumed to be UTC
      - Aware datetimes are converted to UTC
    """
    pass

def to_naive_utc(value: DatetimeLike) -> datetime:
    """
    Converts any datetime-like value to a naive UTC datetime.

    This is a convenience wrapper around to_utc() that strips timezone information.
    """
    pass

def now() -> datetime:
    """
    Returns the current UTC time as a UTC-aware datetime.
    """
    pass

...

def to_timedelta(value: Union[
    list,
    int,
    float,
    str,
    timedelta,
    "pd.Timedelta",   # if pandas installed
    "np.timedelta64", # if numpy installed
    "pendulum.Duration", # if pendulum installed
]) -> timedelta:
    """
    - Numbers: interpreted as seconds.
    - Strings are converted as follows:
      1. Parse compact format (\d+d\d+h\d+m\d+s, e.g. "3d5h12m40s")
      2. Parse word form ("2 hours 5 minutes", e.g. "1 day 3 hours")
    - Common timedelta-like objects converted appropriately (timedelta, pd.Timedelta, ...)
    """
    pass
```
