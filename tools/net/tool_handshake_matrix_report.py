#!/usr/bin/env python3
"""Generate deterministic handshake compatibility matrix report."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, write_canonical_json
from tools.xstack.sessionx.net_handshake import run_loopback_handshake
from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture


def _run_case(repo_root: str, case: dict) -> Dict[str, object]:
    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id=str(case.get("save_id", "")),
        requested_replication_policy_id=str(case.get("requested_replication_policy_id", "")),
        anti_cheat_policy_id=str(case.get("anti_cheat_policy_id", "")),
        server_profile_id=str(case.get("server_profile_id", "")),
        server_policy_id=str(case.get("server_policy_id", "")),
        securex_policy_id=str(case.get("securex_policy_id", "")),
        desired_law_profile_id=str(case.get("desired_law_profile_id", "")),
    )
    lock_payload = copy.deepcopy(dict(fixture["lock_payload"]))
    signature_status = str(case.get("signature_status", "")).strip()
    if signature_status:
        lock_payload["resolved_packs"] = [
            dict(dict(row or {}), signature_status=signature_status)
            for row in list(lock_payload.get("resolved_packs") or [])
            if isinstance(row, dict)
        ]
    session_spec = copy.deepcopy(dict(fixture["session_spec"]))
    schema_versions = case.get("schema_versions")
    if isinstance(schema_versions, dict):
        network = dict(session_spec.get("network") or {})
        merged_schema_versions = dict(network.get("schema_versions") or {})
        for key in sorted(schema_versions.keys()):
            merged_schema_versions[str(key)] = str(schema_versions[key])
        network["schema_versions"] = merged_schema_versions
        session_spec["network"] = network
    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=session_spec,
        lock_payload=lock_payload,
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    refusal = dict(result.get("refusal") or {})
    return {
        "case_id": str(case.get("case_id", "")),
        "result": str(result.get("result", "")),
        "reason_code": str(refusal.get("reason_code", "")),
        "expected_result": str(case.get("expected_result", "")),
        "expected_reason_code": str(case.get("expected_reason_code", "")),
        "match": (
            str(result.get("result", "")) == str(case.get("expected_result", ""))
            and str(refusal.get("reason_code", "")) == str(case.get("expected_reason_code", ""))
        ),
    }


def _matrix_cases() -> List[dict]:
    return [
        {
            "case_id": "ranked.accept_signed",
            "save_id": "save.net.report.rank.accept",
            "requested_replication_policy_id": "policy.net.lockstep",
            "anti_cheat_policy_id": "policy.ac.rank_strict",
            "server_profile_id": "server.profile.rank_strict",
            "server_policy_id": "server.policy.ranked.strict",
            "securex_policy_id": "securex.policy.rank_strict",
            "signature_status": "signed",
            "expected_result": "complete",
            "expected_reason_code": "",
        },
        {
            "case_id": "ranked.refuse_unsigned",
            "save_id": "save.net.report.rank.unsigned",
            "requested_replication_policy_id": "policy.net.lockstep",
            "anti_cheat_policy_id": "policy.ac.rank_strict",
            "server_profile_id": "server.profile.rank_strict",
            "server_policy_id": "server.policy.ranked.strict",
            "securex_policy_id": "securex.policy.rank_strict",
            "signature_status": "unsigned",
            "expected_result": "refused",
            "expected_reason_code": "refusal.net.handshake_securex_denied",
        },
        {
            "case_id": "ranked.refuse_observer_law",
            "save_id": "save.net.report.rank.observer",
            "requested_replication_policy_id": "policy.net.lockstep",
            "anti_cheat_policy_id": "policy.ac.rank_strict",
            "server_profile_id": "server.profile.rank_strict",
            "server_policy_id": "server.policy.ranked.strict",
            "securex_policy_id": "securex.policy.rank_strict",
            "desired_law_profile_id": "law.lab.observe_only",
            "signature_status": "signed",
            "expected_result": "refused",
            "expected_reason_code": "refusal.net.handshake_policy_not_allowed",
        },
        {
            "case_id": "private.refuse_schema_version",
            "save_id": "save.net.report.private.schema_mismatch",
            "requested_replication_policy_id": "policy.net.lockstep",
            "anti_cheat_policy_id": "policy.ac.private_relaxed",
            "server_profile_id": "server.profile.private_relaxed",
            "server_policy_id": "server.policy.private.default",
            "securex_policy_id": "securex.policy.private_relaxed",
            "schema_versions": {"session_spec": "9.9.9"},
            "expected_result": "refused",
            "expected_reason_code": "refusal.net.handshake_schema_version_mismatch",
        },
    ]


def _markdown(rows: List[dict], content_hash: str) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-16",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: canon-aligned documentation set for convergence and release preparation",
        "",
        "# Handshake Compatibility Matrix",
        "",
        "| case_id | expected_result | expected_reason_code | actual_result | actual_reason_code | match |",
        "|---|---|---|---|---|---|",
    ]
    for row in sorted((dict(item) for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("case_id", ""))):
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                str(row.get("case_id", "")),
                str(row.get("expected_result", "")),
                str(row.get("expected_reason_code", "")),
                str(row.get("result", "")),
                str(row.get("reason_code", "")),
                "yes" if bool(row.get("match", False)) else "no",
            )
        )
    lines.extend(["", "matrix_hash: `{}`".format(content_hash), ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic handshake compatibility matrix report.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--out-md", default="docs/audit/HANDSHAKE_COMPAT_MATRIX.md")
    parser.add_argument("--out-json", default="docs/audit/HANDSHAKE_COMPAT_MATRIX.json")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    cases = _matrix_cases()
    rows = [_run_case(repo_root=repo_root, case=dict(case)) for case in cases]
    payload = {
        "schema_version": "1.0.0",
        "matrix_id": "net.handshake.compatibility",
        "rows": sorted((dict(item) for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("case_id", ""))),
        "extensions": {},
    }
    payload["matrix_hash"] = canonical_sha256(payload)

    out_json_abs = os.path.join(repo_root, str(args.out_json).replace("/", os.sep))
    out_md_abs = os.path.join(repo_root, str(args.out_md).replace("/", os.sep))
    write_canonical_json(out_json_abs, payload)
    markdown = _markdown(payload["rows"], str(payload.get("matrix_hash", "")))
    os.makedirs(os.path.dirname(out_md_abs), exist_ok=True)
    with open(out_md_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(markdown)

    print(
        json.dumps(
            {
                "result": "complete",
                "matrix_hash": str(payload.get("matrix_hash", "")),
                "rows": len(payload["rows"]),
                "out_md": norm(os.path.relpath(out_md_abs, repo_root)),
                "out_json": norm(os.path.relpath(out_json_abs, repo_root)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

