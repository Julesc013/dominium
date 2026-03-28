"""E165 knowledge bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E165_KNOWLEDGE_BYPASS_SMELL"


class KnowledgeBypassSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = ("src/", "tools/xstack/sessionx/")

_KNOWLEDGE_BYPASS_PATTERNS = (
    re.compile(r"\bstate\s*\[\s*[\"']knowledge_receipts[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bknowledge_receipts\s*\.append\s*\(", re.IGNORECASE),
    re.compile(r"\bsubject_knowledge\b\s*=", re.IGNORECASE),
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
                    if not any(pattern.search(snippet) for pattern in _KNOWLEDGE_BYPASS_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.knowledge_bypass_smell",
                            severity="VIOLATION",
                            confidence=0.93,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["knowledge receipt mutation outside process-mediated SIG path", snippet[:140]],
                            suggested_classification="INVALID",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-DIRECT-KNOWLEDGE-TRANSFER"],
                            related_paths=[rel_path, "signals/transport/transport_engine.py"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

