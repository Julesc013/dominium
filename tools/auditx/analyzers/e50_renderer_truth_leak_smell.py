"""E50 renderer truth leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E50_RENDERER_TRUTH_LEAK_SMELL"
TARGETS = (
    "src/client/render/render_model_adapter.py",
    "src/client/render/representation_resolver.py",
    "src/client/render/snapshot_capture.py",
    "src/client/render/renderers/null_renderer.py",
    "src/client/render/renderers/software_renderer.py",
    "tools/xstack/sessionx/render_model.py",
    "tools/render/tool_render_capture.py",
    "tools/render/render_cli.py",
)
FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state|process_runtime)\b", re.IGNORECASE)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    for rel_path in TARGETS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="render.renderer_truth_leak_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["Renderer boundary file missing; truth-isolation cannot be validated."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-RENDERER-CONSUMES-RENDERMODEL-ONLY"],
                    related_paths=[rel_path],
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            snippet = str(line).strip()
            if not snippet or not FORBIDDEN_PATTERN.search(snippet):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="render.renderer_truth_leak_smell",
                    severity="VIOLATION",
                    confidence=0.94,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Renderer path references forbidden truth/process symbol.",
                        snippet[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-RENDERER-CONSUMES-RENDERMODEL-ONLY"],
                    related_paths=[rel_path],
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
