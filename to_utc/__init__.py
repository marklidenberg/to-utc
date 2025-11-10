from importlib.metadata import version

try:
    __version__ = version("to-utc")
except (ImportError, Exception):
    __version__ = "unknown"

from .to_utc import to_utc
from .to_naive_utc import to_naive_utc
from .to_timedelta import to_timedelta
from .now import now

__all__ = [
    "__version__",
    "to_utc",
    "to_naive_utc",
    "to_timedelta",
    "now",
]
