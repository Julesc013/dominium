"""E6 Shard-map drift analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E6_SHARD_MAP_DRIFT"
WATCH_PREFIXES = (
    "data/registries/shard_map_registry.json",
    "data/registries/perception_interest_policy_registry.json",
    "data/registries/net_server_policy_registry.json",
    "src/net/srz/",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(path: str) -> Tuple[Dict[str, object], str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_object"
    return payload, ""


def _record_rows(repo_root: str, rel_path: str, key: str) -> Tuple[List[dict], str]:
    payload, err = _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
    if err:
        return [], err
    rows = (((payload.get("record") or {}).get(key)) or [])
    if not isinstance(rows, list):
        return [], "invalid_rows"
    return [dict(row) for row in rows if isinstance(row, dict)], ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    shard_rows, shard_err = _record_rows(repo_root, "data/registries/shard_map_registry.json", "shard_maps")
    perception_rows, perception_err = _record_rows(
        repo_root,
        "data/registries/perception_interest_policy_registry.json",
        "policies",
    )
    server_rows, server_err = _record_rows(repo_root, "data/registries/net_server_policy_registry.json", "policies")
    if shard_err or perception_err or server_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.shard_map_drift",
                severity="RISK",
                confidence=0.94,
                file_path="data/registries/shard_map_registry.json",
                evidence=["One or more SRZ hybrid registry files are missing or invalid JSON."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-NET-POLICY-REGISTRIES-VALID",
                    "INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                ],
                related_paths=[
                    "data/registries/shard_map_registry.json",
                    "data/registries/perception_interest_policy_registry.json",
                    "data/registries/net_server_policy_registry.json",
                ],
            )
        )
        return findings

    shard_ids: Set[str] = set()
    for row in shard_rows:
        shard_map_id = str(row.get("shard_map_id", "")).strip()
        if shard_map_id:
            shard_ids.add(shard_map_id)

    perception_ids: Set[str] = set()
    for row in perception_rows:
        policy_id = str(row.get("policy_id", "")).strip()
        if policy_id:
            perception_ids.add(policy_id)

    for row in sorted(server_rows, key=lambda item: str(item.get("policy_id", ""))):
        server_policy_id = str(row.get("policy_id", "")).strip() or "<unknown>"
        allowed_replication = sorted(
            set(str(item).strip() for item in (row.get("allowed_replication_policy_ids") or []) if str(item).strip())
        )
        if "policy.net.srz_hybrid" not in allowed_replication:
            continue
        ext = dict(row.get("extensions") or {})
        shard_map_id = str(ext.get("default_shard_map_id", "")).strip()
        if not shard_map_id or shard_map_id not in shard_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.shard_map_drift",
                    severity="RISK",
                    confidence=0.9,
                    file_path="data/registries/net_server_policy_registry.json",
                    evidence=[
                        "server policy {} allows policy.net.srz_hybrid but has invalid extensions.default_shard_map_id={}".format(
                            server_policy_id,
                            shard_map_id or "<empty>",
                        )
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP"],
                    related_paths=[
                        "data/registries/net_server_policy_registry.json",
                        "data/registries/shard_map_registry.json",
                    ],
                )
            )
        perception_policy_id = str(ext.get("perception_interest_policy_id", "")).strip()
        if not perception_policy_id or perception_policy_id not in perception_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.shard_map_drift",
                    severity="RISK",
                    confidence=0.9,
                    file_path="data/registries/net_server_policy_registry.json",
                    evidence=[
                        "server policy {} allows policy.net.srz_hybrid but has invalid extensions.perception_interest_policy_id={}".format(
                            server_policy_id,
                            perception_policy_id or "<empty>",
                        )
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP"],
                    related_paths=[
                        "data/registries/net_server_policy_registry.json",
                        "data/registries/perception_interest_policy_registry.json",
                    ],
                )
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

