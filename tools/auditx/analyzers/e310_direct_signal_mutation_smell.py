"""E310 direct-signal-mutation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E310_DIRECT_SIGNAL_MUTATION_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e310_direct_signal_mutation_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/",
    "tools/xstack/sessionx/process_runtime.py",
    "data/registries/process_registry.json",
)

_ALLOWED_PATHS = {
    "src/logic/signal/signal_store.py",
    "tools/xstack/sessionx/process_runtime.py",
}
_DIRECT_MUTATION_PATTERNS = (
    re.compile(r'\["logic_signal_rows"\]\s*='),
    re.compile(r'\["logic_signal_store_state"\]\s*='),
    re.compile(r'\["logic_signal_change_records"\]\s*='),
    re.compile(r'\["logic_signal_trace_artifacts"\]\s*='),
    re.compile(r'\["logic_signal_coupling_change_rows"\]\s*='),
    re.compile(r'\["logic_signal_compute_runtime_state"\]\s*='),
)


class DirectSignalMutationSmell:
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

    for root_rel in ("src", "tools"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path in _ALLOWED_PATHS or rel_path.startswith("tools/xstack/testx/tests/"):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for pattern in _DIRECT_MUTATION_PATTERNS:
                    match = pattern.search(text)
                    if not match:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="logic.direct_signal_mutation_smell",
                            severity="VIOLATION",
                            confidence=0.93,
                            file_path=rel_path,
                            line=1,
                            evidence=["logic signal state mutated outside canonical signal process/store path", match.group(0)],
                            suggested_classification="INVALID",
                            recommended_action="REWRITE",
                            related_invariants=["INV-SIGNAL-UPDATES-PROCESS-ONLY"],
                            related_paths=[rel_path, "src/logic/signal/signal_store.py", "tools/xstack/sessionx/process_runtime.py"],
                        )
                    )
                    break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
