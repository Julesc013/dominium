"""E129 control-plane bypass smell analyzer."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E129_CONTROL_PLANE_BYPASS_SMELL"
WATCH_PREFIXES = (
    "src/",
    "docs/audit/TOPOLOGY_MAP.json",
)

TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"
CONTROL_PLANE_NODE_ID = "module:src/control/control_plane_engine.py"

DIRECT_PROCESS_CALL_RE = re.compile(r"\b(?:run_process|execute_process|runtime_execute_intent|execute_intent)\s*\(")
PROCESS_LITERAL_RE = re.compile(r"[\"']process\.[A-Za-z0-9_.-]+[\"']")
CONTROL_USAGE_TOKENS = (
    "from src.control",
    "import src.control",
    "src.control.",
    "build_control_intent(",
    "build_control_resolution(",
)
ALLOWED_DIRECT_DISPATCH_PATHS = {
    "src/client/interaction/interaction_dispatch.py",
    "src/net/policies/policy_server_authoritative.py",
    "src/net/srz/shard_coordinator.py",
}


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
        if not module_path or not node_id:
            continue
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
    if not module_rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.control_plane_bypass_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=TOPOLOGY_REL,
                line=1,
                evidence=["missing module declarations in topology map"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TOPOLOGY-MAP-PRESENT", "INV-CONTROL-PLANE-ONLY-DISPATCH"],
                related_paths=[TOPOLOGY_REL],
            )
        )
        return findings

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
            module_node_id = _module_node_id_for_path(rel_path, module_rows)
            has_control_usage = any(token in lowered for token in CONTROL_USAGE_TOKENS)

            if has_control_usage and module_node_id not in dependency_nodes:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.control_plane_bypass_smell",
                        severity="VIOLATION",
                        confidence=0.93,
                        file_path=rel_path,
                        line=1,
                        evidence=[
                            "control-plane usage detected without declared topology dependency",
                            "module_node_id={}".format(module_node_id or "missing"),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=[
                            "INV-CONTROL-PLANE-ONLY-DISPATCH",
                            "INV-CONTROL-INTENT-REQUIRED",
                        ],
                        related_paths=[rel_path, TOPOLOGY_REL],
                    )
                )

            if rel_path in ALLOWED_DIRECT_DISPATCH_PATHS:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                snippet = str(line).strip()
                if not snippet or snippet.startswith("#"):
                    continue
                if not DIRECT_PROCESS_CALL_RE.search(snippet):
                    continue
                if not PROCESS_LITERAL_RE.search(snippet):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.control_plane_bypass_smell",
                        severity="VIOLATION",
                        confidence=0.95,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "direct process dispatch detected outside control-plane allowlist",
                            snippet[:180],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH", "INV-CONTROL-INTENT-REQUIRED"],
                        related_paths=[rel_path, "src/control/control_plane_engine.py"],
                    )
                )
                break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

