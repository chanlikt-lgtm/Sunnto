"""Per-activity metric computation.

Responsibility: derive meaning from cleaned samples.
Add new metrics here (training load, power zones, cadence zones, …).
Called by core/pipeline.py after processor.py has cleaned the samples.
"""

from ..models.activity import Activity
from ..models.metrics import ActivityMetrics
from ..utils.constants import MAX_VALID_PACE_MIN_KM
from .sport_classifier import classify_sport


def compute_metrics(activity: Activity) -> Activity:
    """
    Populate ActivityMetrics summary fields from cleaned sample data.
    Parser-supplied fields (hr_zones, vo2max, epoc, …) are preserved;
    only None fields are computed here.

    Requires: activity.is_processed == True (core.processor.process() must run first).
    """
    if not activity.is_processed:
        raise RuntimeError(
            f"compute_metrics() requires a processed activity ('{activity.file_id}' is not). "
            "Call core.processor.process() first."
        )
    if not activity.samples:
        return activity

    df = activity.to_dataframe()
    m  = activity.metrics or ActivityMetrics()

    # ── Heart rate ─────────────────────────────────────────────────────────────
    if "hr" in df.columns and df["hr"].notna().any():
        if m.avg_hr is None:
            m.avg_hr = round(float(df["hr"].mean()), 1)
        if m.max_hr is None:
            m.max_hr = round(float(df["hr"].max()), 1)

    # ── Pace ───────────────────────────────────────────────────────────────────
    if "pace" in df.columns and df["pace"].notna().any():
        if m.avg_pace is None:
            valid = df["pace"][(df["pace"] > 0) & (df["pace"] < MAX_VALID_PACE_MIN_KM)]
            m.avg_pace = round(float(valid.mean()), 2) if not valid.empty else None

    # ── Cadence ────────────────────────────────────────────────────────────────
    if "cadence" in df.columns and df["cadence"].notna().any():
        if m.avg_cadence is None:
            m.avg_cadence = round(float(df["cadence"].mean()), 1)

    # ── Temperature ────────────────────────────────────────────────────────────
    if "temperature" in df.columns and df["temperature"].notna().any():
        if m.avg_temp is None:
            m.avg_temp = round(float(df["temperature"].mean()), 1)

    # ── Sport category — set once here, read by views ─────────────────────────
    if activity.sport_category is not None:
        raise RuntimeError(
            f"compute_metrics() called twice on the same activity ('{activity.file_id}'). "
            "It must be called exactly once per activity instance."
        )
    activity.sport_category = classify_sport(activity)

    # ── ADD NEW METRICS BELOW ──────────────────────────────────────────────────
    # Example future metrics:
    #   m.training_load  = compute_training_load(df, m)
    #   m.cadence_zones  = compute_cadence_zones(df)
    #   m.power_zones    = compute_power_zones(df, activity)

    activity.metrics = m
    return activity
