#!/usr/bin/env python3
"""Deterministic SecureX policy verification for lockfile pack signatures."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload  # noqa: E402
from tools.xstack.sessionx.common import norm, read_json_object  # noqa: E402


ALLOWED_SIGNATURE_STATUS = {
    "official",
    "signed",
    "verified",
    "unsigned",
    "classroom-restricted",
    "revoked",
}


def _repo_root(value: str) -> str:
    token = str(value).strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str]) -> Dict[str, object]:
    payload = {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": dict(relevant_ids or {}),
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": "$",
            }
        ],
    }
    return payload


def _policy_rows(payload: dict) -> List[dict]:
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("policies"), list):
        return [dict(row) for row in payload.get("policies") or [] if isinstance(row, dict)]
    record = payload.get("record")
    if isinstance(record, dict) and isinstance(record.get("policies"), list):
        return [dict(row) for row in record.get("policies") or [] if isinstance(row, dict)]
    return []


def _load_securex_policy_registry(repo_root: str, registry_path: str = "") -> Tuple[List[dict], str]:
    candidate_paths: List[str] = []
    token = str(registry_path).strip()
    if token:
        candidate_paths.append(os.path.normpath(os.path.abspath(token)))
    candidate_paths.append(os.path.join(repo_root, "build", "registries", "securex_policy.registry.json"))
    candidate_paths.append(os.path.join(repo_root, "data", "registries", "securex_policy_registry.json"))
    for abs_path in candidate_paths:
        payload, err = read_json_object(abs_path)
        if err:
            continue
        rows = _policy_rows(payload)
        if rows:
            return rows, ""
    return [], "securex policy registry is missing or invalid"


def _select_policy(rows: List[dict], policy_id: str) -> Tuple[dict, str]:
    requested = str(policy_id).strip()
    for row in sorted((dict(item) for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("securex_policy_id", ""))):
        if str(row.get("securex_policy_id", "")).strip() == requested:
            return row, ""
    return {}, "securex policy '{}' is not present".format(requested or "<empty>")


def _verify_rows(policy: dict, resolved_packs: List[dict]) -> Tuple[List[dict], List[dict]]:
    findings: List[dict] = []
    violations: List[dict] = []
    required_status = sorted(set(str(item).strip() for item in (policy.get("required_signature_status") or []) if str(item).strip()))
    allow_unsigned = bool(policy.get("allow_unsigned", False))
    allow_classroom = bool(policy.get("allow_classroom_restricted", False))
    for row in sorted((dict(item) for item in (resolved_packs or []) if isinstance(item, dict)), key=lambda item: str(item.get("pack_id", ""))):
        pack_id = str(row.get("pack_id", "")).strip() or "<unknown>"
        signature_status = str(row.get("signature_status", "")).strip()
        finding = {
            "pack_id": pack_id,
            "signature_status": signature_status,
            "status": "pass",
            "code": "",
            "message": "",
        }
        if signature_status not in ALLOWED_SIGNATURE_STATUS:
            finding["status"] = "refused"
            finding["code"] = "refusal.net.handshake_securex_denied"
            finding["message"] = "pack uses unknown signature_status"
            violations.append(dict(finding))
        elif required_status and signature_status not in required_status:
            finding["status"] = "refused"
            finding["code"] = "refusal.net.handshake_securex_denied"
            finding["message"] = "signature_status not allowed by securex policy"
            violations.append(dict(finding))
        elif (not allow_unsigned) and signature_status == "unsigned":
            finding["status"] = "refused"
            finding["code"] = "refusal.net.handshake_securex_denied"
            finding["message"] = "unsigned pack forbidden by securex policy"
            violations.append(dict(finding))
        elif (not allow_classroom) and signature_status == "classroom-restricted":
            finding["status"] = "refused"
            finding["code"] = "refusal.net.handshake_securex_denied"
            finding["message"] = "classroom-restricted pack forbidden by securex policy"
            violations.append(dict(finding))
        findings.append(finding)
    return findings, violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify lockfile pack signatures against a SecureX policy.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--lockfile", default="")
    parser.add_argument("--securex-policy-id", required=True)
    parser.add_argument("--policy-registry", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    lockfile_path = str(args.lockfile).strip()
    if lockfile_path:
        lock_abs = os.path.normpath(os.path.abspath(lockfile_path))
    else:
        lock_abs = os.path.join(repo_root, "build", "lockfile.json")

    lock_payload, lock_err = read_json_object(lock_abs)
    if lock_err:
        out = _refusal(
            "LOCKFILE_MISMATCH",
            "lockfile is missing or invalid JSON",
            "Generate lockfile and rerun securex verification.",
            {"lockfile_path": norm(lock_abs)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2
    lock_check = validate_lockfile_payload(lock_payload)
    if str(lock_check.get("result", "")) != "complete":
        out = _refusal(
            "LOCKFILE_MISMATCH",
            "lockfile failed deterministic validation",
            "Rebuild lockfile from deterministic bundle inputs.",
            {"lockfile_path": norm(lock_abs)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    rows, rows_err = _load_securex_policy_registry(repo_root=repo_root, registry_path=str(args.policy_registry))
    if rows_err:
        out = _refusal(
            "refusal.net.handshake_securex_denied",
            rows_err,
            "Compile securex policy registry and retry.",
            {"securex_policy_id": str(args.securex_policy_id)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2
    policy, policy_err = _select_policy(rows=rows, policy_id=str(args.securex_policy_id))
    if policy_err:
        out = _refusal(
            "refusal.net.handshake_securex_denied",
            policy_err,
            "Choose a securex policy id present in securex policy registry.",
            {"securex_policy_id": str(args.securex_policy_id)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    findings, violations = _verify_rows(policy=policy, resolved_packs=list(lock_payload.get("resolved_packs") or []))
    deterministic_report = {
        "schema_version": "1.0.0",
        "securex_policy_id": str(policy.get("securex_policy_id", "")),
        "signature_verification_required": bool(policy.get("signature_verification_required", False)),
        "verification_mode": "status_only_stub",
        "lockfile_path": norm(lock_abs),
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "findings": findings,
        "violation_count": len(violations),
    }
    deterministic_report["report_hash"] = canonical_sha256(deterministic_report)
    if violations:
        out = _refusal(
            "refusal.net.handshake_securex_denied",
            "one or more packs violate securex policy",
            "Use a compatible lockfile/policy pair and retry.",
            {
                "securex_policy_id": str(policy.get("securex_policy_id", "")),
                "first_pack_id": str(violations[0].get("pack_id", "")),
            },
        )
        out["report"] = deterministic_report
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    out = {
        "result": "complete",
        "message": "securex lockfile verification passed",
        "report": deterministic_report,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
