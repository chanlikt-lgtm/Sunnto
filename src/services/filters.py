"""Filter a list of activities by date, sport type, etc."""

from datetime import datetime, timezone
from typing import List, Optional
from ..models.activity import Activity
from ..utils.datetime_utils import date_range_bounds


def by_date_preset(activities: List[Activity], preset: str) -> List[Activity]:
    """Filter using a preset like '7d', '30d', 'all'."""
    if preset == "all":
        return activities
    start, end = date_range_bounds(preset)
    return [a for a in activities if _in_range(a.start_time, start, end)]


def by_date_range(activities: List[Activity],
                  start: Optional[datetime],
                  end: Optional[datetime]) -> List[Activity]:
    if start is None and end is None:
        return activities
    return [a for a in activities if _in_range(a.start_time, start, end)]


def by_sport(activities: List[Activity], sports: List[str]) -> List[Activity]:
    if not sports:
        return activities
    return [a for a in activities if a.sport in sports]


def _in_range(dt: datetime, start: Optional[datetime], end: Optional[datetime]) -> bool:
    if dt is None:
        return False
    # Make aware if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if start and dt < start:
        return False
    if end and dt > end:
        return False
    return True
