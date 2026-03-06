#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-8 software pipeline windows."""

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


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: object) -> list:
    return sorted(
        set(
            str(item).strip()
            for item in list(values or [])
            if str(item).strip()
        )
    )


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
    return final_state if final_state else dict(payload)


def _build_artifact_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("software_artifact_rows"))
            if isinstance(item, Mapping)
            and str(item.get("kind", "")).strip() in {"binary", "package", "test_report"}
        ),
        key=lambda item: str(item.get("artifact_id", "")),
    )
    return canonical_sha256(
        [
            {
                "artifact_id": str(row.get("artifact_id", "")).strip(),
                "content_hash": str(row.get("content_hash", "")).strip(),
                "produced_by_run_id": str(row.get("produced_by_run_id", "")).strip(),
            }
            for row in rows
        ]
    )


def _compiled_model_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("compiled_model_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("compiled_model_id", "")),
    )
    return canonical_sha256(
        [
            {
                "compiled_model_id": str(row.get("compiled_model_id", "")).strip(),
                "source_hash": str(row.get("source_hash", "")).strip(),
                "compiled_type_id": str(row.get("compiled_type_id", "")).strip(),
                "equivalence_proof_ref": str(row.get("equivalence_proof_ref", "")).strip(),
                "validity_domain_ref": str(row.get("validity_domain_ref", "")).strip(),
            }
            for row in rows
        ]
    )


def _signature_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("software_artifact_rows"))
            if isinstance(item, Mapping)
            and str(item.get("kind", "")).strip() == "signature"
        ),
        key=lambda item: str(item.get("artifact_id", "")),
    )
    return canonical_sha256(
        [
            {
                "artifact_id": str(row.get("artifact_id", "")).strip(),
                "content_hash": str(row.get("content_hash", "")).strip(),
                "produced_by_run_id": str(row.get("produced_by_run_id", "")).strip(),
            }
            for row in rows
        ]
    )


def _deployment_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("deployment_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("deploy_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "deploy_id": str(row.get("deploy_id", "")).strip(),
                "artifact_id": str(row.get("artifact_id", "")).strip(),
                "from_subject_id": str(row.get("from_subject_id", "")).strip(),
                "to_address": str(row.get("to_address", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def verify_pipeline_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "build_artifact_hash_chain": _build_artifact_hash(state),
        "compiled_model_hash_chain": _compiled_model_hash(state),
        "signature_hash_chain": _signature_hash(state),
        "deployment_hash_chain": _deployment_hash(state),
    }
    recorded = {
        "build_artifact_hash_chain": str(state.get("build_artifact_hash_chain", "")).strip().lower(),
        "compiled_model_hash_chain": str(state.get("compiled_model_hash_chain", "")).strip().lower(),
        "signature_hash_chain": str(state.get("signature_hash_chain", "")).strip().lower(),
        "deployment_hash_chain": str(state.get("deployment_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in (
        "build_artifact_hash_chain",
        "compiled_model_hash_chain",
        "signature_hash_chain",
        "deployment_hash_chain",
    ):
        if recorded.get(key) and recorded.get(key) != observed.get(key):
            violations.append("recorded {} does not match replay hash".format(key))

    report = {
        "result": "complete" if not violations else "violation",
        "observed": observed,
        "recorded": recorded,
        "violations": violations,
    }
    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = {
            "build_artifact_hash_chain": _build_artifact_hash(expected_state),
            "compiled_model_hash_chain": _compiled_model_hash(expected_state),
            "signature_hash_chain": _signature_hash(expected_state),
            "deployment_hash_chain": _deployment_hash(expected_state),
        }
        report["expected"] = expected
        for key in (
            "build_artifact_hash_chain",
            "compiled_model_hash_chain",
            "signature_hash_chain",
            "deployment_hash_chain",
        ):
            if expected.get(key) != observed.get(key):
                report["violations"].append(
                    "{} mismatch against expected replay baseline".format(key)
                )
        if report["violations"]:
            report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic replay hashes for PROC-8 software pipeline windows."
    )
    parser.add_argument("--state-path", default="build/process/proc8_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {"result": "error", "reason": "state_read_failed", "details": state_err},
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
                        "details": expected_err,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_pipeline_replay_window(
        state_payload=state_payload, expected_payload=expected_payload
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
