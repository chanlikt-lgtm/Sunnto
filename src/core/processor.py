"""Clean raw Activity samples: interpolate gaps, smooth noise.

Responsibility: mechanical data quality only.
No metric computation — see services/analytics.py.

MUTATION CONTRACT
-----------------
process() mutates Sample objects in-place. This is intentional and safe
under one condition: call it exactly once, immediately after parse, before
the Activity is stored or passed to any other layer.

Call site: core/pipeline.py — right after parse_suunto_json(), before
the activity reaches DashboardController or any service.

If you ever need to:
  - cache pre- and post-processed versions of the same activity, or
  - call process() more than once on the same object,
switch to returning new Sample objects instead of mutating.
"""

import pandas as pd
from ..models.activity import Activity


def process(activity: Activity) -> Activity:
    """
    Smooth and gap-fill sample channels IN-PLACE.

    Mutates: activity.samples[*].hr, .pace, .cadence, .temperature
    Safe to call: once only, immediately after parsing.
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

    # Write cleaned values back to sample objects  ← intentional mutation
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
