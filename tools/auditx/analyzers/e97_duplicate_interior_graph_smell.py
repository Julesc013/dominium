"""E97 duplicate interior graph smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E97_DUPLICATE_INTERIOR_GRAPH_SMELL"
INTERIOR_ENGINE_PATH = "interior/interior_engine.py"


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

    core_text = _read_text(repo_root, INTERIOR_ENGINE_PATH)
    if not core_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interior.duplicate_interior_graph_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=INTERIOR_ENGINE_PATH,
                line=1,
                evidence=["missing interior graph substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-ADHOC-OCCLUSION"],
                related_paths=[INTERIOR_ENGINE_PATH],
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
            if rel_path.startswith(("src/interior/", "src/core/graph/")):
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            has_interior_graph_logic = (
                "from_volume_id" in text
                and "to_volume_id" in text
                and "portal_type_id" in text
                and ("path_exists(" in text or "reachable_volumes(" in text)
            )
            if not has_interior_graph_logic:
                continue
            if "from interior" in text or "import interior" in text or "interior." in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interior.duplicate_interior_graph_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["interior graph/portal traversal logic detected outside src/interior"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-OCCLUSION"],
                    related_paths=[rel_path, INTERIOR_ENGINE_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

