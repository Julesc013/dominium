"""E88 routing duplication smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E88_ROUTING_DUPLICATION_SMELL"
CORE_ROUTING_PATH = "core/graph/routing_engine.py"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    core_text = _read_text(repo_root, CORE_ROUTING_PATH)
    if not core_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.routing_duplication_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=CORE_ROUTING_PATH,
                line=1,
                evidence=["missing core routing substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NETWORKGRAPH-ONLY"],
                related_paths=[CORE_ROUTING_PATH],
            )
        )
        return findings

    src_root = os.path.join(repo_root, "src")
    for root, _dirs, files in os.walk(src_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path.startswith("src/core/graph/"):
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            has_custom_routing_tokens = (
                "heapq.heappush(" in text
                and "route_policy_id" in text
                and "path_edge_ids" in text
                and "path_node_ids" in text
            )
            imports_core_graph = (
                "from core.graph" in text
                or "import core.graph" in text
                or "core.graph." in text
            )
            if has_custom_routing_tokens and (not imports_core_graph):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.routing_duplication_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=1,
                        evidence=["routing/path traversal tokens detected outside core routing substrate"],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NETWORKGRAPH-ONLY"],
                        related_paths=[rel_path, CORE_ROUTING_PATH],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

