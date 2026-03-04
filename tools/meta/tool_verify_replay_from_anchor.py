#!/usr/bin/env python3
"""Verify deterministic replay consistency from a provenance compaction anchor."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.provenance import normalize_compaction_marker_rows, verify_replay_from_compaction_anchor  # noqa: E402


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def _resolve_state_payload(payload: Mapping[str, object]) -> dict:
    direct = dict(payload or {})
    record = dict(payload.get("record") or {}) if isinstance(payload.get("record"), Mapping) else {}
    if record and isinstance(record.get("compaction_markers"), list):
        return dict(record)
    return direct


def _latest_marker_id(state_payload: Mapping[str, object]) -> str:
    rows = normalize_compaction_marker_rows(state_payload.get("compaction_markers"))
    if not rows:
        return ""
    return str(rows[-1].get("marker_id", "")).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay consistency from a PROV compaction marker anchor.")
    parser.add_argument("--state-path", default="", help="JSON state payload path.")
    parser.add_argument("--marker-id", default="", help="Explicit compaction marker id. Defaults to latest marker.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.provenance.state_path_required",
                    "message": "provide --state-path",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    payload, error = _read_json(os.path.normpath(os.path.abspath(state_path)))
    if error:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.provenance.state_payload_invalid",
                    "message": error,
                    "state_path": os.path.normpath(os.path.abspath(state_path)),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    state_payload = _resolve_state_payload(payload)
    marker_id = str(args.marker_id or "").strip() or _latest_marker_id(state_payload)
    if not marker_id:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.provenance.compaction_marker_missing",
                    "message": "no compaction_marker found; provide --marker-id or state payload with compaction_markers",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    report = verify_replay_from_compaction_anchor(
        state_payload=state_payload,
        marker_id=marker_id,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
