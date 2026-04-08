"""Per-second data point model."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Sample:
    time_s: float                  # seconds from activity start
    hr: Optional[float] = None     # bpm
    speed: Optional[float] = None  # m/s
    pace: Optional[float] = None   # min/km
    altitude: Optional[float] = None   # metres
    cadence: Optional[float] = None    # steps/min
    temperature: Optional[float] = None  # Celsius
    distance: Optional[float] = None   # cumulative metres
    lat: Optional[float] = None    # degrees
    lon: Optional[float] = None    # degrees
    power: Optional[float] = None  # watts
    vertical_speed: Optional[float] = None  # m/s
