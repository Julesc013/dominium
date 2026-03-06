#!/usr/bin/env python3
"""Compact PROC derived artifacts and verify replay from compaction anchors."""

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

from src.meta.provenance import (  # noqa: E402
    compact_provenance_window,
    verify_replay_from_compaction_anchor,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def _state_payload(payload: Mapping[str, object]) -> dict:
    ext = _as_map(payload.get("extensions"))
    snap = _as_map(ext.get("final_state_snapshot"))
    return snap if snap else dict(payload)


def _classification_rows() -> list:
    return [
        {"artifact_type_id": "process.explain", "classification": "derived", "compaction_allowed": True},
        {"artifact_type_id": "process.observation", "classification": "derived", "compaction_allowed": True},
        {"artifact_type_id": "process.research.candidate", "classification": "derived", "compaction_allowed": True},
        {"artifact_type_id": "process.run.record", "classification": "canonical", "compaction_allowed": False},
        {"artifact_type_id": "process.step.record", "classification": "canonical", "compaction_allowed": False},
        {"artifact_type_id": "process.capsule.execution", "classification": "canonical", "compaction_allowed": False},
    ]


def verify_proc_compaction(
    *,
    state_payload: Mapping[str, object],
    shard_id: str,
    start_tick: int,
    end_tick: int,
) -> dict:
    state = _state_payload(state_payload)
    compacted = compact_provenance_window(
        state_payload=state,
        classification_rows=_classification_rows(),
        shard_id=str(shard_id or "shard.proc"),
        start_tick=int(max(0, int(start_tick))),
        end_tick=int(max(int(start_tick), int(end_tick))),
        emit_summary=True,
    )
    if str(compacted.get("result", "")).strip() != "complete":
        return {
            "result": "violation",
            "reason": str(compacted.get("reason_code", "")).strip() or "compaction_failed",
            "details": compacted,
        }
    marker = _as_map(compacted.get("compaction_marker"))
    marker_id = str(marker.get("marker_id", "")).strip()
    replay = verify_replay_from_compaction_anchor(
        state_payload=_as_map(compacted.get("state")),
        marker_id=marker_id,
    )
    result = "complete" if str(replay.get("result", "")).strip() == "complete" else "violation"
    report = {
        "result": result,
        "marker_id": marker_id,
        "removed_total": int(compacted.get("removed_total", 0) or 0),
        "compaction_marker_hash_chain": str(compacted.get("compaction_marker_hash_chain", "")).strip(),
        "pre_compaction_hash": str(compacted.get("pre_compaction_hash", "")).strip(),
        "post_compaction_hash": str(compacted.get("post_compaction_hash", "")).strip(),
        "replay_result": replay,
        "state": _as_map(compacted.get("state")),
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, state="", deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compact derived PROC artifacts and verify replay anchors."
    )
    parser.add_argument("--state-path", default="build/process/proc9_report.json")
    parser.add_argument("--start-tick", type=int, default=0)
    parser.add_argument("--end-tick", type=int, default=999999)
    parser.add_argument("--shard-id", default="shard.proc.stress")
    parser.add_argument("--out-state-path", default="")
    args = parser.parse_args()

    state_payload, state_err = _read_json(os.path.normpath(os.path.abspath(str(args.state_path))))
    if state_err:
        print(json.dumps({"result": "error", "reason": "state_read_failed", "details": state_err}, indent=2, sort_keys=True))
        return 2

    report = verify_proc_compaction(
        state_payload=state_payload,
        shard_id=str(args.shard_id),
        start_tick=int(args.start_tick),
        end_tick=int(args.end_tick),
    )
    out_state_path = str(args.out_state_path or "").strip()
    if out_state_path:
        abs_out = os.path.normpath(os.path.abspath(out_state_path))
        parent = os.path.dirname(abs_out)
        if parent and (not os.path.isdir(parent)):
            os.makedirs(parent, exist_ok=True)
        with open(abs_out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(_as_map(report.get("state")), handle, indent=2, sort_keys=True)
            handle.write("\n")

    print(json.dumps(dict(report, state="(omitted)"), indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
