"""E170 ad-hoc loss smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E170_ADHOC_LOSS_SMELL"


class AdHocLossSmell:
    analyzer_id = ANALYZER_ID


_LOSS_PATTERNS = (
    re.compile(r"\bloss_permille\b", re.IGNORECASE),
    re.compile(r"\bfield_loss_modifier_permille\b", re.IGNORECASE),
    re.compile(r"\bdelivery_state\s*=\s*[\"']lost[\"']", re.IGNORECASE),
    re.compile(r"\breturn\s+[\"']lost[\"']", re.IGNORECASE),
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
        "signals/transport/transport_engine.py",
        "signals/transport/channel_executor.py",
        "tools/auditx/analyzers/e170_adhoc_loss_smell.py",
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
                if not any(pattern.search(snippet) for pattern in _LOSS_PATTERNS):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.adhoc_loss_smell",
                        severity="RISK",
                        confidence=0.85,
                        file_path=rel_path,
                        line=line_no,
                        evidence=["loss logic appears outside SIG transport quality layer", snippet[:140]],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-LOSS-POLICY-REGISTERED"],
                        related_paths=[rel_path, "signals/transport/transport_engine.py"],
                    )
                )
                break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
