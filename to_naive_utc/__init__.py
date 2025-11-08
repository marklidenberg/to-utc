from importlib.metadata import version

try:
    __version__ = version("to-naive-utc")
except Exception:
    __version__ = "unknown"

from .to_naive_utc import to_naive_utc
from .to_timedelta import to_timedelta

__all__ = [
    "__version__",
    "to_naive_utc",
    "to_timedelta",
]
