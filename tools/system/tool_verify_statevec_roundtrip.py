#!/usr/bin/env python3
"""Verify STATEVEC-0 deterministic serialize/deserialize roundtrip stability."""

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

from system.statevec import (  # noqa: E402
    deserialize_state,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    serialize_state,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


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
    final_state = _as_map(ext.get("final_state_snapshot"))
    if final_state:
        return final_state
    return dict(payload)


def _definition_hash(rows: object) -> str:
    normalized = normalize_state_vector_definition_rows(rows)
    return canonical_sha256(
        [
            {
                "owner_id": str(row.get("owner_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "state_fields": list(row.get("state_fields") or []),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            }
            for row in normalized
        ]
    )


def _snapshot_hash(rows: object) -> str:
    normalized = normalize_state_vector_snapshot_rows(rows)
    return canonical_sha256(
        [
            {
                "snapshot_id": str(row.get("snapshot_id", "")).strip(),
                "owner_id": str(row.get("owner_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "serialized_state": _as_map(row.get("serialized_state")),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            }
            for row in normalized
        ]
    )


def verify_statevec_roundtrip(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    definition_rows = normalize_state_vector_definition_rows(state.get("state_vector_definition_rows") or [])
    snapshot_rows = normalize_state_vector_snapshot_rows(state.get("state_vector_snapshot_rows") or [])

    report = {
        "result": "complete",
        "violations": [],
        "owner_reports": [],
        "observed": {
            "state_vector_definition_hash_chain": _definition_hash(definition_rows),
            "state_vector_snapshot_hash_chain": _snapshot_hash(snapshot_rows),
        },
        "recorded": {
            "state_vector_definition_hash_chain": str(state.get("state_vector_definition_hash_chain", "")).strip().lower(),
            "state_vector_snapshot_hash_chain": str(state.get("state_vector_snapshot_hash_chain", "")).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    for snapshot in snapshot_rows:
        owner_id = str(snapshot.get("owner_id", "")).strip()
        expected_version = str(snapshot.get("version", "")).strip() or "1.0.0"
        tick = int(max(0, _as_int(snapshot.get("tick", 0), 0)))

        restored = deserialize_state(
            snapshot_row=snapshot,
            state_vector_definition_rows=definition_rows,
            expected_version=expected_version,
        )
        owner_report = {
            "owner_id": owner_id,
            "snapshot_id": str(snapshot.get("snapshot_id", "")).strip(),
            "restored": str(restored.get("result", "")).strip(),
            "roundtrip": "refused",
            "reason_code": str(restored.get("reason_code", "")).strip(),
            "matches": False,
            "anchor_matches": False,
            "snapshot_id_matches": False,
        }
        if str(restored.get("result", "")).strip() != "complete":
            report["violations"].append(
                "state vector deserialize failed for owner {}".format(owner_id or "unknown")
            )
            report["owner_reports"].append(owner_report)
            continue

        serialization = serialize_state(
            owner_id=owner_id,
            source_state=_as_map(restored.get("restored_state")),
            state_vector_definition_rows=definition_rows,
            current_tick=tick,
            expected_version=expected_version,
            extensions={"source": "tool_verify_statevec_roundtrip"},
        )
        owner_report["roundtrip"] = str(serialization.get("result", "")).strip()
        owner_report["reason_code"] = str(serialization.get("reason_code", "")).strip()
        if str(serialization.get("result", "")).strip() != "complete":
            report["violations"].append(
                "state vector serialize failed for owner {}".format(owner_id or "unknown")
            )
            report["owner_reports"].append(owner_report)
            continue

        replay_snapshot = _as_map(serialization.get("snapshot_row"))
        owner_report["matches"] = _as_map(snapshot.get("serialized_state")) == _as_map(
            replay_snapshot.get("serialized_state")
        )
        owner_report["anchor_matches"] = str(restored.get("anchor_hash", "")).strip() == str(
            serialization.get("anchor_hash", "")
        ).strip()
        owner_report["snapshot_id_matches"] = str(snapshot.get("snapshot_id", "")).strip() == str(
            replay_snapshot.get("snapshot_id", "")
        ).strip()
        if not owner_report["matches"]:
            report["violations"].append(
                "serialized state mismatch after roundtrip for owner {}".format(owner_id or "unknown")
            )
        if not owner_report["anchor_matches"]:
            report["violations"].append(
                "anchor hash mismatch after roundtrip for owner {}".format(owner_id or "unknown")
            )
        if not owner_report["snapshot_id_matches"]:
            report["violations"].append(
                "snapshot id mismatch after roundtrip for owner {}".format(owner_id or "unknown")
            )
        report["owner_reports"].append(owner_report)

    for key in (
        "state_vector_definition_hash_chain",
        "state_vector_snapshot_hash_chain",
    ):
        recorded = str(_as_map(report.get("recorded")).get(key, "")).strip().lower()
        observed = str(_as_map(report.get("observed")).get(key, "")).strip().lower()
        if recorded and (recorded != observed):
            report["violations"].append("recorded {} does not match observed hash".format(key))

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        report["expected"] = {
            "state_vector_definition_hash_chain": _definition_hash(
                expected_state.get("state_vector_definition_rows") or []
            ),
            "state_vector_snapshot_hash_chain": _snapshot_hash(
                expected_state.get("state_vector_snapshot_rows") or []
            ),
        }
        for key in (
            "state_vector_definition_hash_chain",
            "state_vector_snapshot_hash_chain",
        ):
            expected_value = str(_as_map(report.get("expected")).get(key, "")).strip().lower()
            observed_value = str(_as_map(report.get("observed")).get(key, "")).strip().lower()
            if expected_value != observed_value:
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["owner_reports"] = sorted(
        [dict(row) for row in list(report.get("owner_reports") or []) if isinstance(row, Mapping)],
        key=lambda row: (
            str(row.get("owner_id", "")),
            str(row.get("snapshot_id", "")),
        ),
    )
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify STATEVEC-0 deterministic roundtrip stability.")
    parser.add_argument("--state-path", default="build/system/statevec0_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {
                    "result": "error",
                    "reason": "state_read_failed",
                    "state_path": state_path,
                    "details": state_err,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_abs = os.path.normpath(os.path.abspath(expected_path))
        expected_payload, expected_err = _read_json(expected_abs)
        if expected_err:
            print(
                json.dumps(
                    {
                        "result": "error",
                        "reason": "expected_state_read_failed",
                        "expected_state_path": expected_abs,
                        "details": expected_err,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_statevec_roundtrip(
        state_payload=state_payload,
        expected_payload=expected_payload,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
