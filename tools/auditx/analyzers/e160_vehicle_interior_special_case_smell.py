"""E160 vehicle interior special-case smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E160_VEHICLE_INTERIOR_SPECIAL_CASE_SMELL"


class VehicleInteriorSpecialCaseSmell:
    analyzer_id = ANALYZER_ID


_SPECIAL_CASE_PATTERNS = (
    re.compile(r"\bif\b[^\n]*(?:vehicle|train|rail|car|plane|boat)[^\n]*(?:cabin|interior|pressure|smoke|flood)", re.IGNORECASE),
    re.compile(r"\bvehicle_cabin_(?:pressure|oxygen|smoke|flood|leak)\b", re.IGNORECASE),
    re.compile(r"\b(?:cabin|cockpit)_only\b", re.IGNORECASE),
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
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "src/interior/compartment_flow_engine.py",
        "src/interior/compartment_flow_builder.py",
        "src/inspection/inspection_engine.py",
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
                    if not any(pattern.search(snippet) for pattern in _SPECIAL_CASE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.vehicle_interior_special_case_smell",
                            severity="RISK",
                            confidence=0.88,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["vehicle interior special-case detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-INTERIORS-USE-INT-SUBSTRATE",
                                "INV-NO-ADHOC-VEHICLE-CABIN-LOGIC",
                            ],
                            related_paths=[
                                rel_path,
                                "docs/mobility/VEHICLE_INTERIORS.md",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
