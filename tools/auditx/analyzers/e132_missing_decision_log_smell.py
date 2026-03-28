"""E132 missing decision-log smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E132_MISSING_DECISION_LOG_SMELL"
WATCH_PREFIXES = (
    "src/",
    "docs/audit/TOPOLOGY_MAP.json",
)

TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"
CONTROL_PLANE_REL = "control/control_plane_engine.py"
CONTROL_PLANE_NODE_ID = "module:control/control_plane_engine.py"
ALLOWED_UNLOGGED_MARKERS = (
    "control_intent_id is required",
    "requested_action_id is required",
    "requested action is unknown",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_lines(repo_root: str, rel_path: str) -> List[str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []


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

    lines = _read_lines(repo_root, CONTROL_PLANE_REL)
    if not lines:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_decision_log_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=CONTROL_PLANE_REL,
                line=1,
                evidence=["missing control plane file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[CONTROL_PLANE_REL],
            )
        )
        return findings

    full_text = "\n".join(lines)
    for token in ("_write_decision_log(", "_decision_log_row(", "decision_log_ref"):
        if token in full_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_decision_log_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=CONTROL_PLANE_REL,
                line=1,
                evidence=["missing decision-log integration token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[CONTROL_PLANE_REL],
            )
        )

    for line_no, line in enumerate(lines, start=1):
        snippet = str(line).strip()
        if '"result": "refused"' not in snippet:
            continue
        window_start = max(1, line_no - 20)
        context = "\n".join(lines[window_start - 1 : line_no])
        if "_finalize_refusal(" in context or "_write_decision_log(" in context:
            continue
        if any(marker in context for marker in ALLOWED_UNLOGGED_MARKERS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_decision_log_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=CONTROL_PLANE_REL,
                line=line_no,
                evidence=["refusal path not tied to decision-log emission", snippet[:180]],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[CONTROL_PLANE_REL],
            )
        )

    topology = _read_topology(repo_root)
    module_rows = _module_rows(topology)
    dependency_nodes = _control_dependency_nodes(topology)

    src_root = os.path.join(repo_root, "src")
    if not os.path.isdir(src_root):
        return sorted(
            findings,
            key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
        )

    for walk_root, dirs, files in os.walk(src_root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
            if rel_path.startswith("src/control/"):
                continue
            lines_local = _read_lines(repo_root, rel_path)
            if not lines_local:
                continue
            text_local = "\n".join(lines_local).lower()
            if "build_control_resolution(" not in text_local:
                continue
            module_node_id = _module_node_id_for_path(rel_path, module_rows)
            if module_node_id in dependency_nodes:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_decision_log_smell",
                    severity="VIOLATION",
                    confidence=0.91,
                    file_path=rel_path,
                    line=1,
                    evidence=[
                        "module uses build_control_resolution without declared control dependency",
                        "module_node_id={}".format(module_node_id or "missing"),
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DECISION-LOG-MANDATORY", "INV-CONTROL-PLANE-ONLY-DISPATCH"],
                    related_paths=[rel_path, TOPOLOGY_REL],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

