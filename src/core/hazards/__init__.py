"""Deterministic core hazard helpers."""

from .hazard_engine import (
    HazardError,
    accumulate_hazard,
    hazard_triggered,
    normalize_hazard_model,
)

__all__ = [
    "HazardError",
    "accumulate_hazard",
    "hazard_triggered",
    "normalize_hazard_model",
]

