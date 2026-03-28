"""E89 non-deterministic routing smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E89_NONDETERMINISTIC_ROUTING_SMELL"
ROUTING_ENGINE_PATH = "core/graph/routing_engine.py"
GRAPH_ENGINE_PATH = "core/graph/network_graph_engine.py"

REQUIRED_ROUTING_TOKENS = (
    "build_route_cache_key(",
    "canonical_sha256(",
    "query_route_result(",
    "path_edge_ids",
    "path_node_ids",
    "constraints_hash",
    "sorted(",
)
REQUIRED_GRAPH_TOKENS = (
    "heapq.heappush(",
    "next_tie = \"|\".join(next_route)",
    "sorted(",
)
FORBIDDEN_NONDET_TOKENS = (
    "time.time(",
    "datetime.now(",
    "uuid.uuid4(",
    "random.",
    "secrets.",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(*, findings, text: str, path: str, tokens, invariant_id: str) -> None:
    for token in tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_routing_smell",
                severity="RISK",
                confidence=0.88,
                file_path=path,
                line=1,
                evidence=["missing deterministic routing token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=[invariant_id],
                related_paths=[path],
            )
        )


def _append_nondet_token_findings(*, findings, text: str, path: str, invariant_id: str) -> None:
    for token in FORBIDDEN_NONDET_TOKENS:
        if token not in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_routing_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=path,
                line=1,
                evidence=["non-deterministic token in routing substrate", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
                related_paths=[path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    routing_text = _read_text(repo_root, ROUTING_ENGINE_PATH)
    if not routing_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_routing_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=ROUTING_ENGINE_PATH,
                line=1,
                evidence=["missing core routing substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NETWORKGRAPH-ONLY"],
                related_paths=[ROUTING_ENGINE_PATH],
            )
        )
    else:
        _append_missing_token_findings(
            findings=findings,
            text=routing_text,
            path=ROUTING_ENGINE_PATH,
            tokens=REQUIRED_ROUTING_TOKENS,
            invariant_id="INV-NETWORKGRAPH-ONLY",
        )
        _append_nondet_token_findings(
            findings=findings,
            text=routing_text,
            path=ROUTING_ENGINE_PATH,
            invariant_id="INV-NETWORKGRAPH-ONLY",
        )

    graph_text = _read_text(repo_root, GRAPH_ENGINE_PATH)
    if not graph_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_routing_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=GRAPH_ENGINE_PATH,
                line=1,
                evidence=["missing core graph substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NETWORKGRAPH-ONLY"],
                related_paths=[GRAPH_ENGINE_PATH],
            )
        )
    else:
        _append_missing_token_findings(
            findings=findings,
            text=graph_text,
            path=GRAPH_ENGINE_PATH,
            tokens=REQUIRED_GRAPH_TOKENS,
            invariant_id="INV-NETWORKGRAPH-ONLY",
        )
        _append_nondet_token_findings(
            findings=findings,
            text=graph_text,
            path=GRAPH_ENGINE_PATH,
            invariant_id="INV-NETWORKGRAPH-ONLY",
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

