"""E108 undeclared registry smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List, Set

from analyzers.base import make_finding


ANALYZER_ID = "E108_UNDECLARED_REGISTRY_SMELL"
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


def _registry_paths(repo_root: str) -> List[str]:
    out: List[str] = []
    root = os.path.join(repo_root, "data", "registries")
    if not os.path.isdir(root):
        return out
    for walk_root, dirs, files in os.walk(root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            out.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
    return sorted(set(out))


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
                category="architecture.undeclared_registry_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=TOPOLOGY_REL,
                line=1,
                evidence=["missing topology nodes for registry declaration checks"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-REGISTRY"],
                related_paths=[TOPOLOGY_REL],
            )
        )
        return findings

    declared_registry_paths: Set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("node_kind", "")).strip() != "registry":
            continue
        token = _norm(str(node.get("path", "")).strip())
        if token:
            declared_registry_paths.add(token)

    for path in _registry_paths(repo_root):
        if path in declared_registry_paths:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_registry_smell",
                severity="RISK",
                confidence=0.91,
                file_path=path,
                line=1,
                evidence=["registry path missing from topology registry nodes"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-REGISTRY"],
                related_paths=[path, TOPOLOGY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

