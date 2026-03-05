#!/usr/bin/env python3
"""Verify SYS-5 certification replay hashes across deterministic state windows."""

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

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


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


def _certification_result_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_certification_result_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_type_id", "")),
            str(item.get("result_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "result_id": str(row.get("result_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "cert_type_id": str(row.get("cert_type_id", "")).strip(),
                "pass": bool(row.get("pass", False)),
                "failed_checks": _sorted_tokens(row.get("failed_checks")),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _certificate_artifact_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_certificate_artifact_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("issued_tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_type_id", "")),
            str(item.get("cert_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "cert_id": str(row.get("cert_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "cert_type_id": str(row.get("cert_type_id", "")).strip(),
                "issuer_subject_id": str(row.get("issuer_subject_id", "")).strip(),
                "issued_tick": int(max(0, _as_int(row.get("issued_tick", 0), 0))),
                "valid_until_tick": (
                    None
                    if row.get("valid_until_tick") is None
                    else int(max(0, _as_int(row.get("valid_until_tick", 0), 0)))
                ),
                "status": str(dict(row.get("extensions") or {}).get("status", "active")).strip()
                or "active",
            }
            for row in rows
        ]
    )


def _revocation_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_certificate_revocation_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_id", "")),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "cert_id": str(row.get("cert_id", "")).strip(),
                "cert_type_id": str(row.get("cert_type_id", "")).strip(),
                "reason_code": str(row.get("reason_code", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _observed_hashes(state: Mapping[str, object]) -> dict:
    return {
        "system_certification_result_hash_chain": _certification_result_hash(state),
        "system_certificate_artifact_hash_chain": _certificate_artifact_hash(state),
        "system_certificate_revocation_hash_chain": _revocation_hash(state),
    }


def verify_certification_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = _observed_hashes(state)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "system_certification_result_hash_chain": str(
                state.get(
                    "system_certification_result_hash_chain",
                    state.get("certification_result_hash_chain", ""),
                )
            )
            .strip()
            .lower(),
            "system_certificate_artifact_hash_chain": str(
                state.get(
                    "system_certificate_artifact_hash_chain",
                    state.get("certificate_artifact_hash_chain", ""),
                )
            )
            .strip()
            .lower(),
            "system_certificate_revocation_hash_chain": str(
                state.get(
                    "system_certificate_revocation_hash_chain",
                    state.get("revocation_hash_chain", ""),
                )
            )
            .strip()
            .lower(),
        },
        "deterministic_fingerprint": "",
    }
    for key in (
        "system_certification_result_hash_chain",
        "system_certificate_artifact_hash_chain",
        "system_certificate_revocation_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and (recorded != observed_value):
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = _observed_hashes(expected_state)
        report["expected"] = dict(expected)
        for key in (
            "system_certification_result_hash_chain",
            "system_certificate_artifact_hash_chain",
            "system_certificate_revocation_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic replay hashes for SYS-5 certification windows."
    )
    parser.add_argument("--state-path", default="build/system/sys5_certification_report.json")
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
        loaded_expected, expected_err = _read_json(expected_abs)
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
        expected_payload = loaded_expected

    report = verify_certification_replay_window(
        state_payload=state_payload,
        expected_payload=expected_payload,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if str(report.get("result", "")).strip() != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
