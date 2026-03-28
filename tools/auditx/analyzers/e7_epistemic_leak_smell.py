"""E7 Epistemic leak smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E7_EPISTEMIC_LEAK_SMELL"
TARGET_NET_FILES = (
    "net/policies/policy_server_authoritative.py",
    "net/srz/shard_coordinator.py",
)
REQUIRED_NET_TOKENS = (
    "schema_name=\"net_perceived_delta\"",
    "epistemic_policy_id",
    "retention_policy_id",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json_object(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_root"
    return payload, ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in TARGET_NET_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.epistemic_leak_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["target net file missing for epistemic leak analysis"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NET-PERCEIVED-ONLY"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in REQUIRED_NET_TOKENS:
            if token not in text:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.epistemic_leak_smell",
                        severity="RISK",
                        confidence=0.85,
                        file_path=rel_path,
                        line=1,
                        evidence=["missing expected epistemic transport token '{}'".format(token)],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-PERCEIVED-ONLY", "INV-EPISTEMIC-POLICY-REQUIRED"],
                        related_paths=[rel_path],
                    )
                )
        for line_no, line in enumerate(text.splitlines(), start=1):
            lower = str(line).lower()
            if "ch.truth.overlay" in lower and "observe_truth" not in lower:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.epistemic_leak_smell",
                        severity="WARN",
                        confidence=0.65,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "truth overlay channel token found in network policy module",
                            str(line).strip()[:200],
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-PERCEIVED-ONLY"],
                        related_paths=[rel_path],
                    )
                )

    registry_path = "data/registries/epistemic_policy_registry.json"
    payload, err = _read_json_object(repo_root, registry_path)
    if err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.epistemic_leak_smell",
                severity="RISK",
                confidence=0.8,
                file_path=registry_path,
                line=1,
                evidence=["unable to parse epistemic policy registry JSON"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-EPISTEMIC-POLICY-REQUIRED"],
                related_paths=[registry_path],
            )
        )
        return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))

    rows = (((payload.get("record") or {}).get("policies")) or [])
    by_id = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("epistemic_policy_id", "")).strip()
        if policy_id:
            by_id[policy_id] = row

    required_forbidden = {
        "ep.policy.player_diegetic": {"ch.truth.overlay.terrain_height", "ch.truth.overlay.anchor_hash"},
        "ep.policy.spectator_limited": {"ch.truth.overlay.terrain_height", "ch.truth.overlay.anchor_hash"},
    }
    for policy_id in sorted(required_forbidden.keys()):
        row = dict(by_id.get(policy_id) or {})
        if not row:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.epistemic_leak_smell",
                    severity="WARN",
                    confidence=0.7,
                    file_path=registry_path,
                    line=1,
                    evidence=["required epistemic policy '{}' missing".format(policy_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-EPISTEMIC-POLICY-REQUIRED"],
                    related_paths=[registry_path],
                )
            )
            continue
        forbidden = set(str(item).strip() for item in (row.get("forbidden_channels") or []) if str(item).strip())
        missing_forbidden = sorted(required_forbidden[policy_id] - forbidden)
        if missing_forbidden:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.epistemic_leak_smell",
                    severity="WARN",
                    confidence=0.72,
                    file_path=registry_path,
                    line=1,
                    evidence=[
                        "policy '{}' missing expected forbidden channels".format(policy_id),
                        "missing={}".format(",".join(missing_forbidden)),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-EPISTEMIC-POLICY-REQUIRED"],
                    related_paths=[registry_path],
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

