"""E287 hidden-unlock smell analyzer for PROC-4 maturity gating discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E287_HIDDEN_UNLOCK_SMELL"


class HiddenUnlockSmell:
    analyzer_id = ANALYZER_ID


_HIDDEN_UNLOCK_PATTERNS = (
    re.compile(r"\bprocess_capsule_eligible\s*=\s*True\b", re.IGNORECASE),
    re.compile(r"\bcurrent_maturity_state\s*=\s*[\"']capsule_eligible[\"']", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "process"),
        os.path.join(repo_root, "tools", "process"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/process/process_run_engine.py",
        "src/process/maturity/maturity_engine.py",
        "tools/xstack/repox/check.py",
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
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _HIDDEN_UNLOCK_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.hidden_unlock_smell",
                            severity="RISK",
                            confidence=0.89,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "hidden process maturity/capsule unlock detected outside canonical PROC-4 gating path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-MAGIC-UNLOCKS",
                            ],
                            related_paths=[
                                rel_path,
                                "src/process/process_run_engine.py",
                                "src/process/maturity/maturity_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
