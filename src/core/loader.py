"""Scan folder and load raw JSON files."""

import os
import json
import glob
from typing import List, Tuple


def scan_folder(folder: str) -> List[str]:
    """Return sorted list of .json file paths in folder."""
    pattern = os.path.join(folder, "*.json")
    return sorted(glob.glob(pattern))


def load_json(path: str) -> Tuple[str, dict]:
    """
    Load a single Suunto JSON file.
    Returns (file_id, data_dict) or raises on parse error.
    """
    file_id = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "DeviceLog" not in data:
        raise ValueError(f"{path}: missing DeviceLog key")
    return file_id, data
