"""E61 nondeterministic graph order smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E61_NONDETERMINISTIC_GRAPH_ORDER_SMELL"
BLUEPRINT_ENGINE_PATH = "materials/blueprint_engine.py"
BLUEPRINT_TOOL_PATH = "tools/materials/tool_blueprint_compile.py"


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

    blueprint_engine_text = _read_text(repo_root, BLUEPRINT_ENGINE_PATH)
    blueprint_tool_text = _read_text(repo_root, BLUEPRINT_TOOL_PATH)
    required_engine_tokens = (
        "sorted(",
        "compile_blueprint_artifacts(",
        "blueprint_compile_cache_key(",
        "edge_id",
        "node_id",
    )
    required_tool_tokens = (
        "cache_key",
        "pack_lock_hash",
        "compile_blueprint_artifacts(",
    )

    if not blueprint_engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_graph_order_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=BLUEPRINT_ENGINE_PATH,
                line=1,
                evidence=["blueprint engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DETERMINISTIC-BLUEPRINT-COMPILATION"],
                related_paths=[BLUEPRINT_ENGINE_PATH],
            )
        )
    else:
        for token in required_engine_tokens:
            if token in blueprint_engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.nondeterministic_graph_order_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=BLUEPRINT_ENGINE_PATH,
                    line=1,
                    evidence=["blueprint engine missing deterministic ordering token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DETERMINISTIC-BLUEPRINT-COMPILATION"],
                    related_paths=[BLUEPRINT_ENGINE_PATH],
                )
            )

    if not blueprint_tool_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_graph_order_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=BLUEPRINT_TOOL_PATH,
                line=1,
                evidence=["blueprint compile tool missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DETERMINISTIC-BLUEPRINT-COMPILATION"],
                related_paths=[BLUEPRINT_TOOL_PATH],
            )
        )
    else:
        for token in required_tool_tokens:
            if token in blueprint_tool_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.nondeterministic_graph_order_smell",
                    severity="RISK",
                    confidence=0.83,
                    file_path=BLUEPRINT_TOOL_PATH,
                    line=1,
                    evidence=["blueprint compile tool missing deterministic cache/provenance token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DETERMINISTIC-BLUEPRINT-COMPILATION"],
                    related_paths=[BLUEPRINT_TOOL_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
