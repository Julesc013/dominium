"""E131 silent downgrade smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E131_SILENT_DOWNGRADE_SMELL"
WATCH_PREFIXES = (
    "src/",
    "docs/audit/TOPOLOGY_MAP.json",
)

TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"
CONTROL_PLANE_REL = "control/control_plane_engine.py"
CONTROL_PLANE_NODE_ID = "module:control/control_plane_engine.py"
DOWNGRADE_MARKERS = (
    "downgrade.",
    "budget_insufficient",
    "rank_fairness",
    "epistemic_limits",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_topology(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, TOPOLOGY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _module_rows(topology_payload: dict) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for row in list(topology_payload.get("nodes") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("node_kind", "")).strip() != "module":
            continue
        module_path = _norm(str(row.get("path", "")).strip())
        node_id = str(row.get("node_id", "")).strip()
        if module_path and node_id:
            out.append((module_path, node_id))
    return sorted(out, key=lambda item: len(str(item[0])), reverse=True)


def _module_node_id_for_path(rel_path: str, module_rows: List[Tuple[str, str]]) -> str:
    rel = _norm(rel_path)
    for module_path, node_id in module_rows:
        if rel == module_path or rel.startswith(module_path + "/"):
            return str(node_id)
    return ""


def _control_dependency_nodes(topology_payload: dict) -> Set[str]:
    out: Set[str] = set()
    for row in list(topology_payload.get("edges") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("edge_kind", "")).strip() not in ("depends_on", "consumes"):
            continue
        if str(row.get("to_node_id", "")).strip() != CONTROL_PLANE_NODE_ID:
            continue
        from_node_id = str(row.get("from_node_id", "")).strip()
        if from_node_id:
            out.add(from_node_id)
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    control_text = _read_text(repo_root, CONTROL_PLANE_REL)
    if not control_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=CONTROL_PLANE_REL,
                line=1,
                evidence=["missing control-plane downgrade path file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC", "INV-DECISION-LOG-MANDATORY"],
                related_paths=[CONTROL_PLANE_REL],
            )
        )
        return findings

    for token in ("negotiate_request(", "downgrade_entries", "_write_decision_log("):
        if token in control_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=CONTROL_PLANE_REL,
                line=1,
                evidence=["missing control-plane downgrade/logging token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC", "INV-DECISION-LOG-MANDATORY"],
                related_paths=[CONTROL_PLANE_REL],
            )
        )

    topology = _read_topology(repo_root)
    module_rows = _module_rows(topology)
    dependency_nodes = _control_dependency_nodes(topology)

    src_root = os.path.join(repo_root, "src")
    if not os.path.isdir(src_root):
        return findings

    for walk_root, dirs, files in os.walk(src_root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
            if rel_path.startswith(("src/control/", "tools/", "docs/")):
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            lowered = text.lower()
            if not any(marker in lowered for marker in DOWNGRADE_MARKERS):
                continue
            module_node_id = _module_node_id_for_path(rel_path, module_rows)
            has_declared_dependency = module_node_id in dependency_nodes
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.silent_downgrade_smell",
                    severity="RISK" if has_declared_dependency else "VIOLATION",
                    confidence=0.88 if has_declared_dependency else 0.94,
                    file_path=rel_path,
                    line=1,
                    evidence=[
                        "downgrade marker found outside control subsystem",
                        "module_node_id={}".format(module_node_id or "missing"),
                    ],
                    suggested_classification="NEEDS_REVIEW" if has_declared_dependency else "INVALID",
                    recommended_action="ADD_RULE" if has_declared_dependency else "REWRITE",
                    related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC", "INV-DECISION-LOG-MANDATORY"],
                    related_paths=[rel_path, CONTROL_PLANE_REL, TOPOLOGY_REL],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

