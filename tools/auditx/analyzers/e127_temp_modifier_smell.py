"""E127 temp modifier smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E127_TEMP_MODIFIER_SMELL"
_TEMP_PATTERNS = (
    re.compile(r"state\[[\"'](?:interior_movement_constraints|temporary_[^\"']+|temp_[^\"']+)[\"']\]\s*="),
    re.compile(r"\b(speed|traction|visibility)\b\s*\*=\s*(?:0?\.\d+|\d+\s*/\s*\d+)"),
    re.compile(r"\bif\b[^\n]*(damag|smoke|flood)[^\n]*\b(speed|traction|visibility)\b"),
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

    effect_engine_rel = "src/control/effects/effect_engine.py"
    if not _read_text(repo_root, effect_engine_rel):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.temp_modifier_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=effect_engine_rel,
                line=1,
                evidence=["missing effect engine module"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-EFFECT-USES-ENGINE"],
                related_paths=[effect_engine_rel],
            )
        )
        return findings

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if not snippet or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _TEMP_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.temp_modifier_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["ad-hoc temporary modifier pattern outside effect engine", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-NO-ADHOC-TEMP-MODIFIERS"],
                            related_paths=[rel_path, effect_engine_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

