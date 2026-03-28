"""E137 structural bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E137_STRUCTURAL_BYPASS_SMELL"
RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
MECH_ENGINE_REL = "mechanics/structural_graph_engine.py"

_FAILURE_ASSIGN_RE = re.compile(r"failure_state[^\n=]*=\s*[\"']failed[\"']", re.IGNORECASE)


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

    runtime_text = _read_text(repo_root, RUNTIME_REL)
    mech_text = _read_text(repo_root, MECH_ENGINE_REL)
    if (not runtime_text) or (not mech_text):
        missing = RUNTIME_REL if not runtime_text else MECH_ENGINE_REL
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.structural_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=missing,
                line=1,
                evidence=["missing mechanics runtime/engine integration file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-STRUCTURAL-FAILURE-THROUGH-MECH"],
                related_paths=[RUNTIME_REL, MECH_ENGINE_REL],
            )
        )
        return findings

    required_tokens = (
        'elif process_id == "process.mechanics_fracture":',
        'elif process_id == "process.mechanics_tick":',
        "evaluate_structural_graphs(",
    )
    for token in required_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.structural_bypass_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=RUNTIME_REL,
                line=1,
                evidence=["missing mechanics process routing token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-STRUCTURAL-FAILURE-THROUGH-MECH"],
                related_paths=[RUNTIME_REL],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools"),
    )
    skip_prefixes = (
        "src/mechanics/",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if "structural" not in snippet.lower():
                        continue
                    if not _FAILURE_ASSIGN_RE.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.structural_bypass_smell",
                            severity="RISK",
                            confidence=0.88,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["structural failure assignment outside mechanics fracture process", snippet[:180]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-STRUCTURAL-FAILURE-THROUGH-MECH"],
                            related_paths=[rel_path, RUNTIME_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

