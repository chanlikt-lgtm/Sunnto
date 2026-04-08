"""Cross-activity analytics (totals, trends, summaries)."""

from typing import List, Dict
from ..models.activity import Activity
from ..utils.datetime_utils import format_pace, format_duration


def weekly_summary(activities: List[Activity]) -> List[Dict]:
    """Aggregate activities into ISO week buckets."""
    from collections import defaultdict
    buckets = defaultdict(lambda: {"count": 0, "distance_km": 0.0,
                                    "duration_min": 0.0, "calories": 0})
    for a in activities:
        if a.start_time is None:
            continue
        key = a.start_time.strftime("%Y-W%W")
        buckets[key]["count"]       += 1
        buckets[key]["distance_km"] += a.distance_km
        buckets[key]["duration_min"] += a.duration_min
        if a.metrics and a.metrics.calories:
            buckets[key]["calories"] += a.metrics.calories
    return [{"week": k, **v} for k, v in sorted(buckets.items())]


def sport_breakdown(activities: List[Activity]) -> Dict[str, int]:
    """Count activities per sport type."""
    from collections import Counter
    return dict(Counter(a.sport for a in activities))


def activity_table_rows(activities: List[Activity]) -> List[Dict]:
    """Flatten activities to table-friendly dicts."""
    rows = []
    for a in activities:
        m = a.metrics or {}
        rows.append({
            "Date":     a.date_str,
            "Sport":    a.sport,
            "Dist km":  a.distance_km,
            "Time":     format_duration(a.duration_s),
            "Avg HR":   getattr(m, "avg_hr", None),
            "Avg Pace": format_pace(getattr(m, "avg_pace", None)),
            "Ascent m": a.ascent_m,
            "Calories": getattr(m, "calories", None),
            "EPOC":     getattr(m, "epoc", None),
            "VO2max":   getattr(m, "vo2max", None),
            "Recovery h": getattr(m, "recovery_h", None),
            "Device":   a.device_name,
        })
    return rows
