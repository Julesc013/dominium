"""E106 undeclared subsystem smell analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Set

from analyzers.base import make_finding


ANALYZER_ID = "E106_UNDECLARED_SUBSYSTEM_SMELL"
TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_topology(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, TOPOLOGY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _existing_subsystems(repo_root: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for root_name in ("engine", "game", "client", "server", "platform", "launcher", "setup"):
        abs_root = os.path.join(repo_root, root_name)
        if os.path.isdir(abs_root):
            out[root_name] = root_name
    for root_name in ("src", "tools"):
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for entry in sorted(os.listdir(abs_root)):
            abs_path = os.path.join(abs_root, entry)
            if not os.path.isdir(abs_path) or entry.startswith(".") or entry == "__pycache__":
                continue
            out[entry] = _norm("{}/{}".format(root_name, entry))
    return dict(sorted(out.items(), key=lambda item: str(item[0])))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    topology = _read_topology(repo_root)
    nodes = list(topology.get("nodes") or [])
    if not nodes:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_subsystem_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=TOPOLOGY_REL,
                line=1,
                evidence=["missing topology nodes"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TOPOLOGY-MAP-PRESENT"],
                related_paths=[TOPOLOGY_REL],
            )
        )
        return findings

    declared_subsystems: Set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("node_kind", "")).strip() not in ("module", "tool"):
            continue
        owner = str(node.get("owner_subsystem", "")).strip()
        if owner:
            declared_subsystems.add(owner)

    for subsystem, path in _existing_subsystems(repo_root).items():
        if subsystem in declared_subsystems:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_subsystem_smell",
                severity="RISK",
                confidence=0.9,
                file_path=path,
                line=1,
                evidence=[
                    "subsystem '{}' is present in repository but missing from topology owner_subsystem declarations".format(
                        subsystem
                    )
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TOPOLOGY-MAP-PRESENT"],
                related_paths=[path, TOPOLOGY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

