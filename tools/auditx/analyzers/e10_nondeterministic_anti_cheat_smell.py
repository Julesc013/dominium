"""E10 Non-deterministic anti-cheat smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E10_NONDETERMINISTIC_ANTI_CHEAT_SMELL"
WATCH_PREFIXES = (
    "src/net/anti_cheat/",
    "src/net/policies/",
    "src/net/srz/",
)

SCAN_ROOTS = (
    "src/net/anti_cheat",
    "src/net/policies",
    "src/net/srz",
)
FORBIDDEN_PATTERNS = (
    (r"\btime\.time\s*\(", "time.time"),
    (r"\btime\.perf_counter\s*\(", "time.perf_counter"),
    (r"\btime\.monotonic\s*\(", "time.monotonic"),
    (r"\bdatetime\.(datetime\.)?now\s*\(", "datetime.now"),
    (r"\bdate\.today\s*\(", "date.today"),
    (r"\brandom\.", "random module"),
    (r"\buuid\.uuid4\s*\(", "uuid4"),
    (r"\bsleep\s*\(", "sleep"),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_paths(repo_root: str):
    for root in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            for filename in sorted(files):
                _, ext = os.path.splitext(filename.lower())
                if ext not in (".py", ".c", ".cc", ".cpp", ".h", ".hpp"):
                    continue
                abs_path = os.path.join(walk_root, filename)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                yield rel_path, abs_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    anti_engine_rel = "src/net/anti_cheat/anti_cheat_engine.py"
    anti_engine_abs = os.path.join(repo_root, anti_engine_rel.replace("/", os.sep))
    if os.path.isfile(anti_engine_abs):
        try:
            anti_text = open(anti_engine_abs, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            anti_text = ""
        for token in ("_event_id(", "_action_id(", "canonical_sha256(", "tick"):
            if token not in anti_text:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.nondeterministic_anti_cheat_smell",
                        severity="RISK",
                        confidence=0.82,
                        file_path=anti_engine_rel,
                        line=1,
                        evidence=["anti-cheat engine missing deterministic construction token '{}'".format(token)],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-ANTI_CHEAT-POLICY-REGISTRY-VALID", "INV-NO-HIDDEN-BAN"],
                        related_paths=[anti_engine_rel],
                    )
                )

    for rel_path, abs_path in _iter_paths(repo_root):
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            source = str(line)
            lower = source.lower()
            if lower.strip().startswith("#"):
                continue
            for pattern, label in FORBIDDEN_PATTERNS:
                if re.search(pattern, source, flags=re.IGNORECASE):
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="net.nondeterministic_anti_cheat_smell",
                            severity="VIOLATION",
                            confidence=0.96,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "non-deterministic token '{}' detected in anti-cheat/network path".format(label),
                                source.strip()[:200],
                            ],
                            suggested_classification="INVALID",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-ANTI_CHEAT-POLICY-REGISTRY-VALID"],
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

