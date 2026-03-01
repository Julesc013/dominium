"""E130 hidden privilege escalation smell analyzer."""

from __future__ import annotations

import json
import os
import re
from typing import List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E130_HIDDEN_PRIVILEGE_ESCALATION_SMELL"
WATCH_PREFIXES = (
    "src/",
    "docs/audit/TOPOLOGY_MAP.json",
)

TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"
CONTROL_PLANE_NODE_ID = "module:src/control/control_plane_engine.py"

PRIVILEGE_PATTERNS = (
    re.compile(r"\bprivilege_level\s*=\s*[\"']admin[\"']", re.IGNORECASE),
    re.compile(r"\bprivilege_level\s*==\s*[\"']admin[\"']", re.IGNORECASE),
    re.compile(r"\bentitlement\.control\.admin\b", re.IGNORECASE),
    re.compile(r"\bmeta_override\b", re.IGNORECASE),
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
            module_node_id = _module_node_id_for_path(rel_path, module_rows)
            for line_no, line in enumerate(text.splitlines(), start=1):
                snippet = str(line).strip()
                if not snippet or snippet.startswith("#"):
                    continue
                if not any(pattern.search(snippet) for pattern in PRIVILEGE_PATTERNS):
                    continue
                has_declared_dependency = module_node_id in dependency_nodes
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="security.hidden_privilege_escalation_smell",
                        severity="RISK" if has_declared_dependency else "VIOLATION",
                        confidence=0.9 if has_declared_dependency else 0.95,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "privilege escalation marker detected outside control subsystem",
                            snippet[:180],
                            "module_node_id={}".format(module_node_id or "missing"),
                        ],
                        suggested_classification="NEEDS_REVIEW" if has_declared_dependency else "INVALID",
                        recommended_action="ADD_RULE" if has_declared_dependency else "REWRITE",
                        related_invariants=[
                            "INV-CONTROL-INTENT-REQUIRED",
                            "INV-CONTROL-PLANE-ONLY-DISPATCH",
                        ],
                        related_paths=[rel_path, TOPOLOGY_REL],
                    )
                )
                break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

