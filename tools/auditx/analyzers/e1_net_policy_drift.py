"""E1 Net policy drift analyzer."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E1_NET_POLICY_DRIFT"
WATCH_PREFIXES = (
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_resync_strategy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "data/registries/anti_cheat_module_registry.json",
    "tools/xstack/sessionx/",
    "tools/xstack/serverx/",
    "tools/xstack/controlx/",
    "docs/net/",
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


def _registry_rows(repo_root: str, rel_path: str, key: str) -> Tuple[List[dict], str]:
    payload, err = _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
    if err:
        return [], err
    rows = (((payload.get("record") or {}).get(key)) or [])
    if not isinstance(rows, list):
        return [], "invalid_rows"
    return [row for row in rows if isinstance(row, dict)], ""


def _scan_policy_refs(repo_root: str) -> Dict[str, Set[str]]:
    out = {"policy.net": set(), "policy.ac": set()}
    token_re = re.compile(r'["\'](policy\.(?:net|ac)\.[a-z0-9_.-]+)["\']', re.IGNORECASE)
    roots = (
        os.path.join(repo_root, "tools", "xstack"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
    )
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, dirs, files in os.walk(root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                ext = os.path.splitext(name.lower())[1]
                if ext not in {".py", ".json", ".md", ".cpp", ".cc", ".c", ".hpp", ".h"}:
                    continue
                abs_path = os.path.join(walk_root, name)
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                for token in sorted(set(token_re.findall(text))):
                    if token.startswith("policy.net."):
                        out["policy.net"].add(token)
                    if token.startswith("policy.ac."):
                        out["policy.ac"].add(token)
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    replication_rows, replication_err = _registry_rows(
        repo_root=repo_root,
        rel_path="data/registries/net_replication_policy_registry.json",
        key="policies",
    )
    resync_rows, resync_err = _registry_rows(
        repo_root=repo_root,
        rel_path="data/registries/net_resync_strategy_registry.json",
        key="strategies",
    )
    anti_cheat_rows, anti_cheat_err = _registry_rows(
        repo_root=repo_root,
        rel_path="data/registries/anti_cheat_policy_registry.json",
        key="policies",
    )
    anti_cheat_module_rows, anti_cheat_module_err = _registry_rows(
        repo_root=repo_root,
        rel_path="data/registries/anti_cheat_module_registry.json",
        key="modules",
    )
    if replication_err or resync_err or anti_cheat_err or anti_cheat_module_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.policy_drift",
                severity="RISK",
                confidence=0.95,
                file_path="data/registries/net_replication_policy_registry.json",
                evidence=["One or more multiplayer policy registries are missing or invalid JSON."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                related_paths=[
                    "data/registries/net_replication_policy_registry.json",
                    "data/registries/net_resync_strategy_registry.json",
                    "data/registries/anti_cheat_policy_registry.json",
                    "data/registries/anti_cheat_module_registry.json",
                ],
            )
        )
        return findings

    replication_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in replication_rows
        if str(row.get("policy_id", "")).strip()
    )
    resync_ids = set(
        str(row.get("strategy_id", "")).strip()
        for row in resync_rows
        if str(row.get("strategy_id", "")).strip()
    )
    anti_cheat_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in anti_cheat_rows
        if str(row.get("policy_id", "")).strip()
    )
    module_ids = set(
        str(row.get("module_id", "")).strip()
        for row in anti_cheat_module_rows
        if str(row.get("module_id", "")).strip()
    )

    for row in replication_rows:
        policy_id = str(row.get("policy_id", "")).strip()
        strategy_id = str(row.get("resync_strategy_id", "")).strip()
        if policy_id and strategy_id and strategy_id not in resync_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.policy_drift",
                    severity="RISK",
                    confidence=0.9,
                    file_path="data/registries/net_replication_policy_registry.json",
                    evidence=["policy_id={} references missing resync_strategy_id={}".format(policy_id, strategy_id)],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                    related_paths=[
                        "data/registries/net_replication_policy_registry.json",
                        "data/registries/net_resync_strategy_registry.json",
                    ],
                )
            )

    for row in resync_rows:
        strategy_id = str(row.get("strategy_id", "")).strip()
        for policy_id in sorted(set(str(item).strip() for item in (row.get("supported_policies") or []) if str(item).strip())):
            if policy_id not in replication_ids:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.policy_drift",
                        severity="RISK",
                        confidence=0.89,
                        file_path="data/registries/net_resync_strategy_registry.json",
                        evidence=["strategy_id={} references missing policy_id={}".format(strategy_id, policy_id)],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                        related_paths=[
                            "data/registries/net_resync_strategy_registry.json",
                            "data/registries/net_replication_policy_registry.json",
                        ],
                    )
                )

    for row in anti_cheat_rows:
        policy_id = str(row.get("policy_id", "")).strip()
        for module_id in sorted(set(str(item).strip() for item in (row.get("modules_enabled") or []) if str(item).strip())):
            if module_id not in module_ids:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.policy_drift",
                        severity="RISK",
                        confidence=0.9,
                        file_path="data/registries/anti_cheat_policy_registry.json",
                        evidence=["policy_id={} references missing module_id={}".format(policy_id, module_id)],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                        related_paths=[
                            "data/registries/anti_cheat_policy_registry.json",
                            "data/registries/anti_cheat_module_registry.json",
                        ],
                    )
                )

    refs = _scan_policy_refs(repo_root=repo_root)
    for policy_id in sorted(refs["policy.net"]):
        if policy_id not in replication_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.policy_drift",
                    severity="WARN",
                    confidence=0.82,
                    file_path="tools/xstack/sessionx/runner.py",
                    evidence=["Repository reference to undeclared replication policy '{}'".format(policy_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                    related_paths=[
                        "data/registries/net_replication_policy_registry.json",
                    ],
                )
            )
    for policy_id in sorted(refs["policy.ac"]):
        if policy_id not in anti_cheat_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.policy_drift",
                    severity="WARN",
                    confidence=0.82,
                    file_path="tools/xstack/sessionx/runner.py",
                    evidence=["Repository reference to undeclared anti-cheat policy '{}'".format(policy_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-NET-POLICY-REGISTRIES-VALID"],
                    related_paths=[
                        "data/registries/anti_cheat_policy_registry.json",
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
