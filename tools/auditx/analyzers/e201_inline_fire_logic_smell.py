"""E201 inline fire/combustion logic smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E201_INLINE_FIRE_LOGIC_SMELL"


class InlineFireLogicSmell:
    analyzer_id = ANALYZER_ID


_INLINE_FIRE_PATTERN = re.compile(
    r"\b(?:fire|ignition|combust|fuel_remaining|spread_threshold|heat_release_rate)\b[^\n]*(?:=|\.append\(|\.extend\()",
    re.IGNORECASE,
)

_EXEMPT_SNIPPET_TOKENS = (
    "model_type.therm_ignite_stub",
    "model_type.therm_combust_stub",
    "model.therm_ignite_stub",
    "model.therm_combust_stub",
    "process.start_fire",
    "process.fire_tick",
    "process.end_fire",
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
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "models/model_engine.py",
        "thermal/network/thermal_network_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "inspection/inspection_engine.py",
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
                    if not _INLINE_FIRE_PATTERN.search(snippet):
                        continue
                    lower = snippet.lower()
                    if any(token in lower for token in _EXEMPT_SNIPPET_TOKENS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_fire_logic_smell",
                            severity="RISK",
                            confidence=0.85,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["fire/combustion logic detected outside canonical model/process pathway", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-FIRE-MODEL-ONLY", "INV-NO-ADHOC-BURN-LOGIC"],
                            related_paths=[
                                rel_path,
                                "thermal/network/thermal_network_engine.py",
                                "models/model_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

