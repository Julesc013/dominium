"""E2 Truth-over-net smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E2_TRUTH_OVER_NET_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/",
    "tools/xstack/controlx/",
    "tools/xstack/registry_compile/",
    "server/",
    "client/",
    "docs/net/",
)


TRUTH_OVER_NET_RE = re.compile(
    r"(truthmodel|truth_model).*(serialize|json|packet|socket|network|replication|delta|snapshot)"
    r"|"
    r"(serialize|json|packet|socket|network|replication|delta|snapshot).*(truthmodel|truth_model)",
    re.IGNORECASE,
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_code_files(repo_root: str):
    roots = (
        os.path.join(repo_root, "tools", "xstack"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
    )
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, dirs, files in os.walk(root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                ext = os.path.splitext(name.lower())[1]
                if ext not in {".py", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}:
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(("tools/xstack/testx/tests/", "tools/auditx/", "tools/xstack/auditx/")):
                    continue
                yield rel_path, abs_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path, abs_path in _iter_code_files(repo_root):
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            lower = str(line).lower()
            if "truth_snapshot_hash" in lower:
                continue
            if "perceived" in lower and "truth_model" not in lower and "truthmodel" not in lower:
                continue
            if TRUTH_OVER_NET_RE.search(str(line)):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.truth_over_net_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "Potential TruthModel network serialization smell.",
                            line.strip()[:200],
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-TRUTH-OVER-NET"],
                        related_paths=[rel_path],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
