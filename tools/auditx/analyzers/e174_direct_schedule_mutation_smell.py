"""E174 direct schedule mutation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E174_DIRECT_SCHEDULE_MUTATION_SMELL"


class DirectScheduleMutationSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = ("src/signals/", "tools/xstack/sessionx/")

_MUTATION_PATTERNS = (
    re.compile(r"\btravel_schedules?\b", re.IGNORECASE),
    re.compile(r"\bprocess\.travel_schedule_set\b", re.IGNORECASE),
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
        "signals/institutions/dispatch_engine.py",
        "tools/auditx/analyzers/e174_direct_schedule_mutation_smell.py",
    }
    scan_roots = (
        os.path.join(repo_root, "src", "signals"),
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
                if rel_path in allow_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _MUTATION_PATTERNS):
                        continue
                    if ("=" not in snippet) and ("append(" not in snippet) and ("update(" not in snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.direct_schedule_mutation_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible direct travel schedule mutation outside dispatch control path", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-INSTITUTIONAL-SCHEDULES-THROUGH-CTRL"],
                            related_paths=[rel_path, "signals/institutions/dispatch_engine.py"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
