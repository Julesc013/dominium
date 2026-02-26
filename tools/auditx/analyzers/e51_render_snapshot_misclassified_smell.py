"""E51 render snapshot misclassified smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E51_RENDER_SNAPSHOT_MISCLASSIFIED_SMELL"
DOC_PATH = "docs/render/RENDER_SNAPSHOT_ARTIFACTS.md"
PIPELINE_PATHS = (
    "src/client/render/snapshot_capture.py",
    "tools/render/tool_render_capture.py",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    doc_abs = os.path.join(repo_root, DOC_PATH.replace("/", os.sep))
    doc_text = _read_text(doc_abs)
    if not doc_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="render.render_snapshot_misclassified_smell",
                severity="RISK",
                confidence=0.95,
                file_path=DOC_PATH,
                line=1,
                evidence=["Render snapshot artifact taxonomy doc missing."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RENDER_SNAPSHOTS_DERIVED_ONLY"],
                related_paths=[DOC_PATH],
            )
        )
    elif "DERIVED" not in doc_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="render.render_snapshot_misclassified_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=DOC_PATH,
                line=1,
                evidence=["Render snapshot doc does not classify artifacts as DERIVED."],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-RENDER_SNAPSHOTS_DERIVED_ONLY"],
                related_paths=[DOC_PATH],
            )
        )

    derived_anchor = False
    for rel_path in PIPELINE_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        text = _read_text(abs_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="render.render_snapshot_misclassified_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["Render snapshot pipeline file missing."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-RENDER_SNAPSHOTS_DERIVED_ONLY"],
                    related_paths=[rel_path],
                )
            )
            continue
        lower = text.lower()
        if "run_meta" in lower and "render_snapshots" in lower:
            derived_anchor = True
        if "truth_model" in lower or "truthmodel" in lower or "process_runtime" in lower:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="render.render_snapshot_misclassified_smell",
                    severity="VIOLATION",
                    confidence=0.92,
                    file_path=rel_path,
                    line=1,
                    evidence=["Render snapshot pipeline references forbidden truth/process symbols."],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-RENDER_SNAPSHOTS_DERIVED_ONLY"],
                    related_paths=[rel_path],
                )
            )
    if not derived_anchor:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="render.render_snapshot_misclassified_smell",
                severity="RISK",
                confidence=0.86,
                file_path="src/client/render/snapshot_capture.py",
                line=1,
                evidence=["No deterministic derived storage anchor found (run_meta/render_snapshots)."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RENDER_SNAPSHOTS_DERIVED_ONLY"],
                related_paths=["src/client/render/snapshot_capture.py", "tools/render/tool_render_capture.py"],
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
