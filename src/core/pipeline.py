"""Orchestrate load -> parse -> process for all JSON files."""

import os
from typing import List, Optional
from .loader import scan_folder, load_json
from .parser import parse_suunto_json
from .processor import process
from ..services.analytics import compute_metrics
from ..models.activity import Activity


def load_all(folder: str) -> List[Activity]:
    """
    Scan folder, parse and process every JSON file.
    Skips files that fail with a printed warning.
    Returns list sorted newest-first.
    """
    paths = scan_folder(folder)
    if not paths:
        print(f"[pipeline] No JSON files found in: {folder}")
        return []

    activities = []
    for path in paths:
        try:
            file_id, data = load_json(path)
            act = parse_suunto_json(data, file_id)
            act = process(act)          # clean: smooth, gap-fill
            act = compute_metrics(act)  # summarise: avg HR, pace, temp, …
            activities.append(act)
            print(f"[pipeline] Loaded: {act.label}")
        except Exception as e:
            print(f"[pipeline] SKIP {os.path.basename(path)}: {e}")

    # Sort newest first
    activities.sort(key=lambda a: a.start_time or 0, reverse=True)
    return activities


def load_one(path: str) -> Optional[Activity]:
    """Load and process a single file."""
    try:
        file_id, data = load_json(path)
        act = parse_suunto_json(data, file_id)
        act = process(act)
        return compute_metrics(act)
    except Exception as e:
        print(f"[pipeline] Error loading {path}: {e}")
        return None
