"""Hardware profile capture and normalization for PerformX."""

from __future__ import annotations

import os
import platform
from typing import Any, Dict


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _memory_bytes() -> int:
    if hasattr(os, "sysconf"):
        names = ("SC_PAGE_SIZE", "SC_PHYS_PAGES")
        if all(name in os.sysconf_names for name in names):
            try:
                return int(os.sysconf("SC_PAGE_SIZE")) * int(os.sysconf("SC_PHYS_PAGES"))
            except (OSError, ValueError):
                return 0
    return 0


def _cpu_class(cpu_count: int) -> str:
    if cpu_count <= 0:
        return "unknown"
    if cpu_count <= 4:
        return "entry"
    if cpu_count <= 8:
        return "mainstream"
    return "high"


def capture_hardware_profile() -> Dict[str, Any]:
    cpu_count = _safe_int(os.cpu_count(), 0)
    return {
        "cpu_model": str(platform.processor() or platform.machine() or "unknown").strip() or "unknown",
        "cpu_count": cpu_count,
        "cpu_class": _cpu_class(cpu_count),
        "memory_bytes": _memory_bytes(),
        "os": str(platform.system() or "unknown").strip().lower(),
        "arch": str(platform.machine() or "unknown").strip().lower(),
    }


def select_profile(profile_registry_payload: Dict[str, Any], hardware: Dict[str, Any]) -> Dict[str, Any]:
    profiles = profile_registry_payload.get("record", {}).get("profiles", [])
    if not isinstance(profiles, list):
        return {"profile_id": "profile.default", "cpu_class": "unknown", "normalization_factor": 1.0}
    cpu_class = str(hardware.get("cpu_class", "unknown")).strip()
    fallback = None
    for row in profiles:
        if not isinstance(row, dict):
            continue
        if fallback is None:
            fallback = row
        if str(row.get("cpu_class", "")).strip() == cpu_class:
            return row
    if isinstance(fallback, dict):
        return fallback
    return {"profile_id": "profile.default", "cpu_class": "unknown", "normalization_factor": 1.0}


def normalize_value(raw_value: float, normalization_factor: float) -> float:
    if normalization_factor <= 0.0:
        return float(raw_value)
    return float(raw_value) / float(normalization_factor)

