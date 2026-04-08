"""Clean raw Activity samples: interpolate gaps, smooth noise.

Responsibility: mechanical data quality only.
No metric computation — see services/analytics.py.
"""

import pandas as pd
from ..models.activity import Activity


def process(activity: Activity) -> Activity:
    """
    Smooth and gap-fill sample channels in-place.
    Returns the same activity with cleaned samples.
    """
    if not activity.samples:
        return activity

    df = activity.to_dataframe()

    # Rolling 10-sample smoothing for noisy sensor channels
    for col in ("hr", "pace", "cadence", "temperature"):
        if col in df.columns and df[col].notna().any():
            df[col] = (
                df[col]
                .interpolate(limit_direction="both")
                .rolling(10, center=True, min_periods=1)
                .mean()
                .round(1)
            )

    # Write cleaned values back to sample objects
    for i, s in enumerate(activity.samples):
        row = df.iloc[i]
        s.hr          = _safe(row.get("hr"))
        s.pace        = _safe(row.get("pace"))
        s.cadence     = _safe(row.get("cadence"))
        s.temperature = _safe(row.get("temperature"))

    return activity


def _safe(val):
    if val is None:
        return None
    try:
        f = float(val)
        return None if (f != f) else round(f, 1)   # NaN → None
    except (TypeError, ValueError):
        return None
