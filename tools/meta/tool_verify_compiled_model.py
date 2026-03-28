#!/usr/bin/env python3
"""Verify COMPILE-0 compiled-model reproducibility from stored source snapshot."""

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

from meta.compile import evaluate_compile_request  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _rows(payload: Mapping[str, object], key: str) -> list[dict]:
    direct = payload.get(key)
    if isinstance(direct, list):
        return [dict(item) for item in direct if isinstance(item, Mapping)]
    record = _as_map(payload.get("record"))
    record_rows = record.get(key)
    if isinstance(record_rows, list):
        return [dict(item) for item in record_rows if isinstance(item, Mapping)]
    return []


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be object"
    return dict(payload), ""


def _load_registry(repo_root: str, rel_path: str, fallback: dict) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload, err = _read_json(abs_path)
    if err:
        return dict(fallback)
    return payload


def verify_compiled_model(
    *,
    repo_root: str,
    state_payload: Mapping[str, object],
    compiled_model_id: str,
) -> dict:
    model_id = str(compiled_model_id or "").strip()
    model_rows = _rows(state_payload, "compiled_model_rows")
    model_row = {}
    for row in model_rows:
        if str(row.get("compiled_model_id", "")).strip() == model_id:
            model_row = dict(row)
            break
    if not model_row:
        return {
            "result": "refusal",
            "reason_code": "refusal.compile.model_not_found",
            "compiled_model_id": model_id,
        }

    model_ext = _as_map(model_row.get("extensions"))
    source_ref_snapshot = _as_map(model_ext.get("source_ref_snapshot"))
    if not source_ref_snapshot:
        return {
            "result": "refusal",
            "reason_code": "refusal.compile.source_snapshot_missing",
            "compiled_model_id": model_id,
        }

    compile_eval = evaluate_compile_request(
        current_tick=0,
        compile_request={
            "request_id": "verify.{}".format(model_id),
            "source_kind": str(model_row.get("source_kind", "")).strip(),
            "source_ref": source_ref_snapshot,
            "target_compiled_type_id": str(model_row.get("compiled_type_id", "")).strip(),
            "error_bound_policy_id": _as_map(state_payload).get("error_bound_policy_id"),
            "extensions": {"source": "tool_verify_compiled_model"},
        },
        compiled_type_registry_payload=_load_registry(
            repo_root,
            "data/registries/compiled_type_registry.json",
            {"record": {"compiled_types": []}},
        ),
        verification_procedure_registry_payload=_load_registry(
            repo_root,
            "data/registries/verification_procedure_registry.json",
            {"record": {"verification_procedures": []}},
        ),
        compile_policy_registry_payload=_load_registry(
            repo_root,
            "data/registries/compile_policy_registry.json",
            {"record": {"compile_policies": []}},
        ),
        compile_policy_id=str(model_ext.get("compile_policy_id", "")).strip() or "compile.default",
    )
    if str(compile_eval.get("result", "")).strip() != "complete":
        return {
            "result": "violation",
            "reason_code": str(compile_eval.get("reason_code", "refusal.compile.invalid")).strip()
            or "refusal.compile.invalid",
            "compiled_model_id": model_id,
        }

    baseline_payload_hash = str(_as_map(model_row.get("compiled_payload_ref")).get("payload_hash", "")).strip()
    replay_payload_hash = str(
        _as_map(_as_map(compile_eval.get("compiled_model_row")).get("compiled_payload_ref")).get("payload_hash", "")
    ).strip()
    proof_ref = str(model_row.get("equivalence_proof_ref", "")).strip()
    baseline_proof_row = {}
    for row in _rows(state_payload, "equivalence_proof_rows"):
        if str(row.get("proof_id", "")).strip() == proof_ref:
            baseline_proof_row = dict(row)
            break
    replay_proof_row = dict(compile_eval.get("equivalence_proof_row") or {})

    payload_match = bool(baseline_payload_hash and baseline_payload_hash == replay_payload_hash)
    proof_match = (
        str(baseline_proof_row.get("proof_kind", "")).strip()
        == str(replay_proof_row.get("proof_kind", "")).strip()
        and str(baseline_proof_row.get("verification_procedure_id", "")).strip()
        == str(replay_proof_row.get("verification_procedure_id", "")).strip()
    )
    all_match = bool(payload_match and proof_match)
    report = {
        "result": "complete" if all_match else "violation",
        "compiled_model_id": model_id,
        "baseline_payload_hash": baseline_payload_hash,
        "replay_payload_hash": replay_payload_hash,
        "payload_match": payload_match,
        "proof_match": proof_match,
        "baseline_proof_kind": str(baseline_proof_row.get("proof_kind", "")).strip(),
        "replay_proof_kind": str(replay_proof_row.get("proof_kind", "")).strip(),
        "baseline_verification_procedure_id": str(
            baseline_proof_row.get("verification_procedure_id", "")
        ).strip(),
        "replay_verification_procedure_id": str(
            replay_proof_row.get("verification_procedure_id", "")
        ).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify COMPILE-0 compiled model determinism from source snapshot."
    )
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--state-path", required=True)
    parser.add_argument("--compiled-model-id", required=True)
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    if not os.path.isabs(state_path):
        state_path = os.path.normpath(os.path.join(repo_root, state_path))
    state_payload, err = _read_json(state_path)
    if err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.compile.invalid_state_payload",
                    "message": str(err),
                    "state_path": state_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    report = verify_compiled_model(
        repo_root=repo_root,
        state_payload=state_payload,
        compiled_model_id=str(args.compiled_model_id),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
