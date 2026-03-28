"""E167 non-deterministic queue order smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E167_NON_DETERMINISTIC_QUEUE_ORDER_SMELL"


class NonDeterministicQueueOrderSmell:
    analyzer_id = ANALYZER_ID


_UNSORTED_QUEUE_LOOP_PATTERN = re.compile(
    r"\bfor\s+\w+\s+in\s+queue_rows\b(?!\s*\))|\bfor\s+\w+\s+in\s+signal_transport_queue_rows\b",
    re.IGNORECASE,
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

    scan_root = os.path.join(repo_root, "src", "signals")
    if not os.path.isdir(scan_root):
        return findings

    allow_files = {
        "tools/auditx/analyzers/e167_nondeterministic_queue_order_smell.py",
    }
    for walk_root, _dirs, files in os.walk(scan_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(walk_root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path in allow_files:
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if not _UNSORTED_QUEUE_LOOP_PATTERN.search(snippet):
                    continue
                if "sorted(" in snippet:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.nondeterministic_queue_order_smell",
                        severity="RISK",
                        confidence=0.83,
                        file_path=rel_path,
                        line=line_no,
                        evidence=["queue processing appears unsorted", snippet[:140]],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-ADHOC-CAPACITY-LOGIC"],
                        related_paths=[rel_path, "signals/transport/channel_executor.py"],
                    )
                )
                break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

