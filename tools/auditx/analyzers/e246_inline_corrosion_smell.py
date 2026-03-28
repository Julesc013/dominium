"""E246 inline corrosion/fouling/scaling smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E246_INLINE_CORROSION_SMELL"


class InlineCorrosionSmell:
    analyzer_id = ANALYZER_ID


_INLINE_PATTERNS = (
    re.compile(r"\bcorrosion_(?:rate|level)\b\s*=", re.IGNORECASE),
    re.compile(r"\bfouling_(?:rate|level)\b\s*=", re.IGNORECASE),
    re.compile(r"\bscaling_(?:rate|level)\b\s*=", re.IGNORECASE),
    re.compile(r"\bdegradation_level\b\s*=", re.IGNORECASE),
)

_SCAN_PREFIXES = (
    "src/chem/",
    "src/fluid/",
    "src/thermal/",
    "src/mechanics/",
    "tools/xstack/sessionx/",
)

_SKIP_PREFIXES = (
    "docs/",
    "schema/",
    "schemas/",
    "tools/auditx/analyzers/",
    "tools/xstack/testx/tests/",
)

_ALLOWED_FILES = {
    "chem/degradation/degradation_engine.py",
    "models/model_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/repox/check.py",
}


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
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    for scan_root in scan_roots:
        if not os.path.isdir(scan_root):
            continue
        for root, _dirs, files in os.walk(scan_root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                if not rel_path.startswith(_SCAN_PREFIXES):
                    continue
                if rel_path.startswith(_SKIP_PREFIXES):
                    continue
                if rel_path in _ALLOWED_FILES:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _INLINE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_corrosion_smell",
                            severity="RISK",
                            confidence=0.84,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline degradation assignment detected outside CHEM model engine", snippet[:160]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-DEGRADATION-MODEL-ONLY",
                                "INV-NO-ADHOC-PIPE-RESTRICTION",
                            ],
                            related_paths=[
                                rel_path,
                                "chem/degradation/degradation_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
