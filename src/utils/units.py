"""Unit conversion factors and pure conversion functions for Suunto sensor data.

Rules:
- Numeric factors (RAD_TO_DEG, HZ_TO_BPM, …) live here, not in constants.py.
- constants.py is for domain thresholds and defaults, not math factors.
- datetime_utils.py is for time/date formatting only.
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
