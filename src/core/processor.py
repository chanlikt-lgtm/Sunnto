"""Post-process a parsed Activity: fill gaps, compute rolling stats."""

import pandas as pd
import numpy as np
from ..models.activity import Activity
from ..models.metrics import ActivityMetrics


def process(activity: Activity) -> Activity:
    """
    Enrich activity samples with rolling averages and fill forward.
    Modifies in-place and returns the activity.
    """
    if not activity.samples:
        return activity

    df = activity.to_dataframe()

    # Rolling 10-sample smoothing for noisy channels
    for col in ("hr", "pace", "cadence", "temperature"):
        if col in df.columns and df[col].notna().any():
            df[col] = df[col].interpolate(limit_direction="both").rolling(
                10, center=True, min_periods=1
            ).mean().round(1)

    # Write smoothed values back to samples
    for i, s in enumerate(activity.samples):
        row = df.iloc[i]
        s.hr          = _safe(row.get("hr"))
        s.pace        = _safe(row.get("pace"))
        s.cadence     = _safe(row.get("cadence"))
        s.temperature = _safe(row.get("temperature"))

    # Compute summary metrics if not set
    m = activity.metrics or ActivityMetrics()
    if m.avg_hr is None and df["hr"].notna().any():
        m.avg_hr  = round(float(df["hr"].mean()), 1)
        m.max_hr  = round(float(df["hr"].max()), 1)
    if m.avg_pace is None and df["pace"].notna().any():
        valid = df["pace"][(df["pace"] > 0) & (df["pace"] < 30)]
        m.avg_pace = round(float(valid.mean()), 2) if not valid.empty else None
    if m.avg_cadence is None and df["cadence"].notna().any():
        m.avg_cadence = round(float(df["cadence"].mean()), 1)
    if m.avg_temp is None and df["temperature"].notna().any():
        m.avg_temp = round(float(df["temperature"].mean()), 1)
    activity.metrics = m

    return activity


def _safe(val):
    if val is None:
        return None
    try:
        f = float(val)
        return None if (f != f) else round(f, 1)   # NaN check
    except (TypeError, ValueError):
        return None
