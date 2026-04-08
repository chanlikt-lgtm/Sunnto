"""Parse Suunto proprietary JSON format into domain models."""

import math
from typing import Dict, Any, List

from ..models.sample import Sample
from ..models.metrics import ActivityMetrics, HrZones, Lap
from ..utils.units import RAD_TO_DEG, HZ_TO_BPM, HZ_TO_RPM, K_TO_C, speed_to_pace
from ..utils.datetime_utils import parse_iso


def parse_suunto_json(data: Dict[str, Any], file_id: str):
    """
    Parse a loaded Suunto JSON dict into an Activity.
    Returns Activity instance (import deferred to avoid circular deps).
    """
    from ..models.activity import Activity

    dl     = data["DeviceLog"]
    header = dl["Header"]
    raw_samples = dl.get("Samples", [])
    windows     = dl.get("Windows", [])

    start_time = parse_iso(header.get("DateTime"))
    device_info = header.get("Device") or {}
    device_name = device_info.get("Name") or "Suunto"

    samples = _parse_samples(raw_samples, start_time)
    metrics = _parse_metrics(header, windows)

    from ..models.activity import Activity
    return Activity(
        file_id=file_id,
        start_time=start_time,
        activity_type_id=header.get("ActivityType") or 0,
        duration_s=header.get("Duration") or 0.0,
        distance_m=header.get("Distance") or 0.0,
        ascent_m=header.get("Ascent") or 0.0,
        descent_m=header.get("Descent") or 0.0,
        device_name=device_name,
        samples=samples,
        metrics=metrics,
    )


# ── Sample parsing ─────────────────────────────────────────────────────────────

def _parse_samples(raw: list, start_time) -> List[Sample]:
    """
    Convert flat Suunto sample list into Sample objects.
    Suunto emits one key per sample — carry last known value forward.
    """
    last = {}   # accumulator
    samples = []

    t0 = None
    for entry in raw:
        ts = parse_iso(entry.get("TimeISO8601"))
        if ts is None:
            continue
        if t0 is None:
            t0 = ts
        time_s = (ts - t0).total_seconds()

        # Update accumulator with present keys
        if "HR" in entry and entry["HR"] is not None:
            last["hr"] = round(entry["HR"] * HZ_TO_BPM, 1)

        if "Speed" in entry and entry["Speed"] is not None:
            v = entry["Speed"]
            last["speed"] = round(v, 3)
            last["pace"]  = speed_to_pace(v)

        if "Altitude" in entry and entry["Altitude"] is not None:
            last["altitude"] = round(entry["Altitude"], 1)

        if "Cadence" in entry and entry["Cadence"] is not None:
            last["cadence"] = round(entry["Cadence"] * HZ_TO_RPM, 1)

        if "Temperature" in entry and entry["Temperature"] is not None:
            last["temperature"] = round(entry["Temperature"] + K_TO_C, 1)

        if "Distance" in entry and entry["Distance"] is not None:
            last["distance"] = entry["Distance"]

        if "Latitude" in entry and entry["Latitude"] is not None:
            last["lat"] = round(entry["Latitude"] * RAD_TO_DEG, 6)
            last["lon"] = round(entry["Longitude"] * RAD_TO_DEG, 6)

        if "Power" in entry and entry["Power"] is not None:
            last["power"] = entry["Power"]

        if "VerticalSpeed" in entry and entry["VerticalSpeed"] is not None:
            last["vertical_speed"] = round(entry["VerticalSpeed"], 3)

        # Only emit a sample when we have at least one meaningful field
        if len(last) > 0:
            samples.append(Sample(
                time_s=round(time_s, 1),
                hr=last.get("hr"),
                speed=last.get("speed"),
                pace=last.get("pace"),
                altitude=last.get("altitude"),
                cadence=last.get("cadence"),
                temperature=last.get("temperature"),
                distance=last.get("distance"),
                lat=last.get("lat"),
                lon=last.get("lon"),
                power=last.get("power"),
                vertical_speed=last.get("vertical_speed"),
            ))

    return samples


# ── Metrics parsing ────────────────────────────────────────────────────────────

def _parse_metrics(header: dict, windows: list) -> ActivityMetrics:
    hz_raw = header.get("HrZones") or {}
    def _hz_to_bpm(v):
        return round(v * HZ_TO_BPM, 0) if v else None

    hr_zones = HrZones(
        z1_s=hz_raw.get("Zone1Duration") or 0.0,
        z2_s=hz_raw.get("Zone2Duration") or 0.0,
        z3_s=hz_raw.get("Zone3Duration") or 0.0,
        z4_s=hz_raw.get("Zone4Duration") or 0.0,
        z5_s=hz_raw.get("Zone5Duration") or 0.0,
        z2_bpm=_hz_to_bpm(hz_raw.get("Zone2LowerLimit")),
        z3_bpm=_hz_to_bpm(hz_raw.get("Zone3LowerLimit")),
        z4_bpm=_hz_to_bpm(hz_raw.get("Zone4LowerLimit")),
        z5_bpm=_hz_to_bpm(hz_raw.get("Zone5LowerLimit")),
    )

    laps = []
    for i, w in enumerate(windows):
        win = w.get("Window") or {}
        dist = win.get("Distance") or 0
        dur  = win.get("Duration") or 0
        cad_list = win.get("Cadence") or [{}]
        hr_list  = win.get("HR") or [{}]
        avg_hr   = (hr_list[0].get("Avg") or 0) * HZ_TO_BPM if hr_list else None
        avg_spd_list = win.get("Speed") or [{}]
        avg_spd  = avg_spd_list[0].get("Avg") if avg_spd_list else None
        avg_pace = speed_to_pace(avg_spd)
        laps.append(Lap(
            index=i + 1,
            distance_m=dist,
            duration_s=dur,
            avg_hr=round(avg_hr, 1) if avg_hr else None,
            avg_pace=avg_pace,
            ascent_m=win.get("Ascent"),
        ))

    energy_j = header.get("Energy") or 0
    recovery_s = header.get("RecoveryTime") or 0

    return ActivityMetrics(
        hr_zones=hr_zones,
        laps=laps,
        epoc=header.get("EPOC"),
        vo2max=header.get("MAXVO2"),
        recovery_h=round(recovery_s / 3600, 1) if recovery_s else None,
        calories=round(energy_j / 4184) if energy_j else None,
        peak_training_effect=header.get("PeakTrainingEffect"),
        fitness_age=header.get("FitnessAge"),
        step_count=header.get("StepCount"),
    )
