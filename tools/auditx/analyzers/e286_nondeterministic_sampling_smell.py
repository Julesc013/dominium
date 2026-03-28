"""E286 nondeterministic-sampling smell analyzer for PROC-3 discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E286_NONDETERMINISTIC_SAMPLING_SMELL"


class NondeterministicSamplingSmell:
    analyzer_id = ANALYZER_ID


_NONDETERMINISTIC_PATTERNS = (
    re.compile(r"\brandom\.(?:random|randint|randrange|choice|choices|uniform)\s*\(", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\buuid4\s*\(", re.IGNORECASE),
    re.compile(r"\btime\.(?:time|time_ns|perf_counter)\s*\(", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "process", "qc"),
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
                    if not any(pattern.search(snippet) for pattern in _NONDETERMINISTIC_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="determinism.nondeterministic_sampling_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "nondeterministic source detected in PROC-3 QC sampling path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-SAMPLING-DETERMINISTIC",
                            ],
                            related_paths=[
                                rel_path,
                                "process/qc/qc_engine.py",
                                "data/registries/sampling_strategy_registry.json",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
