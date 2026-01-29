import json
import os
from datetime import date


OVERRIDES_PATH = os.path.join("docs", "architecture", "LOCKLIST_OVERRIDES.json")


def _load_overrides(repo_root):
    path = os.path.join(repo_root, OVERRIDES_PATH)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return []
    overrides = payload.get("overrides", [])
    if not isinstance(overrides, list):
        return []
    return overrides


def _parse_date(value):
    if not value or not isinstance(value, str):
        return None
    parts = value.split("-")
    if len(parts) != 3:
        return None
    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        return date(year, month, day)
    except ValueError:
        return None


def is_override_active(repo_root, invariant_id, today=None):
    if today is None:
        today = date.today()
    for entry in _load_overrides(repo_root):
        inv = entry.get("invariant")
        if inv != invariant_id:
            continue
        expiry = _parse_date(entry.get("expires"))
        if expiry is None:
            continue
        if expiry >= today:
            return True
    return False
