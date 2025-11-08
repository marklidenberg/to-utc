# to-utc

Timezones are error-prone. The safest approach is to store and process datetimes in **UTC** consistently.

* `to_utc`: converts any datetime-like value to a UTC-aware `datetime.datetime`
* `to_timedelta`: converts any timedelta-like value to `datetime.timedelta`

```python
def to_utc(value: Union[
    datetime,
    str,
    int,
    float,
    date,
    "pendulum.DateTime" # if pendulum installed
    "pd.Timestamp",   # if pandas installed
    "np.datetime64",  # if numpy installed
    "arrow.Arrow",    # if arrow installed
]) -> datetime: 
    """
      - Numbers are handled as timestamps (try seconds → milliseconds → microseconds)
      - Strings are converted as follows
        1. "now" → current time
        2. Try fixed patterns
          - %Y-%m-%d
          - %Y-%m-%d %H:%M:%S
          - %Y-%m-%dT%H:%M:%S
          - %Y-%m-%dT%H:%M:%SZ
          - %Y-%m-%d %H:%M:%S.%f
          - %Y-%m-%dT%H:%M:%S.%fZ
          - %Y%m%d
          - %Y%m%d%H%M%S
          - %Y-%m-%d %H:%M:%S%z
          - %Y-%m-%dT%H:%M:%S%z
        3. Fallback to dateutil.parser.parse
      - Common datetime-like objects are converted as expected (datetime, date, pd.Timestamp, ...)
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
      1. Parse compact combo (\d+d\d+h\d+m\d+s, e.g. "3d5h12m40s")  
      2. Parse single-unit (\d+[dhms], e.g. "45m"),  
      3. Parse word form ("2 hours 5 minutes", e.g. "1 day 3 hours")
    - Common timedelta-like objects converted appropriately (timedelta, pd.Timedelta, ...)
    """
    pass

...

from to_utc import to_utc, to_timedelta

to_utc("2024-01-01T15:00:00+03:00")  # -> datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
to_utc(1754942420)  # -> datetime(2025, 08, 11, 20, 0, 20, tzinfo=timezone.utc)

to_timedelta(120)    # -> timedelta(minutes=2)
to_timedelta("1h30m15s")    # -> timedelta(hours=1, minutes=30, seconds=15)
```