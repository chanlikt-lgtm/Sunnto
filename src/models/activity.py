"""Activity domain model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import pandas as pd

from .sample import Sample
from .metrics import ActivityMetrics
from ..utils.constants import ACTIVITY_TYPES


@dataclass
class Activity:
    file_id: str                        # stem of source filename
    start_time: datetime
    activity_type_id: int
    duration_s: float
    distance_m: float
    ascent_m: float
    descent_m: float
    device_name: str

    samples: List[Sample] = field(default_factory=list)
    metrics: Optional[ActivityMetrics] = None

    # ── Convenience properties ─────────────────────────────────────────────────

    @property
    def sport(self) -> str:
        base = ACTIVITY_TYPES.get(self.activity_type_id, f"Sport {self.activity_type_id}")
        # Refine Walking ↔ Running → Jogging by pace (requires metrics to be set)
        if self.metrics and self.metrics.avg_pace:
            pace = self.metrics.avg_pace
            if base == "Walking" and pace < 7.0:    # faster than 7 min/km → jogging
                return "Jogging"
            if base == "Running" and pace >= 7.0:   # slower than 7 min/km → jogging
                return "Jogging"
        return base

    @property
    def sport_category(self) -> str:
        """GUI rendering category: 'endurance', 'swimming', 'gym', or 'sleep'."""
        from ..utils.sport_classifier import classify_sport
        return classify_sport(self)

    @property
    def distance_km(self) -> float:
        return round(self.distance_m / 1000, 2)

    @property
    def duration_min(self) -> float:
        return round(self.duration_s / 60, 1)

    @property
    def date_str(self) -> str:
        return self.start_time.strftime("%Y-%m-%d")

    @property
    def label(self) -> str:
        return f"{self.date_str}  {self.sport}  {self.distance_km} km"

    # ── DataFrame helper ───────────────────────────────────────────────────────

    def to_dataframe(self) -> pd.DataFrame:
        if not self.samples:
            return pd.DataFrame()
        return pd.DataFrame([vars(s) for s in self.samples])

    def has_gps(self) -> bool:
        return any(s.lat is not None for s in self.samples)

    def has_hr(self) -> bool:
        return any(s.hr is not None for s in self.samples)
