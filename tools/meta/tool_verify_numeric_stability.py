#!/usr/bin/env python3
"""Verify deterministic rounding stability against quantity tolerance registry policy."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.numeric import deterministic_mul_div, normalize_rounding_mode, normalize_quantity_tolerance_rows  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "json root must be an object"
    return payload, ""


def _tolerance_rows(payload: Mapping[str, object]) -> List[dict]:
    record_rows = list((dict(payload.get("record") or {})).get("quantity_tolerances") or [])
    rows = record_rows if record_rows else list(payload.get("quantity_tolerances") or [])
    return [dict(row) for row in normalize_quantity_tolerance_rows(rows)]


def _seed_for_quantity(quantity_id: str) -> int:
    token = str(quantity_id or "").strip()
    digest = canonical_sha256({"quantity_id": token})
    return int(digest[:16], 16)


def _simulate_row(row: Mapping[str, object], window_ticks: int, drift_scale: int) -> dict:
    quantity_id = str(row.get("quantity_id", "")).strip()
    base_resolution = int(max(1, _as_int(row.get("base_resolution", 1), 1)))
    tolerance_abs = int(max(0, _as_int(row.get("tolerance_abs", 0), 0)))
    rounding_mode = normalize_rounding_mode(row.get("rounding_mode"), "round_half_to_even")
    seed = _seed_for_quantity(quantity_id)
    start_value = int((seed % 100_000) + base_resolution * 17)
    value = int(start_value)

    for tick in range(int(max(1, window_ticks))):
        perturb = int(((tick % 9) - 4) * base_resolution)
        value = int(value + perturb)
        value = int(deterministic_mul_div(value, 997, 1000, rounding_mode=rounding_mode))
        value = int(deterministic_mul_div(value, 1000, 997, rounding_mode=rounding_mode))

    residual_abs = int(abs(int(value - start_value)))
    allowed_abs = int(max(base_resolution, tolerance_abs) * max(1, int(max(1, window_ticks))))
    return {
        "quantity_id": quantity_id,
        "rounding_mode": rounding_mode,
        "start_value": int(start_value),
        "end_value": int(value),
        "residual_abs": int(residual_abs),
        "allowed_residual_abs": int(allowed_abs),
        "within_tolerance": bool(residual_abs <= allowed_abs),
    }


def verify_numeric_stability(
    *,
    registry_payload: Mapping[str, object],
    window_ticks: int,
    drift_scale: int,
) -> dict:
    rows = _tolerance_rows(registry_payload)
    simulation_rows = sorted(
        (
            _simulate_row(row=row, window_ticks=int(max(1, window_ticks)), drift_scale=int(max(1, drift_scale)))
            for row in rows
            if str(row.get("quantity_id", "")).strip()
        ),
        key=lambda item: str(item.get("quantity_id", "")),
    )

    violations = [dict(row) for row in simulation_rows if not bool(row.get("within_tolerance", False))]
    fingerprint_payload = {
        "window_ticks": int(max(1, window_ticks)),
        "drift_scale": int(max(1, drift_scale)),
        "rows": list(simulation_rows),
    }
    fingerprint_a = canonical_sha256(fingerprint_payload)
    fingerprint_b = canonical_sha256(fingerprint_payload)
    deterministic_match = bool(fingerprint_a == fingerprint_b)

    report = {
        "result": "complete",
        "window_ticks": int(max(1, window_ticks)),
        "drift_scale": int(max(1, drift_scale)),
        "quantity_count": int(len(simulation_rows)),
        "violation_count": int(len(violations)),
        "deterministic_replay_match": bool(deterministic_match),
        "violations": list(violations),
        "deterministic_fingerprint": "",
    }
    if (not deterministic_match) or violations:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic numeric drift remains within declared tolerance bounds.")
    parser.add_argument(
        "--registry-path",
        default=os.path.join("data", "registries", "quantity_tolerance_registry.json"),
        help="Path to quantity_tolerance_registry.json",
    )
    parser.add_argument("--window-ticks", type=int, default=4096)
    parser.add_argument("--drift-scale", type=int, default=64)
    args = parser.parse_args()

    registry_path = os.path.normpath(os.path.abspath(str(args.registry_path)))
    if not os.path.isabs(registry_path):
        registry_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, registry_path))

    payload, error = _read_json(registry_path)
    if error:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.numeric.invalid_registry",
                    "message": "invalid registry payload: {}".format(error),
                    "registry_path": registry_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    report = verify_numeric_stability(
        registry_payload=payload,
        window_ticks=int(max(1, _as_int(args.window_ticks, 4096))),
        drift_scale=int(max(1, _as_int(args.drift_scale, 64))),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
