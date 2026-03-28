"""E224 silent leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E224_SILENT_LEAK_SMELL"


class SilentLeakSmell:
    analyzer_id = ANALYZER_ID


_LEAK_MUTATION_PATTERNS = (
    re.compile(r"\bprocess_start_leak\s*\(", re.IGNORECASE),
    re.compile(r"\bprocess_leak_tick\s*\(", re.IGNORECASE),
    re.compile(r"\bleak_state_rows\b", re.IGNORECASE),
)


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

    scan_roots = (
        os.path.join(repo_root, "src", "fluid"),
        os.path.join(repo_root, "src", "interior"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "fluid/network/fluid_network_engine.py",
        "tools/fluid/tool_run_fluid_stress.py",
        "tools/xstack/sessionx/process_runtime.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                if not any(pattern.search(text) for pattern in _LEAK_MUTATION_PATTERNS):
                    continue
                if ("leak_event_rows" in text) or ("decision_log_rows" in text) or ("safety_event_rows" in text):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="reliability.silent_leak_smell",
                        severity="RISK",
                        confidence=0.83,
                        file_path=rel_path,
                        line=1,
                        evidence=[
                            "leak mutation logic appears without explicit leak/event decision logging surface",
                            "missing leak_event_rows/decision_log_rows emission tokens",
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-ALL-FAILURES-LOGGED",
                            "INV-FLUID-FAILURE-THROUGH-SAFETY-OR-PROCESS",
                        ],
                        related_paths=[rel_path, "fluid/network/fluid_network_engine.py"],
                    )
                )
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
