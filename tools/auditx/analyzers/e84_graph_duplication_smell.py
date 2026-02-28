"""E84 graph duplication smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E84_GRAPH_DUPLICATION_SMELL"
WATCH_PREFIXES = ("src/", "docs/architecture/")


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

    core_path = "src/core/graph/network_graph_engine.py"
    core_text = _read_text(repo_root, core_path)
    if not core_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.graph_duplication_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=core_path,
                line=1,
                evidence=["missing core graph substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DUPLICATE-GRAPH-SUBSTRATES"],
                related_paths=[core_path],
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
            if (
                "heapq.heappush(" in text
                and "from_node_id" in text
                and "to_node_id" in text
                and "edge_id" in text
            ):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.graph_duplication_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=1,
                        evidence=["graph/path traversal tokens outside core graph substrate"],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-DUPLICATE-GRAPH-SUBSTRATES"],
                        related_paths=[rel_path, core_path],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

