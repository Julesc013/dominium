"""E192 infinite cascade smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E192_INFINITE_CASCADE_SMELL"


class InfiniteCascadeSmell:
    analyzer_id = ANALYZER_ID


_UNBOUNDED_LOOP_PATTERN = re.compile(r"\bwhile\s+True\b", re.IGNORECASE)
_CASCADE_CONTEXT_PATTERN = re.compile(r"\b(?:cascade|fault|trip|protection)\b", re.IGNORECASE)


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
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    required_runtime_tokens = (
        "cascade_max_iterations",
        "cascade_iteration_limit_reached",
        "for iteration_index in range(int(cascade_max_iterations))",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.infinite_cascade_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=runtime_rel,
                line=1,
                evidence=["missing bounded electrical cascade control token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ELEC-CASCADE-BOUNDED"],
                related_paths=[runtime_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "electric"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
        "schema/",
        "schemas/",
    )
    allowed_files = {runtime_rel}
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
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _UNBOUNDED_LOOP_PATTERN.search(snippet):
                        continue
                    if not _CASCADE_CONTEXT_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.infinite_cascade_smell",
                            severity="RISK",
                            confidence=0.83,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["unbounded loop in electrical cascade context", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-ELEC-CASCADE-BOUNDED"],
                            related_paths=[rel_path, runtime_rel],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

