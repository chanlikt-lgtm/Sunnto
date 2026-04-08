"""Transform activity data for chart/map consumption."""

import pandas as pd
from ..models.activity import Activity
from ..utils.datetime_utils import format_pace


def chart_dataframe(activity: Activity) -> pd.DataFrame:
    """Return a clean DataFrame ready for plotting."""
    df = activity.to_dataframe()
    if df.empty:
        return df

    # Minutes axis
    df["min"] = df["time_s"] / 60.0

    # Remove outlier pace values (> 30 min/km = walking in place)
    if "pace" in df.columns:
        df.loc[df["pace"] > 30, "pace"] = None

    return df


def gps_track(activity: Activity):
    """Return [(lat, lon), ...] list of GPS coordinates."""
    return [
        (s.lat, s.lon)
        for s in activity.samples
        if s.lat is not None and s.lon is not None
    ]


def lap_table(activity: Activity) -> list:
    """Return lap data as list of dicts for Dash DataTable."""
    if not activity.metrics or not activity.metrics.laps:
        return []
    rows = []
    for lap in activity.metrics.laps:
        rows.append({
            "Lap":      lap.index,
            "Dist m":   round(lap.distance_m, 0),
            "Time":     _fmt_dur(lap.duration_s),
            "Avg HR":   round(lap.avg_hr, 0) if lap.avg_hr else "--",
            "Avg Pace": format_pace(lap.avg_pace),
            "Ascent m": round(lap.ascent_m, 1) if lap.ascent_m else "--",
        })
    return rows


def _fmt_dur(s):
    if not s:
        return "--"
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"
