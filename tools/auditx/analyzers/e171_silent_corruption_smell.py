"""E171 silent corruption smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E171_SILENT_CORRUPTION_SMELL"


class SilentCorruptionSmell:
    analyzer_id = ANALYZER_ID


_CORRUPTION_PATTERN = re.compile(r"\bcorrupt(?:ed|ion)?\b", re.IGNORECASE)


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

    transport_rel = "signals/transport/transport_engine.py"
    executor_rel = "signals/transport/channel_executor.py"
    transport_text = _read_text(repo_root, transport_rel)
    executor_text = _read_text(repo_root, executor_rel)

    if "corrupted" in transport_text and "build_message_delivery_event(" not in transport_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_corruption_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=transport_rel,
                line=1,
                evidence=["transport includes corruption states but no delivery event builder usage"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-MESSAGE-DROP"],
                related_paths=[transport_rel],
            )
        )
    if "corrupted" in executor_text and "corrupted_view" not in executor_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_corruption_smell",
                severity="RISK",
                confidence=0.88,
                file_path=executor_rel,
                line=1,
                evidence=["channel executor emits corruption state without explicit corruption metadata marker"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-MESSAGE-DROP"],
                related_paths=[executor_rel],
            )
        )

    allow_files = {
        transport_rel,
        executor_rel,
        "tools/auditx/analyzers/e171_silent_corruption_smell.py",
    }
    scan_root = os.path.join(repo_root, "src")
    if os.path.isdir(scan_root):
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
                    if not _CORRUPTION_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.silent_corruption_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible corruption handling outside SIG transport event path", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-DIRECT-MESSAGE-DROP"],
                            related_paths=[rel_path, transport_rel],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
