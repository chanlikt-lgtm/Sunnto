"""Pure unit conversion factors and functions.

Contract (enforced in review):
- Functions must be float → float or float → Optional[float] only.
- No pandas, no DataFrames, no imports from services/ or views/.
- No app-specific branching — these are physics/math, not business logic.

Where things live:
- units.py          → conversion factors + pure math functions  (this file)
- constants.py      → domain thresholds, defaults, lookup tables
- datetime_utils.py → time/date parsing and formatting only
"""

# ── Conversion factors ─────────────────────────────────────────────────────────
RAD_TO_DEG = 57.29577951308232   # 180 / π  — lat/lon radians → degrees
HZ_TO_BPM  = 60.0                # Hz → beats per minute  (HR, cadence)
HZ_TO_RPM  = 60.0                # Hz → revolutions per minute (same factor)
K_TO_C     = -273.15             # Kelvin offset → Celsius


# ── Conversion functions ───────────────────────────────────────────────────────

def speed_to_pace(mps: float):
    """Convert speed (m/s) → pace (min/km). Returns None if speed is too low."""
    if mps is None or mps <= 0.05:
        return None
    return round(1000.0 / (mps * 60.0), 2)
