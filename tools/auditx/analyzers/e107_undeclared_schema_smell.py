"""E107 undeclared schema smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List, Set

from analyzers.base import make_finding


ANALYZER_ID = "E107_UNDECLARED_SCHEMA_SMELL"
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


def _schema_paths(repo_root: str) -> List[str]:
    out: List[str] = []
    for root_name, suffix in (("schema", ".schema"), ("schemas", ".schema.json")):
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(suffix):
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
                category="architecture.undeclared_schema_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=TOPOLOGY_REL,
                line=1,
                evidence=["missing topology nodes for schema declaration checks"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-SCHEMA"],
                related_paths=[TOPOLOGY_REL],
            )
        )
        return findings

    declared_schema_paths: Set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("node_kind", "")).strip() != "schema":
            continue
        token = _norm(str(node.get("path", "")).strip())
        if token:
            declared_schema_paths.add(token)

    for path in _schema_paths(repo_root):
        if path in declared_schema_paths:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_schema_smell",
                severity="RISK",
                confidence=0.91,
                file_path=path,
                line=1,
                evidence=["schema path missing from topology schema nodes"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-SCHEMA"],
                related_paths=[path, TOPOLOGY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

