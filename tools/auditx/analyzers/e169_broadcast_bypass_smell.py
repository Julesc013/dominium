"""E169 broadcast bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E169_BROADCAST_BYPASS_SMELL"


class BroadcastBypassSmell:
    analyzer_id = ANALYZER_ID


_BROADCAST_PATTERNS = (
    re.compile(r"\bbroadcast_subject_ids\b", re.IGNORECASE),
    re.compile(r"\bbroadcast_scope\b", re.IGNORECASE),
    re.compile(r"\bgroup_id\b", re.IGNORECASE),
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

    allow_files = {
        "src/signals/addressing/address_engine.py",
        "src/signals/transport/transport_engine.py",
        "tools/auditx/analyzers/e169_broadcast_bypass_smell.py",
    }
    scan_root = os.path.join(repo_root, "src")
    if not os.path.isdir(scan_root):
        return findings

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
                if not any(pattern.search(snippet) for pattern in _BROADCAST_PATTERNS):
                    continue
                if "recipient_address" in snippet:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.broadcast_bypass_smell",
                        severity="RISK",
                        confidence=0.86,
                        file_path=rel_path,
                        line=line_no,
                        evidence=["broadcast/group semantics outside address engine", snippet[:140]],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-DIRECT-ARTIFACT-DELIVERY"],
                        related_paths=[rel_path, "src/signals/addressing/address_engine.py"],
                    )
                )
                break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
