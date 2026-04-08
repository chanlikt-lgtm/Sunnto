"""Derived metrics computed from raw samples."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class HrZones:
    z1_s: float = 0.0
    z2_s: float = 0.0
    z3_s: float = 0.0
    z4_s: float = 0.0
    z5_s: float = 0.0
    # Lower boundary of each zone in bpm (None = unknown)
    z2_bpm: Optional[float] = None
    z3_bpm: Optional[float] = None
    z4_bpm: Optional[float] = None
    z5_bpm: Optional[float] = None

    def total_s(self) -> float:
        return self.z1_s + self.z2_s + self.z3_s + self.z4_s + self.z5_s

    def thresholds_bpm(self):
        """Return [z2, z3, z4, z5] bpm thresholds (may contain None)."""
        return [self.z2_bpm, self.z3_bpm, self.z4_bpm, self.z5_bpm]


@dataclass
class Lap:
    index: int
    distance_m: float
    duration_s: float
    avg_hr: Optional[float] = None
    avg_pace: Optional[float] = None   # min/km
    ascent_m: Optional[float] = None


@dataclass
class ActivityMetrics:
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    avg_pace: Optional[float] = None     # min/km
    avg_speed: Optional[float] = None    # m/s
    max_speed: Optional[float] = None    # m/s
    avg_cadence: Optional[float] = None
    avg_temp: Optional[float] = None
    avg_power: Optional[float] = None
    hr_zones: Optional[HrZones] = None
    laps: Optional[List[Lap]] = None
    epoc: Optional[float] = None
    vo2max: Optional[float] = None
    recovery_h: Optional[float] = None
    calories: Optional[int] = None
    peak_training_effect: Optional[float] = None
    fitness_age: Optional[int] = None
    step_count: Optional[int] = None
