#!/usr/bin/env python3
"""PerformX minimal budget/fidelity placeholder checks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return None, "invalid json"


def _registry_policy_rows(repo_root: str, file_name: str, key: str):
    path = os.path.join(repo_root, "build", "registries", file_name)
    payload, err = _read_json(path)
    if err or not isinstance(payload, dict):
        return [], "missing registry '{}'".format(file_name)
    rows = payload.get(key)
    if not isinstance(rows, list):
        return [], "registry '{}' missing key '{}'".format(file_name, key)
    out = [dict(item) for item in rows if isinstance(item, dict)]
    return sorted(out, key=lambda row: str(row.get("policy_id", ""))), ""


def _load_session_example(repo_root: str):
    schema_path = os.path.join(repo_root, "schemas", "session_spec.schema.json")
    payload, err = _read_json(schema_path)
    if err:
        return {}, err
    if not isinstance(payload, dict):
        return {}, "invalid schema object"
    examples = payload.get("examples")
    if not isinstance(examples, list) or not examples or not isinstance(examples[0], dict):
        return {}, "missing schema examples"
    return dict(examples[0]), ""


def _search_token(repo_root: str, token: str) -> bool:
    if not token:
        return True
    roots = (
        "packs",
        "docs/contracts",
    )
    token_bytes = token.encode("utf-8")
    for root in roots:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                abs_path = os.path.join(walk_root, name)
                try:
                    blob = open(abs_path, "rb").read()
                except OSError:
                    continue
                if token_bytes in blob:
                    return True
    return False


def run_performx_check(repo_root: str, profile: str) -> Dict[str, object]:
    _ = profile
    findings: List[Dict[str, object]] = []
    details: Dict[str, object] = {
        "policy_registry_status": {},
    }
    example, err = _load_session_example(repo_root)
    if err:
        findings.append(
            {
                "severity": "warn",
                "code": "warn.performx.session_example_unavailable",
                "message": "session_spec schema example unavailable: {}".format(err),
            }
        )
    else:
        budget_id = str(example.get("budget_policy_id", "")).strip()
        fidelity_id = str(example.get("fidelity_policy_id", "")).strip()
        if budget_id and not _search_token(repo_root, budget_id):
            findings.append(
                {
                    "severity": "warn",
                    "code": "warn.performx.missing_budget_policy_reference",
                    "message": "budget_policy_id '{}' not found in packs/docs placeholder sources".format(budget_id),
                }
            )
        if fidelity_id and not _search_token(repo_root, fidelity_id):
            findings.append(
                {
                    "severity": "warn",
                    "code": "warn.performx.missing_fidelity_policy_reference",
                    "message": "fidelity_policy_id '{}' not found in packs/docs placeholder sources".format(fidelity_id),
                }
            )

    activation_rows, activation_err = _registry_policy_rows(
        repo_root=repo_root,
        file_name="activation_policy.registry.json",
        key="activation_policies",
    )
    budget_rows, budget_err = _registry_policy_rows(
        repo_root=repo_root,
        file_name="budget_policy.registry.json",
        key="budget_policies",
    )
    fidelity_rows, fidelity_err = _registry_policy_rows(
        repo_root=repo_root,
        file_name="fidelity_policy.registry.json",
        key="fidelity_policies",
    )
    details["policy_registry_status"] = {
        "activation_count": len(activation_rows),
        "budget_count": len(budget_rows),
        "fidelity_count": len(fidelity_rows),
    }
    for msg in (activation_err, budget_err, fidelity_err):
        if not msg:
            continue
        findings.append(
            {
                "severity": "warn",
                "code": "warn.performx.policy_registry_unavailable",
                "message": msg,
            }
        )

    budget_id = str(example.get("budget_policy_id", "")).strip() if isinstance(example, dict) else ""
    fidelity_id = str(example.get("fidelity_policy_id", "")).strip() if isinstance(example, dict) else ""
    budget_row = {}
    fidelity_row = {}
    for row in budget_rows:
        if str(row.get("policy_id", "")).strip() == budget_id:
            budget_row = row
            break
    for row in fidelity_rows:
        if str(row.get("policy_id", "")).strip() == fidelity_id:
            fidelity_row = row
            break
    if budget_id and not budget_row and not budget_err:
        findings.append(
            {
                "severity": "warn",
                "code": "warn.performx.default_budget_missing_from_registry",
                "message": "default session budget policy '{}' is not present in budget_policy.registry.json".format(budget_id),
            }
        )
    if fidelity_id and not fidelity_row and not fidelity_err:
        findings.append(
            {
                "severity": "warn",
                "code": "warn.performx.default_fidelity_missing_from_registry",
                "message": "default session fidelity policy '{}' is not present in fidelity_policy.registry.json".format(fidelity_id),
            }
        )

    if budget_row and fidelity_row:
        tier_weights = budget_row.get("tier_compute_weights")
        if not isinstance(tier_weights, dict):
            tier_weights = {}
        entity_weight = int(budget_row.get("entity_compute_weight", 0) or 0)
        proxy_entities = 0
        for tier_row in fidelity_row.get("tiers") or []:
            if not isinstance(tier_row, dict):
                continue
            proxy_entities += int(tier_row.get("micro_entities_target", 0) or 0)
        proxy_compute = (
            int(tier_weights.get("coarse", 0) or 0)
            + int(tier_weights.get("medium", 0) or 0)
            + int(tier_weights.get("fine", 0) or 0)
            + (proxy_entities * entity_weight)
        )
        details["deterministic_proxy"] = {
            "budget_policy_id": str(budget_row.get("policy_id", "")),
            "fidelity_policy_id": str(fidelity_row.get("policy_id", "")),
            "proxy_entities": int(proxy_entities),
            "proxy_compute_units": int(proxy_compute),
        }

    ordered = sorted(findings, key=lambda row: (str(row.get("severity", "")), str(row.get("code", "")), str(row.get("message", ""))))
    return {
        "status": "pass",
        "message": "performx placeholder checks completed (warnings={})".format(len(ordered)),
        "findings": ordered,
        "details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PerformX placeholder checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()
    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_performx_check(repo_root=repo_root, profile=str(args.profile))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
