"""E164 direct message smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E164_DIRECT_MESSAGE_SMELL"


class DirectMessageSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = ("src/", "tools/xstack/sessionx/")

_DIRECT_MESSAGE_PATTERNS = (
    re.compile(r"\b(?:inbox|mailbox|message_queue)\b\s*\.append\s*\(", re.IGNORECASE),
    re.compile(r"\b(?:inbox|mailbox|message_queue)\b\s*\[", re.IGNORECASE),
    re.compile(r"\b(?:broadcast|send)\w*\s*\(", re.IGNORECASE),
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

    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    )
    allowed_files = {
        "signals/transport/transport_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
    }
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
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
                    if not any(pattern.search(snippet) for pattern in _DIRECT_MESSAGE_PATTERNS):
                        continue
                    if "signal" in snippet.lower() or "message" in snippet.lower() or "broadcast" in snippet.lower():
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.direct_message_smell",
                                severity="RISK",
                                confidence=0.88,
                                file_path=rel_path,
                                line=line_no,
                                evidence=["possible direct message propagation outside SIG transport path", snippet[:140]],
                                suggested_classification="TODO-BLOCKED",
                                recommended_action="REWRITE",
                                related_invariants=["INV-SIGNAL-TRANSPORT-ONLY"],
                                related_paths=[rel_path, "signals/transport/transport_engine.py"],
                            )
                        )
                        break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

