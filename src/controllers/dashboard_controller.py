"""Central state controller — loads data and answers queries."""

from typing import List, Optional
import yaml
import os

from ..core.pipeline import load_all
from ..models.activity import Activity
from ..services.analytics import compute_metrics
from ..services.filters import by_date_preset, by_sport


class DashboardController:
    def __init__(self, config_path: str = None):
        self._config = _load_config(config_path)
        self._all_activities: List[Activity] = []
        self._loaded = False

    # ── Data loading ───────────────────────────────────────────────────────────

    def ensure_loaded(self):
        if not self._loaded:
            folder = self._config["data"]["json_folder"]
            activities = load_all(folder)                        # load + parse + clean
            self._all_activities = [compute_metrics(a) for a in activities]  # summarise
            self._loaded = True

    def reload(self):
        self._loaded = False
        self.ensure_loaded()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_activity_options(self) -> List[dict]:
        """Return [{label, value}, ...] for the activity dropdown."""
        self.ensure_loaded()
        return [{"label": a.label, "value": a.file_id}
                for a in self._all_activities]

    def get_activity(self, file_id: str) -> Optional[Activity]:
        self.ensure_loaded()
        return next((a for a in self._all_activities if a.file_id == file_id), None)

    def get_filtered(self, date_preset: str = "all",
                     sports: List[str] = None) -> List[Activity]:
        self.ensure_loaded()
        acts = by_date_preset(self._all_activities, date_preset)
        if sports:
            acts = by_sport(acts, sports)
        return acts

    def get_sport_options(self) -> List[dict]:
        self.ensure_loaded()
        sports = sorted({a.sport for a in self._all_activities})
        return [{"label": s, "value": s} for s in sports]

    def get_latest(self) -> Optional[Activity]:
        self.ensure_loaded()
        return self._all_activities[0] if self._all_activities else None

    @property
    def config(self):
        return self._config


def _load_config(path: str = None) -> dict:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    path = os.path.abspath(path)
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f)
    # Defaults
    return {"data": {"json_folder": "E:/claude/suunto/JSON"},
            "app":  {"title": "Fitness Dashboard", "port": 8050, "debug": True}}
