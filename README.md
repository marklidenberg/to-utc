# to-utc

Timezones are error-prone. The safest approach is to store and process datetimes in **UTC** consistently.

* `to_utc`: `datetime-like` → `datetime.datetime` with UTC timezone

```python
>>> from to_utc import to_utc

>>> to_utc("2024-01-01T15:00:00+03:00")
datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

>>> to_utc(1754942420)
datetime.datetime(2025, 8, 11, 20, 0, 20, tzinfo=datetime.timezone.utc)
```

* `to_naive_utc`: `datetime-like` → naive `datetime.datetime` (assumes UTC)

```python
>>> from to_utc import to_naive_utc

>>> to_naive_utc("2024-01-01T15:00:00+03:00")
datetime.datetime(2024, 1, 1, 12, 0, 0)

>>> to_naive_utc(1754942420)
datetime.datetime(2025, 8, 11, 20, 0, 20)
```

* `now`: current UTC time as UTC-aware `datetime.datetime`

```python
>>> from to_utc import now

>>> now()
datetime.datetime(2025, 11, 10, 14, 30, 45, 123456, tzinfo=datetime.timezone.utc)
```

* `to_timedelta`: `timedelta-like` → `datetime.timedelta`

```python
>>> from to_utc import to_timedelta

>>> to_timedelta(120)
datetime.timedelta(seconds=120)

>>> to_timedelta("1h30m15s")
datetime.timedelta(seconds=5415)
```
