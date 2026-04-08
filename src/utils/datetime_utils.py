"""Date/time helper utilities."""

from datetime import datetime, timedelta, timezone
import re


def parse_iso(s: str) -> datetime:
    """Parse ISO-8601 string including offset notation (+08:00)."""
    if s is None:
        return None
    # Python 3.6 fromisoformat doesn't handle offset, so normalise first
    s = re.sub(r"(\d{2}:\d{2}:\d{2}\.\d+)([+-]\d{2}:\d{2})$",
               lambda m: m.group(1) + m.group(2).replace(":", ""), s)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def to_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc)


def format_duration(seconds: float) -> str:
    """Format seconds as H:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "--"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_pace(min_per_km: float) -> str:
    """Format decimal min/km as M:SS /km."""
    if min_per_km is None or min_per_km <= 0 or min_per_km > 59:
        return "--"
    m = int(min_per_km)
    s = int((min_per_km - m) * 60)
    return f"{m}:{s:02d}"


def date_range_bounds(preset: str):
    """Return (start, end) datetime for a preset string like '7d'."""
    now = datetime.now(timezone.utc)
    if preset == "all":
        return None, None
    days = int(preset.rstrip("d"))
    return now - timedelta(days=days), now
