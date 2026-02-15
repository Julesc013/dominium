#!/usr/bin/env python3
"""Deterministic SecureX policy verification for a single pack manifest."""

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
    return {
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


def _policy_rows(payload: dict) -> List[dict]:
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("policies"), list):
        return [dict(row) for row in payload.get("policies") or [] if isinstance(row, dict)]
    record = payload.get("record")
    if isinstance(record, dict) and isinstance(record.get("policies"), list):
        return [dict(row) for row in record.get("policies") or [] if isinstance(row, dict)]
    return []


def _load_policy(repo_root: str, policy_id: str, registry_path: str = "") -> Tuple[dict, str]:
    candidate_paths: List[str] = []
    token = str(registry_path).strip()
    if token:
        candidate_paths.append(os.path.normpath(os.path.abspath(token)))
    candidate_paths.append(os.path.join(repo_root, "build", "registries", "securex_policy.registry.json"))
    candidate_paths.append(os.path.join(repo_root, "data", "registries", "securex_policy_registry.json"))
    rows: List[dict] = []
    for abs_path in candidate_paths:
        payload, err = read_json_object(abs_path)
        if err:
            continue
        rows = _policy_rows(payload)
        if rows:
            break
    if not rows:
        return {}, "securex policy registry is missing or invalid"
    requested = str(policy_id).strip()
    for row in sorted((dict(item) for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("securex_policy_id", ""))):
        if str(row.get("securex_policy_id", "")).strip() == requested:
            return row, ""
    return {}, "securex policy '{}' is not present".format(requested or "<empty>")


def _verify(signature_status: str, policy: dict) -> Tuple[bool, str]:
    status = str(signature_status).strip()
    if status not in ALLOWED_SIGNATURE_STATUS:
        return False, "unknown signature_status"
    required = set(str(item).strip() for item in (policy.get("required_signature_status") or []) if str(item).strip())
    if required and status not in required:
        return False, "signature_status not allowed by securex policy"
    if (not bool(policy.get("allow_unsigned", False))) and status == "unsigned":
        return False, "unsigned pack forbidden by securex policy"
    if (not bool(policy.get("allow_classroom_restricted", False))) and status == "classroom-restricted":
        return False, "classroom-restricted pack forbidden by securex policy"
    return True, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a pack manifest against SecureX policy.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--pack-manifest", required=True)
    parser.add_argument("--securex-policy-id", required=True)
    parser.add_argument("--policy-registry", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    manifest_abs = os.path.normpath(os.path.abspath(str(args.pack_manifest)))
    manifest, manifest_err = read_json_object(manifest_abs)
    if manifest_err:
        out = _refusal(
            "PACK_INCOMPATIBLE",
            "pack manifest is missing or invalid JSON",
            "Provide a valid pack.json manifest path.",
            {"pack_manifest": norm(manifest_abs)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2
    signature_status = str(manifest.get("signature_status", "")).strip()
    pack_id = str(manifest.get("pack_id", "")).strip() or "<unknown>"

    policy, policy_err = _load_policy(
        repo_root=repo_root,
        policy_id=str(args.securex_policy_id),
        registry_path=str(args.policy_registry),
    )
    if policy_err:
        out = _refusal(
            "refusal.net.handshake_securex_denied",
            policy_err,
            "Choose a securex policy id present in securex policy registry.",
            {"securex_policy_id": str(args.securex_policy_id)},
        )
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    ok, message = _verify(signature_status=signature_status, policy=policy)
    report = {
        "schema_version": "1.0.0",
        "pack_id": pack_id,
        "pack_manifest": norm(manifest_abs),
        "signature_status": signature_status,
        "securex_policy_id": str(policy.get("securex_policy_id", "")),
        "signature_verification_required": bool(policy.get("signature_verification_required", False)),
        "verification_mode": "status_only_stub",
    }
    report["report_hash"] = canonical_sha256(report)
    if not ok:
        out = _refusal(
            "refusal.net.handshake_securex_denied",
            message,
            "Use a pack signature_status compatible with the selected securex policy.",
            {"pack_id": pack_id, "securex_policy_id": str(policy.get("securex_policy_id", ""))},
        )
        out["report"] = report
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    out = {
        "result": "complete",
        "message": "securex pack verification passed",
        "report": report,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
