"""NUMERIC-DISCIPLINE-0 shared TestX helpers."""

from __future__ import annotations

from astro.illumination.illumination_geometry_engine import (
    cos_permille_from_angle_mdeg,
    sin_permille_from_angle_mdeg,
)
from meta.numeric import (
    ROUND_HALF_TO_EVEN,
    deterministic_divide,
    deterministic_mul_div,
)
from tools.audit.arch_audit_common import scan_float_in_truth
from tools.xstack.compatx.canonical_json import canonical_sha256


def numeric_ops_payload() -> dict:
    return {
        "divide": {
            "5_over_2": deterministic_divide(5, 2, rounding_mode=ROUND_HALF_TO_EVEN),
            "7_over_2": deterministic_divide(7, 2, rounding_mode=ROUND_HALF_TO_EVEN),
            "minus_7_over_2": deterministic_divide(-7, 2, rounding_mode=ROUND_HALF_TO_EVEN),
        },
        "mul_div": {
            "5_times_3_over_2": deterministic_mul_div(5, 3, 2, rounding_mode=ROUND_HALF_TO_EVEN),
            "11_times_7_over_3": deterministic_mul_div(11, 7, 3, rounding_mode=ROUND_HALF_TO_EVEN),
        },
        "trig": {
            "cos_0": cos_permille_from_angle_mdeg(0),
            "cos_90000": cos_permille_from_angle_mdeg(90_000),
            "cos_180000": cos_permille_from_angle_mdeg(180_000),
            "sin_0": sin_permille_from_angle_mdeg(0),
            "sin_90000": sin_permille_from_angle_mdeg(90_000),
            "sin_180000": sin_permille_from_angle_mdeg(180_000),
            "sin_30000": sin_permille_from_angle_mdeg(30_000),
            "cos_60000": cos_permille_from_angle_mdeg(60_000),
        },
    }


def numeric_ops_hash() -> str:
    return canonical_sha256(numeric_ops_payload())


def float_in_truth_blocking_count(repo_root: str) -> int:
    report = scan_float_in_truth(repo_root)
    return int(report.get("blocking_finding_count", 0) or 0)
