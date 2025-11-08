from importlib.metadata import version

try:
    __version__ = version("to-utc")
except Exception:
    __version__ = "unknown"

from .to_utc import to_utc
from .to_timedelta import to_timedelta

__all__ = [
    "__version__",
    "to_utc",
    "to_timedelta",
]
