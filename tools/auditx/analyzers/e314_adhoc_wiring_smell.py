"""E314 ad hoc wiring smell analyzer for LOGIC-3."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E314_AD_HOC_WIRING_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e314_adhoc_wiring_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/",
    "tools/xstack/sessionx/process_runtime.py",
)

_ALLOWED_PATHS = {
    "src/logic/network/logic_network_engine.py",
    "src/logic/network/logic_network_validator.py",
    "src/logic/network/instrumentation_binding.py",
    "src/logic/network/__init__.py",
    "src/logic/__init__.py",
    "tools/xstack/sessionx/process_runtime.py",
}
_PATTERNS = (
    re.compile(r"\blogic_network_graph_rows\b"),
    re.compile(r"\bfrom_node_id\b"),
    re.compile(r"\bto_node_id\b"),
    re.compile(r"\b(?:node_kind|edge_kind)\b"),
)


class AdHocWiringSmell:
    analyzer_id = ANALYZER_ID


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

    abs_root = os.path.join(repo_root, "src", "logic")
    if os.path.isdir(abs_root):
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path in _ALLOWED_PATHS:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                matches = sum(1 for pattern in _PATTERNS if pattern.search(text))
                if matches < 2:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="logic.adhoc_wiring_smell",
                        severity="VIOLATION",
                        confidence=0.95,
                        file_path=rel_path,
                        line=1,
                        evidence=["logic topology payload appears outside sanctioned network modules", rel_path],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-LOGIC-WIRING-USES-NETWORKGRAPH"],
                        related_paths=[rel_path, "src/logic/network/logic_network_engine.py"],
                    )
                )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
